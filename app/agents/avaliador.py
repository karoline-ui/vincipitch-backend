"""
═══════════════════════════════════════════════════════════════════════════════
VINCIPITCH.AI - AGENTE AVALIADOR DE STARTUPS
═══════════════════════════════════════════════════════════════════════════════
Agente principal que avalia startups com base no pitch/questionário
Utiliza prompts específicos por setor com métricas e KPIs do mercado
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from openai import AsyncOpenAI

from ..core.config import get_settings, CRITERIOS_PADRAO, PESOS_PADRAO
from .config_setores import get_config_setor, METRICAS_POR_SETOR

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPTS ESPECÍFICOS POR SETOR
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_system_prompt(setor: str) -> str:
    """Gera system prompt específico para o setor"""
    config = get_config_setor(setor)
    
    kpis_texto = "\n".join([f"  • {kpi}" for kpi in config['kpis_principais']])
    
    benchmarks_texto = ""
    for key, value in config['benchmarks'].items():
        nome = key.replace("_", " ").title()
        if isinstance(value, float):
            if value < 1:
                benchmarks_texto += f"  • {nome}: {value*100:.0f}%\n"
            else:
                benchmarks_texto += f"  • {nome}: {value}x\n"
        else:
            benchmarks_texto += f"  • {nome}: {value}\n"
    
    perguntas_texto = "\n".join([f"  • {p}" for p in config['perguntas_avaliacao']])
    
    return f"""Você é um ANALISTA SÊNIOR DE VENTURE CAPITAL especializado em {config['nome_display']}.

═══════════════════════════════════════════════════════════════════════════════
🎯 EXPERTISE: {config['nome_display'].upper()}
═══════════════════════════════════════════════════════════════════════════════

Setor: {config['descricao']}

📊 KPIs CRÍTICOS QUE VOCÊ DEVE AVALIAR:
{kpis_texto}

📈 BENCHMARKS DO MERCADO:
{benchmarks_texto}

❓ PERGUNTAS-CHAVE PARA AVALIAR {config['nome_display'].upper()}:
{perguntas_texto}

═══════════════════════════════════════════════════════════════════════════════
⚖️ ESCALA DE AVALIAÇÃO (0-4):
═══════════════════════════════════════════════════════════════════════════════

**4.0 = EXCEPCIONAL** (top 5% do setor)
- KPIs acima dos benchmarks de mercado
- Tração comprovada (clientes pagantes, MRR, parcerias formalizadas)
- Diferenciação tecnológica ou de modelo de negócio clara
- Equipe com track record no setor
- Validação regulatória/certificações quando aplicável

**3.0-3.9 = BOM/SÓLIDO** (top 25%)
- KPIs alinhados ou próximos aos benchmarks
- Piloto realizado com resultados mensuráveis
- Proposta de valor diferenciada e fundamentada
- Equipe com experiência relevante
- Processo regulatório em andamento quando aplicável

**2.0-2.9 = ADEQUADO** (mediana)
- Ideia coerente mas KPIs não demonstrados ou abaixo do benchmark
- Sem validação forte de mercado
- Diferenciação genérica ou pouco clara
- Equipe com gaps importantes
- Sem clareza sobre aspectos regulatórios

**1.0-1.9 = FRACO** (bottom 25%)
- Conceito vago ou mal fundamentado
- Sem métricas ou evidências
- Mercado mal definido
- Modelo de negócio questionável

**0-0.9 = MUITO FRACO** (bottom 5%)
- Proposta inviável ou inadequada para o setor
- Desconhecimento do mercado
- Riscos críticos não endereçados

═══════════════════════════════════════════════════════════════════════════════
⚠️ REGRAS CRÍTICAS DE AVALIAÇÃO:
═══════════════════════════════════════════════════════════════════════════════

1. USE DECIMAIS (ex: 2.3, 3.7, 1.5) - NÃO apenas números inteiros
2. DISTRIBUA as notas - é IMPOSSÍVEL uma startup ter todas as notas iguais
3. COMPARE com os benchmarks do setor ao avaliar
4. PENALIZE severamente quando KPIs críticos do setor não são mencionados
5. RECOMPENSE quando há métricas concretas e validação de mercado
6. Cada critério deve ter uma justificativa ESPECÍFICA de 2-3 frases

Você DEVE retornar um JSON válido com a estrutura especificada."""


def gerar_criterios_setor(setor: str) -> str:
    """Gera texto com critérios específicos do setor"""
    config = get_config_setor(setor)
    
    texto = f"\n═══════════════════════════════════════════════════════════════════════════════\n"
    texto += f"🎯 CRITÉRIOS ESPECÍFICOS PARA {config['nome_display'].upper()}:\n"
    texto += f"═══════════════════════════════════════════════════════════════════════════════\n\n"
    
    criterios_map = {
        "sumario_executivo": "Sumário Executivo",
        "proposta_valor": "Proposta de Valor",
        "concorrencia": "Concorrência",
        "mercado_alvo": "Mercado Alvo",
        "canais_distribuicao": "Canais de Distribuição",
        "relacionamento_clientes": "Relacionamento com Clientes",
        "fontes_receita": "Fontes de Receita",
        "recursos_principais": "Recursos Principais",
        "atividades_chave": "Atividades-Chave",
        "parceiros": "Parceiros",
        "estrutura_custos": "Estrutura de Custos",
        "referencias_indicacao": "Referências de Indicação"
    }
    
    for key, nome in criterios_map.items():
        descricao = config['criterios_especificos'].get(key, "Avaliar conforme padrão")
        texto += f"• **{nome}**: {descricao}\n"
    
    return texto


HUMAN_PROMPT_AVALIACAO = """Analise este questionário/pitch de startup e avalie cada critério com base nas métricas e KPIs específicos do setor.

═══════════════════════════════════════════════════════════════════════════════
📄 CONTEÚDO DO PITCH:
═══════════════════════════════════════════════════════════════════════════════

{conteudo_pitch}

═══════════════════════════════════════════════════════════════════════════════
📋 CRITÉRIOS GERAIS A AVALIAR:
═══════════════════════════════════════════════════════════════════════════════

1. **Sumário Executivo**: Problema validado, solução específica, tração demonstrada
2. **Proposta de Valor**: Diferenciação clara, benefícios quantificados, barreira defensável
3. **Concorrência**: Análise profunda com nomes, estratégia competitiva clara
4. **Mercado Alvo**: TAM/SAM/SOM com fontes, segmentação clara, tendências
5. **Canais de Distribuição**: Canais específicos, CAC conhecido, estratégia de escala
6. **Relacionamento com Clientes**: LTV conhecido, NPS, estratégia de retenção
7. **Fontes de Receita**: Modelo claro, pricing validado, unit economics
8. **Recursos Principais**: IP, tecnologia, equipe, certificações
9. **Atividades-Chave**: Processos detalhados, roadmap com milestones
10. **Parceiros**: Parcerias FORMALIZADAS (nomes específicos, contratos)
11. **Estrutura de Custos**: COGS detalhado, burn rate, runway
12. **Referências de Indicação**: Clientes pagantes, MRR/ARR, cases documentados

{criterios_setor}

═══════════════════════════════════════════════════════════════════════════════
📝 FORMATO DE RESPOSTA (JSON):
═══════════════════════════════════════════════════════════════════════════════

REGRAS IMPORTANTES:
1. Use DECIMAIS nas notas (ex: 2.3, 3.7, 1.5) - NÃO apenas números inteiros
2. As notas DEVEM variar entre os critérios - é impossível todos serem iguais
3. Compare SEMPRE com os KPIs e benchmarks do setor mencionados no system prompt
4. Cada justificativa deve ter 2-3 frases explicando a nota com base no pitch

Retorne APENAS um JSON válido neste formato:

{{
  "empresa": "Nome da empresa identificado no pitch",
  "setor": "{setor}",
  "sumario_executivo": 2.7,
  "proposta_valor": 3.2,
  "concorrencia": 1.8,
  "mercado_alvo": 2.4,
  "canais_distribuicao": 2.1,
  "relacionamento_clientes": 2.9,
  "fontes_receita": 3.5,
  "recursos_principais": 2.6,
  "atividades_chave": 2.2,
  "parceiros": 1.5,
  "estrutura_custos": 2.3,
  "referencias_indicacao": 1.9,
  "justificativa_sumario": "Justificativa detalhada de 2-3 frases explicando a nota, citando evidências específicas do pitch e comparando com KPIs do setor.",
  "justificativa_proposta": "Justificativa detalhada...",
  "justificativa_concorrencia": "Justificativa detalhada...",
  "justificativa_mercado": "Justificativa detalhada...",
  "justificativa_canais": "Justificativa detalhada...",
  "justificativa_relacionamento": "Justificativa detalhada...",
  "justificativa_receita": "Justificativa detalhada...",
  "justificativa_recursos": "Justificativa detalhada...",
  "justificativa_atividades": "Justificativa detalhada...",
  "justificativa_parceiros": "Justificativa detalhada...",
  "justificativa_custos": "Justificativa detalhada...",
  "justificativa_referencias": "Justificativa detalhada...",
  "nota_final": 2.43
}}

IMPORTANTE: 
- A nota_final deve ser a MÉDIA EXATA das 12 notas (calcule corretamente)
- Use notas com UMA casa decimal (ex: 2.3, não 2.33333)
- TODAS as 12 justificativas são OBRIGATÓRIAS
- Retorne APENAS o JSON, sem texto antes ou depois"""


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPTS DE DIAGNÓSTICO (específico por setor)
# ═══════════════════════════════════════════════════════════════════════════════

def gerar_system_prompt_diagnostico(setor: str) -> str:
    """Gera system prompt de diagnóstico específico para o setor"""
    config = get_config_setor(setor)
    
    return f"""Você é um CONSULTOR ESTRATÉGICO DE VENTURE CAPITAL especializado em {config['nome_display']}.

Com base nas notas e avaliação de uma startup do setor de {config['nome_display']}, você deve gerar um diagnóstico estratégico completo.

CONTEXTO DO SETOR: {config['descricao']}

KPIs IMPORTANTES PARA O DIAGNÓSTICO:
{chr(10).join([f"• {kpi}" for kpi in config['kpis_principais'][:5]])}

Seja direto, técnico e acionável. Suas recomendações devem ser específicas para o setor de {config['nome_display']} e práticas.

Retorne APENAS um JSON válido."""


HUMAN_PROMPT_DIAGNOSTICO = """Com base nesta avaliação, gere um diagnóstico estratégico completo:

═══════════════════════════════════════════════════════════════════════════════
📊 DADOS DA EMPRESA:
═══════════════════════════════════════════════════════════════════════════════

Nome: {empresa}
Setor: {setor}

═══════════════════════════════════════════════════════════════════════════════
📈 NOTAS RECEBIDAS:
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
📝 FORMATO DE RESPOSTA (JSON):
═══════════════════════════════════════════════════════════════════════════════

Gere recomendações ESPECÍFICAS para o setor {setor}. Retorne APENAS um JSON válido:

{{
  "empresa": "{empresa}",
  "setor": "{setor}",
  "pontos_fortes": ["3 pontos fortes específicos baseados nas notas altas"],
  "pontos_fracos": ["3 pontos fracos específicos baseados nas notas baixas"],
  "oportunidades": ["2-3 oportunidades de mercado específicas do setor"],
  "ameacas": ["2-3 ameaças ou riscos específicos do setor"],
  "recomendacoes": ["5 recomendações estratégicas práticas e específicas para o setor"],
  "proximos_passos": ["3 ações imediatas priorizadas"],
  "resumo_executivo": "Parágrafo de 3-4 frases com visão geral da startup, potencial e principais desafios",
  "classificacao_potencial": "alto|medio|baixo",
  "classificacao_risco": "alto|medio|baixo", 
  "recomendacao_investimento": "investir|considerar|declinar",
  "nota_final": {nota_final}
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto antes ou depois."""


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE AGENTE AVALIADOR
# ═══════════════════════════════════════════════════════════════════════════════

class AgenteAvaliador:
    """
    Agente responsável por avaliar pitches de startups.
    Utiliza prompts específicos por setor com KPIs e métricas de mercado.
    """
    
    def __init__(self, config_setor: Dict[str, Any] = None):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = self.settings.OPENAI_MODEL
        self.config_setor = config_setor or {}
    
    async def avaliar(
        self, 
        conteudo_pitch: str,
        setor_hint: str = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Avalia um pitch de startup usando prompts específicos do setor.
        
        Args:
            conteudo_pitch: Texto do pitch/questionário da startup
            setor_hint: Dica do setor (se conhecido previamente)
            max_retries: Número máximo de tentativas
            
        Returns:
            Dicionário com notas e justificativas para cada critério
        """
        if not conteudo_pitch or len(conteudo_pitch.strip()) < 50:
            return self._resultado_erro("Conteúdo do pitch muito curto ou vazio")
        
        # Detecta ou usa setor fornecido
        setor = setor_hint or self._detectar_setor(conteudo_pitch)
        
        # Prepara conteúdo (resume se muito longo)
        if len(conteudo_pitch) > 15000:
            conteudo_pitch = self._resumir_conteudo(conteudo_pitch)
        
        # Gera prompts específicos do setor
        system_prompt = gerar_system_prompt(setor)
        criterios_setor = gerar_criterios_setor(setor)
        
        user_content = HUMAN_PROMPT_AVALIACAO.format(
            conteudo_pitch=conteudo_pitch,
            criterios_setor=criterios_setor,
            setor=setor
        )
        
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Avaliação - Tentativa {attempt + 1}/{max_retries} - Setor: {setor}")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.3,  # Baixa para consistência, mas permite variação
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                resultado = json.loads(content)
                
                # Valida e recalcula nota final
                resultado = self._validar_e_ajustar_resultado(resultado, setor)
                
                logger.info(f"Avaliação concluída: {resultado.get('empresa')} - Nota: {resultado.get('nota_final')}")
                return resultado
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro de JSON na tentativa {attempt + 1}: {e}")
                last_error = e
                # Tenta extrair JSON manualmente
                try:
                    resultado = self._extrair_json_manual(response.choices[0].message.content)
                    resultado = self._validar_e_ajustar_resultado(resultado, setor)
                    return resultado
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {e}")
                last_error = e
                
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        logger.error(f"Todas as tentativas falharam: {last_error}")
        return self._resultado_erro(str(last_error))
    
    def _detectar_setor(self, texto: str) -> str:
        """Detecta o setor da startup baseado no conteúdo"""
        texto_lower = texto.lower()
        
        setores_keywords = {
            "fintech": ["fintech", "financeiro", "pagamento", "crédito", "banco", "pix", "cartão", "empréstimo", "investimento"],
            "healthtech": ["healthtech", "saúde", "médico", "hospital", "telemedicina", "paciente", "clínica", "diagnóstico"],
            "edtech": ["edtech", "educação", "ensino", "curso", "escola", "aluno", "aprendizado", "treinamento"],
            "construtech": ["construtech", "construção", "obra", "construtora", "engenharia civil", "bim", "incorporadora"],
            "agrotech": ["agrotech", "agro", "agricultura", "fazenda", "produtor rural", "safra", "pecuária"],
            "retailtech": ["retailtech", "varejo", "e-commerce", "loja", "marketplace", "comércio"],
            "logtech": ["logtech", "logística", "entrega", "frete", "transporte", "supply chain"],
            "hrtech": ["hrtech", "rh", "recrutamento", "funcionário", "contratação", "gestão de pessoas"],
            "legaltech": ["legaltech", "jurídico", "advocacia", "contrato", "compliance"],
            "insurtech": ["insurtech", "seguro", "sinistro", "apólice", "cobertura"],
            "proptech": ["proptech", "imobiliário", "imóvel", "aluguel", "compra e venda"],
            "foodtech": ["foodtech", "alimentação", "delivery", "restaurante", "comida"],
            "martech": ["martech", "marketing", "publicidade", "mídia", "automação de marketing"],
            "cleantech": ["cleantech", "energia", "solar", "sustentável", "carbono", "renovável"],
        }
        
        scores = {}
        for setor, keywords in setores_keywords.items():
            score = sum(1 for kw in keywords if kw in texto_lower)
            if score > 0:
                scores[setor] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return "outro"
    
    def _validar_e_ajustar_resultado(self, resultado: Dict[str, Any], setor: str) -> Dict[str, Any]:
        """Valida e ajusta o resultado da avaliação"""
        criterios = [
            "sumario_executivo", "proposta_valor", "concorrencia", "mercado_alvo",
            "canais_distribuicao", "relacionamento_clientes", "fontes_receita",
            "recursos_principais", "atividades_chave", "parceiros",
            "estrutura_custos", "referencias_indicacao"
        ]
        
        # Garante que todas as notas existem e estão no range correto
        notas = []
        for criterio in criterios:
            nota = resultado.get(criterio, 2.0)
            if nota is None:
                nota = 2.0
            nota = max(0, min(4, float(nota)))
            resultado[criterio] = round(nota, 1)
            notas.append(resultado[criterio])
        
        # Recalcula nota final como média
        resultado['nota_final'] = round(sum(notas) / len(notas), 2)
        
        # Garante setor
        resultado['setor'] = setor
        
        # Garante justificativas padrão se ausentes
        justificativas = [
            "justificativa_sumario", "justificativa_proposta", "justificativa_concorrencia",
            "justificativa_mercado", "justificativa_canais", "justificativa_relacionamento",
            "justificativa_receita", "justificativa_recursos", "justificativa_atividades",
            "justificativa_parceiros", "justificativa_custos", "justificativa_referencias"
        ]
        
        for just in justificativas:
            if not resultado.get(just):
                resultado[just] = "Justificativa não fornecida pela IA."
        
        return resultado
    
    def _resumir_conteudo(self, texto: str) -> str:
        """Resume conteúdo muito longo mantendo informações relevantes"""
        keywords = [
            'empresa', 'negócio', 'produto', 'serviço', 'mercado', 'cliente',
            'receita', 'faturamento', 'financeiro', 'investimento', 'capital',
            'equipe', 'fundador', 'tecnologia', 'inovação', 'diferencial',
            'crescimento', 'tração', 'competidor', 'estratégia', 'objetivo',
            'patente', 'certificação', 'regulatório', 'parceria', 'cac', 'ltv',
            'mrr', 'arr', 'churn', 'nps', 'kpi', 'métrica', 'benchmark'
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
    """Agente responsável por gerar diagnóstico estratégico específico do setor"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = self.settings.OPENAI_MODEL
    
    async def diagnosticar(self, avaliacao: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """
        Gera diagnóstico estratégico baseado na avaliação.
        Usa prompts específicos do setor.
        
        Args:
            avaliacao: Resultado da avaliação do agente avaliador
            max_retries: Número máximo de tentativas
            
        Returns:
            Dicionário com diagnóstico completo
        """
        setor = avaliacao.get("setor", "outro")
        system_prompt = gerar_system_prompt_diagnostico(setor)
        
        user_content = HUMAN_PROMPT_DIAGNOSTICO.format(
            empresa=avaliacao.get("empresa", "N/A"),
            setor=setor,
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
                logger.info(f"Diagnóstico - Tentativa {attempt + 1}/{max_retries} - Setor: {setor}")
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.4,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                resultado = json.loads(content)
                
                logger.info(f"Diagnóstico concluído: {resultado.get('empresa')}")
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


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def get_setores_disponiveis() -> list:
    """Retorna lista de setores disponíveis para avaliação"""
    return list(METRICAS_POR_SETOR.keys())


def get_info_setor(setor: str) -> Dict[str, Any]:
    """Retorna informações completas sobre um setor"""
    return get_config_setor(setor)