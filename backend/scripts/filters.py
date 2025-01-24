import cv2
import numpy as np
import os

def apply_min_filter(image):
    """Apply minimum filter to the image"""
    return cv2.erode(image, np.ones((3,3), np.uint8))

def apply_max_filter(image):
    """Apply maximum filter to the image"""
    return cv2.dilate(image, np.ones((3,3), np.uint8))

def compute_histograms(image):
    """Compute regular and cumulative histograms."""
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    return hist, hist_cum

def main():
    print("\nMin-Max Filter Tool")
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

        processed_image = image.copy()
        
        while True:
            print("\nSelect filter type:")
            print("1. Min Filter")
            print("2. Max Filter")
            print("3. Done - Save Result")
            print("4. Cancel")
            
            choice = input("Choice (1/2/3/4): ").strip()
            
            if choice == "4":
                break
            elif choice == "3":
                # Save the result
                output_path = f"{os.path.splitext(image_path)[0]}_filtered.png"
                cv2.imwrite(output_path, processed_image)
                print(f"\nProcessed image saved as: {output_path}")
                break
            elif choice in ["1", "2"]:
                # Apply selected filter
                if choice == "1":
                    processed_image = apply_min_filter(processed_image)
                    print("Min filter applied")
                else:
                    processed_image = apply_max_filter(processed_image)
                    print("Max filter applied")
                
                # Show current result
                cv2.imshow('Current Result', processed_image)
                cv2.waitKey(1000)  # Display for 1 second
            else:
                print("Invalid choice. Please try again.")

        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 