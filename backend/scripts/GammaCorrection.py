import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def apply_gamma_correction(image_path, gamma):
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Could not load image.")
        return

    # Normalize image to [0,1]
    norm_img = image / 255.0

    # Apply gamma correction
    image_gamma = np.power(norm_img, gamma)
    image_gamma = (image_gamma * 255).astype(np.uint8)

    # Show results
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(image, cmap='gray')
    axes[0].set_title('Original')
    axes[0].axis('off')

    axes[1].imshow(image_gamma, cmap='gray')
    axes[1].set_title(f'Gamma corrected (gamma={gamma})')
    axes[1].axis('off')

    plt.tight_layout()
    plt.show()

    while True:
        save = input("\nDo you want to save the gamma-corrected image? (y/n): ").strip().lower()
        if save in ['y', 'n']:
            break
        print("Please enter 'y' for yes or 'n' for no.")

    if save == 'y':
        base_name = os.path.splitext(image_path)[0]
        ext = os.path.splitext(image_path)[1]
        output_path = f"{base_name}_gamma{gamma}{ext}"
        cv2.imwrite(output_path, image_gamma)
        print(f"Image saved as: {output_path}")

def main():
    print("\nGamma Correction Tool")
    print("--------------------")
    print("Enter the path to your image file (or 'q' to quit)")
    print("Example: images/test.jpg or ./photo.png\n")

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
                gamma = float(input("Enter gamma value (0.1 - 5.0): ").strip())
                if 0.1 <= gamma <= 5.0:
                    break
                else:
                    print("Please enter a value between 0.1 and 5.0")
            except ValueError:
                print("Please enter a valid number")

        apply_gamma_correction(image_path, gamma)

if __name__ == "__main__":
    main() 