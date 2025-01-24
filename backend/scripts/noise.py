import cv2
import numpy as np
import os

def add_noise(image, noise_type, intensity):
    """
    Add noise to an image
    
    Args:
        image: numpy array of the image
        noise_type: 'salt-pepper' or 'gaussian'
        intensity: float for noise intensity/std_dev
    """
    if noise_type == "salt-pepper":
        # Add salt and pepper noise
        noise_img = image.copy()
        # Generate random coordinates for noise
        rng = np.random.default_rng()
        coords = rng.random(image.shape) < intensity
        # Randomly assign white or black
        noise_img[coords] = rng.choice([0, 255], coords.sum())
        return noise_img
        
    elif noise_type == "gaussian":
        # Convert image to float for proper noise addition
        float_img = image.astype(float)
        # Generate Gaussian noise with mean=0 and std=intensity
        noise = np.random.normal(0, intensity, image.shape)
        # Add noise to image
        noisy_img = float_img + noise
        # Clip values to valid range and convert back to uint8
        return np.clip(noisy_img, 0, 255).astype(np.uint8)
    else:
        raise ValueError("Invalid noise type. Must be 'salt-pepper' or 'gaussian'")

def main():
    print("\nNoise Addition Tool")
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

        # Get noise type
        print("\nSelect noise type:")
        print("1. Salt & Pepper")
        print("2. Gaussian")
        noise_choice = input("Choice (1/2): ").strip()
        
        noise_type = "salt-pepper" if noise_choice == "1" else "gaussian"
        
        # Get intensity
        if noise_type == "salt-pepper":
            intensity = float(input("Enter noise density (0-1): ").strip())
        else:
            intensity = float(input("Enter standard deviation (1-50): ").strip())

        # Process image
        try:
            noisy_image = add_noise(image, noise_type, intensity)
            # Save result
            output_path = f"{os.path.splitext(image_path)[0]}_{noise_type}_noise.png"
            cv2.imwrite(output_path, noisy_image)
            print(f"\nProcessed image saved as: {output_path}")
        except Exception as e:
            print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main() 