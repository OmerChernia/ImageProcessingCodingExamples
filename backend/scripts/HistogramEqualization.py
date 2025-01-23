import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import os

def compute_histograms(image):
    """Compute regular and cumulative histograms."""
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    return hist, hist_cum

def apply_histogram_equalization(image):
    """Apply histogram equalization using OpenCV's built-in function."""
    return cv2.equalizeHist(image)

def plot_analysis(image_path):
    """Plot analysis of the image before and after equalization."""
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load image.")
        return

    # Compute histograms for original
    hist_orig, cum_orig = compute_histograms(image)

    # Equalize
    equalized = apply_histogram_equalization(image)
    hist_eq, cum_eq = compute_histograms(equalized)

    # Plot
    fig = plt.figure(figsize=(10, 6))
    gs = fig.add_gridspec(2, 2)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(image, cmap='gray')
    ax1.set_title('Original Image')
    ax1.axis('off')

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(hist_orig, color='blue')
    ax2.set_title('Histogram (Original)')
    ax2.set_xlabel('Intensity')
    ax2.set_ylabel('Count')

    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(cum_orig, color='blue')
    ax3.set_title('Cumulative (Original)')
    ax3.set_xlabel('Intensity')
    ax3.set_ylabel('Cumulative')

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(cum_eq, color='green')
    ax4.set_title('Cumulative (Equalized)')
    ax4.set_xlabel('Intensity')
    ax4.set_ylabel('Cumulative')

    # Add cursor for the last subplot
    cursor4 = Cursor(ax4, useblit=True, color='red', linewidth=1)
    ax4.format_coord = lambda x, y: f'Intensity: {int(x)}, Cumulative: {y:.3f}'

    plt.tight_layout()
    plt.show()

    # Ask if user wants to save the equalized image
    while True:
        save = input("\nDo you want to save the equalized image? (y/n): ").strip().lower()
        if save in ['y', 'n']:
            break
        print("Please enter 'y' for yes or 'n' for no.")

    if save == 'y':
        base_name = os.path.splitext(image_path)[0]
        ext = os.path.splitext(image_path)[1]
        output_path = f"{base_name}_equalized{ext}"
        cv2.imwrite(output_path, equalized)
        print(f"Image saved as: {output_path}")

    print("\nHistogram Equalization Analysis Tool")

def main():
    print("\nHistogram Equalization Analysis Tool")
    print("----------------------------------")
    print("Enter the path to your image file (or 'q' to quit)")
    print("Example: images/test.jpg or ./photo.png\n")

    while True:
        image_path = input("Image path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break

        if image_path:
            plot_analysis(image_path)
        else:
            print("Please enter a valid path or 'q' to quit.")

if __name__ == "__main__":
    main() 