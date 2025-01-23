from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.image_processing import router as image_processing_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router at some prefix, e.g. "/api"
app.include_router(image_processing_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
