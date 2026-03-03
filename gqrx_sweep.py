#!/usr/bin/env python3
"""
GQRX Antenna Sweep Tool
Connects to a GQRX remote control socket and sweeps frequencies
to determine the best reception range for the connected antenna.
"""

import socket
import time
import argparse
import csv
import sys
from datetime import datetime


class GqrxConnection:
    """Manages the TCP socket connection to GQRX's remote control interface."""

    def __init__(self, host="127.0.0.1", port=7356, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        """Establish connection to GQRX."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            print(f"[+] Connected to GQRX at {self.host}:{self.port}")
            return True
        except socket.error as e:
            print(f"[!] Connection failed: {e}")
            return False

    def disconnect(self):
        """Close the connection."""
        if self.sock:
            try:
                self.sock.close()
            except socket.error:
                pass
            self.sock = None
            print("[+] Disconnected from GQRX")

    def _send_command(self, command):
        """Send a command to GQRX and return the response."""
        if not self.sock:
            raise ConnectionError("Not connected to GQRX")
        try:
            self.sock.sendall((command + "\n").encode())
            response = b""
            while True:
                chunk = self.sock.recv(4096)
                response += chunk
                if b"\n" in chunk:
                    break
            return response.decode().strip()
        except socket.error as e:
            raise ConnectionError(f"Communication error: {e}")

    def set_frequency(self, freq_hz):
        """Set the receiver frequency in Hz."""
        resp = self._send_command(f"F {int(freq_hz)}")
        return "RPRT 0" in resp

    def get_frequency(self):
        """Get the current receiver frequency in Hz."""
        resp = self._send_command("f")
        try:
            return int(resp.split("\n")[0])
        except (ValueError, IndexError):
            return None

    def get_signal_strength(self):
        """Get the current signal strength (dBFS)."""
        resp = self._send_command("l STRENGTH")
        try:
            return float(resp.split("\n")[0])
        except (ValueError, IndexError):
            return None

    def set_mode(self, mode, bandwidth=0):
        """Set demodulator mode (FM, AM, WFM, USB, LSB, CW)."""
        resp = self._send_command(f"M {mode} {bandwidth}")
        return "RPRT 0" in resp

    def get_mode(self):
        """Get the current demodulator mode."""
        resp = self._send_command("m")
        return resp.split("\n")[0] if resp else None


def parse_frequency(freq_str):
    """Parse a frequency string with optional suffix (K, M, G)."""
    freq_str = freq_str.strip().upper()
    multipliers = {"K": 1e3, "M": 1e6, "G": 1e9}
    for suffix, mult in multipliers.items():
        if freq_str.endswith(suffix):
            return int(float(freq_str[:-1]) * mult)
    return int(float(freq_str))


def format_freq(freq_hz):
    """Format a frequency in Hz to a human-readable string."""
    if freq_hz >= 1e9:
        return f"{freq_hz / 1e9:.3f} GHz"
    elif freq_hz >= 1e6:
        return f"{freq_hz / 1e6:.3f} MHz"
    elif freq_hz >= 1e3:
        return f"{freq_hz / 1e3:.1f} kHz"
    return f"{freq_hz:.0f} Hz"


class AntennaSweeper:
    """Performs frequency sweeps and analyzes antenna performance."""

    def __init__(self, connection, start_freq, end_freq, step_size,
                 dwell_time=0.5, samples_per_step=3):
        self.conn = connection
        self.start_freq = start_freq
        self.end_freq = end_freq
        self.step_size = step_size
        self.dwell_time = dwell_time
        self.samples_per_step = samples_per_step
        self.results = []  # list of (freq_hz, avg_signal_dbfs)

    def _measure_at_frequency(self, freq_hz):
        """Take multiple signal strength readings at a frequency and average."""
        if not self.conn.set_frequency(freq_hz):
            print(f"  [!] Failed to set frequency {format_freq(freq_hz)}")
            return None
        # Let the receiver settle
        time.sleep(self.dwell_time)
        readings = []
        for _ in range(self.samples_per_step):
            strength = self.conn.get_signal_strength()
            if strength is not None:
                readings.append(strength)
            time.sleep(0.05)
        if not readings:
            return None
        return sum(readings) / len(readings)

    def sweep(self):
        """Perform the full frequency sweep."""
        self.results = []
        num_steps = int((self.end_freq - self.start_freq) / self.step_size) + 1
        print(f"\n{'='*60}")
        print(f"  ANTENNA SWEEP")
        print(f"  Range: {format_freq(self.start_freq)} -> {format_freq(self.end_freq)}")
        print(f"  Step:  {format_freq(self.step_size)}  |  Steps: {num_steps}")
        print(f"  Dwell: {self.dwell_time}s  |  Samples/step: {self.samples_per_step}")
        print(f"{'='*60}\n")

        for i in range(num_steps):
            freq = self.start_freq + i * self.step_size
            if freq > self.end_freq:
                break
            avg_db = self._measure_at_frequency(freq)
            if avg_db is not None:
                self.results.append((freq, avg_db))
                bar_len = max(0, int((avg_db + 120) / 2))
                bar = "█" * bar_len
                print(f"  {format_freq(freq):>14s}  {avg_db:7.1f} dBFS  {bar}")
            else:
                print(f"  {format_freq(freq):>14s}  [no reading]")

        print(f"\n[+] Sweep complete. {len(self.results)} measurements taken.\n")
        return self.results

    def analyze_results(self):
        """Analyze sweep results and find best/worst ranges."""
        if not self.results:
            return None
        sorted_by_signal = sorted(self.results, key=lambda x: x[1], reverse=True)
        best = sorted_by_signal[0]
        worst = sorted_by_signal[-1]
        avg_signal = sum(r[1] for r in self.results) / len(self.results)

        # Find the best contiguous range (top 25% signals)
        threshold = avg_signal + (best[1] - avg_signal) * 0.5
        good_freqs = [r[0] for r in self.results if r[1] >= threshold]
        best_range_start = min(good_freqs) if good_freqs else best[0]
        best_range_end = max(good_freqs) if good_freqs else best[0]

        return {
            "best_freq": best[0],
            "best_signal": best[1],
            "worst_freq": worst[0],
            "worst_signal": worst[1],
            "avg_signal": avg_signal,
            "best_range_start": best_range_start,
            "best_range_end": best_range_end,
            "threshold": threshold,
            "total_measurements": len(self.results),
        }

    def print_report(self):
        """Print a human-readable analysis report."""
        analysis = self.analyze_results()
        if not analysis:
            print("[!] No results to analyze.")
            return
        print(f"{'='*60}")
        print(f"  ANTENNA ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"  Best frequency:    {format_freq(analysis['best_freq'])} "
              f"({analysis['best_signal']:.1f} dBFS)")
        print(f"  Worst frequency:   {format_freq(analysis['worst_freq'])} "
              f"({analysis['worst_signal']:.1f} dBFS)")
        print(f"  Average signal:    {analysis['avg_signal']:.1f} dBFS")
        print(f"  Good range:        {format_freq(analysis['best_range_start'])} "
              f"- {format_freq(analysis['best_range_end'])}")
        print(f"  Threshold used:    {analysis['threshold']:.1f} dBFS")
        print(f"  Measurements:      {analysis['total_measurements']}")
        print(f"{'='*60}")
        spread = analysis['best_signal'] - analysis['worst_signal']
        if spread < 6:
            print("  Verdict: Antenna performs fairly evenly across the range.")
        elif spread < 15:
            print("  Verdict: Antenna has a moderate preference for the good range.")
        else:
            print("  Verdict: Antenna is strongly tuned to the good range.")
        print(f"{'='*60}\n")

    def save_results(self, filename=None):
        """Save sweep results to a CSV file."""
        if not self.results:
            print("[!] No results to save.")
            return
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"antenna_sweep_{ts}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["frequency_hz", "frequency_readable", "signal_dbfs"])
            for freq, signal in self.results:
                writer.writerow([freq, format_freq(freq), f"{signal:.1f}"])
        print(f"[+] Results saved to {filename}")
        return filename


def main():
    parser = argparse.ArgumentParser(
        description="GQRX Antenna Sweep - Find your antenna's best frequency range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --host 192.168.1.50 --start 88M --end 108M --step 500K
  %(prog)s --start 144M --end 148M --step 100K --dwell 1.0
  %(prog)s --start 430M --end 440M --step 250K --samples 5 --output results.csv

Frequency suffixes: K (kHz), M (MHz), G (GHz)
Requires GQRX running with Remote Control enabled (Tools > Remote Control).
        """,
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="GQRX remote control IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7356,
                        help="GQRX remote control port (default: 7356)")
    parser.add_argument("--start", required=True,
                        help="Start frequency (e.g., 88M, 144000000)")
    parser.add_argument("--end", required=True,
                        help="End frequency (e.g., 108M, 148000000)")
    parser.add_argument("--step", required=True,
                        help="Step size (e.g., 500K, 100000)")
    parser.add_argument("--dwell", type=float, default=0.5,
                        help="Dwell time per step in seconds (default: 0.5)")
    parser.add_argument("--samples", type=int, default=3,
                        help="Signal samples per step (default: 3)")
    parser.add_argument("--mode", default=None,
                        help="Set demodulator mode before sweep (FM, AM, WFM, USB, LSB, CW)")
    parser.add_argument("--output", default=None,
                        help="Output CSV filename (auto-generated if omitted)")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save results to CSV")

    args = parser.parse_args()

    # Parse frequencies
    try:
        start_freq = parse_frequency(args.start)
        end_freq = parse_frequency(args.end)
        step_size = parse_frequency(args.step)
    except ValueError as e:
        print(f"[!] Invalid frequency: {e}")
        sys.exit(1)

    if start_freq >= end_freq:
        print("[!] Start frequency must be less than end frequency.")
        sys.exit(1)
    if step_size <= 0:
        print("[!] Step size must be positive.")
        sys.exit(1)

    # Connect to GQRX
    conn = GqrxConnection(host=args.host, port=args.port)
    if not conn.connect():
        print("[!] Could not connect to GQRX. Make sure:")
        print("    1. GQRX is running")
        print("    2. Remote Control is enabled (Tools > Remote Control)")
        print(f"    3. It's listening on {args.host}:{args.port}")
        sys.exit(1)

    try:
        # Optionally set mode
        if args.mode:
            if conn.set_mode(args.mode.upper()):
                print(f"[+] Mode set to {args.mode.upper()}")
            else:
                print(f"[!] Failed to set mode to {args.mode}")

        # Run sweep
        sweeper = AntennaSweeper(
            connection=conn,
            start_freq=start_freq,
            end_freq=end_freq,
            step_size=step_size,
            dwell_time=args.dwell,
            samples_per_step=args.samples,
        )
        sweeper.sweep()
        sweeper.print_report()

        if not args.no_save:
            sweeper.save_results(args.output)

    except KeyboardInterrupt:
        print("\n[!] Sweep interrupted by user.")
    except ConnectionError as e:
        print(f"\n[!] Lost connection to GQRX: {e}")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    main()
