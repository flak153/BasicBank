from fastapi import FastAPI
from app.api.api import api_router
from app.database import engine, Base

# Create all database tables defined in the metadata
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application with a title
app = FastAPI(title="Bank API")

# Include the API router to handle all API endpoints
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application using Uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=8000)