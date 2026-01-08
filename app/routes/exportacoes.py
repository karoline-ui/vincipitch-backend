"""
Rotas para exportação de relatórios.
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response, StreamingResponse
import io

from app.core.supabase import SupabaseService, get_supabase_service
from app.models.schemas import (
    ExportacaoCreate, ExportacaoResponse, SetorEnum
)
from app.services.document_exporter import DocumentExporter
from app.services.chart_generator import ChartGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exportacoes", tags=["Exportações"])


@router.post("/empresa/{empresa_id}/pdf", response_class=Response)
async def exportar_empresa_pdf(
    empresa_id: UUID,
    incluir_graficos: bool = Query(True),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Exporta relatório completo de uma empresa em PDF.
    
    Inclui:
    - Sumário executivo
    - Notas por critério
    - Gráfico radar (se incluir_graficos=True)
    - Diagnóstico SWOT
    - Recomendações
    """
    try:
        # Obtém dados
        empresa = await supabase.obter_empresa(str(empresa_id))
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        analise = await supabase.obter_analise_empresa(str(empresa_id))
        if not analise:
            raise HTTPException(status_code=404, detail="Empresa não possui análise")
        
        # Gera gráfico se solicitado
        grafico_radar = None
        if incluir_graficos:
            chart_gen = ChartGenerator()
            notas = {
                "sumario_executivo": analise.get("nota_sumario_executivo", 0),
                "proposta_valor": analise.get("nota_proposta_valor", 0),
                "concorrencia": analise.get("nota_concorrencia", 0),
                "mercado_alvo": analise.get("nota_mercado_alvo", 0),
                "canais_distribuicao": analise.get("nota_canais_distribuicao", 0),
                "relacionamento_clientes": analise.get("nota_relacionamento_clientes", 0),
                "fontes_receita": analise.get("nota_fontes_receita", 0),
                "recursos_principais": analise.get("nota_recursos_principais", 0),
                "atividades_chave": analise.get("nota_atividades_chave", 0),
                "parceiros": analise.get("nota_parceiros", 0),
                "estrutura_custos": analise.get("nota_estrutura_custos", 0),
                "referencias_indicacao": analise.get("nota_referencias_indicacao", 0)
            }
            grafico_radar = chart_gen.gerar_radar_criterios(notas, titulo=f"Análise - {empresa['nome']}")
        
        # Exporta PDF
        exporter = DocumentExporter()
        pdf_bytes = await exporter.exportar_pdf(
            analise=analise,
            empresa=empresa,
            grafico_radar=grafico_radar,
            diagnostico=analise.get('diagnostico', {})
        )
        
        # Tenta salvar registro da exportação (não bloqueia se falhar)
        try:
            nome_arquivo = f"relatorio_{empresa['nome'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            storage_path = f"exportacoes/{empresa_id}/{nome_arquivo}"
            
            await supabase.upload_arquivo("exportacoes", storage_path, pdf_bytes, "application/pdf")
            
            await supabase.criar_exportacao({
                "tipo": "relatorio_empresa",
                "formato": "pdf",
                "empresa_id": str(empresa_id),
                "analise_id": analise['id'],
                "nome_arquivo": nome_arquivo,
                "storage_path": storage_path,
                "tamanho_bytes": len(pdf_bytes),
                "contem_graficos": incluir_graficos
            })
        except Exception as e:
            logger.warning(f"Não foi possível salvar registro da exportação: {e}")
            nome_arquivo = f"relatorio_{empresa['nome'].replace(' ', '_')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/empresa/{empresa_id}/docx", response_class=Response)
async def exportar_empresa_docx(
    empresa_id: UUID,
    incluir_graficos: bool = Query(True),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Exporta relatório de uma empresa em Word (DOCX)."""
    try:
        empresa = await supabase.obter_empresa(str(empresa_id))
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        analise = await supabase.obter_analise_empresa(str(empresa_id))
        if not analise:
            raise HTTPException(status_code=404, detail="Empresa não possui análise")
        
        # Gera gráfico se solicitado
        grafico_radar = None
        if incluir_graficos:
            chart_gen = ChartGenerator()
            notas = {k: analise.get(f"nota_{k}", 0) for k in [
                "sumario_executivo", "proposta_valor", "concorrencia", "mercado_alvo",
                "canais_distribuicao", "relacionamento_clientes", "fontes_receita",
                "recursos_principais", "atividades_chave", "parceiros",
                "estrutura_custos", "referencias_indicacao"
            ]}
            grafico_radar = chart_gen.gerar_radar_criterios(notas)
        
        # Exporta DOCX
        exporter = DocumentExporter()
        docx_bytes = await exporter.exportar_docx(
            analise=analise,
            empresa=empresa,
            grafico_radar=grafico_radar,
            diagnostico=analise.get('diagnostico', {})
        )
        
        nome_arquivo = f"relatorio_{empresa['nome'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar DOCX: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ranking/xlsx", response_class=Response)
async def exportar_ranking_xlsx(
    setor: Optional[SetorEnum] = None,
    limite: int = Query(100, ge=1, le=500),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Exporta ranking completo para Excel (XLSX).
    
    Inclui:
    - Aba de ranking com todas as notas
    - Aba de estatísticas
    """
    try:
        # Obtém dados
        if setor:
            ranking = await supabase.obter_ranking_setor(setor.value, limite=limite)
        else:
            ranking = await supabase.obter_ranking_geral(limite=limite)
        
        items = ranking.get("items", [])
        if not items:
            raise HTTPException(status_code=404, detail="Sem dados para exportar")
        
        # Obtém dados das empresas
        empresas = []
        for item in items:
            empresa = await supabase.obter_empresa(item.get('id', item.get('empresa_id')))
            if empresa:
                empresas.append(empresa)
        
        # Prepara análises
        analises = []
        for item in items:
            analise = await supabase.obter_analise_empresa(item.get('id', item.get('empresa_id')))
            if analise:
                analise['empresa_id'] = item.get('id', item.get('empresa_id'))
                analises.append(analise)
        
        # Exporta XLSX
        exporter = DocumentExporter()
        titulo = f"Ranking VinciPitch" + (f" - {setor.value.title()}" if setor else " - Geral")
        xlsx_bytes = await exporter.exportar_xlsx(
            analises=analises,
            empresas=empresas,
            titulo=titulo
        )
        
        nome_arquivo = f"ranking_{'_'.join([setor.value] if setor else ['geral'])}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return Response(
            content=xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar XLSX: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ranking/pdf", response_class=Response)
async def exportar_ranking_pdf(
    setor: Optional[SetorEnum] = None,
    limite: int = Query(50, ge=1, le=100),
    incluir_graficos: bool = Query(True),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Exporta ranking em PDF com gráficos."""
    try:
        # Obtém dados
        if setor:
            ranking = await supabase.obter_ranking_setor(setor.value, limite=limite)
        else:
            ranking = await supabase.obter_ranking_geral(limite=limite)
        
        items = ranking.get("items", [])
        if not items:
            raise HTTPException(status_code=404, detail="Sem dados para exportar")
        
        # Calcula estatísticas
        notas = [item.get("nota_final", 0) for item in items if item.get("nota_final")]
        import numpy as np
        estatisticas = {
            "total": len(items),
            "media": np.mean(notas) if notas else 0,
            "mediana": np.median(notas) if notas else 0,
            "desvio_padrao": np.std(notas) if notas else 0
        }
        
        # Gera gráfico se solicitado
        grafico_barras = None
        if incluir_graficos:
            chart_gen = ChartGenerator()
            grafico_barras = chart_gen.gerar_barras_ranking(items[:15])
        
        # Exporta PDF
        exporter = DocumentExporter()
        titulo = f"Ranking VinciPitch.AI" + (f" - {setor.value.title()}" if setor else "")
        pdf_bytes = await exporter.exportar_ranking_pdf(
            ranking=items,
            estatisticas=estatisticas,
            grafico_barras=grafico_barras,
            titulo=titulo
        )
        
        nome_arquivo = f"ranking_{'_'.join([setor.value] if setor else ['geral'])}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar ranking PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTAÇÃO DE COMPARAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/comparacao/{empresa_a_id}/{empresa_b_id}/pdf", response_class=Response)
async def exportar_comparacao_pdf(
    empresa_a_id: UUID,
    empresa_b_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Exporta comparação entre duas empresas em PDF."""
    try:
        # Obtém dados das empresas
        empresa_a = await supabase.obter_empresa(str(empresa_a_id))
        empresa_b = await supabase.obter_empresa(str(empresa_b_id))
        
        if not empresa_a or not empresa_b:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        # Obtém análises
        analise_a = await supabase.obter_analise_empresa(str(empresa_a_id))
        analise_b = await supabase.obter_analise_empresa(str(empresa_b_id))
        
        if not analise_a or not analise_b:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        # Gera gráfico comparativo
        chart_gen = ChartGenerator()
        dados_a = {"nome": empresa_a['nome'], **analise_a}
        dados_b = {"nome": empresa_b['nome'], **analise_b}
        grafico_comparativo = chart_gen.gerar_comparativo(dados_a, dados_b)
        
        # Exporta PDF
        exporter = DocumentExporter()
        pdf_bytes = await exporter.exportar_comparacao_pdf(
            empresa_a=empresa_a,
            empresa_b=empresa_b,
            analise_a=analise_a,
            analise_b=analise_b,
            grafico_comparativo=grafico_comparativo
        )
        
        nome_arquivo = f"comparacao_{empresa_a['nome']}_{empresa_b['nome']}_{datetime.now().strftime('%Y%m%d')}.pdf"
        nome_arquivo = nome_arquivo.replace(' ', '_')
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar comparação PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comparacao/{empresa_a_id}/{empresa_b_id}/docx", response_class=Response)
async def exportar_comparacao_docx(
    empresa_a_id: UUID,
    empresa_b_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Exporta comparação entre duas empresas em Word (DOCX)."""
    try:
        # Obtém dados das empresas
        empresa_a = await supabase.obter_empresa(str(empresa_a_id))
        empresa_b = await supabase.obter_empresa(str(empresa_b_id))
        
        if not empresa_a or not empresa_b:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        # Obtém análises
        analise_a = await supabase.obter_analise_empresa(str(empresa_a_id))
        analise_b = await supabase.obter_analise_empresa(str(empresa_b_id))
        
        if not analise_a or not analise_b:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        # Gera gráfico comparativo
        chart_gen = ChartGenerator()
        dados_a = {"nome": empresa_a['nome'], **analise_a}
        dados_b = {"nome": empresa_b['nome'], **analise_b}
        grafico_comparativo = chart_gen.gerar_comparativo(dados_a, dados_b)
        
        # Exporta DOCX
        exporter = DocumentExporter()
        docx_bytes = await exporter.exportar_comparacao_docx(
            empresa_a=empresa_a,
            empresa_b=empresa_b,
            analise_a=analise_a,
            analise_b=analise_b,
            grafico_comparativo=grafico_comparativo
        )
        
        nome_arquivo = f"comparacao_{empresa_a['nome']}_{empresa_b['nome']}_{datetime.now().strftime('%Y%m%d')}.docx"
        nome_arquivo = nome_arquivo.replace(' ', '_')
        
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar comparação DOCX: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list)
async def listar_exportacoes(
    tipo: Optional[str] = Query(None, regex="^(relatorio_empresa|ranking|comparativo|dashboard|planilha)$"),
    formato: Optional[str] = Query(None, regex="^(pdf|xlsx|docx|pptx|csv|json)$"),
    limite: int = Query(20, ge=1, le=100),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Lista exportações realizadas."""
    try:
        filtros = {}
        if tipo:
            filtros["tipo"] = tipo
        if formato:
            filtros["formato"] = formato
        
        exportacoes = await supabase.listar_exportacoes(filtros=filtros, limite=limite)
        return exportacoes
    except Exception as e:
        logger.error(f"Erro ao listar exportações: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{exportacao_id}/download")
async def download_exportacao(
    exportacao_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Faz download de uma exportação existente."""
    try:
        exportacao = await supabase.obter_exportacao(str(exportacao_id))
        if not exportacao:
            raise HTTPException(status_code=404, detail="Exportação não encontrada")
        
        # Obtém arquivo do storage
        arquivo_bytes = await supabase.download_arquivo(
            "exportacoes",
            exportacao['storage_path']
        )
        
        # Determina content-type
        content_types = {
            "pdf": "application/pdf",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "csv": "text/csv",
            "json": "application/json"
        }
        
        content_type = content_types.get(exportacao['formato'], "application/octet-stream")
        
        # Atualiza contador de downloads
        await supabase.incrementar_downloads(str(exportacao_id))
        
        return Response(
            content=arquivo_bytes,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={exportacao['nome_arquivo']}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer download: {e}")
        raise HTTPException(status_code=500, detail=str(e))