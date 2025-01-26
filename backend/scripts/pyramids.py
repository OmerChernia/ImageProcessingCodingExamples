import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def build_gaussian_pyramid(image, levels):
    """
    Build Gaussian pyramid for an image.
    
    Args:
        image: Input grayscale image
        levels: Number of pyramid levels
    
    Returns:
        List of images forming the Gaussian pyramid
    """
    pyramid = [image.copy()]
    for i in range(levels - 1):
        # Blur and downsample
        img = cv2.pyrDown(pyramid[i])
        pyramid.append(img)
    return pyramid

def build_laplacian_pyramid(gaussian_pyramid):
    """
    Build Laplacian pyramid from a Gaussian pyramid.
    
    Args:
        gaussian_pyramid: List of images forming the Gaussian pyramid
    
    Returns:
        List of images forming the Laplacian pyramid (original values),
        List of images for visualization (with +128)
    """
    laplacian_pyramid = []
    laplacian_display = []
    
    for i in range(len(gaussian_pyramid) - 1):
        # Upsample current level
        expanded = cv2.pyrUp(gaussian_pyramid[i + 1], 
                           dstsize=(gaussian_pyramid[i].shape[1], 
                                  gaussian_pyramid[i].shape[0]))
        # Compute difference
        laplacian = cv2.subtract(gaussian_pyramid[i], expanded)
        laplacian_pyramid.append(laplacian)
        
        # Create display version with +128
        display = cv2.add(laplacian.copy(), 128)
        laplacian_display.append(display)
    
    # Add the smallest Gaussian level as the last Laplacian level
    laplacian_pyramid.append(gaussian_pyramid[-1])
    laplacian_display.append(gaussian_pyramid[-1])
    
    return laplacian_pyramid, laplacian_display

def reconstruct_from_laplacian(laplacian_pyramid):
    """
    Reconstruct original image from a Laplacian pyramid.
    Uses the original Laplacian values (not the display values).
    """
    reconstructed = laplacian_pyramid[-1]
    for i in range(len(laplacian_pyramid) - 2, -1, -1):
        expanded = cv2.pyrUp(reconstructed, 
                           dstsize=(laplacian_pyramid[i].shape[1],
                                  laplacian_pyramid[i].shape[0]))
        reconstructed = cv2.add(expanded, laplacian_pyramid[i])
    return reconstructed

def main():
    print("\nImage Pyramids Tool")
    print("-----------------")
    
    while True:
        image_path = input("\nEnter image path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            break
            
        if not os.path.exists(image_path):
            print("Error: File not found.")
            continue
            
        # Load image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print("Error: Could not load image.")
            continue
            
        # Get number of levels
        try:
            levels = int(input("Enter number of pyramid levels (3-6): ").strip())
            if not 3 <= levels <= 6:
                print("Number of levels must be between 3 and 6")
                continue
        except ValueError:
            print("Please enter a valid number")
            continue
            
        # Build pyramids
        gaussian_pyramid = build_gaussian_pyramid(image, levels)
        laplacian_pyramid, laplacian_display = build_laplacian_pyramid(gaussian_pyramid)
        
        # Display results
        plt.figure(figsize=(15, 5))
        
        # Display Gaussian pyramid
        plt.subplot(131)
        plt.title('Gaussian Pyramid')
        for i, img in enumerate(gaussian_pyramid):
            plt.subplot(levels, 3, i*3 + 1)
            plt.imshow(img, cmap='gray')
            plt.axis('off')
            
        # Display Laplacian pyramid
        for i, img in enumerate(laplacian_display):
            plt.subplot(levels, 3, i*3 + 2)
            plt.imshow(img, cmap='gray')
            plt.axis('off')
            
        # Reconstruct and display
        reconstructed = reconstruct_from_laplacian(laplacian_pyramid)
        plt.subplot(133)
        plt.imshow(reconstructed, cmap='gray')
        plt.title('Reconstructed')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        # Save option
        if input("\nSave results? (y/n): ").lower() == 'y':
            base_name = os.path.splitext(image_path)[0]
            cv2.imwrite(f"{base_name}_reconstructed.png", reconstructed)
            print(f"Saved reconstructed image as: {base_name}_reconstructed.png")

if __name__ == "__main__":
    main() 