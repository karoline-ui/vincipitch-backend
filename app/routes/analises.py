"""
Rotas para processamento e gerenciamento de análises.
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from app.core.supabase import SupabaseService, get_supabase_service
from app.core.config import settings
from app.models.schemas import (
    AnaliseResponse, SetorEnum, StatusAnaliseEnum,
    SuccessResponse, ErrorResponse, PerguntaIACreate, PerguntaIAResponse
)
from app.agents.avaliador import AgenteAvaliador, AgenteDiagnostico
from app.services.chart_generator import ChartGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analises", tags=["Análises"])


async def processar_empresa_background(
    empresa_id: str,
    documento_id: str,
    supabase: SupabaseService
):
    """
    Processa análise de uma empresa em background.
    
    1. Obtém texto do documento
    2. Busca configuração da IA pelo setor
    3. Executa avaliação com agente
    4. Gera diagnóstico estratégico
    5. Salva análise completa
    """
    analise_id = None
    
    try:
        # Obtém empresa e documento
        empresa = await supabase.obter_empresa(empresa_id)
        documento = await supabase.obter_documento(documento_id)
        
        if not empresa or not documento:
            logger.error(f"Empresa ou documento não encontrado: {empresa_id}/{documento_id}")
            return
        
        # Obtém configuração da IA pelo setor
        ia_config = await supabase.obter_config_ia(empresa['setor'])
        
        # Cria registro de análise como "processando"
        analise_data = {
            "empresa_id": empresa_id,
            "documento_id": documento_id,
            "ia_config_id": ia_config['id'] if ia_config else None,
            "status": "processando"
        }
        analise = await supabase.criar_analise(analise_data)
        analise_id = analise['id']
        
        # Prepara texto para avaliação
        texto_pitch = documento.get('texto_limpo') or documento.get('texto_extraido', '')
        
        if not texto_pitch or len(texto_pitch) < 100:
            raise ValueError("Texto do pitch insuficiente para análise")
        
        # Inicializa agentes (com config do setor se disponível)
        avaliador = AgenteAvaliador(config_setor=ia_config)
        diagnosticador = AgenteDiagnostico()
        
        # Executa avaliação
        logger.info(f"Iniciando avaliação da empresa {empresa['nome']}")
        inicio = datetime.now()
        
        avaliacao = await avaliador.avaliar(conteudo_pitch=texto_pitch)
        
        # Executa diagnóstico
        diagnostico = await diagnosticador.diagnosticar(avaliacao)
        
        tempo_ms = int((datetime.now() - inicio).total_seconds() * 1000)
        
        # Monta dados da análise (o agente retorna campos sem prefixo "nota_")
        analise_completa = {
            # Notas
            "nota_sumario_executivo": avaliacao.get("sumario_executivo", 0),
            "nota_proposta_valor": avaliacao.get("proposta_valor", 0),
            "nota_concorrencia": avaliacao.get("concorrencia", 0),
            "nota_mercado_alvo": avaliacao.get("mercado_alvo", 0),
            "nota_canais_distribuicao": avaliacao.get("canais_distribuicao", 0),
            "nota_relacionamento_clientes": avaliacao.get("relacionamento_clientes", 0),
            "nota_fontes_receita": avaliacao.get("fontes_receita", 0),
            "nota_recursos_principais": avaliacao.get("recursos_principais", 0),
            "nota_atividades_chave": avaliacao.get("atividades_chave", 0),
            "nota_parceiros": avaliacao.get("parceiros", 0),
            "nota_estrutura_custos": avaliacao.get("estrutura_custos", 0),
            "nota_referencias_indicacao": avaliacao.get("referencias_indicacao", 0),
            "nota_final": avaliacao.get("nota_final", 0),
            "nota_final_percentual": avaliacao.get("nota_final", 0) * 25,  # 0-100
            
            # Justificativas
            "justificativa_sumario": avaliacao.get("justificativa_sumario", ""),
            "justificativa_proposta": avaliacao.get("justificativa_proposta", ""),
            "justificativa_concorrencia": avaliacao.get("justificativa_concorrencia", ""),
            "justificativa_mercado": avaliacao.get("justificativa_mercado", ""),
            "justificativa_canais": avaliacao.get("justificativa_canais", ""),
            "justificativa_relacionamento": avaliacao.get("justificativa_relacionamento", ""),
            "justificativa_receita": avaliacao.get("justificativa_receita", ""),
            "justificativa_recursos": avaliacao.get("justificativa_recursos", ""),
            "justificativa_atividades": avaliacao.get("justificativa_atividades", ""),
            "justificativa_parceiros": avaliacao.get("justificativa_parceiros", ""),
            "justificativa_custos": avaliacao.get("justificativa_custos", ""),
            "justificativa_referencias": avaliacao.get("justificativa_referencias", ""),
            
            # Critérios específicos do setor
            "criterios_setor": avaliacao.get("criterios_setor", {}),
            
            # Diagnóstico
            "diagnostico": {
                "pontos_fortes": diagnostico.get("pontos_fortes", []),
                "pontos_fracos": diagnostico.get("pontos_fracos", []),
                "oportunidades": diagnostico.get("oportunidades", []),
                "ameacas": diagnostico.get("ameacas", []),
                "recomendacoes": diagnostico.get("recomendacoes", []),
                "proximos_passos": diagnostico.get("proximos_passos", [])
            },
            "resumo_executivo": diagnostico.get("resumo_executivo", ""),
            
            # Classificações
            "classificacao_potencial": diagnostico.get("classificacao_potencial", "medio"),
            "classificacao_risco": diagnostico.get("classificacao_risco", "medio"),
            "recomendacao_investimento": diagnostico.get("recomendacao_investimento", ""),
            
            # Controle
            "status": "concluida",
            "modelo_usado": "gpt-4.1",
            "tempo_processamento_ms": tempo_ms,
            "tokens_input": avaliacao.get("tokens_input", 0),
            "tokens_output": avaliacao.get("tokens_output", 0)
        }
        
        # Atualiza análise
        await supabase.atualizar_analise(analise_id, analise_completa)
        
        logger.info(f"Análise concluída para {empresa['nome']} - Nota: {analise_completa['nota_final']:.2f}")
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        if analise_id:
            await supabase.atualizar_analise(analise_id, {
                "status": "erro",
                "diagnostico": {"erro": str(e)}
            })


@router.post("/processar/{empresa_id}", response_model=SuccessResponse)
async def processar_analise(
    empresa_id: UUID,
    documento_id: Optional[UUID] = None,
    background_tasks: BackgroundTasks = None,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Inicia processamento de análise para uma empresa.
    
    - Se documento_id não for informado, usa o documento mais recente
    - Processamento é feito em background
    - Retorna imediatamente com status de "iniciado"
    """
    try:
        # Verifica empresa
        empresa = await supabase.obter_empresa(str(empresa_id))
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        # Obtém documento
        if documento_id:
            documento = await supabase.obter_documento(str(documento_id))
        else:
            documentos = await supabase.listar_documentos_empresa(str(empresa_id))
            documento = documentos[0] if documentos else None
        
        if not documento:
            raise HTTPException(
                status_code=400, 
                detail="Nenhum documento encontrado. Faça upload do pitch primeiro."
            )
        
        if not documento.get('processado'):
            raise HTTPException(
                status_code=400,
                detail="Documento ainda não foi processado. Aguarde extração do texto."
            )
        
        # Agenda processamento em background
        background_tasks.add_task(
            processar_empresa_background,
            str(empresa_id),
            documento['id'],
            supabase
        )
        
        return SuccessResponse(
            success=True,
            message=f"Análise iniciada para {empresa['nome']}. Aguarde processamento."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar análise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/processar-lote", response_model=SuccessResponse)
async def processar_lote(
    empresa_ids: List[UUID],
    background_tasks: BackgroundTasks,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Processa análises em lote para múltiplas empresas.
    
    - Máximo de 10 empresas por vez
    - Processamento paralelo em background
    """
    if len(empresa_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Máximo de 10 empresas por lote"
        )
    
    empresas_agendadas = []
    erros = []
    
    for empresa_id in empresa_ids:
        try:
            empresa = await supabase.obter_empresa(str(empresa_id))
            if not empresa:
                erros.append(f"{empresa_id}: Empresa não encontrada")
                continue
            
            documentos = await supabase.listar_documentos_empresa(str(empresa_id))
            if not documentos or not documentos[0].get('processado'):
                erros.append(f"{empresa_id}: Sem documento processado")
                continue
            
            background_tasks.add_task(
                processar_empresa_background,
                str(empresa_id),
                documentos[0]['id'],
                supabase
            )
            empresas_agendadas.append(empresa['nome'])
            
        except Exception as e:
            erros.append(f"{empresa_id}: {str(e)}")
    
    return SuccessResponse(
        success=True,
        message=f"Agendadas {len(empresas_agendadas)} análises",
        data={
            "agendadas": empresas_agendadas,
            "erros": erros
        }
    )


@router.get("/{analise_id}", response_model=AnaliseResponse)
async def obter_analise(
    analise_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Obtém detalhes de uma análise específica."""
    try:
        analise = await supabase.obter_analise(str(analise_id))
        if not analise:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        return analise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter análise: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analise_id}/grafico-radar")
async def obter_grafico_radar(
    analise_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Gera e retorna gráfico radar da análise."""
    try:
        analise = await supabase.obter_analise(str(analise_id))
        if not analise:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        # Prepara notas
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
        
        # Gera gráfico
        chart_gen = ChartGenerator()
        grafico_bytes = chart_gen.gerar_radar_criterios(notas)
        
        from fastapi.responses import Response
        return Response(
            content=grafico_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=radar_{analise_id}.png"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[AnaliseResponse])
async def listar_analises(
    status: Optional[StatusAnaliseEnum] = None,
    setor: Optional[SetorEnum] = None,
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Lista análises com filtros."""
    try:
        filtros = {}
        if status:
            filtros["status"] = status.value
        if setor:
            filtros["setor"] = setor.value
        
        analises = await supabase.listar_analises(
            filtros=filtros,
            limite=limite,
            offset=offset
        )
        return analises
    except Exception as e:
        logger.error(f"Erro ao listar análises: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/perguntar", response_model=PerguntaIAResponse)
async def perguntar_ia(
    pergunta: PerguntaIACreate,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """
    Faz uma pergunta à IA sobre uma análise específica.
    
    Permite perguntas como:
    - "Por que a nota de mercado foi baixa?"
    - "O que poderia melhorar na proposta de valor?"
    - "Compare com outras empresas do setor"
    """
    try:
        # Obtém contexto
        analise = await supabase.obter_analise(str(pergunta.analise_id))
        if not analise:
            raise HTTPException(status_code=404, detail="Análise não encontrada")
        
        empresa = await supabase.obter_empresa(analise['empresa_id'])
        
        # TODO: Implementar agente explicador
        # Por enquanto retorna resposta placeholder
        resposta = f"Pergunta recebida sobre {empresa['nome']}: {pergunta.pergunta}"
        
        # Salva pergunta
        pergunta_salva = await supabase.salvar_pergunta({
            "usuario_id": pergunta.usuario_id,
            "empresa_id": analise['empresa_id'],
            "analise_id": str(pergunta.analise_id),
            "pergunta": pergunta.pergunta,
            "resposta": resposta,
            "tipo_pergunta": "explicacao",
            "modelo_usado": "gpt-4.1"
        })
        
        return pergunta_salva
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        raise HTTPException(status_code=500, detail=str(e))
