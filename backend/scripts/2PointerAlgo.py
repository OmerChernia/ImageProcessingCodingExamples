import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def load_and_validate_images(path_a, path_b):
    """Load and validate two grayscale images."""
    # Check if files exist
    if not os.path.exists(path_a) or not os.path.exists(path_b):
        print("Error: One or both image files not found.")
        return None, None
    
    # Load images in grayscale
    img_a = cv2.imread(path_a, cv2.IMREAD_GRAYSCALE)
    img_b = cv2.imread(path_b, cv2.IMREAD_GRAYSCALE)
    
    if img_a is None or img_b is None:
        print("Error: Could not load one or both images.")
        return None, None
        
    return img_a, img_b

def compute_histograms(image):
    """Compute regular, normalized, and cumulative histograms."""
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    norm_hist = hist / hist.sum()
    cum_hist = norm_hist.cumsum()
    return hist, norm_hist, cum_hist

def find_monotonic_mapping(cum_hist_a, cum_hist_b):
    """Create a monotonic intensity mapping from Image A to Image B 
    using 2-pointer technique on their cumulative histograms."""
    mapping = np.full(256, -1, dtype=int)
    ptr_b = 0

    for intensity_a in range(256):
        target_cum = cum_hist_a[intensity_a]

        # Find matching cumulative value in B
        while ptr_b < 256 and cum_hist_b[ptr_b] < target_cum:
            ptr_b += 1
        
        if ptr_b < 256:
            mapping[intensity_a] = ptr_b
        else:
            break
    
    return mapping

def plot_analysis(img_a, img_b):
    """Plot comprehensive analysis of the two images."""
    # Compute histograms
    hist_a, norm_a, cum_a = compute_histograms(img_a)
    hist_b, norm_b, cum_b = compute_histograms(img_b)

    # Find monotonic mapping
    mapping = find_monotonic_mapping(cum_a, cum_b)

    # Create figure with subplots
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(3, 2)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(img_a, cmap='gray')
    ax1.set_title('Image A')
    ax1.axis('off')
    
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(img_b, cmap='gray')
    ax2.set_title('Image B')
    ax2.axis('off')
    
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(hist_a, color='blue', label='Hist A')
    ax3.plot(hist_b, color='orange', label='Hist B')
    ax3.set_title('Histograms')
    ax3.set_xlabel('Intensity')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True)
    
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(cum_a, color='blue', label='Cumulative A')
    ax4.plot(cum_b, color='orange', label='Cumulative B')
    ax4.set_title('Cumulative Histograms')
    ax4.set_xlabel('Intensity')
    ax4.set_ylabel('Cumulative')
    ax4.legend()
    ax4.grid(True)

    ax5 = fig.add_subplot(gs[2, 0])
    matched_image = np.zeros_like(img_a, dtype=np.uint8)
    # Apply mapping
    for i in range(img_a.shape[0]):
        for j in range(img_a.shape[1]):
            val = mapping[img_a[i, j]]
            matched_image[i, j] = 0 if val == -1 else val
    ax5.imshow(matched_image, cmap='gray')
    ax5.set_title('Image A after Intensity Mapping')
    ax5.axis('off')

    ax6 = fig.add_subplot(gs[2, 1])
    valid_mappings = mapping != -1
    ax6.plot(np.where(valid_mappings)[0], mapping[valid_mappings], 'g.', label='Monotonic Mapping')
    ax6.set_title('Monotonic Mapping between Images')
    ax6.set_xlabel('Intensity in Image A')
    ax6.set_ylabel('Intensity in Image B')
    ax6.grid(True)
    ax6.legend()

    plt.tight_layout()
    plt.show()

def main():
    print("\nImage Analysis Tool")
    print("-----------------")
    print("Enter paths for two grayscale images (or 'q' to quit)")
    print("Example: images/test1.jpg and images/test2.jpg\n")

    while True:
        # Get paths for both images
        path_a = input("Path to Image A (or 'q' to quit): ").strip()
        if path_a.lower() == 'q':
            print("Goodbye!")
            break

        path_b = input("Path to Image B (or 'q' to quit): ").strip()
        if path_b.lower() == 'q':
            print("Goodbye!")
            break

        # Load and validate images
        img_a, img_b = load_and_validate_images(path_a, path_b)
        if img_a is None or img_b is None:
            continue

        # Perform and display analysis
        plot_analysis(img_a, img_b)

        print("\nAnalysis complete. Ready for next pair of images.\n")

if __name__ == "__main__":
    main() 