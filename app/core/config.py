"""
═══════════════════════════════════════════════════════════════════════════════
VINCIPITCH.AI - CONFIGURAÇÕES DO BACKEND
═══════════════════════════════════════════════════════════════════════════════
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do ambiente"""
    
    # App
    APP_NAME: str = "VinciPitch.AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.2
    
    # Storage
    STORAGE_BUCKET_DOCS: str = "documentos-pitch"
    STORAGE_BUCKET_EXPORTS: str = "exportacoes"
    STORAGE_BUCKET_CHARTS: str = "graficos"
    
    # Limites
    MAX_PDF_SIZE_MB: int = 50
    MAX_BATCH_SIZE: int = 10
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 3600
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cached das configurações"""
    return Settings()


# Instância global das configurações
settings = get_settings()


# Constantes dos setores
SETORES = [
    "biotech",
    "greentech", 
    "healthtech",
    "fintech",
    "edtech",
    "agritech",
    "cosmetica_natural",
    "cybersecurity",
    "retailtech",
    "martech",
    "foodtech",
    "proptech",
    "legaltech",
    "insurtech",
    "outro"
]

# Critérios de avaliação padrão
CRITERIOS_PADRAO = [
    "sumario_executivo",
    "proposta_valor",
    "concorrencia",
    "mercado_alvo",
    "canais_distribuicao",
    "relacionamento_clientes",
    "fontes_receita",
    "recursos_principais",
    "atividades_chave",
    "parceiros",
    "estrutura_custos",
    "referencias_indicacao"
]

# Pesos padrão dos critérios
PESOS_PADRAO = {
    "sumario_executivo": 8,
    "proposta_valor": 10,
    "concorrencia": 8,
    "mercado_alvo": 10,
    "canais_distribuicao": 7,
    "relacionamento_clientes": 7,
    "fontes_receita": 10,
    "recursos_principais": 10,
    "atividades_chave": 7,
    "parceiros": 8,
    "estrutura_custos": 7,
    "referencias_indicacao": 8
}
