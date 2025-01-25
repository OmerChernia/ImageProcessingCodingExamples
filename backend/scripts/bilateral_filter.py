import cv2
import numpy as np
import os

def apply_bilateral_filter(image, d, sigma_color, sigma_space):
    """
    Apply bilateral filter to the image
    
    Args:
        image: Input image (grayscale)
        d: Diameter of each pixel neighborhood
        sigma_color: Filter sigma in the color space
        sigma_space: Filter sigma in the coordinate space
    """
    filtered = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    return filtered

def main():
    print("\nBilateral Filter Tool")
    print("--------------------")
    print("Enter the path to your image file (or 'q' to quit)")
    
    while True:
        image_path = input("\nImage path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break
            
        if not os.path.exists(image_path):
            print("Error: File not found.")
            continue
            
        # Load the image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print("Error: Could not load image.")
            continue
            
        # Get filter parameters
        try:
            d = int(input("Enter diameter of neighborhood (odd number, e.g., 9): ").strip())
            if d % 2 == 0:
                d += 1  # Ensure odd number
            sigma_color = float(input("Enter sigma color (e.g., 75): ").strip())
            sigma_space = float(input("Enter sigma space (e.g., 75): ").strip())
            
            # Apply filter
            filtered = apply_bilateral_filter(image, d, sigma_color, sigma_space)
            
            # Save result
            output_path = f"{os.path.splitext(image_path)[0]}_bilateral.png"
            cv2.imwrite(output_path, filtered)
            print(f"\nProcessed image saved as: {output_path}")
            
        except ValueError as e:
            print(f"Error: Invalid input - {str(e)}")
        except Exception as e:
            print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main() 