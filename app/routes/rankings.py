"""
Rotas para rankings e estatísticas.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response

from app.core.supabase import SupabaseService, get_supabase_service
from app.models.schemas import (
    RankingResponse, EstatisticasSetor, SetorEnum,
    ComparacaoCreate, ComparacaoResponse, FiltrosAnalise
)
from app.services.chart_generator import ChartGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rankings", tags=["Rankings"])


@router.get("/geral", response_model=RankingResponse)
async def obter_ranking_geral(
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Obtém ranking geral de todas as startups.
    
    Ordenado por nota final (maior para menor).
    """
    try:
        ranking = await supabase.obter_ranking_geral(limite=limite, offset=offset)
        
        return RankingResponse(
            tipo="geral",
            items=ranking.get("items", []),
            total=ranking.get("total", 0),
            estatisticas={
                "media": ranking.get("media", 0),
                "mediana": ranking.get("mediana", 0),
                "desvio_padrao": ranking.get("desvio_padrao", 0)
            }
        )
    except Exception as e:
        logger.error(f"Erro ao obter ranking geral: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/setor/{setor}", response_model=RankingResponse)
async def obter_ranking_setor(
    setor: SetorEnum,
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Obtém ranking de startups de um setor específico.
    """
    try:
        ranking = await supabase.obter_ranking_setor(
            setor=setor.value,
            limite=limite,
            offset=offset
        )
        
        return RankingResponse(
            tipo="setor",
            setor=setor.value,
            items=ranking.get("items", []),
            total=ranking.get("total", 0),
            estatisticas=ranking.get("estatisticas", {})
        )
    except Exception as e:
        logger.error(f"Erro ao obter ranking do setor {setor}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estatisticas", response_model=List[EstatisticasSetor])
async def obter_estatisticas_setores(
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Obtém estatísticas agregadas por setor.
    
    Inclui: total de empresas, média, mínimo, máximo, desvio padrão.
    """
    try:
        estatisticas = await supabase.obter_estatisticas_setores()
        return estatisticas
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estatisticas/{setor}", response_model=EstatisticasSetor)
async def obter_estatisticas_setor(
    setor: SetorEnum,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Obtém estatísticas de um setor específico."""
    try:
        estatisticas = await supabase.obter_estatisticas_setor(setor.value)
        if not estatisticas:
            raise HTTPException(
                status_code=404, 
                detail=f"Sem dados para o setor {setor.value}"
            )
        return estatisticas
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do setor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filtrar", response_model=RankingResponse)
async def filtrar_ranking(
    filtros: FiltrosAnalise,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Filtra ranking com critérios avançados.
    
    Permite filtrar por:
    - Setores (múltiplos)
    - Estágios (múltiplos)
    - Faixa de nota
    - Faixa de faturamento
    - Classificação de potencial/risco
    """
    try:
        ranking = await supabase.filtrar_ranking(filtros.model_dump(exclude_unset=True))
        
        return RankingResponse(
            tipo="customizado",
            items=ranking.get("items", []),
            total=ranking.get("total", 0),
            estatisticas=ranking.get("estatisticas", {})
        )
    except Exception as e:
        logger.error(f"Erro ao filtrar ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comparar", response_model=ComparacaoResponse)
async def comparar_empresas(
    comparacao: ComparacaoCreate,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Compara duas empresas lado a lado.
    
    Retorna:
    - Notas comparativas por critério
    - Vencedor geral
    - Justificativa da IA
    """
    try:
        # Obtém análises das duas empresas
        analise_a = await supabase.obter_analise_empresa(str(comparacao.empresa_a_id))
        analise_b = await supabase.obter_analise_empresa(str(comparacao.empresa_b_id))
        
        if not analise_a:
            raise HTTPException(
                status_code=404, 
                detail=f"Empresa A ({comparacao.empresa_a_id}) não possui análise"
            )
        if not analise_b:
            raise HTTPException(
                status_code=404, 
                detail=f"Empresa B ({comparacao.empresa_b_id}) não possui análise"
            )
        
        # Obtém dados das empresas
        empresa_a = await supabase.obter_empresa(str(comparacao.empresa_a_id))
        empresa_b = await supabase.obter_empresa(str(comparacao.empresa_b_id))
        
        # Monta comparativo
        criterios = [
            "sumario_executivo", "proposta_valor", "concorrencia", "mercado_alvo",
            "canais_distribuicao", "relacionamento_clientes", "fontes_receita",
            "recursos_principais", "atividades_chave", "parceiros",
            "estrutura_custos", "referencias_indicacao"
        ]
        
        comparativo = {}
        vitorias_a = 0
        vitorias_b = 0
        
        for criterio in criterios:
            nota_a = analise_a.get(f"nota_{criterio}", 0) or 0
            nota_b = analise_b.get(f"nota_{criterio}", 0) or 0
            
            vencedor = None
            if nota_a > nota_b:
                vencedor = "A"
                vitorias_a += 1
            elif nota_b > nota_a:
                vencedor = "B"
                vitorias_b += 1
            
            comparativo[criterio] = {
                "nota_a": nota_a,
                "nota_b": nota_b,
                "diferenca": nota_a - nota_b,
                "vencedor": vencedor
            }
        
        # Determina vencedor geral
        nota_final_a = analise_a.get("nota_final", 0) or 0
        nota_final_b = analise_b.get("nota_final", 0) or 0
        
        if nota_final_a > nota_final_b:
            vencedor_id = str(comparacao.empresa_a_id)
            margem = nota_final_a - nota_final_b
        elif nota_final_b > nota_final_a:
            vencedor_id = str(comparacao.empresa_b_id)
            margem = nota_final_b - nota_final_a
        else:
            vencedor_id = None
            margem = 0
        
        # Salva comparação
        comparacao_data = {
            "empresa_a_id": str(comparacao.empresa_a_id),
            "empresa_b_id": str(comparacao.empresa_b_id),
            "analise_a_id": analise_a['id'],
            "analise_b_id": analise_b['id'],
            "vencedor_id": vencedor_id,
            "margem_diferenca": margem,
            "comparativo": comparativo,
            "justificativa_ia": f"{empresa_a['nome']} vs {empresa_b['nome']}: {'Empate técnico' if not vencedor_id else f'Vencedor com margem de {margem:.2f}'}"
        }
        
        resultado = await supabase.criar_comparacao(comparacao_data)
        
        # Enriquece resposta
        resultado["empresa_a"] = empresa_a
        resultado["empresa_b"] = empresa_b
        resultado["vitorias_a"] = vitorias_a
        resultado["vitorias_b"] = vitorias_b
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao comparar empresas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparar/{empresa_a_id}/{empresa_b_id}/grafico")
async def obter_grafico_comparativo(
    empresa_a_id: UUID,
    empresa_b_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Gera gráfico comparativo entre duas empresas."""
    try:
        # Obtém dados
        analise_a = await supabase.obter_analise_empresa(str(empresa_a_id))
        analise_b = await supabase.obter_analise_empresa(str(empresa_b_id))
        empresa_a = await supabase.obter_empresa(str(empresa_a_id))
        empresa_b = await supabase.obter_empresa(str(empresa_b_id))
        
        if not all([analise_a, analise_b, empresa_a, empresa_b]):
            raise HTTPException(status_code=404, detail="Dados não encontrados")
        
        # Prepara dados
        dados_a = {"nome": empresa_a['nome'], **analise_a}
        dados_b = {"nome": empresa_b['nome'], **analise_b}
        
        # Gera gráfico
        chart_gen = ChartGenerator()
        grafico_bytes = chart_gen.gerar_comparativo(dados_a, dados_b)
        
        return Response(
            content=grafico_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=comparativo_{empresa_a_id}_{empresa_b_id}.png"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico comparativo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grafico-barras")
async def obter_grafico_ranking(
    setor: Optional[SetorEnum] = None,
    limite: int = Query(15, ge=5, le=30),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Gera gráfico de barras do ranking."""
    try:
        if setor:
            ranking = await supabase.obter_ranking_setor(setor.value, limite=limite)
        else:
            ranking = await supabase.obter_ranking_geral(limite=limite)
        
        items = ranking.get("items", [])
        if not items:
            raise HTTPException(status_code=404, detail="Sem dados para gerar gráfico")
        
        chart_gen = ChartGenerator()
        titulo = f"Top {limite} Startups" + (f" - {setor.value.title()}" if setor else " - Geral")
        grafico_bytes = chart_gen.gerar_barras_ranking(items, titulo=titulo, max_empresas=limite)
        
        return Response(
            content=grafico_bytes,
            media_type="image/png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grafico-distribuicao")
async def obter_grafico_distribuicao(
    setor: Optional[SetorEnum] = None,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Gera histograma de distribuição de notas."""
    try:
        if setor:
            ranking = await supabase.obter_ranking_setor(setor.value, limite=500)
        else:
            ranking = await supabase.obter_ranking_geral(limite=500)
        
        items = ranking.get("items", [])
        notas = [item.get("nota_final", 0) for item in items if item.get("nota_final")]
        
        if not notas:
            raise HTTPException(status_code=404, detail="Sem dados para gerar gráfico")
        
        chart_gen = ChartGenerator()
        grafico_bytes = chart_gen.gerar_distribuicao_notas(
            notas,
            titulo="Distribuição de Notas",
            setor=setor.value if setor else None
        )
        
        return Response(
            content=grafico_bytes,
            media_type="image/png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de distribuição: {e}")
        raise HTTPException(status_code=500, detail=str(e))
