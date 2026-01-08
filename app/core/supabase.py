"""
═══════════════════════════════════════════════════════════════════════════════
VINCIPITCH.AI - CLIENTE SUPABASE
═══════════════════════════════════════════════════════════════════════════════
"""

import logging
from supabase import create_client, Client
from functools import lru_cache
from .config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """Retorna cliente Supabase com anon key (para operações do usuário)"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@lru_cache()
def get_supabase_admin() -> Client:
    """Retorna cliente Supabase com service key (para operações admin)"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


class SupabaseService:
    """Serviço centralizado para operações com Supabase"""

    def __init__(self, use_admin: bool = False):
        self.client = get_supabase_admin() if use_admin else get_supabase_client()
        self.settings = get_settings()

    # ═══════════════════════════════════════════════════════════════════════════
    # EMPRESAS
    # ═══════════════════════════════════════════════════════════════════════════

    async def listar_empresas(
        self,
        filtros: dict = None,
        limite: int = 100,
        offset: int = 0,
        ordem: str = "created_at",
        direcao: str = "desc",
    ):
        query = self.client.table("empresas").select("*", count="exact")

        if filtros:
            if filtros.get("setor"):
                query = query.eq("setor", filtros["setor"])
            if filtros.get("estagio"):
                query = query.eq("estagio", filtros["estagio"])
            if filtros.get("faturamento_minimo"):
                query = query.gte("faturamento_anual", filtros["faturamento_minimo"])
            if filtros.get("busca"):
                query = query.ilike("nome", f"%{filtros['busca']}%")

        query = query.range(offset, offset + limite - 1)
        query = query.order(ordem, desc=(direcao == "desc"))

        result = query.execute()
        return result.data if result.data else [], result.count or 0

    async def obter_empresa(self, empresa_id: str):
        result = (
            self.client.table("empresas").select("*").eq("id", empresa_id).single().execute()
        )
        return result.data if result.data else None

    async def criar_empresa(self, dados: dict):
        result = self.client.table("empresas").insert(dados).execute()
        return result.data[0] if result.data else None

    async def atualizar_empresa(self, empresa_id: str, dados: dict):
        result = self.client.table("empresas").update(dados).eq("id", empresa_id).execute()
        return result.data[0] if result.data else None

    async def deletar_empresa(self, empresa_id: str):
        """
        Hard delete da empresa.
        Se você preferir soft delete, troque por update({"deleted_at": ...})
        """
        # 1) pega documentos da empresa (para limpar storage se quiser)
        docs = await self.listar_documentos_empresa(empresa_id)

        # 2) remove registros de documentos (se existir tabela)
        if docs:
            doc_ids = [d["id"] for d in docs if d.get("id")]
            if doc_ids:
                self.client.table("documentos").delete().in_("id", doc_ids).execute()

        # 3) remove a empresa
        self.client.table("empresas").delete().eq("id", empresa_id).execute()

        # 4) tenta limpar storage (best-effort)
        #    (se seu bucket permitir remove e o path estiver correto)
        try:
            paths = [d["storage_path"] for d in docs if d.get("storage_path")]
            if paths:
                self.client.storage.from_("documentos-pitch").remove(paths)
        except Exception:
            # não impede delete caso storage não permita
            pass

        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # DOCUMENTOS
    # ═══════════════════════════════════════════════════════════════════════════

    async def criar_documento(self, dados: dict):
        result = self.client.table("documentos").insert(dados).execute()
        return result.data[0] if result.data else None

    async def atualizar_documento(self, doc_id: str, dados: dict):
        result = self.client.table("documentos").update(dados).eq("id", doc_id).execute()
        return result.data[0] if result.data else None

    async def obter_documento(self, doc_id: str):
        result = self.client.table("documentos").select("*").eq("id", doc_id).single().execute()
        return result.data if result.data else None

    async def listar_documentos_empresa(self, empresa_id: str):
        result = (
            self.client.table("documentos")
            .select("*")
            .eq("empresa_id", empresa_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data if result.data else []

    async def deletar_documento(self, documento_id: str):
        # pega antes para deletar do storage
        doc = await self.obter_documento(documento_id)
        if not doc:
            return False

        # remove registro
        self.client.table("documentos").delete().eq("id", documento_id).execute()

        # remove arquivo do storage (best-effort)
        try:
            if doc.get("storage_path"):
                self.client.storage.from_("documentos-pitch").remove([doc["storage_path"]])
        except Exception:
            pass

        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # ANÁLISES
    # ═══════════════════════════════════════════════════════════════════════════

    async def criar_analise(self, dados: dict):
        result = self.client.table("analises").insert(dados).execute()
        return result.data[0] if result.data else None

    async def atualizar_analise(self, analise_id: str, dados: dict):
        result = self.client.table("analises").update(dados).eq("id", analise_id).execute()
        return result.data[0] if result.data else None

    async def obter_analise(self, analise_id: str):
        result = self.client.table("analises").select("*").eq("id", analise_id).single().execute()
        return result.data if result.data else None

    async def obter_analise_empresa(self, empresa_id: str):
        result = (
            self.client.table("analises")
            .select("*")
            .eq("empresa_id", empresa_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def listar_analises(self, filtros: dict = None, limite: int = 20, offset: int = 0):
        query = self.client.table("analises").select("*")
        
        if filtros:
            if filtros.get("status"):
                query = query.eq("status", filtros["status"])
            if filtros.get("setor"):
                # Precisa fazer join com empresas para filtrar por setor
                pass
        
        query = query.order("created_at", desc=True).range(offset, offset + limite - 1)
        result = query.execute()
        return result.data if result.data else []

    async def obter_config_ia(self, setor: str):
        """Obtém configuração de IA para o setor"""
        try:
            result = (
                self.client.table("ia_config")
                .select("*")
                .eq("setor", setor)
                .eq("ativo", True)
                .single()
                .execute()
            )
            return result.data if result.data else None
        except:
            # Se não existir tabela ou config, retorna None
            return None

    async def salvar_pergunta(self, dados: dict):
        """Salva pergunta feita à IA"""
        try:
            result = self.client.table("perguntas_ia").insert(dados).execute()
            return result.data[0] if result.data else dados
        except:
            return dados

    # ═══════════════════════════════════════════════════════════════════════════
    # RANKINGS E COMPARAÇÕES
    # ═══════════════════════════════════════════════════════════════════════════

    async def obter_ranking_geral(self, limite: int = 50, offset: int = 0):
        """Obtém ranking geral de empresas ordenado por nota final (sem duplicatas)"""
        try:
            # Busca análises com join de empresas
            result = (
                self.client.table("analises")
                .select("*, empresas(*)")
                .eq("status", "concluida")
                .order("nota_final", desc=True)
                .execute()
            )
            
            # Remove duplicatas - mantém apenas a análise mais recente por empresa
            empresas_vistas = set()
            items = []
            notas = []
            
            for analise in (result.data or []):
                empresa_id = analise.get("empresa_id")
                
                # Pula se já vimos essa empresa
                if empresa_id in empresas_vistas:
                    continue
                    
                empresas_vistas.add(empresa_id)
                empresa = analise.get("empresas", {})
                nota = analise.get("nota_final", 0) or 0
                notas.append(nota)
                
                items.append({
                    "posicao": len(items) + 1,
                    "id": empresa_id,
                    "nome": empresa.get("nome", "N/A"),
                    "setor": empresa.get("setor", "outro"),
                    "estagio": empresa.get("estagio", "ideacao"),
                    "nota_final": nota,
                    "nota_final_percentual": nota * 25,
                    "classificacao_potencial": analise.get("classificacao_potencial", "medio"),
                    "faturamento_anual": empresa.get("faturamento_anual")
                })
                
                # Para quando atingir o limite
                if len(items) >= limite:
                    break
            
            # Calcula estatísticas
            media = sum(notas) / len(notas) if notas else 0
            notas_sorted = sorted(notas)
            mediana = notas_sorted[len(notas_sorted)//2] if notas_sorted else 0
            
            return {
                "items": items,
                "total": len(items),
                "media": round(media, 2),
                "mediana": round(mediana, 2),
                "desvio_padrao": 0
            }
        except Exception as e:
            print(f"Erro obter_ranking_geral: {e}")
            return {"items": [], "total": 0, "media": 0, "mediana": 0, "desvio_padrao": 0}

    async def obter_ranking_setor(self, setor: str, limite: int = 50, offset: int = 0):
        """Obtém ranking de empresas de um setor específico (sem duplicatas)"""
        try:
            # Primeiro busca empresas do setor
            empresas_result = (
                self.client.table("empresas")
                .select("id")
                .eq("setor", setor)
                .execute()
            )
            
            empresa_ids = [e["id"] for e in (empresas_result.data or [])]
            
            if not empresa_ids:
                return {"items": [], "total": 0, "estatisticas": {}}
            
            # Busca análises dessas empresas
            result = (
                self.client.table("analises")
                .select("*, empresas(*)")
                .in_("empresa_id", empresa_ids)
                .eq("status", "concluida")
                .order("nota_final", desc=True)
                .execute()
            )
            
            # Remove duplicatas - mantém apenas a análise mais recente por empresa
            empresas_vistas = set()
            items = []
            
            for analise in (result.data or []):
                empresa_id = analise.get("empresa_id")
                
                # Pula se já vimos essa empresa
                if empresa_id in empresas_vistas:
                    continue
                    
                empresas_vistas.add(empresa_id)
                empresa = analise.get("empresas", {})
                nota = analise.get("nota_final", 0) or 0
                
                items.append({
                    "posicao": len(items) + 1,
                    "id": empresa_id,
                    "nome": empresa.get("nome", "N/A"),
                    "setor": empresa.get("setor", setor),
                    "estagio": empresa.get("estagio", "ideacao"),
                    "nota_final": nota,
                    "nota_final_percentual": nota * 25,
                    "classificacao_potencial": analise.get("classificacao_potencial", "medio")
                })
                
                if len(items) >= limite:
                    break
            
            return {"items": items, "total": len(items), "estatisticas": {}}
        except Exception as e:
            print(f"Erro obter_ranking_setor: {e}")
            return {"items": [], "total": 0, "estatisticas": {}}

    async def obter_estatisticas_setores(self):
        """Obtém estatísticas agregadas por setor (sem duplicatas de empresa)"""
        try:
            result = (
                self.client.table("analises")
                .select("empresa_id, nota_final, empresas(setor)")
                .eq("status", "concluida")
                .order("created_at", desc=True)
                .execute()
            )
            
            # Remove duplicatas - mantém apenas a análise mais recente por empresa
            empresas_vistas = set()
            analises_unicas = []
            
            for analise in (result.data or []):
                empresa_id = analise.get("empresa_id")
                if empresa_id in empresas_vistas:
                    continue
                empresas_vistas.add(empresa_id)
                analises_unicas.append(analise)
            
            # Agrupa por setor
            por_setor = {}
            for analise in analises_unicas:
                setor = analise.get("empresas", {}).get("setor", "outro")
                nota = analise.get("nota_final", 0) or 0
                
                if setor not in por_setor:
                    por_setor[setor] = []
                por_setor[setor].append(nota)
            
            estatisticas = []
            for setor, notas in por_setor.items():
                if notas:
                    estatisticas.append({
                        "setor": setor,
                        "total_empresas": len(notas),
                        "media_nota": round(sum(notas) / len(notas), 2),
                        "menor_nota": min(notas),
                        "maior_nota": max(notas),
                        "desvio_padrao": 0
                    })
            
            return estatisticas
        except Exception as e:
            print(f"Erro obter_estatisticas_setores: {e}")
            return []

    async def obter_estatisticas_setor(self, setor: str):
        """Obtém estatísticas de um setor específico"""
        estatisticas = await self.obter_estatisticas_setores()
        for est in estatisticas:
            if est.get("setor") == setor:
                return est
        return None

    async def filtrar_ranking(self, filtros: dict):
        """Filtra ranking com critérios avançados"""
        try:
            query = (
                self.client.table("analises")
                .select("*, empresas(*)")
                .eq("status", "concluida")
            )
            
            # Aplica filtros de nota
            if filtros.get("nota_minima"):
                query = query.gte("nota_final", filtros["nota_minima"])
            if filtros.get("nota_maxima"):
                query = query.lte("nota_final", filtros["nota_maxima"])
            
            # Ordenação
            ordem = filtros.get("ordenar_por", "nota_final")
            direcao = filtros.get("ordem", "desc") == "desc"
            query = query.order(ordem, desc=direcao)
            
            # Paginação
            limite = filtros.get("limite", 50)
            offset = filtros.get("offset", 0)
            query = query.range(offset, offset + limite - 1)
            
            result = query.execute()
            
            items = []
            for i, analise in enumerate(result.data or []):
                empresa = analise.get("empresas", {})
                
                # Filtra por setores se especificado
                if filtros.get("setores") and empresa.get("setor") not in filtros["setores"]:
                    continue
                # Filtra por estágios se especificado
                if filtros.get("estagios") and empresa.get("estagio") not in filtros["estagios"]:
                    continue
                
                nota = analise.get("nota_final", 0) or 0
                items.append({
                    "posicao": i + 1,
                    "id": analise.get("empresa_id"),
                    "nome": empresa.get("nome", "N/A"),
                    "setor": empresa.get("setor", "outro"),
                    "nota_final": nota,
                    "nota_final_percentual": nota * 25
                })
            
            return {"items": items, "total": len(items), "estatisticas": {}}
        except Exception as e:
            print(f"Erro filtrar_ranking: {e}")
            return {"items": [], "total": 0, "estatisticas": {}}

    async def criar_comparacao(self, dados: dict):
        """Cria registro de comparação entre empresas"""
        try:
            result = self.client.table("comparacoes").insert(dados).execute()
            return result.data[0] if result.data else dados
        except Exception as e:
            # Se tabela não existe, retorna os dados mesmo assim
            print(f"Erro criar_comparacao (tabela pode não existir): {e}")
            from datetime import datetime
            dados["id"] = dados.get("id", "temp-" + str(datetime.now().timestamp()))
            dados["created_at"] = datetime.now().isoformat()
            return dados

    # ═══════════════════════════════════════════════════════════════════════════
    # STORAGE
    # ═══════════════════════════════════════════════════════════════════════════

    async def upload_arquivo(self, bucket: str, path: str, arquivo: bytes, content_type: str = "application/octet-stream"):
        try:
            return self.client.storage.from_(bucket).upload(path, arquivo, {"content-type": content_type})
        except Exception as e:
            logger.warning(f"Erro ao fazer upload para {bucket}/{path}: {e}")
            return None

    async def download_arquivo(self, bucket: str, path: str):
        return self.client.storage.from_(bucket).download(path)

    async def obter_url_publico(self, bucket: str, path: str):
        return self.client.storage.from_(bucket).get_public_url(path)

    # ═══════════════════════════════════════════════════════════════════════════
    # EXPORTAÇÕES
    # ═══════════════════════════════════════════════════════════════════════════

    async def criar_exportacao(self, dados: dict):
        """Registra uma exportação no banco."""
        try:
            result = self.client.table("exportacoes").insert(dados).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.warning(f"Erro ao registrar exportação: {e}")
            return None


def get_supabase_service() -> SupabaseService:
    """Dependência FastAPI para injetar o serviço Supabase"""
    return SupabaseService(use_admin=True)