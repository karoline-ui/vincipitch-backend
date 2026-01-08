"""
═══════════════════════════════════════════════════════════════════════════════
VINCIPITCH.AI - MODELOS PYDANTIC
═══════════════════════════════════════════════════════════════════════════════
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class SetorEnum(str, Enum):
    AGRITECH = "agritech"
    BIOTECH = "biotech"
    CONSTRUTECH = "construtech"
    COSMETICA_NATURAL = "cosmetica_natural"
    CYBERSECURITY = "cybersecurity"
    EDTECH = "edtech"
    FINTECH = "fintech"
    FOODTECH = "foodtech"
    GREENTECH = "greentech"
    HEALTHTECH = "healthtech"
    INSURTECH = "insurtech"
    LEGALTECH = "legaltech"
    MARTECH = "martech"
    PROPTECH = "proptech"
    RETAILTECH = "retailtech"
    OUTRO = "outro"


class StatusAnaliseEnum(str, Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDA = "concluida"
    ERRO = "erro"
    REVISAO = "revisao"


class EstagioStartupEnum(str, Enum):
    IDEACAO = "ideacao"
    VALIDACAO = "validacao"
    MVP = "mvp"
    PRODUCT_MARKET_FIT = "product_market_fit"
    ESCALA = "escala"
    EXPANSAO = "expansao"
    MADURO = "maduro"


class ClassificacaoRiscoEnum(str, Enum):
    MUITO_BAIXO = "muito_baixo"
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    MUITO_ALTO = "muito_alto"


# ═══════════════════════════════════════════════════════════════════════════════
# RESPOSTAS GENÉRICAS
# ═══════════════════════════════════════════════════════════════════════════════

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """
    Compatível com o que suas rotas estão retornando em empresas.py:
    PaginatedResponse(success=True, data=[...], total=..., limit=..., offset=...)
    """
    success: bool = True
    data: List[Any]
    total: int
    limit: int
    offset: int


# ═══════════════════════════════════════════════════════════════════════════════
# EMPRESA
# ═══════════════════════════════════════════════════════════════════════════════

class EmpresaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    setor: SetorEnum
    subsetor: Optional[str] = None
    estagio: EstagioStartupEnum = EstagioStartupEnum.IDEACAO
    cidade: Optional[str] = None
    estado: Optional[str] = None
    pais: str = "Brasil"
    ano_fundacao: Optional[int] = None
    numero_funcionarios: Optional[int] = None
    faturamento_anual: Optional[float] = None
    faturamento_mensal: Optional[float] = None
    mrr: Optional[float] = None
    arr: Optional[float] = None
    valuation: Optional[float] = None
    runway_meses: Optional[int] = None
    capital_levantado: Optional[float] = None
    rodada_atual: Optional[str] = None
    investidores: Optional[List[str]] = []
    numero_clientes: Optional[int] = None
    numero_usuarios: Optional[int] = None
    cac: Optional[float] = None
    ltv: Optional[float] = None
    churn_rate: Optional[float] = None
    nps_score: Optional[int] = None
    tags: Optional[List[str]] = []
    descricao_curta: Optional[str] = None

    @validator("investidores", "tags", pre=True, always=True)
    def set_list_default(cls, v):
        return v or []


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    nome: Optional[str] = None
    setor: Optional[SetorEnum] = None
    estagio: Optional[EstagioStartupEnum] = None
    website: Optional[str] = None
    descricao_curta: Optional[str] = None
    faturamento_anual: Optional[float] = None
    faturamento_mensal: Optional[float] = None
    mrr: Optional[float] = None
    arr: Optional[float] = None
    valuation: Optional[float] = None
    runway_meses: Optional[int] = None
    capital_levantado: Optional[float] = None
    rodada_atual: Optional[str] = None
    investidores: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class EmpresaResponse(EmpresaBase):
    id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTO
# ═══════════════════════════════════════════════════════════════════════════════

class DocumentoBase(BaseModel):
    empresa_id: UUID
    nome_arquivo: str
    tipo_arquivo: str = "pdf"
    tamanho_bytes: Optional[int] = None


class DocumentoCreate(DocumentoBase):
    storage_path: str


class DocumentoResponse(DocumentoBase):
    id: UUID
    storage_path: str
    texto_extraido: Optional[str] = None
    texto_limpo: Optional[str] = None
    numero_paginas: Optional[int] = None
    metodo_extracao: Optional[str] = None
    qualidade_extracao: Optional[float] = None
    processado: bool = False
    erro_processamento: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# ANÁLISE / RANKING / FILTROS / COMPARAÇÃO (mantive igual ao seu, só garantindo nomes)
# ═══════════════════════════════════════════════════════════════════════════════

class AnaliseCreate(BaseModel):
    empresa_id: UUID
    documento_id: Optional[UUID] = None
    sessao_id: Optional[UUID] = None


class AnaliseResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    documento_id: Optional[UUID] = None
    sessao_id: Optional[UUID] = None
    status: StatusAnaliseEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RankingItem(BaseModel):
    posicao: Optional[int] = None
    id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    nome: str
    setor: str
    nota_final: float
    variacao: Optional[int] = None
    resumo: Optional[str] = None
    classificacao_potencial: Optional[str] = None
    classificacao_risco: Optional[str] = None


class RankingResponse(BaseModel):
    tipo: str
    setor: Optional[str] = None
    items: List[RankingItem] = []
    total: int = 0
    estatisticas: Optional[Dict[str, Any]] = None
    
    # Campos calculados para compatibilidade com frontend
    @property
    def total_empresas(self) -> int:
        return self.total
    
    @property
    def media_geral(self) -> float:
        if self.estatisticas:
            return self.estatisticas.get("media", 0)
        return 0
    
    @property
    def ranking(self) -> List[RankingItem]:
        return self.items


class EstatisticasSetor(BaseModel):
    setor: SetorEnum
    total_empresas: int
    media_nota: float
    menor_nota: float
    maior_nota: float
    desvio_padrao: Optional[float] = None
    media_faturamento: Optional[float] = None


class FiltrosAnalise(BaseModel):
    setores: List[SetorEnum] = []
    estagios: List[EstagioStartupEnum] = []
    nota_minima: Optional[float] = Field(None, ge=0, le=4)
    nota_maxima: Optional[float] = Field(None, ge=0, le=4)
    faturamento_minimo: Optional[float] = None
    faturamento_maximo: Optional[float] = None
    tags: List[str] = []
    ordenar_por: str = "nota_final"
    ordem: str = "desc"
    limite: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


class ComparacaoCreate(BaseModel):
    empresa_a_id: UUID
    empresa_b_id: UUID


class ComparacaoResponse(BaseModel):
    id: Optional[UUID] = None
    empresa_a_id: UUID
    empresa_b_id: UUID
    vencedor_id: Optional[UUID] = None
    margem_diferenca: Optional[float] = 0
    comparativo: Dict[str, Any] = {}
    justificativa_ia: Optional[str] = None
    created_at: Optional[datetime] = None
    # Campos extras para frontend
    empresa_a: Optional[Dict[str, Any]] = None
    empresa_b: Optional[Dict[str, Any]] = None
    vitorias_a: Optional[int] = 0
    vitorias_b: Optional[int] = 0


# ═══════════════════════════════════════════════════════════════════════════════
# PERGUNTAS IA
# ═══════════════════════════════════════════════════════════════════════════════

class PerguntaIACreate(BaseModel):
    analise_id: UUID
    pergunta: str
    usuario_id: Optional[str] = None


class PerguntaIAResponse(BaseModel):
    id: Optional[UUID] = None
    analise_id: UUID
    pergunta: str
    resposta: str
    tipo_pergunta: Optional[str] = None
    modelo_usado: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════

class ExportacaoCreate(BaseModel):
    empresa_id: Optional[UUID] = None
    tipo: str = "pdf"  # pdf, docx, xlsx
    filtros: Optional[Dict[str, Any]] = None


class ExportacaoResponse(BaseModel):
    id: UUID
    empresa_id: Optional[UUID] = None
    tipo: str
    status: str = "pendente"
    url_download: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
