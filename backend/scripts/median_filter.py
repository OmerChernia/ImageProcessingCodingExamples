import cv2
import numpy as np
import os

def apply_median_filter(image, kernel_size):
    """Apply median filter to the image with specified kernel size"""
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.medianBlur(image, kernel_size)

def compute_histograms(image):
    """Compute regular and cumulative histograms."""
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    return hist, hist_cum

def main():
    print("\nMedian Filter Tool")
    print("------------------")
    print("Enter the path to your image file (or 'q' to quit)")

    while True:
        image_path = input("Image path: ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break

        if not os.path.exists(image_path):
            print(f"Error: File '{image_path}' not found.")
            continue

        # Load the image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print("Error: Could not load image.")
            continue

        while True:
            try:
                kernel_size = int(input("Enter kernel size (odd number, e.g., 3, 5, 7): ").strip())
                if kernel_size < 3:
                    print("Kernel size must be at least 3")
                    continue
                if kernel_size % 2 == 0:
                    print("Kernel size must be odd. Adding 1 to make it odd.")
                    kernel_size += 1
                break
            except ValueError:
                print("Please enter a valid number")

        # Process image
        try:
            processed_image = apply_median_filter(image, kernel_size)
            # Save result
            output_path = f"{os.path.splitext(image_path)[0]}_median_{kernel_size}.png"
            cv2.imwrite(output_path, processed_image)
            print(f"\nProcessed image saved as: {output_path}")
        except Exception as e:
            print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main() 