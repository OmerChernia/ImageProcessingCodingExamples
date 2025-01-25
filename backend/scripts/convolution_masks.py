import cv2
import numpy as np
import os

def get_default_mask(mask_type, kernel_size):
    """Return a predefined convolution mask"""
    if mask_type == "identity":
        # Identity mask - doesn't change the image
        mask = np.zeros((kernel_size, kernel_size))
        center = kernel_size // 2
        mask[center, center] = 1
        return mask

    elif mask_type == "shift":
        # Shift mask - moves the image slightly
        mask = np.zeros((kernel_size, kernel_size))
        mask[0, -1] = 1
        return mask

    elif mask_type == "gaussian":
        # Gaussian mask - blurs the image
        sigma = 1.0
        ax = np.linspace(-(kernel_size - 1) / 2., (kernel_size - 1) / 2., kernel_size)
        xx, yy = np.meshgrid(ax, ax)
        kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
        return kernel / np.sum(kernel)

    elif mask_type == "sharpen":
        # Sharpening mask
        mask = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        if kernel_size > 3:
            # Pad with zeros for larger kernels
            pad_size = (kernel_size - 3) // 2
            mask = np.pad(mask, pad_size, mode='constant')
        return mask

    else:
        raise ValueError("Invalid mask type")

def apply_convolution(image, mask, add_128=False):
    """Apply convolution mask to the image"""
    result = cv2.filter2D(image, -1, mask)
    if add_128:
        result = np.clip(result + 128, 0, 255).astype(np.uint8)
    return result

def compute_histograms(image):
    """Compute regular and cumulative histograms."""
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    return hist, hist_cum

def main():
    print("\nConvolution Masks Tool")
    print("--------------------")
    print("Enter the path to your image file (or 'q' to quit)")

    while True:
        image_path = input("\nImage path: ").strip()
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

        # Get kernel size
        while True:
            try:
                kernel_size = int(input("\nEnter kernel size (odd number, e.g., 3, 5, 7): ").strip())
                if kernel_size < 3:
                    print("Kernel size must be at least 3")
                    continue
                if kernel_size % 2 == 0:
                    print("Kernel size must be odd. Adding 1 to make it odd.")
                    kernel_size += 1
                break
            except ValueError:
                print("Please enter a valid number")

        # Get mask type or custom input
        print("\nSelect mask type:")
        print("1. Identity Mask")
        print("2. Shift Mask")
        print("3. Gaussian Mask")
        print("4. Sharpen Mask")
        print("5. Custom Mask")
        
        choice = input("\nChoice (1-5): ").strip()
        
        try:
            if choice == "5":
                # Custom mask input
                print(f"\nEnter {kernel_size}x{kernel_size} mask values (space-separated):")
                mask = []
                for i in range(kernel_size):
                    while True:
                        try:
                            row = list(map(float, input(f"Row {i+1}: ").strip().split()))
                            if len(row) != kernel_size:
                                print(f"Please enter exactly {kernel_size} values")
                                continue
                            mask.append(row)
                            break
                        except ValueError:
                            print("Invalid input. Please enter numbers only")
                mask = np.array(mask)
            else:
                # Get predefined mask
                mask_type = {
                    "1": "identity",
                    "2": "shift",
                    "3": "gaussian",
                    "4": "sharpen"
                }[choice]
                mask = get_default_mask(mask_type, kernel_size)

            # Apply convolution
            processed = apply_convolution(image, mask)
            
            # Save result
            output_path = f"{os.path.splitext(image_path)[0]}_convolution.png"
            cv2.imwrite(output_path, processed)
            print(f"\nProcessed image saved as: {output_path}")
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main() 