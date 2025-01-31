import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def apply_fourier_filter(image, filter_type, params):
    """
    Apply frequency domain filtering using Fourier transform.
    
    Args:
        image: Input grayscale image
        filter_type: 'low_pass', 'high_pass', or 'band_pass'
        params: Dictionary containing filter parameters:
            - radius: for low/high pass
            - inner_radius, outer_radius: for band pass
            - gaussian: boolean for gaussian smoothing
            - add_dc: boolean for adding 128 to result
    """
    # Apply FFT
    f_transform = np.fft.fft2(image)
    f_shift = np.fft.fftshift(f_transform)
    
    rows, cols = image.shape
    center_row, center_col = rows // 2, cols // 2
    
    # Create mask based on filter type
    mask = np.zeros((rows, cols), np.float32)
    y, x = np.ogrid[-center_row:rows-center_row, -center_col:cols-center_col]
    distances = np.sqrt(x*x + y*y)
    
    if filter_type == "low_pass":
        radius = params['radius']
        if params['gaussian']:
            mask = np.exp(-(distances**2) / (2 * radius**2))
        else:
            mask = distances <= radius
            
    elif filter_type == "high_pass":
        radius = params['radius']
        if params['gaussian']:
            mask = 1 - np.exp(-(distances**2) / (2 * radius**2))
        else:
            mask = distances > radius
            
    elif filter_type == "band_pass":
        inner_radius = params['inner_radius']
        outer_radius = params['outer_radius']
        if params['gaussian']:
            mask = np.exp(-(distances - (inner_radius + outer_radius)/2)**2 / (2 * ((outer_radius - inner_radius)/4)**2))
        else:
            mask = (distances >= inner_radius) & (distances <= outer_radius)
    
    # Apply mask and inverse FFT
    f_shift_filtered = f_shift * mask
    f_inverse = np.fft.ifftshift(f_shift_filtered)
    img_back = np.fft.ifft2(f_inverse)
    img_filtered = np.abs(img_back)
    
    # Add DC component (128) if requested
    if params.get('add_dc', False):
        img_filtered += 128
        
    img_filtered = np.clip(img_filtered, 0, 255).astype(np.uint8)
    
    # Prepare magnitude spectrum for visualization
    magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
    magnitude_spectrum = np.clip(magnitude_spectrum, 0, 255).astype(np.uint8)
    
    filtered_spectrum = 20 * np.log(np.abs(f_shift_filtered) + 1)
    filtered_spectrum = np.clip(filtered_spectrum, 0, 255).astype(np.uint8)
    
    return img_filtered, magnitude_spectrum, filtered_spectrum

def main():
    print("\nFourier Domain Filtering Tool")
    print("---------------------------")
    
    while True:
        # Get image path
        image_path = input("\nEnter image path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            break
            
        if not os.path.exists(image_path):
            print("Error: File not found")
            continue
            
        # Read image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print("Error: Could not read image")
            continue
            
        # Get filter type
        print("\nSelect filter type:")
        print("1. Low Pass")
        print("2. High Pass")
        print("3. Band Pass")
        filter_choice = input("Choice (1/2/3): ").strip()
        
        # Get parameters based on filter type
        params = {'gaussian': input("Use Gaussian smoothing? (y/n): ").lower() == 'y'}
        
        if filter_choice == "1":
            filter_type = "low_pass"
            params['radius'] = int(input("Enter radius (10-100): ").strip())
        elif filter_choice == "2":
            filter_type = "high_pass"
            params['radius'] = int(input("Enter radius (10-100): ").strip())
        elif filter_choice == "3":
            filter_type = "band_pass"
            params['inner_radius'] = int(input("Enter inner radius (10-100): ").strip())
            params['outer_radius'] = int(input("Enter outer radius (>inner radius): ").strip())
        else:
            print("Invalid choice")
            continue
            
        # Process image
        filtered_img, magnitude_spectrum, filtered_spectrum = apply_fourier_filter(
            image, filter_type, params
        )
        
        # Display results
        plt.figure(figsize=(12, 8))
        
        plt.subplot(221), plt.imshow(image, cmap='gray')
        plt.title('Original Image'), plt.axis('off')
        
        plt.subplot(222), plt.imshow(magnitude_spectrum, cmap='gray')
        plt.title('Magnitude Spectrum'), plt.axis('off')
        
        plt.subplot(223), plt.imshow(filtered_spectrum, cmap='gray')
        plt.title('Filtered Spectrum'), plt.axis('off')
        
        plt.subplot(224), plt.imshow(filtered_img, cmap='gray')
        plt.title('Filtered Image'), plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        # Save option
        if input("\nSave filtered image? (y/n): ").lower() == 'y':
            output_path = f"{os.path.splitext(image_path)[0]}_{filter_type}_filtered.png"
            cv2.imwrite(output_path, filtered_img)
            print(f"Saved as: {output_path}")

if __name__ == "__main__":
    main() 