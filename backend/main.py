from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from fastapi import HTTPException
import json

app = FastAPI()

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # בפיתוח, אפשר להשתמש ב-* 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def encode_image(image):
    _, buffer = cv2.imencode('.png', image)
    return f"data:image/png;base64,{base64.b64encode(buffer).decode()}"

def compute_histograms(image):
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    hist_cum = hist_norm.cumsum()
    return hist.tolist(), hist_cum.tolist()

@app.post("/image/histogram")
async def histogram_equalization(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Compute original histograms
    orig_hist, orig_cum = compute_histograms(img)
    
    # Apply equalization
    equalized = cv2.equalizeHist(img)
    
    # Compute equalized histograms
    eq_hist, eq_cum = compute_histograms(equalized)
    
    return {
        "processedImage": encode_image(equalized),
        "histogramData": {
            "original": {
                "histogram": orig_hist,
                "cumulative": orig_cum
            },
            "processed": {
                "histogram": eq_hist,
                "cumulative": eq_cum
            }
        }
    }

@app.post("/image/contrast")
async def contrast_stretching(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Compute original histograms
    orig_hist, orig_cum = compute_histograms(img)
    
    # Apply contrast stretching
    min_val = np.min(img)
    max_val = np.max(img)
    stretched = ((img - min_val) * 255 / (max_val - min_val)).astype(np.uint8)
    
    # Compute stretched histograms
    str_hist, str_cum = compute_histograms(stretched)
    
    return {
        "processedImage": encode_image(stretched),
        "histogramData": {
            "original": {
                "histogram": orig_hist,
                "cumulative": orig_cum
            },
            "processed": {
                "histogram": str_hist,
                "cumulative": str_cum
            }
        }
    }

@app.post("/image/noise")
async def add_noise(
    image: UploadFile = File(...),
    noise_type: str = Form(...),
    param: float = Form(...)
):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if noise_type == "gaussian":
        noisy = cv2.GaussianBlur(img, (5,5), param)
    elif noise_type == "salt_pepper":
        noisy = add_salt_pepper_noise(img, param)
    else:
        raise HTTPException(status_code=400, detail="Invalid noise type")
    
    return {"processedImage": encode_image(noisy)}

@app.post("/image/transform")
async def transform_image(
    image: UploadFile = File(...),
    transform_type: str = Form(...),
    params: str = Form(...)
):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    params = json.loads(params)
    if transform_type == "rotation":
        matrix = cv2.getRotationMatrix2D((img.shape[1]/2, img.shape[0]/2), params['angle'], 1)
        transformed = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
    elif transform_type == "translation":
        matrix = np.float32([[1,0,params['tx']],[0,1,params['ty']]])
        transformed = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
    else:
        raise HTTPException(status_code=400, detail="Invalid transform type")
    
    return {"processedImage": encode_image(transformed)}

@app.post("/image/filter")
async def apply_filter(
    image: UploadFile = File(...),
    filter_type: str = Form(...),
    kernel_size: int = Form(...)
):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if filter_type == "min":
        filtered = cv2.erode(img, np.ones((kernel_size,kernel_size),np.uint8))
    elif filter_type == "max":
        filtered = cv2.dilate(img, np.ones((kernel_size,kernel_size),np.uint8))
    elif filter_type == "median":
        filtered = cv2.medianBlur(img, kernel_size)
    elif filter_type == "mean":
        filtered = cv2.blur(img, (kernel_size,kernel_size))
    else:
        raise HTTPException(status_code=400, detail="Invalid filter type")
    
    return {"processedImage": encode_image(filtered)}

@app.post("/image/convolution")
async def apply_convolution(
    image: UploadFile = File(...),
    mask_type: str = Form(...)
):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if mask_type == "sobel_x":
        kernel = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])
    elif mask_type == "sobel_y":
        kernel = np.array([[-1,-2,-1],[0,0,0],[1,2,1]])
    else:
        raise HTTPException(status_code=400, detail="Invalid mask type")
    
    filtered = cv2.filter2D(img, -1, kernel)
    return {"processedImage": encode_image(filtered)}

@app.post("/image/fourier")
async def fourier_transform(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20*np.log(np.abs(fshift))
    
    return {"processedImage": encode_image(magnitude_spectrum.astype(np.uint8))}

@app.post("/image/fourier-filter")
async def fourier_filter(
    image: UploadFile = File(...),
    filter_type: str = Form(...),
    cutoff: float = Form(...)
):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    rows, cols = img.shape
    crow, ccol = rows//2, cols//2
    
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    
    mask = np.ones((rows,cols), np.uint8)
    if filter_type == "lowpass":
        mask[crow-int(cutoff):crow+int(cutoff), ccol-int(cutoff):ccol+int(cutoff)] = 0
    elif filter_type == "highpass":
        mask[crow-int(cutoff):crow+int(cutoff), ccol-int(cutoff):ccol+int(cutoff)] = 1
    
    fshift = fshift * mask
    f_ishift = np.fft.ifftshift(fshift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    
    return {"processedImage": encode_image(img_back.astype(np.uint8))}

@app.post("/image/pyramids")
async def image_pyramids(
    image: UploadFile = File(...),
    levels: int = Form(...)
):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    pyramid = [img]
    for i in range(levels):
        img = cv2.pyrDown(img)
        pyramid.append(img)
    
    result = np.hstack(pyramid)
    return {"processedImage": encode_image(result)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
