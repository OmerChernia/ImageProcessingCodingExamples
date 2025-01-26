import cv2
import numpy as np
import os

def build_gaussian_pyramid(img, levels):
    """Build Gaussian pyramid up to specified levels."""
    pyramid = [img.copy()]
    current_img = img.copy()
    
    # Calculate maximum possible levels based on image size
    max_levels = int(np.floor(np.log2(min(img.shape[0], img.shape[1])))) - 2
    levels = min(levels, max_levels)  # Use the smaller of requested or max possible
    
    for i in range(levels - 1):
        # Check if image is too small for another level
        if current_img.shape[0] < 16 or current_img.shape[1] < 16:
            break
            
        current_img = cv2.pyrDown(current_img)
        pyramid.append(current_img)
    
    return pyramid

def build_laplacian_pyramid(gaussian_pyramid):
    """
    Build Laplacian pyramid from a Gaussian pyramid.
    Returns both original values and display values (+128).
    """
    laplacian_pyramid = []
    laplacian_display = []
    
    for i in range(len(gaussian_pyramid) - 1):
        # Get current and next level
        current = gaussian_pyramid[i]
        next_level = gaussian_pyramid[i + 1]
        
        # Expand next level to current size
        expanded = cv2.pyrUp(next_level, dstsize=(current.shape[1], current.shape[0]))
        
        # Compute Laplacian
        laplacian = cv2.subtract(current, expanded)
        laplacian_pyramid.append(laplacian)
        
        # Create display version
        display = cv2.add(laplacian.copy(), 128)
        laplacian_display.append(display)
    
    # Add the smallest Gaussian level as the last Laplacian level
    laplacian_pyramid.append(gaussian_pyramid[-1])
    laplacian_display.append(gaussian_pyramid[-1])
    
    return laplacian_pyramid, laplacian_display

def create_blend_mask(size, blend_type="full", blend_position=0.5):
    """
    Create a blending mask based on the specified type.
    
    Args:
        size: Tuple of (height, width)
        blend_type: "full" for gaussian blend or "half" for left-right split
        blend_position: Position of the blend (0.0-1.0)
    """
    height, width = size
    mask = np.zeros((height, width), dtype=np.float32)
    
    if blend_type == "full":
        # Create gaussian blend mask
        center_x = int(width * blend_position)
        center_y = height // 2
        sigma = 100
        
        for i in range(height):
            for j in range(width):
                mask[i,j] = np.exp(-((j-center_x)**2 + (i-center_y)**2)/(2*sigma**2))
    
    elif blend_type == "half":
        # Create sharp left-right split
        split_x = int(width * blend_position)
        mask[:, :split_x] = 1.0
        mask[:, split_x:] = 0.0
    
    return mask

def blend_pyramids(lpyr1, lpyr2, mask_pyr):
    """Blend two Laplacian pyramids using a Gaussian mask pyramid."""
    blended_pyr = []
    blended_display = []  # New list for display values
    
    for la, lb, mask in zip(lpyr1, lpyr2, mask_pyr):
        # Blend each level
        blended = la * mask + lb * (1.0 - mask)
        blended_pyr.append(blended)
        
        # Create display version by adding 128 (like we do for other Laplacian levels)
        display = cv2.add(blended.copy(), 128)
        blended_display.append(display)
        
    return blended_pyr, blended_display

def reconstruct_from_laplacian(laplacian_pyramid):
    """Reconstruct image from a Laplacian pyramid."""
    reconstructed = laplacian_pyramid[-1]
    for i in range(len(laplacian_pyramid) - 2, -1, -1):
        expanded = cv2.pyrUp(reconstructed, 
                           dstsize=(laplacian_pyramid[i].shape[1],
                                  laplacian_pyramid[i].shape[0]))
        reconstructed = cv2.add(expanded, laplacian_pyramid[i])
    return reconstructed

def multi_band_blending(img1, img2, levels=4, blend_position=0.5, blend_type="full"):
    """
    Perform multi-band blending of two images.
    
    Args:
        img1, img2: Input images of the same size
        levels: Number of pyramid levels
        blend_position: Position of the blend (0.0-1.0)
        blend_type: "full" for gaussian blend or "half" for left-right split
    """
    # Calculate maximum possible levels
    max_levels = int(np.floor(np.log2(min(img1.shape[0], img1.shape[1])))) - 2
    print(f"Maximum possible levels for this image size: {max_levels}")
    
    # Adjust levels if necessary
    if levels > max_levels:
        print(f"Adjusting levels from {levels} to {max_levels}")
        levels = max_levels

    # Build Gaussian pyramids
    gaussian1 = build_gaussian_pyramid(img1, levels)
    gaussian2 = build_gaussian_pyramid(img2, levels)

    # Build Laplacian pyramids
    laplacian1, laplacian1_display = build_laplacian_pyramid(gaussian1)
    laplacian2, laplacian2_display = build_laplacian_pyramid(gaussian2)

    # Generate blend mask pyramid
    mask = create_blend_mask(img1.shape, blend_type, blend_position)
    mask_pyr = build_gaussian_pyramid(mask, levels)

    # Blend pyramids
    blended_pyr, blended_display = blend_pyramids(laplacian1, laplacian2, mask_pyr)  # Get both regular and display pyramids

    # Reconstruct final image
    result = reconstruct_from_laplacian(blended_pyr)

    return {
        'pyramid1': laplacian1_display,
        'pyramid2': laplacian2_display,
        'blended_pyramid': blended_display,  # Use the display version
        'mask_pyramid': [m * 255 for m in mask_pyr],
        'result': result
    }

def main():
    print("\nMulti-Band Blending Tool")
    print("----------------------")
    
    # Get first image
    while True:
        img1_path = input("\nEnter path to first image (or 'q' to quit): ").strip()
        if img1_path.lower() == 'q':
            return
        
        if not os.path.exists(img1_path):
            print("Error: File not found")
            continue
            
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        if img1 is not None:
            break
        print("Error: Could not load image")
    
    # Get second image
    while True:
        img2_path = input("\nEnter path to second image: ").strip()
        if not os.path.exists(img2_path):
            print("Error: File not found")
            continue
            
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
        if img2 is not None:
            if img2.shape == img1.shape:
                break
            print("Error: Images must be the same size")
            continue
        print("Error: Could not load image")
    
    # Get number of levels
    while True:
        try:
            levels = int(input("\nEnter number of pyramid levels (2-6): ").strip())
            if 2 <= levels <= 6:
                break
            print("Please enter a number between 2 and 6")
        except ValueError:
            print("Please enter a valid number")
    
    # Get blend position
    while True:
        try:
            pos = float(input("\nEnter blend position (0.0-1.0): ").strip())
            if 0.0 <= pos <= 1.0:
                break
            print("Please enter a number between 0.0 and 1.0")
        except ValueError:
            print("Please enter a valid number")
    
    # Get blend type
    while True:
        try:
            blend_type = input("\nEnter blend type (full or half): ").strip()
            if blend_type in ["full", "half"]:
                break
            print("Please enter 'full' or 'half'")
        except ValueError:
            print("Please enter a valid blend type")
    
    try:
        result = multi_band_blending(img1, img2, levels, pos, blend_type)
        
        # Save results
        base_name = f"blend_{os.path.splitext(os.path.basename(img1_path))[0]}_{os.path.splitext(os.path.basename(img2_path))[0]}"
        cv2.imwrite(f"{base_name}_result.png", result['result'])
        print(f"\nBlended image saved as: {base_name}_result.png")
        
    except Exception as e:
        print(f"Error during blending: {str(e)}")

if __name__ == "__main__":
    main() 