"""
Rotas para gerenciamento de empresas/startups.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form

from app.core.supabase import SupabaseService, get_supabase_service
from app.models.schemas import (
    EmpresaCreate, EmpresaUpdate, EmpresaResponse,
    DocumentoResponse, SetorEnum, EstagioStartupEnum,
    SuccessResponse, PaginatedResponse
)
from app.services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("", response_model=PaginatedResponse)
async def listar_empresas(
    setor: Optional[SetorEnum] = None,
    estagio: Optional[EstagioStartupEnum] = None,
    busca: Optional[str] = None,
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ordem: str = Query("created_at", pattern="^(nome|created_at|faturamento_anual)$"),
    direcao: str = Query("desc", pattern="^(asc|desc)$"),
    supabase: SupabaseService = Depends(get_supabase_service),
):
    try:
        filtros = {}
        if setor:
            filtros["setor"] = setor.value
        if estagio:
            filtros["estagio"] = estagio.value
        if busca:
            filtros["busca"] = busca

        empresas, total = await supabase.listar_empresas(
            filtros=filtros, limite=limite, offset=offset, ordem=ordem, direcao=direcao
        )

        return PaginatedResponse(
            success=True,
            data=empresas,
            total=total,
            limit=limite,
            offset=offset,
        )
    except Exception as e:
        logger.error(f"Erro ao listar empresas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def obter_empresa(
    empresa_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    try:
        empresa = await supabase.obter_empresa(str(empresa_id))
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        return empresa
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=EmpresaResponse, status_code=201)
async def criar_empresa(
    empresa: EmpresaCreate,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    try:
        nova_empresa = await supabase.criar_empresa(empresa.model_dump(exclude_unset=True))
        return nova_empresa
    except Exception as e:
        logger.error(f"Erro ao criar empresa: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def atualizar_empresa(
    empresa_id: UUID,
    empresa: EmpresaUpdate,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    try:
        existente = await supabase.obter_empresa(str(empresa_id))
        if not existente:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        atualizada = await supabase.atualizar_empresa(
            str(empresa_id),
            empresa.model_dump(exclude_unset=True),
        )
        return atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{empresa_id}", response_model=SuccessResponse)
async def deletar_empresa(
    empresa_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    try:
        await supabase.deletar_empresa(str(empresa_id))
        return SuccessResponse(success=True, message=f"Empresa {empresa_id} removida com sucesso")
    except Exception as e:
        logger.error(f"Erro ao deletar empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{empresa_id}/analise")
async def obter_analise_empresa(
    empresa_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    """
    Obtém a análise mais recente de uma empresa.
    
    Retorna a análise completa com notas, justificativas e diagnóstico.
    """
    try:
        # Verifica se empresa existe
        empresa = await supabase.obter_empresa(str(empresa_id))
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")
        
        # Busca análise da empresa
        analise = await supabase.obter_analise_empresa(str(empresa_id))
        
        if not analise:
            raise HTTPException(
                status_code=404, 
                detail="Nenhuma análise encontrada para esta empresa"
            )
        
        return analise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter análise da empresa {empresa_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{empresa_id}/documentos", response_model=DocumentoResponse, status_code=201)
async def upload_documento(
    empresa_id: UUID,
    arquivo: UploadFile = File(..., description="PDF do pitch deck"),
    processar: bool = Form(True, description="Processar PDF automaticamente"),
    supabase: SupabaseService = Depends(get_supabase_service),
):
    if not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")

    conteudo = await arquivo.read()

    if len(conteudo) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx: 50MB)")

    try:
        empresa = await supabase.obter_empresa(str(empresa_id))
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        # Sanitizar nome do arquivo (remover acentos, espaços e caracteres especiais)
        import unicodedata
        import re
        
        nome_original = arquivo.filename
        # Remove acentos
        nome_limpo = unicodedata.normalize('NFKD', nome_original).encode('ASCII', 'ignore').decode('ASCII')
        # Substitui espaços e caracteres especiais por underscore
        nome_limpo = re.sub(r'[^\w\-_\.]', '_', nome_limpo)
        # Remove underscores duplicados
        nome_limpo = re.sub(r'_+', '_', nome_limpo)
        # Garante extensão .pdf
        if not nome_limpo.lower().endswith('.pdf'):
            nome_limpo = nome_limpo + '.pdf'
        
        storage_path = f"pitchs/{empresa_id}/{nome_limpo}"

        # Upload do arquivo
        await supabase.upload_arquivo(
            "documentos-pitch",
            storage_path,
            conteudo,
            "application/pdf",
        )

        doc_data = {
            "empresa_id": str(empresa_id),
            "nome_arquivo": nome_original,  # Mantém nome original para exibição
            "tipo_arquivo": "pdf",
            "tamanho_bytes": len(conteudo),
            "storage_path": storage_path,
            "processado": False,
        }

        documento = await supabase.criar_documento(doc_data)

        if processar:
            try:
                processor = PDFProcessor()
                texto_extraido, texto_limpo, metadados = await processor.processar_pdf(conteudo)

                await supabase.atualizar_documento(str(documento["id"]), {
                    "texto_extraido": texto_extraido,
                    "texto_limpo": texto_limpo,
                    "numero_paginas": metadados.get("numero_paginas"),
                    "metodo_extracao": metadados.get("metodo_extracao"),
                    "qualidade_extracao": metadados.get("qualidade_extracao"),
                    "processado": True,
                })

                documento = await supabase.obter_documento(str(documento["id"]))

            except Exception as e:
                logger.error(f"Erro ao processar PDF: {e}")
                await supabase.atualizar_documento(str(documento["id"]), {
                    "erro_processamento": str(e),
                    "processado": False,
                })

        return documento

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{empresa_id}/documentos", response_model=List[DocumentoResponse])
async def listar_documentos(
    empresa_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    try:
        return await supabase.listar_documentos_empresa(str(empresa_id))
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{empresa_id}/documentos/{documento_id}", response_model=SuccessResponse)
async def deletar_documento(
    empresa_id: UUID,
    documento_id: UUID,
    supabase: SupabaseService = Depends(get_supabase_service),
):
    """
    Remove documento:
    - apaga registro da tabela documentos
    - tenta apagar o arquivo do bucket documentos-pitch
    """
    try:
        ok = await supabase.deletar_documento(str(documento_id))
        if not ok:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        return SuccessResponse(success=True, message="Documento removido com sucesso")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar documento {documento_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/setores/lista", response_model=List[str])
async def listar_setores():
    return [s.value for s in SetorEnum]


@router.get("/estagios/lista", response_model=List[str])
async def listar_estagios():
    return [e.value for e in EstagioStartupEnum]
