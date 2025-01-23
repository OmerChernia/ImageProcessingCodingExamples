import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_histograms(image_path):
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load image.")
        return

    # Compute histogram
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(image, cmap='gray')
    axes[0].set_title('Image')
    axes[0].axis('off')

    axes[1].plot(hist, color='blue')
    axes[1].set_title('Histogram')
    axes[1].set_xlabel('Intensity')
    axes[1].set_ylabel('Count')

    axes[2].plot(hist_cum, color='green')
    axes[2].set_title('Cumulative Histogram')
    axes[2].set_xlabel('Intensity')
    axes[2].set_ylabel('Cumulative')

    plt.tight_layout()
    plt.show()

def main():
    print("\nHistogram Plot Tool")
    print("------------------")
    print("Enter the path to your image file (or 'q' to quit)")

    while True:
        image_path = input("Image path: ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break

        if image_path:
            plot_histograms(image_path)
        else:
            print("Please enter a valid path or 'q' to quit.")

if __name__ == "__main__":
    main()