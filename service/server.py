from fastapi import FastAPI
from service.routes import router

def create_app():
    app = FastAPI(
        title="AI Automation System",
        description="Multi-agent system for automating computer operations",
        version="0.1.0"
    )
    
    # Include API routes
    app.include_router(router)
    
    @app.on_event("startup")
    async def startup_event():
        # Initialize any resources needed
        pass
    
    @app.on_event("shutdown")
    async def shutdown_event():
        # Clean up resources
        pass
    
    return app
