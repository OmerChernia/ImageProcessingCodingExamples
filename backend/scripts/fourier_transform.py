import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def apply_fourier_transform(image, center_spectrum=False, apply_log=False):
    """
    Apply Fourier Transform to the image with optional centering and log scaling
    
    Args:
        image: Input grayscale image
        center_spectrum: Whether to center the spectrum (using fftshift)
        apply_log: Whether to apply log scaling to the magnitude spectrum
    """
    # Apply 2D FFT
    f = np.fft.fft2(image)
    
    # Center the spectrum if requested
    if center_spectrum:
        fshift = np.fft.fftshift(f)
    else:
        fshift = f
    
    # Calculate magnitude spectrum
    magnitude_spectrum = np.abs(fshift)
    
    if apply_log:
        # Apply log transform: log(1 + |F(u,v)|)
        magnitude_spectrum = np.log1p(magnitude_spectrum)
    
    # Normalize for display
    magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
    
    # Get reconstructed image
    if center_spectrum:
        f_ishift = np.fft.ifftshift(fshift)
    else:
        f_ishift = fshift
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    
    return magnitude_spectrum.astype(np.uint8), img_back.astype(np.uint8)

def main():
    print("\nFourier Transform Tool")
    print("--------------------")
    
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
            
        # Get parameters
        center_spectrum = input("Center the spectrum? (y/n): ").strip().lower() == 'y'
        apply_log = input("Apply log scaling? (y/n): ").strip().lower() == 'y'
        
        try:
            # Apply Fourier transform
            magnitude_spectrum, reconstructed = apply_fourier_transform(
                image, center_spectrum, apply_log
            )
            
            # Save results
            base_name = os.path.splitext(image_path)[0]
            cv2.imwrite(f"{base_name}_magnitude.png", magnitude_spectrum)
            cv2.imwrite(f"{base_name}_reconstructed.png", reconstructed)
            print(f"\nResults saved as:")
            print(f"Magnitude spectrum: {base_name}_magnitude.png")
            print(f"Reconstructed image: {base_name}_reconstructed.png")
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")

if __name__ == "__main__":
    main() 