from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import store_router, route_router, auth_router, cart_router

# 1. Initialize FastAPI App
app = FastAPI(
    title="OptiShop API",
    description="The Indoor GPS for Grocery Stores",
    version="1.0.0"
)

# 2. CORS Configuration
# Allowing all origins for development; in production, this should be restricted.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Register Routers
# Including routers under the /api/v1 versioned prefix
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(store_router.router, prefix="/api/v1")
app.include_router(route_router.router, prefix="/api/v1")
app.include_router(cart_router.router, prefix="/api/v1")

# 4. Health Check Endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Simple endpoint to verify the API server is up and running.
    """
    return {"status": "OptiShop API is running"}

if __name__ == "__main__":
    import uvicorn
    # Run the application using uvicorn if this script is executed directly
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
