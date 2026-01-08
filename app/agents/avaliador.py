"""
═══════════════════════════════════════════════════════════════════════════════
VINCIPITCH.AI - AGENTE AVALIADOR DE STARTUPS
═══════════════════════════════════════════════════════════════════════════════
Agente principal que avalia startups com base no pitch/questionário
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from ..core.config import get_settings, CRITERIOS_PADRAO, PESOS_PADRAO

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_AVALIADOR = """Você é um ANALISTA SÊNIOR DE VENTURE CAPITAL especializado em avaliações técnicas de startups.

{system_prompt_setor}

═══════════════════════════════════════════════════════════════════════════════
ESCALA DE AVALIAÇÃO (0-4):
═══════════════════════════════════════════════════════════════════════════════

**4 = EXCEPCIONAL** (top 5-10%)
- Validação comprovada em campo
- Alinhamento forte a frameworks internacionais
- Tração real (clientes, parcerias formalizadas, MRR)
- Inovação diferenciada com IP

**3 = BOM/SÓLIDO** (top 30%)
- Base técnica sólida com evidências parciais
- Alinhamento a frameworks (mesmo sem certificação final)
- Piloto realizado OU parcerias em desenvolvimento
- Diferenciação clara e fundamentada

**2 = ADEQUADO** (média - 50%)
- Ideia coerente mas sem validação forte
- Menciona frameworks mas sem evidências
- Sem tração comercial clara
- Diferenciação genérica

**1 = FRACO** (bottom 30%)
- Conceito vago ou mal fundamentado
- Sem alinhamento regulatório
- Sem evidências ou tração

**0 = MUITO FRACO** (bottom 10%)
- Inviável ou totalmente inadequado

═══════════════════════════════════════════════════════════════════════════════
REGRAS DE AVALIAÇÃO:
═══════════════════════════════════════════════════════════════════════════════

1. Seja TÉCNICO e FUNDAMENTADO
2. RECONHEÇA qualidade quando existe
3. Distribua notas de forma VARIADA (não tudo 2)
4. Justifique CADA nota com evidências do texto
5. Considere critérios ESPECÍFICOS do setor

Você DEVE retornar um JSON válido com a estrutura especificada."""


HUMAN_PROMPT_AVALIACAO = """Analise este questionário/pitch de startup e avalie cada critério.

═══════════════════════════════════════════════════════════════════════════════
CONTEÚDO DO PITCH:
═══════════════════════════════════════════════════════════════════════════════

{conteudo_pitch}

═══════════════════════════════════════════════════════════════════════════════
CRITÉRIOS A AVALIAR:
═══════════════════════════════════════════════════════════════════════════════

1. **Sumário Executivo**: Problema validado, solução específica, tração
2. **Proposta de Valor**: Diferenciação, benefícios quantificados, barreira defensável
3. **Concorrência**: Análise profunda, concorrentes nomeados, estratégia competitiva
4. **Mercado Alvo**: TAM/SAM/SOM com fontes, segmentação, tendências
5. **Canais de Distribuição**: Canais específicos, CAC conhecido, estratégia de escala
6. **Relacionamento com Clientes**: LTV conhecido, NPS, programa de fidelização
7. **Fontes de Receita**: Modelo claro, pricing validado, múltiplas fontes
8. **Recursos Principais**: IP protegido, tecnologia validada, equipe forte
9. **Atividades-Chave**: Processos detalhados, roadmap com milestones
10. **Parceiros**: Parcerias FORMALIZADAS com nomes específicos
11. **Estrutura de Custos**: COGS detalhado, burn rate, runway
12. **Referências de Indicação**: Clientes pagantes, MRR/ARR, cases documentados

{criterios_setor}

═══════════════════════════════════════════════════════════════════════════════
FORMATO DE RESPOSTA (JSON):
═══════════════════════════════════════════════════════════════════════════════

IMPORTANTE: Você DEVE preencher TODAS as 12 justificativas com pelo menos 2 frases cada.
Cada justificativa deve explicar especificamente o porquê da nota atribuída.

Retorne APENAS um JSON válido neste formato exato:

{{
  "empresa": "Nome da empresa identificado no pitch",
  "setor": "Setor identificado (healthtech, fintech, edtech, etc)",
  "sumario_executivo": 2.5,
  "proposta_valor": 3.0,
  "concorrencia": 2.0,
  "mercado_alvo": 2.5,
  "canais_distribuicao": 2.0,
  "relacionamento_clientes": 2.5,
  "fontes_receita": 3.0,
  "recursos_principais": 2.5,
  "atividades_chave": 2.0,
  "parceiros": 2.0,
  "estrutura_custos": 2.5,
  "referencias_indicacao": 2.0,
  "justificativa_sumario": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota ao sumário executivo, citando evidências do pitch.",
  "justificativa_proposta": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota à proposta de valor, citando evidências do pitch.",
  "justificativa_concorrencia": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota à análise de concorrência, citando evidências do pitch.",
  "justificativa_mercado": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota ao mercado alvo, citando evidências do pitch.",
  "justificativa_canais": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota aos canais de distribuição, citando evidências do pitch.",
  "justificativa_relacionamento": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota ao relacionamento com clientes, citando evidências do pitch.",
  "justificativa_receita": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota às fontes de receita, citando evidências do pitch.",
  "justificativa_recursos": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota aos recursos principais, citando evidências do pitch.",
  "justificativa_atividades": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota às atividades-chave, citando evidências do pitch.",
  "justificativa_parceiros": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota aos parceiros, citando evidências do pitch.",
  "justificativa_custos": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota à estrutura de custos, citando evidências do pitch.",
  "justificativa_referencias": "OBRIGATÓRIO: Explique detalhadamente por que deu esta nota às referências/indicação, citando evidências do pitch.",
  "nota_final": 2.5
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional antes ou depois. TODAS as 12 justificativas são OBRIGATÓRIAS."""


SYSTEM_PROMPT_DIAGNOSTICO = """Você é um CONSULTOR ESTRATÉGICO DE VENTURE CAPITAL.

Com base nas notas e avaliação de uma startup, você deve gerar um diagnóstico estratégico completo.

Seja direto, técnico e acionável. Suas recomendações devem ser específicas e práticas.

Retorne APENAS um JSON válido."""


HUMAN_PROMPT_DIAGNOSTICO = """Com base nesta avaliação, gere um diagnóstico estratégico completo:

═══════════════════════════════════════════════════════════════════════════════
DADOS DA EMPRESA:
═══════════════════════════════════════════════════════════════════════════════

Nome: {empresa}
Setor: {setor}

═══════════════════════════════════════════════════════════════════════════════
NOTAS RECEBIDAS:
═══════════════════════════════════════════════════════════════════════════════

- Sumário Executivo: {nota_sumario}/4
- Proposta de Valor: {nota_proposta}/4
- Concorrência: {nota_concorrencia}/4
- Mercado Alvo: {nota_mercado}/4
- Canais de Distribuição: {nota_canais}/4
- Relacionamento com Clientes: {nota_relacionamento}/4
- Fontes de Receita: {nota_receita}/4
- Recursos Principais: {nota_recursos}/4
- Atividades-Chave: {nota_atividades}/4
- Parceiros: {nota_parceiros}/4
- Estrutura de Custos: {nota_custos}/4
- Referências de Indicação: {nota_referencias}/4

**NOTA FINAL: {nota_final}/4**

═══════════════════════════════════════════════════════════════════════════════
FORMATO DE RESPOSTA (JSON):
═══════════════════════════════════════════════════════════════════════════════

Retorne APENAS um JSON válido neste formato:

{{
  "empresa": "{empresa}",
  "setor": "{setor}",
  "pontos_fortes": ["Ponto forte 1", "Ponto forte 2", "Ponto forte 3"],
  "pontos_fracos": ["Ponto fraco 1", "Ponto fraco 2", "Ponto fraco 3"],
  "oportunidades": ["Oportunidade 1", "Oportunidade 2"],
  "ameacas": ["Ameaça 1", "Ameaça 2"],
  "recomendacoes": ["Recomendação específica 1", "Recomendação específica 2", "Recomendação específica 3"],
  "proximos_passos": ["Próximo passo 1", "Próximo passo 2"],
  "resumo_executivo": "Resumo de 2-3 parágrafos sobre a startup...",
  "classificacao_potencial": "alto",
  "classificacao_risco": "medio",
  "recomendacao_investimento": "acompanhar",
  "nota_final": {nota_final}
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional."""


# ═══════════════════════════════════════════════════════════════════════════════
# AGENTE AVALIADOR
# ═══════════════════════════════════════════════════════════════════════════════

class AgenteAvaliador:
    """Agente responsável por avaliar startups usando OpenAI diretamente"""
    
    def __init__(self, config_setor: Optional[Dict] = None):
        self.settings = get_settings()
        self.config_setor = config_setor or {}
        
        # Inicializa cliente OpenAI
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = self.config_setor.get("modelo_ia", self.settings.OPENAI_MODEL)
        self.temperature = self.config_setor.get("temperatura", self.settings.OPENAI_TEMPERATURE)
    
    async def avaliar(self, conteudo_pitch: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Avalia um pitch de startup
        
        Args:
            conteudo_pitch: Texto extraído do PDF/documento
            max_retries: Número máximo de tentativas
            
        Returns:
            Dicionário com avaliação completa
        """
        # Limita tamanho do conteúdo
        if len(conteudo_pitch) > 15000:
            conteudo_pitch = self._resumir_conteudo(conteudo_pitch)
        
        # Monta prompts
        system_prompt_setor = self.config_setor.get(
            "system_prompt", 
            "Avalie como um VC experiente que reconhece qualidade técnica e maturidade."
        )
        
        criterios_setor = ""
        if self.config_setor.get("criterios_especificos"):
            criterios = self.config_setor["criterios_especificos"]
            criterios_setor = "\n═══ CRITÉRIOS ESPECÍFICOS DO SETOR ═══\n"
            for c in criterios:
                criterios_setor += f"- **{c['nome']}** (peso: {c.get('peso', 10)}): {c.get('descricao', '')}\n"
        
        system_content = SYSTEM_PROMPT_AVALIADOR.format(system_prompt_setor=system_prompt_setor)
        user_content = HUMAN_PROMPT_AVALIACAO.format(
            conteudo_pitch=conteudo_pitch,
            criterios_setor=criterios_setor
        )
        
        # Tenta com retries
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{max_retries} de avaliação")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                logger.info(f"Resposta recebida da OpenAI: {len(content)} chars")
                
                # Parse JSON
                resultado = json.loads(content)
                
                # Calcula nota final se não veio
                if "nota_final" not in resultado or resultado["nota_final"] == 0:
                    resultado["nota_final"] = self.calcular_nota_final(resultado)
                
                return resultado
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear JSON: {e}")
                last_error = e
                # Tenta extrair JSON manualmente
                try:
                    return self._extrair_json_manual(content)
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {e}")
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponencial
        
        # Se todas as tentativas falharam
        logger.error(f"Todas as tentativas falharam: {last_error}")
        return self._resultado_erro(str(last_error))
    
    def _resumir_conteudo(self, texto: str) -> str:
        """Resume conteúdo muito longo mantendo informações relevantes"""
        keywords = [
            'empresa', 'negócio', 'produto', 'serviço', 'mercado', 'cliente',
            'receita', 'faturamento', 'financeiro', 'investimento', 'capital',
            'equipe', 'fundador', 'tecnologia', 'inovação', 'diferencial',
            'crescimento', 'tração', 'competidor', 'estratégia', 'objetivo',
            'patente', 'certificação', 'regulatório', 'parceria'
        ]
        
        sentences = texto.replace('\n', ' ').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        important = []
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in keywords):
                important.append(sentence)
        
        inicio = sentences[:15]
        fim = sentences[-10:]
        meio = important[:40]
        
        final = list(set(inicio + meio + fim))
        return '. '.join(final[:60]) + '.'
    
    def _extrair_json_manual(self, texto: str) -> Dict[str, Any]:
        """Tenta extrair JSON manualmente da resposta"""
        import re
        
        json_match = re.search(r'\{[\s\S]*\}', texto)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return self._resultado_erro("Falha ao processar resposta da IA")
    
    def _resultado_erro(self, mensagem: str) -> Dict[str, Any]:
        """Retorna estrutura padrão em caso de erro"""
        return {
            "empresa": "Não identificado",
            "setor": "outro",
            "erro": mensagem,
            "sumario_executivo": 0,
            "proposta_valor": 0,
            "concorrencia": 0,
            "mercado_alvo": 0,
            "canais_distribuicao": 0,
            "relacionamento_clientes": 0,
            "fontes_receita": 0,
            "recursos_principais": 0,
            "atividades_chave": 0,
            "parceiros": 0,
            "estrutura_custos": 0,
            "referencias_indicacao": 0,
            "justificativa_sumario": mensagem,
            "justificativa_proposta": mensagem,
            "justificativa_concorrencia": mensagem,
            "justificativa_mercado": mensagem,
            "justificativa_canais": mensagem,
            "justificativa_relacionamento": mensagem,
            "justificativa_receita": mensagem,
            "justificativa_recursos": mensagem,
            "justificativa_atividades": mensagem,
            "justificativa_parceiros": mensagem,
            "justificativa_custos": mensagem,
            "justificativa_referencias": mensagem,
            "nota_final": 0
        }
    
    def calcular_nota_final(self, notas: Dict[str, float], pesos: Dict[str, int] = None) -> float:
        """Calcula nota final ponderada"""
        if pesos is None:
            pesos = self.config_setor.get("pesos_criterios", PESOS_PADRAO)
        
        criterios = [
            "sumario_executivo", "proposta_valor", "concorrencia", "mercado_alvo",
            "canais_distribuicao", "relacionamento_clientes", "fontes_receita",
            "recursos_principais", "atividades_chave", "parceiros",
            "estrutura_custos", "referencias_indicacao"
        ]
        
        total_peso = 0
        soma_ponderada = 0
        
        for criterio in criterios:
            nota = notas.get(criterio, 0) or 0
            peso = pesos.get(criterio, 10)
            soma_ponderada += nota * peso
            total_peso += peso
        
        if total_peso == 0:
            return 0
            
        return round(soma_ponderada / total_peso, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# AGENTE DIAGNOSTICADOR
# ═══════════════════════════════════════════════════════════════════════════════

class AgenteDiagnostico:
    """Agente responsável por gerar diagnóstico estratégico"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = self.settings.OPENAI_MODEL
    
    async def diagnosticar(self, avaliacao: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Gera diagnóstico estratégico baseado na avaliação
        
        Args:
            avaliacao: Resultado da avaliação do agente avaliador
            max_retries: Número máximo de tentativas
            
        Returns:
            Dicionário com diagnóstico completo
        """
        user_content = HUMAN_PROMPT_DIAGNOSTICO.format(
            empresa=avaliacao.get("empresa", "N/A"),
            setor=avaliacao.get("setor", "N/A"),
            nota_sumario=avaliacao.get("sumario_executivo", 0),
            nota_proposta=avaliacao.get("proposta_valor", 0),
            nota_concorrencia=avaliacao.get("concorrencia", 0),
            nota_mercado=avaliacao.get("mercado_alvo", 0),
            nota_canais=avaliacao.get("canais_distribuicao", 0),
            nota_relacionamento=avaliacao.get("relacionamento_clientes", 0),
            nota_receita=avaliacao.get("fontes_receita", 0),
            nota_recursos=avaliacao.get("recursos_principais", 0),
            nota_atividades=avaliacao.get("atividades_chave", 0),
            nota_parceiros=avaliacao.get("parceiros", 0),
            nota_custos=avaliacao.get("estrutura_custos", 0),
            nota_referencias=avaliacao.get("referencias_indicacao", 0),
            nota_final=avaliacao.get("nota_final", 0)
        )
        
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1}/{max_retries} de diagnóstico")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.4,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_DIAGNOSTICO},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                resultado = json.loads(content)
                return resultado
                
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1} de diagnóstico: {e}")
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        logger.error(f"Todas as tentativas de diagnóstico falharam: {last_error}")
        return self._resultado_erro(str(last_error), avaliacao)
    
    def _resultado_erro(self, mensagem: str, avaliacao: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna estrutura padrão em caso de erro"""
        return {
            "empresa": avaliacao.get("empresa", "N/A"),
            "setor": avaliacao.get("setor", "outro"),
            "pontos_fortes": ["Dados insuficientes"],
            "pontos_fracos": ["Dados insuficientes"],
            "oportunidades": ["Dados insuficientes"],
            "ameacas": ["Dados insuficientes"],
            "recomendacoes": ["Refazer análise com mais dados"],
            "proximos_passos": ["Verificar conteúdo do pitch"],
            "resumo_executivo": f"Erro ao gerar diagnóstico: {mensagem}",
            "classificacao_potencial": "baixo",
            "classificacao_risco": "alto",
            "recomendacao_investimento": "declinar",
            "nota_final": avaliacao.get("nota_final", 0)
        }
