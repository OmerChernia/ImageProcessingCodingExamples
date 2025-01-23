import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def get_rotation_matrix(angle_degrees, center, size):
    """Return 3x3 rotation matrix with center correction."""
    angle_rad = np.deg2rad(angle_degrees)
    cx, cy = center

    # Translate to origin
    to_origin = np.array([
        [1, 0, -cx],
        [0, 1, -cy],
        [0, 0, 1]
    ], dtype=np.float32)

    # Basic rotation
    rotation = np.array([
        [ np.cos(angle_rad), np.sin(angle_rad), 0],
        [-np.sin(angle_rad), np.cos(angle_rad), 0],
        [ 0,                 0,                 1]
    ], dtype=np.float32)

    # Translate back
    from_origin = np.array([
        [1, 0, cx],
        [0, 1, cy],
        [0, 0, 1]
    ], dtype=np.float32)

    return from_origin @ rotation @ to_origin

def get_translation_matrix(tx, ty):
    """Return 3x3 translation matrix."""
    matrix = np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ], dtype=np.float32)
    return matrix

def get_scaling_matrix(sx, sy, center):
    """Return 3x3 scaling matrix around a center."""
    cx, cy = center
    to_origin = np.array([
        [1, 0, -cx],
        [0, 1, -cy],
        [0, 0, 1]
    ], dtype=np.float32)

    scale = np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ], dtype=np.float32)

    from_origin = np.array([
        [1, 0, cx],
        [0, 1, cy],
        [0, 0, 1]
    ], dtype=np.float32)

    return from_origin @ scale @ to_origin

def get_shear_matrix(shx, shy, center):
    """Return 3x3 shear matrix around a center."""
    cx, cy = center
    to_origin = np.array([
        [1, 0, -cx],
        [0, 1, -cy],
        [0, 0, 1]
    ], dtype=np.float32)

    shear = np.array([
        [1,   shx, 0],
        [shy, 1,   0],
        [0,   0,   1]
    ], dtype=np.float32)

    from_origin = np.array([
        [1, 0, cx],
        [0, 1, cy],
        [0, 0, 1]
    ], dtype=np.float32)

    return from_origin @ shear @ to_origin

def apply_transformation(image, matrix):
    """Apply transformation matrix to image."""
    height, width = image.shape
    matrix_2x3 = matrix[:2, :]
    return cv2.warpAffine(image, matrix_2x3, (width, height))

def show_transformation_example():
    """Show example matrix formats."""
    print("\nTransformation Matrix Formats (around center point (cx,cy)):")
    print("\n1. Rotation Matrix (θ = angle in degrees):")
    print("Final matrix is: translate_to_center @ rotation @ translate_to_origin")
    print("Basic rotation:")
    print("┌                        ┐")
    print("│ cosθ   sinθ     0       │")
    print("│ -sinθ  cosθ     0       │")
    print("│   0      0       1      │")
    print("└                        ┘")

    print("\n2. Translation Matrix (tx, ty):")
    print("┌                ┐")
    print("│  1    0    tx  │")
    print("│  0    1    ty  │")
    print("│  0    0    1   │")
    print("└                ┘")

    print("\n3. Scaling Matrix (sx, sy):")
    print("Final matrix is: translate_to_center @ scale @ translate_to_origin")
    print("Basic scale:")
    print("┌                ┐")
    print("│  sx   0    0   │")
    print("│  0    sy   0   │")
    print("│  0    0    1   │")
    print("└                ┘")

    print("\n4. Shear Matrix (shx, shy):")
    print("Final matrix is: translate_to_center @ shear @ translate_to_origin")
    print("Basic shear:")
    print("┌                   ┐")
    print("│ 1    shx    0     │")
    print("│ shy   1     0     │")
    print("│ 0     0     1     │")
    print("└                   ┘")

def plot_result(original, transformed, matrix, title, transformation_info):
    """Plot original image, transformed image, and matrix info."""
    fig = plt.figure(figsize=(15, 5))

    ax1 = fig.add_subplot(131)
    ax1.imshow(original, cmap='gray')
    ax1.set_title('Original Image')
    ax1.axis('off')

    ax2 = fig.add_subplot(132)
    ax2.imshow(transformed, cmap='gray')
    ax2.set_title(title)
    ax2.axis('off')

    ax3 = fig.add_subplot(133)
    # Show matrix as text
    matrix_text = "Transformation Matrix:\n"
    for row in matrix:
        matrix_text += f"{row}\n"

    format_text = ""
    if transformation_info['type'] == 'rotation':
        format_text += "\nAngle = " + str(transformation_info['angle'])
    elif transformation_info['type'] == 'translation':
        format_text += f"\nTx = {transformation_info['tx']}"
        format_text += f"\nTy = {transformation_info['ty']}"
    elif transformation_info['type'] == 'scaling':
        format_text += f"\nSx = {transformation_info['sx']}"
        format_text += f"\nSy = {transformation_info['sy']}"
    elif transformation_info['type'] == 'shear':
        format_text += "┌                   ┐\n"
        format_text += "│ 1    shx    0     │\n"
        format_text += "│ shy   1     0     │\n"
        format_text += "│ 0     0     1     │\n"
        format_text += "└                   ┘\n"
        format_text += f"\nshx = {transformation_info['shx']}"
        format_text += f"\nshy = {transformation_info['shy']}"

    ax3.text(0.1, 0.95, matrix_text + format_text,
             fontfamily='monospace', fontsize=10,
             verticalalignment='top')
    ax3.axis('off')

    plt.tight_layout()
    plt.show()

def main():
    print("\nImage Transformation Tool")
    print("------------------------")

    while True:
        image_path = input("\nEnter image path (or 'q' to quit): ").strip()
        if image_path.lower() == 'q':
            print("Goodbye!")
            break

        if not os.path.exists(image_path):
            print("Error: File not found.")
            continue

        # Load grayscale image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print("Error: Could not load image.")
            continue

        height, width = image.shape
        center = (width // 2, height // 2)

        print("\nChoose a transformation:")
        print("1) Rotate")
        print("2) Translate")
        print("3) Scale")
        print("4) Shear")
        print("5) Show transformation examples")

        choice = input("Enter choice (1-5): ").strip()

        if choice == '5':
            show_transformation_example()
            continue

        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice.")
            continue

        try:
            if choice == '1':
                angle = float(input("Enter rotation angle (degrees): "))
                matrix = get_rotation_matrix(angle, center, (width, height))
                title = f'Rotated ({angle}°)'
                info = {'type': 'rotation', 'angle': angle}

            elif choice == '2':
                tx = float(input("Enter x translation: "))
                ty = float(input("Enter y translation: "))
                matrix = get_translation_matrix(tx, ty)
                title = f'Translated (tx={tx}, ty={ty})'
                info = {'type': 'translation', 'tx': tx, 'ty': ty}

            elif choice == '3':
                sx = float(input("Enter x scaling factor: "))
                sy = float(input("Enter y scaling factor: "))
                matrix = get_scaling_matrix(sx, sy, center)
                title = f'Scaled (sx={sx}, sy={sy})'
                info = {'type': 'scaling', 'sx': sx, 'sy': sy}

            elif choice == '4':
                shx = float(input("Enter x shear factor: "))
                shy = float(input("Enter y shear factor: "))
                matrix = get_shear_matrix(shx, shy, center)
                title = f'Sheared ({shx}, {shy})'
                info = {'type': 'shear', 'shx': shx, 'shy': shy}

            transformed = apply_transformation(image, matrix)
            plot_result(image, transformed, matrix, title, info)

        except ValueError:
            print("Invalid input. Please enter numeric values.")
            continue

if __name__ == "__main__":
    main() 