from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.infra.db.session import init_db
from app.api.routes_units import router as units_router
from app.api.routes_tasks import router as tasks_router
from app.api.routes_audit import router as audit_router
from app.api.routes_health import router as health_router
from app.core.exceptions import HREError
from app.adapters.dify_workflow_adapter import DifyWorkflowAdapter  # Import to register


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="HRE-lite",
    description="Heterogeneous Runtime Engine - MVP",
    version="1.0.0",
    lifespan=lifespan
)


# Exception handlers
@app.exception_handler(HREError)
async def hre_exception_handler(request: Request, exc: HREError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


# Include routers
app.include_router(health_router)
app.include_router(units_router)
app.include_router(tasks_router)
app.include_router(audit_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)