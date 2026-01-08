"""
VinciPitch.AI - API Principal
Backend FastAPI para análise de startups com IA.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.routes import empresas_router, analises_router, rankings_router, exportacoes_router

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle da aplicação"""
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("👋 Encerrando aplicação")


# Criação da aplicação
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## VinciPitch.AI - Análise Inteligente de Startups
    
    API para análise automatizada de startups usando IA.
    
    ### Funcionalidades:
    - 📄 Upload de PDFs de startups
    - 🤖 Análise automatizada com IA (12 critérios)
    - 📊 Diagnóstico estratégico detalhado
    - 🏆 Ranking e comparações
    - 📈 Exportação para Excel/PDF
    - 💬 Perguntas analíticas à IA
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS - Permitir origens do GCP
cors_origins = settings.CORS_ORIGINS + [
    "https://*.run.app",  # Cloud Run
    "https://*.appspot.com",  # App Engine
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(empresas_router, prefix="/api/v1")
app.include_router(analises_router, prefix="/api/v1")
app.include_router(rankings_router, prefix="/api/v1")
app.include_router(exportacoes_router, prefix="/api/v1")


# ═══════════════════════════════════════════════════════════════════════════════
# ROTAS BASE / GCP
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """
    Health check para GCP Cloud Run / Load Balancer.
    Retorna status da aplicação.
    """
    return {"ok": True, "status": "healthy"}


@app.get("/whoami")
async def whoami():
    """
    Informações do ambiente para debug.
    Útil para verificar deploy no GCP.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": os.getenv("APP_ENV", "development"),
        "debug": settings.DEBUG,
        "python_env": os.getenv("PYTHONENV", "not_set"),
        "gcp_project": os.getenv("GOOGLE_CLOUD_PROJECT", "not_set"),
        "cloud_run_service": os.getenv("K_SERVICE", "not_set"),
        "cloud_run_revision": os.getenv("K_REVISION", "not_set"),
    }


@app.get("/readiness")
async def readiness():
    """
    Readiness check - verifica se a aplicação está pronta para receber tráfego.
    Usado pelo Kubernetes/Cloud Run.
    """
    # Aqui poderia verificar conexão com Supabase, etc.
    return {"ready": True}


@app.get("/liveness")
async def liveness():
    """
    Liveness check - verifica se a aplicação está viva.
    Usado pelo Kubernetes/Cloud Run.
    """
    return {"alive": True}


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # GCP Cloud Run usa PORT
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )
