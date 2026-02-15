"""
Oracle Engine - Phase 1: FastAPI Application
Main API server for MBTI-based business diagnosis
"""
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.schemas import (
    MBTIType,
    DiagnosisRequest,
    DiagnosisResult,
    PsychometricQuestionsResponse
)
from app.engine import OracleEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize engine
engine = OracleEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Oracle Engine - Phase 1 starting up...")
    logger.info("=" * 60)
    logger.info("System initialized by: 高嶺泰志")
    logger.info("Mission: MBTI-based AI business strategy engine")
    logger.info("=" * 60)
    logger.info("🌐 UI available at: http://127.0.0.1:8000/")
    logger.info("📚 API docs at: http://127.0.0.1:8000/docs")
    logger.info("=" * 60)
    yield
    logger.info("Oracle Engine shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Oracle Engine - Phase 1",
    description="MBTI-based AI business diagnosis and roadmap generation system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Serve the main UI"""
    index_path = Path(__file__).parent.parent / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": "Oracle Engine - Phase 1",
        "status": "operational",
        "creator": "高嶺泰志",
        "note": "index.html not found. Please access API docs at /docs",
        "endpoints": {
            "health": "/health",
            "get_questions": "/questions/{mbti}",
            "diagnose": "/diagnose"
        }
    }


@app.get("/privacy")
async def privacy():
    """Serve the privacy policy page"""
    privacy_path = Path(__file__).parent.parent / "privacy.html"
    if privacy_path.exists():
        return FileResponse(privacy_path)
    raise HTTPException(status_code=404, detail="Privacy policy not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "operational",
        "search": "enabled"
    }


@app.get("/questions/{mbti}", response_model=PsychometricQuestionsResponse)
@limiter.limit("15/minute")
async def get_psychometric_questions(request: Request, mbti: MBTIType):
    """
    Get 5 psychometric questions for a specific MBTI type
    
    Args:
        mbti: MBTI personality type
        
    Returns:
        5 tailored questions for business assessment
    """
    try:
        logger.info(f"Fetching psychometric questions for MBTI: {mbti}")
        questions = engine.get_psychometric_questions(mbti)
        
        return PsychometricQuestionsResponse(
            mbti=mbti,
            questions=questions
        )
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/diagnose", response_model=DiagnosisResult)
@limiter.limit("5/minute")
async def diagnose(request: Request, body: DiagnosisRequest):
    """
    Perform complete business diagnosis
    
    This is the main endpoint that:
    1. Maps MBTI to archetype
    2. Analyzes psychometric responses (if provided)
    3. Searches latest AI business trends
    4. Generates device-optimized roadmap
    5. Teases automation tool
    6. Provides transparent disclaimer
    
    Args:
        request: Diagnosis request with MBTI, device, and optional psychometric responses
        
    Returns:
        Complete diagnosis with roadmap and automation teaser
    """
    try:
        # Log request with business archetype mapping
        archetype = engine.get_archetype(body.mbti)
        device_str = body.device.value

        logger.info("=" * 80)
        logger.info(f"📊 NEW DIAGNOSIS REQUEST")
        logger.info(f"   MBTI: {body.mbti.value}")
        logger.info(f"   Device: {device_str}")
        logger.info(f"   Archetype: {archetype.value}")
        logger.info(f"   Psychometric: {'Completed' if body.psychometric_responses else 'Skipped'}")
        logger.info("=" * 80)

        # Generate diagnosis
        result = await engine.generate_diagnosis(
            mbti=body.mbti,
            device=body.device,
            psychometric_responses=body.psychometric_responses
        )
        
        logger.info(f"✅ Diagnosis completed successfully")
        logger.info(f"   Trends found: {len(result.latest_trends)}")
        logger.info(f"   Roadmap steps: {len(result.strategic_roadmap)}")
        logger.info(f"   Automation tool: {result.automation_teaser.tool_name} ({result.automation_teaser.progress_percentage}%)")
        logger.info("=" * 80)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Diagnosis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis generation failed: {str(e)}"
        )


@app.get("/archetypes")
async def get_archetypes():
    """
    Get all available business archetypes with descriptions
    
    Returns:
        Dictionary of archetypes with profiles
    """
    from app.schemas import ArchetypeType
    
    archetypes = {}
    for archetype in ArchetypeType:
        description, strengths, weaknesses = engine.get_archetype_profile(archetype)
        archetypes[archetype.value] = {
            "name": archetype.value,
            "description": description,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    return archetypes


@app.get("/mbti-mapping")
async def get_mbti_mapping():
    """
    Get MBTI to Archetype mapping
    
    Returns:
        Dictionary showing which MBTI types map to which archetypes
    """
    mapping = {}
    for mbti, archetype in engine.MBTI_TO_ARCHETYPE.items():
        mapping[mbti.value] = archetype.value
    
    return mapping


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Oracle Engine server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
