from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
import cv2
import numpy as np
import os
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
from datetime import datetime, timedelta
import base64
import io
import matplotlib.pyplot as plt
# Import the transformation functions
from scripts.Transformations import (
    get_rotation_matrix,
    get_translation_matrix,
    get_scaling_matrix,
    get_shear_matrix,
    apply_transformation
)
from scripts.noise import add_noise  # Add this import at the top with other imports
from scripts.filters import apply_min_filter, apply_max_filter  # Add this import
from scripts.median_filter import apply_median_filter  # Add this import
from scripts.mean_filter import apply_mean_filter  # Add this import
from scripts.convolution_masks import get_default_mask, apply_convolution  # Add this import
import json
from scripts.fourier_transform import apply_fourier_transform
from scripts.fourier_filters import apply_fourier_filter  # Add this import at the top
from scripts.pyramids import build_gaussian_pyramid, build_laplacian_pyramid, reconstruct_from_laplacian
from scripts.canny_edge import apply_canny_edge

router = APIRouter()

TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Add this function to periodically clean up old files
def cleanup_temp_files():
    """Remove files older than 1 hour from the temp directory"""
    current_time = datetime.now()
    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        if current_time - file_modified > timedelta(hours=1):
            os.remove(filepath)

def compute_histogram_data(image):
    """Compute histogram data and return as base64 encoded image"""
    # Compute histograms
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    
    # Create histogram plot
    plt.figure(figsize=(8, 4))
    
    # Plot regular histogram as bars
    plt.subplot(1, 2, 1)
    plt.bar(range(256), hist, color='blue', alpha=0.7, width=1)
    plt.title('Histogram')
    plt.xlabel('Intensity')
    plt.ylabel('Count')
    
    # Plot cumulative histogram as bars
    plt.subplot(1, 2, 2)
    plt.bar(range(256), hist_cum * hist.max(), color='red', alpha=0.7, width=1)
    plt.title('Cumulative Histogram')
    plt.xlabel('Intensity')
    plt.ylabel('Cumulative')
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    
    # Also return the raw histogram data for interactive display
    return {
        "image": base64.b64encode(buf.getvalue()).decode(),
        "data": {
            "histogram": hist.tolist(),
            "cumulative": (hist_cum * hist.max()).tolist()
        }
    }

@router.post("/brightness")
async def adjust_brightness(image: UploadFile = File(...), value: int = Form(...)):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply brightness adjustment
        adjusted = np.clip(img.astype(np.int16) + value, 0, 255).astype(np.uint8)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([adjusted], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', adjusted)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/contrast")
async def process_contrast(image: UploadFile = File(...), factor: float = Form(...)):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply contrast stretching
        min_val = float(img.min())
        max_val = float(img.max())
        stretched = ((img - min_val) * factor) / (max_val - min_val)
        stretched = np.clip(stretched * 255, 0, 255).astype(np.uint8)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([stretched], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', stretched)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.get("/temp/{filename}")
async def get_temp_file(filename: str):
    file_path = os.path.join(TEMP_DIR, filename)
    return FileResponse(file_path, media_type="image/png")

@router.post("/compute-histogram")
async def compute_image_histogram(
    image: UploadFile = File(...)
):
    """Compute histogram for uploaded image without processing"""
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Compute histogram
    histogram_data = compute_histogram_data(img)
    
    return JSONResponse(histogram_data)

@router.post("/equalize")
async def equalize_histogram(image: UploadFile = File(...)):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply histogram equalization
        equalized = cv2.equalizeHist(img)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([equalized], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', equalized)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/gamma")
async def adjust_gamma(image: UploadFile = File(...), gamma: float = Form(...)):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply gamma correction
        # First normalize the image to 0-1
        normalized = img / 255.0
        # Apply gamma correction
        corrected = np.power(normalized, gamma)
        # Scale back to 0-255 and convert to uint8
        corrected = np.clip(corrected * 255, 0, 255).astype(np.uint8)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([corrected], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', corrected)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/2pointer")
async def analyze_two_images(image_a: UploadFile = File(...), image_b: UploadFile = File(...)):
    try:
        # Read both images
        contents_a = await image_a.read()
        contents_b = await image_b.read()
        
        # Convert to numpy arrays
        nparr_a = np.frombuffer(contents_a, np.uint8)
        nparr_b = np.frombuffer(contents_b, np.uint8)
        
        # Decode images
        img_a = cv2.imdecode(nparr_a, cv2.IMREAD_GRAYSCALE)
        img_b = cv2.imdecode(nparr_b, cv2.IMREAD_GRAYSCALE)
        
        if img_a is None or img_b is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file(s)"}
            )

        # Compute histograms and normalize them
        hist_a = cv2.calcHist([img_a], [0], None, [256], [0, 256]).flatten()
        hist_b = cv2.calcHist([img_b], [0], None, [256], [0, 256]).flatten()
        
        # Normalize histograms
        norm_hist_a = hist_a / hist_a.sum()
        norm_hist_b = hist_b / hist_b.sum()
        
        # Compute cumulative histograms
        cum_hist_a = norm_hist_a.cumsum()
        cum_hist_b = norm_hist_b.cumsum()
        
        # Find monotonic mapping using two-pointer technique
        mapping = np.full(256, -1, dtype=int)  # -1 indicates no mapping
        ptr_b = 0
        
        for intensity_a in range(256):
            target_cum = cum_hist_a[intensity_a]
            
            # Move pointer B until we find a matching or greater cumulative value
            while ptr_b < 256 and cum_hist_b[ptr_b] < target_cum:
                ptr_b += 1
            
            if ptr_b < 256:
                mapping[intensity_a] = ptr_b
            else:
                break
        
        # Apply mapping to create transformed image
        transformed = np.zeros_like(img_a)
        for i in range(img_a.shape[0]):
            for j in range(img_a.shape[1]):
                val = mapping[img_a[i, j]]
                transformed[i, j] = 0 if val == -1 else val
        
        # Encode images to base64
        _, img_a_encoded = cv2.imencode('.png', img_a)
        _, img_b_encoded = cv2.imencode('.png', img_b)
        _, transformed_encoded = cv2.imencode('.png', transformed)
        
        return JSONResponse({
            "imageA": f"data:image/png;base64,{base64.b64encode(img_a_encoded.tobytes()).decode('utf-8')}",
            "imageB": f"data:image/png;base64,{base64.b64encode(img_b_encoded.tobytes()).decode('utf-8')}",
            "transformedImage": f"data:image/png;base64,{base64.b64encode(transformed_encoded.tobytes()).decode('utf-8')}",
            "histogramA": hist_a.tolist(),
            "histogramB": hist_b.tolist(),
            "cumulativeA": (cum_hist_a * hist_a.max()).tolist(),
            "cumulativeB": (cum_hist_b * hist_b.max()).tolist(),
            "mapping": mapping.tolist()
        })
        
    except Exception as e:
        print(f"Error processing images: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process images: {str(e)}"}
        )

@router.post("/transform")
async def transform_image(
    image: UploadFile = File(...),
    type: str = Form(...),
    angle: float = Form(0.0),
    tx: float = Form(0.0),
    ty: float = Form(0.0),
    scale_x: float = Form(1.0),
    scale_y: float = Form(1.0),
    shear_x: float = Form(0.0),
    shear_y: float = Form(0.0)
):
    try:
        # Read and decode image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        height, width = img.shape
        center = (width // 2, height // 2)

        # Get transformation matrix based on type
        if type == "rotation":
            matrix = get_rotation_matrix(angle, center, (width, height))
        elif type == "translation":
            matrix = get_translation_matrix(tx, ty)
        elif type == "scaling":
            matrix = get_scaling_matrix(scale_x, scale_y, center)
        elif type == "shearing":
            matrix = get_shear_matrix(shear_x, shear_y, center)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid transformation type"}
            )

        # Apply transformation
        transformed = apply_transformation(img, matrix)
        
        # Encode the transformed image
        _, img_encoded = cv2.imencode('.png', transformed)
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{base64.b64encode(img_encoded.tobytes()).decode('utf-8')}",
            "transformationMatrix": matrix.tolist()
        })

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/add-noise")
async def process_noise(
    image: UploadFile = File(...),
    noise_type: str = Form(...),
    intensity: float = Form(...),
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply noise
        noise_img = add_noise(img, noise_type, float(intensity))
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([noise_img], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', noise_img)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/apply-filter")
async def process_filter(
    image: UploadFile = File(...),
    filter_sequence: str = Form(...)  # Will receive something like "min,max,min"
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Process the filter sequence
        processed = img.copy()
        filter_list = filter_sequence.split(',')
        
        for filter_type in filter_list:
            if filter_type == 'min':
                processed = apply_min_filter(processed)
            elif filter_type == 'max':
                processed = apply_max_filter(processed)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([processed], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', processed)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist(),
            "appliedFilters": filter_list
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/median-filter")
async def process_median_filter(
    image: UploadFile = File(...),
    kernel_size: int = Form(...)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1

        # Apply median filter
        processed = apply_median_filter(img, kernel_size)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([processed], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', processed)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist(),
            "kernelSize": kernel_size
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/mean-filter")
async def process_mean_filter(
    image: UploadFile = File(...),
    kernel_size: int = Form(...)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1

        # Apply mean filter
        processed = apply_mean_filter(img, kernel_size)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([processed], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', processed)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist(),
            "kernelSize": kernel_size
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/convolution")
async def process_convolution(
    image: UploadFile = File(...),
    kernel_size: int = Form(...),
    mask_type: str = Form(...),
    custom_mask: str = Form(None),
    add_128: bool = Form(False)  # Add this parameter
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1

        # Create mask
        if custom_mask:
            try:
                # Parse custom mask JSON string to numpy array
                mask_data = json.loads(custom_mask)
                mask = np.array(mask_data, dtype=np.float32)
                
                # Verify mask dimensions
                if mask.shape != (kernel_size, kernel_size):
                    raise ValueError(f"Mask dimensions must be {kernel_size}x{kernel_size}")
                
            except Exception as e:
                print(f"Error parsing custom mask: {str(e)}")  # Debug log
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Invalid custom mask: {str(e)}"}
                )
        else:
            mask = get_default_mask(mask_type, kernel_size)

        # Apply convolution with add_128 parameter
        processed = apply_convolution(img, mask, add_128=add_128)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([processed], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', processed)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist(),
            "mask": mask.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.get("/get-mask")
async def get_mask(type: str, size: int):
    try:
        mask = get_default_mask(type, int(size))
        return JSONResponse({
            "mask": mask.tolist()
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get mask: {str(e)}"}
        )

@router.post("/bilateral")
async def process_bilateral(
    image: UploadFile = File(...),
    d: int = Form(...),
    sigma_color: float = Form(...),
    sigma_space: float = Form(...)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply bilateral filter
        filtered = cv2.bilateralFilter(img, d, sigma_color, sigma_space)
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for processed image
        hist_processed = cv2.calcHist([filtered], [0], None, [256], [0, 256]).flatten()
        hist_processed_norm = hist_processed / hist_processed.sum()
        cum_processed = hist_processed_norm.cumsum() * hist_processed.max()
        
        # Encode processed image to base64
        _, processed_img = cv2.imencode('.png', filtered)
        processed_base64 = base64.b64encode(processed_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{processed_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "processedHistogram": hist_processed.tolist(),
            "processedCumulative": cum_processed.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/fourier")
async def process_fourier(
    image: UploadFile = File(...),
    center_spectrum: bool = Form(False),
    apply_log: bool = Form(False)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Apply Fourier transform
        magnitude_spectrum, reconstructed = apply_fourier_transform(
            img, center_spectrum, apply_log
        )
        
        # Compute histograms for original image
        hist_original = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
        hist_original_norm = hist_original / hist_original.sum()
        cum_original = hist_original_norm.cumsum() * hist_original.max()
        
        # Compute histograms for magnitude spectrum
        hist_spectrum = cv2.calcHist([magnitude_spectrum], [0], None, [256], [0, 256]).flatten()
        hist_spectrum_norm = hist_spectrum / hist_spectrum.sum()
        cum_spectrum = hist_spectrum_norm.cumsum() * hist_spectrum.max()
        
        # Encode images to base64
        _, magnitude_img = cv2.imencode('.png', magnitude_spectrum)
        magnitude_base64 = base64.b64encode(magnitude_img.tobytes()).decode('utf-8')
        
        return JSONResponse({
            "magnitudeSpectrum": f"data:image/png;base64,{magnitude_base64}",
            "originalHistogram": hist_original.tolist(),
            "originalCumulative": cum_original.tolist(),
            "spectrumHistogram": hist_spectrum_norm.tolist(),
            "spectrumCumulative": cum_spectrum.tolist()
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/fourier-filter")
async def process_fourier_filter(
    image: UploadFile = File(...),
    filter_type: str = Form(...),
    gaussian: bool = Form(...),
    radius: int = Form(None),
    inner_radius: int = Form(None),
    outer_radius: int = Form(None),
    add_dc: bool = Form(False)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Prepare parameters
        params = {
            'gaussian': gaussian,
            'add_dc': add_dc
        }
        if filter_type == 'band_pass':
            params.update({
                'inner_radius': inner_radius,
                'outer_radius': outer_radius
            })
        else:
            params['radius'] = radius

        # Apply filter
        filtered_img, original_spectrum, filtered_spectrum = apply_fourier_filter(
            img, filter_type, params
        )
        
        # Encode images to base64
        _, filtered_buf = cv2.imencode('.png', filtered_img)
        _, orig_spectrum_buf = cv2.imencode('.png', original_spectrum)
        _, filtered_spectrum_buf = cv2.imencode('.png', filtered_spectrum)
        
        return JSONResponse({
            "filteredImage": f"data:image/png;base64,{base64.b64encode(filtered_buf).decode('utf-8')}",
            "originalSpectrum": f"data:image/png;base64,{base64.b64encode(orig_spectrum_buf).decode('utf-8')}",
            "filteredSpectrum": f"data:image/png;base64,{base64.b64encode(filtered_spectrum_buf).decode('utf-8')}"
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/pyramids")
async def process_pyramids(
    image: UploadFile = File(...),
    levels: int = Form(...)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )

        # Build pyramids
        gaussian_pyramid = build_gaussian_pyramid(img, levels)
        laplacian_pyramid, laplacian_display = build_laplacian_pyramid(gaussian_pyramid)
        reconstructed = reconstruct_from_laplacian(laplacian_pyramid)

        # Encode all images to base64
        gaussian_images = []
        laplacian_images = []
        
        for g_img in gaussian_pyramid:
            _, buf = cv2.imencode('.png', g_img)
            gaussian_images.append(
                f"data:image/png;base64,{base64.b64encode(buf).decode('utf-8')}"
            )
            
        for l_img in laplacian_display:  # Use display version for frontend
            _, buf = cv2.imencode('.png', l_img)
            laplacian_images.append(
                f"data:image/png;base64,{base64.b64encode(buf).decode('utf-8')}"
            )
            
        _, reconstructed_buf = cv2.imencode('.png', reconstructed)
        
        return JSONResponse({
            "gaussianPyramid": gaussian_images,
            "laplacianPyramid": laplacian_images,
            "reconstructedImage": f"data:image/png;base64,{base64.b64encode(reconstructed_buf).decode('utf-8')}"
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

@router.post("/canny-edge")
async def process_canny_edge(
    image: UploadFile = File(...),
    low_threshold: int = Form(...),
    high_threshold: int = Form(...),
    sigma: float = Form(...)
):
    try:
        # Read image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image file"}
            )
            
        # Apply edge detection
        edges = apply_canny_edge(img, low_threshold, high_threshold, sigma)
        
        # Encode result to base64
        _, img_encoded = cv2.imencode('.png', edges)
        edge_base64 = base64.b64encode(img_encoded).decode('utf-8')
        
        return JSONResponse({
            "processedImage": f"data:image/png;base64,{edge_base64}"
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )

# Add similar endpoints for other operations...
