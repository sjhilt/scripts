"""
Extract significant frames from a video when the percentage of change between frames exceeds a given threshold.

Author: Stephen Hilt
Date: 03-10-2025

Requirements:
- Install required packages before running the script:
  pip install opencv-python numpy argparse
"""

import cv2
import numpy as np
import os
import argparse

def calculate_frame_difference(frame1, frame2):
    """
    Calculate the percentage of pixel difference between two frames.

    Args:
        frame1 (numpy.ndarray): The first frame (previous frame).
        frame2 (numpy.ndarray): The second frame (current frame).

    Returns:
        float: The percentage of pixel change between the two frames.
    """
    diff = cv2.absdiff(frame1, frame2)  # Compute absolute difference between frames
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)  # Convert difference to grayscale
    _, threshold_diff = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)  # Apply threshold to highlight significant changes
    changed_pixels = np.count_nonzero(threshold_diff)  # Count non-zero (changed) pixels
    total_pixels = frame1.shape[0] * frame1.shape[1]  # Compute total pixels in the frame
    change_percentage = (changed_pixels / total_pixels) * 100  # Compute percentage change

    return change_percentage

def extract_significant_frames(video_path, output_dir, change_threshold=50.0):
    """
    Extract frames from a video when the percentage of change is greater than the specified threshold.

    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory where extracted frames will be saved.
        change_threshold (float): Percentage of change required to save a frame.
    """
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it does not exist
    
    cap = cv2.VideoCapture(video_path)  # Open the video file
    ret, prev_frame = cap.read()  # Read the first frame
    
    if not ret:
        print("Error: Could not read video file.")
        return

    frame_count = 0  # Counter for frame index
    extracted_frames = 0  # Counter for saved frames

    while True:
        ret, curr_frame = cap.read()  # Read next frame
        if not ret:
            break  # Exit loop if no more frames

        # Calculate frame difference percentage
        change_percentage = calculate_frame_difference(prev_frame, curr_frame)

        # Save frame if change exceeds the threshold
        if change_percentage > change_threshold:
            frame_filename = os.path.join(output_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, curr_frame)
            extracted_frames += 1
            print(f"Saved: {frame_filename} | Change: {change_percentage:.2f}%")

        prev_frame = curr_frame  # Update previous frame for next iteration
        frame_count += 1  # Increment frame counter

    cap.release()  # Release video capture
    print(f"Extraction complete! {extracted_frames} frames saved.")

if __name__ == "__main__":
    # Set up argument parser for command-line input
    parser = argparse.ArgumentParser(description="Extract frames from a video if the % of change is greater than a threshold.")
    parser.add_argument("video_path", type=str, help="Path to the input video file")
    parser.add_argument("--output_dir", type=str, default="output_frames", help="Directory to save extracted frames")
    parser.add_argument("--threshold", type=float, default=50.0, help="Percentage of change threshold for saving frames")

    args = parser.parse_args()

    # Debugging: Confirm the threshold value is received correctly
    print(f"Using threshold: {args.threshold}%")

    # Call function to extract significant frames
    extract_significant_frames(args.video_path, args.output_dir, args.threshold)
