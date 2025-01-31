import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def apply_canny_edge(image, low_threshold, high_threshold, sigma):
    """
    Apply Canny edge detection to an image
    
    Args:
        image: numpy array of the image
        low_threshold: lower threshold for edge detection
        high_threshold: higher threshold for edge detection
        sigma: standard deviation for Gaussian blur
    """
    # Convert to float for proper processing
    img_float = image.astype(float)
    
    # Apply Gaussian blur
    kernel_size = int(2 * round(3 * sigma) + 1)  # Ensure odd kernel size
    blurred = cv2.GaussianBlur(img_float, (kernel_size, kernel_size), sigma)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred.astype(np.uint8), 
                     low_threshold, 
                     high_threshold)
    
    return edges

def plot_analysis(image_path, low_threshold, high_threshold, sigma):
    """Plot analysis of the image before and after edge detection."""
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return
    
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load image.")
        return
    
    # Apply edge detection
    edges = apply_canny_edge(image, low_threshold, high_threshold, sigma)
    
    # Create figure for display
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Display original image
    ax1.imshow(image, cmap='gray')
    ax1.set_title('Original Image')
    ax1.axis('off')
    
    # Display edge detection result
    ax2.imshow(edges, cmap='gray')
    ax2.set_title(f'Canny Edge Detection\n(L={low_threshold}, H={high_threshold}, σ={sigma})')
    ax2.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Ask if user wants to save the edge detection result
    while True:
        save = input("\nDo you want to save the edge detection result? (y/n): ").strip().lower()
        if save in ['y', 'n']:
            break
        print("Please enter 'y' for yes or 'n' for no.")
    
    if save == 'y':
        # Generate output filename
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_edges_L{low_threshold}_H{high_threshold}_s{sigma}.png"
        cv2.imwrite(output_path, edges)
        print(f"Edge detection result saved as: {output_path}")

def main():
    print("\nCanny Edge Detection Tool")
    print("-----------------------")
    print("Enter the path to your image file (or 'q' to quit)")
    
    while True:
        image_path = input("\nImage path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break
            
        if not os.path.exists(image_path):
            print("Error: File not found.")
            continue
            
        # Get parameters
        try:
            low_threshold = int(input("Enter low threshold (0-100): ").strip())
            high_threshold = int(input("Enter high threshold (0-200): ").strip())
            sigma = float(input("Enter sigma for Gaussian blur (0.1-5.0): ").strip())
            
            if not (0 <= low_threshold <= 100 and  
                   0 <= high_threshold <= 200 and  
                   0.1 <= sigma <= 5.0):
                print("Error: Parameters out of valid ranges.")
                continue
                
        except ValueError:
            print("Error: Invalid input. Please enter numeric values.")
            continue
            
        plot_analysis(image_path, low_threshold, high_threshold, sigma)

if __name__ == "__main__":
    main() 