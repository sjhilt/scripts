#!/usr/bin/env python3
# Author: Stephen J. Hilt & Chris Sistrunk
#   Written for ICS Village to demonstrate
#   how replaying of Modbus packets work.
#
# Updated to support selecting the outgoing NIC by binding to a local source IP,
# independent random blink patterns, and synchronized Morse-code blinking.
# For use with Python 3
#########################################################

import argparse
import random
import socket
import struct
import sys
import time


DEFAULT_COILS = (0, 1)

MORSE_CODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "'": ".----.",
    "!": "-.-.--",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "&": ".-...",
    ":": "---...",
    ";": "-.-.-.",
    "=": "-...-",
    "+": ".-.-.",
    "-": "-....-",
    "_": "..--.-",
    '"': ".-..-.",
    "$": "...-..-",
    "@": ".--.-.",
}


def build_write_single_coil(coil, enabled, transaction_id=2, unit_id=1):
    """Build a Modbus/TCP Write Single Coil request."""
    value = 0xFF00 if enabled else 0x0000
    protocol_id = 0
    length = 6
    function_code = 5
    return struct.pack(
        ">HHHBBHH",
        transaction_id,
        protocol_id,
        length,
        unit_id,
        function_code,
        coil,
        value,
    )


def parse_coils(value):
    try:
        coils = tuple(int(item.strip()) for item in value.split(",") if item.strip() != "")
    except ValueError as err:
        raise argparse.ArgumentTypeError("coils must be comma-separated integers") from err

    if not coils:
        raise argparse.ArgumentTypeError("at least one coil is required")
    if any(coil < 0 or coil > 65535 for coil in coils):
        raise argparse.ArgumentTypeError("coil numbers must be between 0 and 65535")
    return coils


def parse_args():
    parser = argparse.ArgumentParser(
        description="Replay Modbus/TCP packets to blink coils/buttons on a PLC.",
        epilog=(
            "Examples:\n"
            "  python3 py3_modturnt.py 192.168.0.3 --source-ip 192.168.0.22\n"
            "  python3 py3_modturnt.py 192.168.0.3 -s 192.168.0.22 --count 20\n"
            "  python3 py3_modturnt.py 192.168.0.3 -s 192.168.0.22 --mode sequential --once\n"
            "  python3 py3_modturnt.py 192.168.0.3 -s 192.168.0.22 --mode morse --message SOS\n"
            "  python3 py3_modturnt.py 192.168.0.3 -s 192.168.0.22 --morse-mode --message SOS --morse-repeat 0 --morse-pause 10\n"
            "  python3 py3_modturnt.py 192.168.0.3 -s 192.168.0.22 --check-only"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("host", help="Target Modbus/TCP host")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=502,
        help="Target Modbus/TCP port (default: 502)",
    )
    parser.add_argument(
        "-s",
        "--source-ip",
        help=(
            "Local IPv4 address to bind before connecting. Use the IP address "
            "assigned to the NIC you want this traffic to leave from."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("random", "sequential", "morse"),
        default="random",
        help=(
            "Blink mode: independent random per-coil timing, original sequential "
            "pulse pattern, or synchronized Morse code (default: random)"
        ),
    )
    parser.add_argument(
        "--coils",
        type=parse_coils,
        default=DEFAULT_COILS,
        help="Comma-separated coil/button numbers to blink (default: 0,1)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help=(
            "Number of random ON events to send before exiting. "
            "Default loops forever."
        ),
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="For sequential mode, send one on/on/off/off cycle and exit",
    )
    parser.add_argument(
        "--min-on",
        type=float,
        default=0.10,
        help="Random mode minimum seconds a selected coil stays on (default: 0.10)",
    )
    parser.add_argument(
        "--max-on",
        type=float,
        default=0.80,
        help="Random mode maximum seconds a selected coil stays on (default: 0.80)",
    )
    parser.add_argument(
        "--min-gap",
        type=float,
        default=0.05,
        help="Random mode minimum seconds each coil stays off before next blink (default: 0.05)",
    )
    parser.add_argument(
        "--max-gap",
        type=float,
        default=0.60,
        help="Random mode maximum seconds each coil stays off before next blink (default: 0.60)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Sequential mode seconds to wait between Modbus writes (default: 1)",
    )
    parser.add_argument(
        "--morse-mode",
        action="store_true",
        help="Shortcut alias for --mode morse",
    )
    parser.add_argument(
        "--message",
        help="Message to blink as Morse code when using --mode morse or --morse-mode",
    )
    parser.add_argument(
        "--morse-unit",
        type=float,
        default=0.25,
        help=(
            "Morse timing unit in seconds. Dot=1 unit, dash=3 units, "
            "letter gap=3 units, word gap=7 units (default: 0.25)"
        ),
    )
    parser.add_argument(
        "--morse-repeat",
        type=int,
        default=1,
        help="Number of times to repeat the Morse message; use 0 to repeat forever (default: 1)",
    )
    parser.add_argument(
        "--morse-pause",
        type=float,
        default=10.0,
        help="Seconds to pause between repeated Morse messages (default: 10)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="TCP connect/read timeout in seconds (default: 5)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only verify that TCP connect works, then exit without sending Modbus packets",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Optional random seed for repeatable random blink patterns",
    )
    args = parser.parse_args()

    if args.morse_mode:
        args.mode = "morse"

    if args.count is not None and args.count < 1:
        parser.error("--count must be 1 or greater")
    if args.min_on < 0 or args.max_on < 0 or args.min_gap < 0 or args.max_gap < 0:
        parser.error("timing values cannot be negative")
    if args.min_on > args.max_on:
        parser.error("--min-on cannot be greater than --max-on")
    if args.min_gap > args.max_gap:
        parser.error("--min-gap cannot be greater than --max-gap")
    if args.mode == "morse":
        if not args.message:
            parser.error("--message is required when using --mode morse")
        if args.morse_unit <= 0:
            parser.error("--morse-unit must be greater than 0")
        if args.morse_repeat < 0:
            parser.error("--morse-repeat must be 0 or greater")
        if args.morse_pause < 0:
            parser.error("--morse-pause cannot be negative")
        unsupported = sorted({ch for ch in args.message.upper() if ch != " " and ch not in MORSE_CODE})
        if unsupported:
            parser.error("unsupported Morse character(s): {}".format(" ".join(unsupported)))

    return args


def connect(host, port, source_ip=None, timeout=5.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    if source_ip:
        # Binding to a local source IP makes the OS use the NIC that owns that IP.
        # Port 0 tells the OS to choose an available ephemeral source port.
        sock.bind((source_ip, 0))
        print("Using local source IP {}".format(source_ip))

    sock.connect((host, port))
    local_ip, local_port = sock.getsockname()
    print("Connected to {}:{} from {}:{}".format(host, port, local_ip, local_port))
    return sock


def send_packet(sock, packet):
    sock.sendall(packet)
    return sock.recv(4096)


def write_coil(sock, coil, enabled, transaction_id=2):
    packet = build_write_single_coil(coil, enabled, transaction_id=transaction_id)
    send_packet(sock, packet)
    print("coil {} -> {}".format(coil, "ON" if enabled else "OFF"))


def write_coils(sock, coils, enabled):
    """Write the same state to all selected coils/buttons."""
    for coil in coils:
        write_coil(sock, coil, enabled)


def run_sequential(sock, coils, interval, once):
    if len(coils) < 2:
        raise ValueError("sequential mode needs at least two coils")

    coil_0, coil_1 = coils[0], coils[1]
    while True:
        write_coil(sock, coil_0, True)
        time.sleep(interval)
        write_coil(sock, coil_1, True)
        time.sleep(interval)
        write_coil(sock, coil_0, False)
        time.sleep(interval)
        write_coil(sock, coil_1, False)
        time.sleep(interval)

        if once:
            break


def run_random(sock, coils, count, min_on, max_on, min_gap, max_gap):
    """Run independent per-coil random blink schedules."""
    now = time.monotonic()
    states = {coil: False for coil in coils}
    next_toggle = {
        coil: now + random.uniform(min_gap, max_gap)
        for coil in coils
    }
    blink_count = 0

    print(
        "Independent random blink mode on coils {}; press Ctrl+C to stop.".format(
            ",".join(map(str, coils))
        )
    )

    while True:
        if count is not None and blink_count >= count and not any(states.values()):
            break

        coil = min(next_toggle, key=next_toggle.get)
        sleep_for = next_toggle[coil] - time.monotonic()
        if sleep_for > 0:
            time.sleep(sleep_for)

        if states[coil]:
            states[coil] = False
            write_coil(sock, coil, False)
            next_toggle[coil] = time.monotonic() + random.uniform(min_gap, max_gap)
        else:
            if count is not None and blink_count >= count:
                next_toggle[coil] = float("inf")
                continue

            blink_count += 1
            on_time = random.uniform(min_on, max_on)
            states[coil] = True
            print("blink {}: coil {} ON for {:.2f}s".format(blink_count, coil, on_time))
            write_coil(sock, coil, True)
            next_toggle[coil] = time.monotonic() + on_time


def print_morse_preview(message):
    parts = []
    for word in message.upper().split(" "):
        letters = [MORSE_CODE[ch] for ch in word if ch in MORSE_CODE]
        parts.append(" ".join(letters))
    print("Morse: {}".format(" / ".join(parts)))


def blink_symbol(sock, coils, symbol, unit):
    duration = unit if symbol == "." else unit * 3
    print("{} ({:.2f}s)".format("DOT" if symbol == "." else "DASH", duration))
    write_coils(sock, coils, True)
    time.sleep(duration)
    write_coils(sock, coils, False)


def run_morse(sock, coils, message, unit, repeat, pause):
    """Blink a message in Morse code with all selected coils/buttons synchronized.

    Standard timing:
      dot = 1 unit ON
      dash = 3 units ON
      gap between dots/dashes in a letter = 1 unit OFF
      gap between letters = 3 units OFF
      gap between words = 7 units OFF
    """
    message = message.upper()
    print(
        "Synchronized Morse mode on coils {} with unit {:.2f}s".format(
            ",".join(map(str, coils)), unit
        )
    )
    print_morse_preview(message)

    repeat_number = 0
    repeat_forever = repeat == 0

    while repeat_forever or repeat_number < repeat:
        repeat_number += 1
        if repeat_forever:
            print("Morse repeat {} (forever; Ctrl+C to stop)".format(repeat_number))
        elif repeat > 1:
            print("Morse repeat {}/{}".format(repeat_number, repeat))

        words = message.split(" ")
        for word_index, word in enumerate(words):
            letters = [ch for ch in word if ch in MORSE_CODE]
            for letter_index, ch in enumerate(letters):
                pattern = MORSE_CODE[ch]
                print("letter {}: {}".format(ch, pattern))

                for symbol_index, symbol in enumerate(pattern):
                    blink_symbol(sock, coils, symbol, unit)
                    if symbol_index < len(pattern) - 1:
                        time.sleep(unit)

                if letter_index < len(letters) - 1:
                    time.sleep(unit * 3)

            if word_index < len(words) - 1:
                time.sleep(unit * 7)

        if repeat_forever or repeat_number < repeat:
            print("Pausing {:.2f}s before next Morse repeat".format(pause))
            time.sleep(pause)


def main():
    args = parse_args()
    sock = None

    if args.seed is not None:
        random.seed(args.seed)

    try:
        sock = connect(args.host, args.port, args.source_ip, args.timeout)

        if args.check_only:
            print("TCP connectivity check succeeded; no Modbus packets were sent.")
            return 0

        if args.mode == "sequential":
            run_sequential(sock, args.coils, args.interval, args.once)
        elif args.mode == "morse":
            run_morse(sock, args.coils, args.message, args.morse_unit, args.morse_repeat, args.morse_pause)
        else:
            run_random(sock, args.coils, args.count, args.min_on, args.max_on, args.min_gap, args.max_gap)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except (OSError, ValueError) as err:
        print("\n||\n|| Error: {}\n||\n".format(err))
        if args.source_ip:
            print(
                "Check that {} is assigned to the NIC connected to the PLC network.".format(
                    args.source_ip
                )
            )
        return 1
    finally:
        if sock is not None:
            for coil in args.coils:
                try:
                    write_coil(sock, coil, False)
                except OSError:
                    pass
            sock.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
