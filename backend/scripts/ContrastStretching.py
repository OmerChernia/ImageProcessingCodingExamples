import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def compute_histograms(image):
    """Compute regular and cumulative histograms."""
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    return hist, hist_cum

def apply_contrast_stretching(image, factor):
    """Apply contrast stretching around the mean intensity."""
    f_image = image.astype(float)
    mean = np.mean(f_image)
    adjusted = mean + factor * (f_image - mean)
    return np.clip(adjusted, 0, 255).astype(np.uint8)

def plot_analysis(image_path, contrast_factor):
    """Plot analysis of the image before and after contrast adjustment."""
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load image.")
        return

    # Compute histograms before
    hist_before, cum_before = compute_histograms(image)

    # Apply contrast adjustment
    adjusted = apply_contrast_stretching(image, contrast_factor)

    # Compute histograms after
    hist_after, cum_after = compute_histograms(adjusted)

    # Plot
    fig = plt.figure(figsize=(12, 6))
    gs = fig.add_gridspec(2, 3)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(image, cmap='gray')
    ax1.set_title('Original')
    ax1.axis('off')

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(hist_before, color='blue')
    ax2.set_title('Histogram (Original)')
    ax2.set_xlabel('Intensity')
    ax2.set_ylabel('Count')

    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(cum_before, color='blue')
    ax3.set_title('Cumulative (Original)')
    ax3.set_xlabel('Intensity')
    ax3.set_ylabel('Cumulative')

    ax4 = fig.add_subplot(gs[1, 0])
    ax4.imshow(adjusted, cmap='gray')
    ax4.set_title(f'Adjusted (factor={contrast_factor:.1f})')
    ax4.axis('off')

    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(hist_after, color='green')
    ax5.set_title('Histogram (Adjusted)')
    ax5.set_xlabel('Intensity')
    ax5.set_ylabel('Count')

    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(cum_after, color='green')
    ax6.set_title('Cumulative (Adjusted)')
    ax6.set_xlabel('Intensity')
    ax6.set_ylabel('Cumulative')

    plt.tight_layout()
    plt.show()

    # Ask if user wants to save
    while True:
        save = input("\nDo you want to save the contrast adjusted image? (y/n): ").strip().lower()
        if save in ['y', 'n']:
            break
        print("Please enter 'y' for yes or 'n' for no.")

    if save == 'y':
        base_name = os.path.splitext(image_path)[0]
        ext = os.path.splitext(image_path)[1]
        output_path = f"{base_name}_contrast{contrast_factor:.1f}{ext}"
        cv2.imwrite(output_path, adjusted)
        print(f"Image saved as: {output_path}")

    print("\nContrast Adjustment Tool")

def main():
    print("\nContrast Adjustment Tool")
    print("----------------------")
    print("Enter the path to your image file (or 'q' to quit)")
    print("Example: images/test.jpg or ./photo.png")
    print("\nContrast factor:")
    print("  > 1.0: increase contrast")
    print("  < 1.0: decrease contrast")
    print("  = 1.0: no change\n")

    while True:
        image_path = input("Image path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break

        if not os.path.exists(image_path):
            print("Error: File not found.")
            continue

        while True:
            try:
                factor = float(input("Enter contrast factor (0.1 - 3.0): ").strip())
                if 0.1 <= factor <= 3.0:
                    break
                else:
                    print("Please enter a value between 0.1 and 3.0")
            except ValueError:
                print("Please enter a valid number")

        plot_analysis(image_path, factor)

if __name__ == "__main__":
    main() 