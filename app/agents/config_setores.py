"""
Configuração de métricas e critérios de avaliação específicos por setor.
Cada setor tem KPIs, métricas e critérios próprios para avaliação de startups.
"""

from typing import Dict, List, Any

# ═══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS E CRITÉRIOS POR SETOR
# ═══════════════════════════════════════════════════════════════════════════════

METRICAS_POR_SETOR: Dict[str, Dict[str, Any]] = {
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FINTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "fintech": {
        "nome_display": "FinTech",
        "descricao": "Tecnologia financeira - pagamentos, crédito, investimentos, seguros",
        "kpis_principais": [
            "CAC (Custo de Aquisição de Cliente)",
            "LTV (Lifetime Value)",
            "LTV/CAC Ratio (ideal > 3x)",
            "MRR/ARR (Receita Recorrente)",
            "Churn Rate (taxa de cancelamento)",
            "NIM (Net Interest Margin) para crédito",
            "Volume de Transações (TPV)",
            "Take Rate (% sobre transações)",
            "Time to Value (TTV)",
            "Compliance Score"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza na proposta de valor financeira, diferenciação competitiva no mercado financeiro",
            "proposta_valor": "Redução de custos vs bancos tradicionais, experiência digital superior, inclusão financeira",
            "concorrencia": "Posicionamento vs fintechs e bancos incumbentes, barreiras de entrada",
            "mercado_alvo": "TAM/SAM/SOM do mercado financeiro, segmentação clara (B2B, B2C, underbanked)",
            "canais_distribuicao": "Estratégia de aquisição digital, parcerias com empresas, embedded finance",
            "relacionamento_clientes": "NPS, suporte 24/7, educação financeira, onboarding digital",
            "fontes_receita": "Modelo de monetização (taxas, spread, assinatura), unit economics",
            "recursos_principais": "Licenças regulatórias, infraestrutura de segurança, capital regulatório",
            "atividades_chave": "Compliance, gestão de risco, desenvolvimento de produto, análise de crédito",
            "parceiros": "Bancos parceiros, bandeiras de cartão, fintechs complementares, reguladores",
            "estrutura_custos": "CAC, infraestrutura cloud, compliance, capital de giro",
            "referencias_indicacao": "Cases de sucesso, volume processado, certificações de segurança"
        },
        "perguntas_avaliacao": [
            "A startup possui ou está em processo de obtenção das licenças regulatórias necessárias?",
            "Qual o LTV/CAC ratio atual e projetado?",
            "Como a startup gerencia riscos de crédito, fraude e compliance?",
            "Qual o volume de transações processado (TPV) e taxa de crescimento?",
            "A infraestrutura de segurança atende aos padrões PCI-DSS, SOC2?",
            "Qual a estratégia de embedded finance ou Banking as a Service?"
        ],
        "benchmarks": {
            "ltv_cac_ratio_bom": 3.0,
            "churn_mensal_aceitavel": 0.05,
            "margem_bruta_ideal": 0.60,
            "payback_meses_ideal": 12
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HEALTHTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "healthtech": {
        "nome_display": "HealthTech",
        "descricao": "Tecnologia em saúde - telemedicina, gestão hospitalar, diagnóstico, wellness",
        "kpis_principais": [
            "CAC (Custo de Aquisição)",
            "LTV (Lifetime Value do paciente/cliente)",
            "DAU/MAU (Usuários Ativos)",
            "Taxa de Adesão ao Tratamento",
            "NPS de Pacientes",
            "Custo por Consulta/Atendimento",
            "Taxa de Resolução na Primeira Consulta",
            "Tempo Médio de Espera",
            "Taxa de Readmissão (hospitalar)",
            "Compliance LGPD/HIPAA"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema de saúde resolvido, impacto em outcomes clínicos",
            "proposta_valor": "Melhoria em resultados de saúde, redução de custos do sistema, acessibilidade",
            "concorrencia": "Diferenciação vs sistema tradicional de saúde, outras healthtechs",
            "mercado_alvo": "Segmentação (B2B hospitais, B2C pacientes, B2B2C operadoras)",
            "canais_distribuicao": "Parcerias com hospitais, operadoras, farmácias, médicos",
            "relacionamento_clientes": "Experiência do paciente, suporte médico, follow-up",
            "fontes_receita": "Modelo (SaaS para hospitais, per member per month, fee-for-service)",
            "recursos_principais": "Registros ANVISA, equipe médica, infraestrutura de dados de saúde",
            "atividades_chave": "Desenvolvimento clínico, validação científica, compliance regulatório",
            "parceiros": "Hospitais, operadoras de saúde, laboratórios, indústria farmacêutica",
            "estrutura_custos": "Equipe médica, infraestrutura, certificações, marketing",
            "referencias_indicacao": "Estudos clínicos, parceiros hospitalares, certificações"
        },
        "perguntas_avaliacao": [
            "A solução possui validação clínica ou estudos comprovando eficácia?",
            "Quais certificações e registros regulatórios (ANVISA, CFM) possui?",
            "Como garantem a segurança e privacidade dos dados de saúde (LGPD)?",
            "Qual o impacto mensurável nos outcomes de saúde dos pacientes?",
            "A startup tem parcerias com hospitais ou operadoras de saúde?",
            "Qual a taxa de adesão dos pacientes/usuários ao tratamento?"
        ],
        "benchmarks": {
            "nps_pacientes_bom": 50,
            "taxa_adesao_ideal": 0.70,
            "custo_por_vida_salva": "mensurável",
            "tempo_espera_ideal_min": 15
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EDTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "edtech": {
        "nome_display": "EdTech",
        "descricao": "Tecnologia educacional - cursos online, tutoria, gestão escolar, gamificação",
        "kpis_principais": [
            "DAU/MAU (Usuários Ativos)",
            "Stickiness Ratio (DAU/MAU)",
            "Taxa de Conclusão de Cursos",
            "Taxa de Retenção de Alunos",
            "NPS de Alunos/Pais",
            "Learning Outcomes (resultados de aprendizagem)",
            "CAC por Aluno",
            "LTV por Aluno",
            "Tempo de Engajamento na Plataforma",
            "Taxa de Conversão Free-to-Paid"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema educacional resolvido, metodologia pedagógica",
            "proposta_valor": "Melhoria nos resultados de aprendizagem, engajamento, acessibilidade",
            "concorrencia": "Diferenciação vs educação tradicional e outras edtechs",
            "mercado_alvo": "Segmentação (K-12, ensino superior, corporativo, lifelong learning)",
            "canais_distribuicao": "B2C direto, B2B escolas, B2B2C empresas, parcerias governamentais",
            "relacionamento_clientes": "Suporte pedagógico, comunidade, gamificação, mentoria",
            "fontes_receita": "Modelo (assinatura, per seat, freemium, certificações pagas)",
            "recursos_principais": "Conteúdo pedagógico, tecnologia de aprendizado adaptativo, instrutores",
            "atividades_chave": "Produção de conteúdo, desenvolvimento de plataforma, análise de dados educacionais",
            "parceiros": "Escolas, universidades, empresas, governo, editoras",
            "estrutura_custos": "Produção de conteúdo, tecnologia, marketing, suporte",
            "referencias_indicacao": "Cases de melhoria de aprendizagem, parcerias institucionais"
        },
        "perguntas_avaliacao": [
            "Qual a taxa de conclusão dos cursos e como se compara ao mercado?",
            "Existem estudos comprovando melhoria nos resultados de aprendizagem?",
            "Qual o engajamento médio dos usuários (tempo na plataforma, frequência)?",
            "A metodologia pedagógica é baseada em evidências científicas?",
            "Qual a estratégia de retenção e redução de churn de alunos?",
            "Como a plataforma personaliza a experiência de aprendizado?"
        ],
        "benchmarks": {
            "taxa_conclusao_bom": 0.30,
            "stickiness_ratio_bom": 0.20,
            "nps_alunos_bom": 40,
            "tempo_engajamento_dia_min": 15
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "construtech": {
        "nome_display": "ConsTech",
        "descricao": "Tecnologia para construção civil - gestão de obras, BIM, marketplace, IoT",
        "kpis_principais": [
            "GMV (Volume Bruto de Mercadorias)",
            "Taxa de Adoção por Construtoras",
            "Redução de Custos de Obra (%)",
            "Redução de Prazo de Obra (%)",
            "NPS de Construtoras/Engenheiros",
            "Número de Projetos Ativos",
            "ARR (Receita Recorrente)",
            "CAC por Construtora",
            "Taxa de Expansão de Conta",
            "Economia Gerada para Clientes"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema da construção civil resolvido, ROI para construtoras",
            "proposta_valor": "Redução de custos, prazos, desperdício, melhoria de qualidade e segurança",
            "concorrencia": "Diferenciação vs métodos tradicionais e outras construtechs",
            "mercado_alvo": "Segmentação (incorporadoras, construtoras, engenheiros, fornecedores)",
            "canais_distribuicao": "Vendas enterprise, parcerias com associações, eventos do setor",
            "relacionamento_clientes": "Suporte técnico, treinamento, consultoria de implementação",
            "fontes_receita": "Modelo (SaaS, marketplace com take rate, licenciamento)",
            "recursos_principais": "Tecnologia BIM/IoT, expertise em construção, integrações com ERPs",
            "atividades_chave": "Desenvolvimento de produto, vendas consultivas, suporte técnico",
            "parceiros": "Construtoras, fornecedores de materiais, incorporadoras, sindicatos",
            "estrutura_custos": "Desenvolvimento, vendas enterprise, suporte técnico",
            "referencias_indicacao": "Cases de economia em obras, parcerias com grandes construtoras"
        },
        "perguntas_avaliacao": [
            "Qual a economia comprovada gerada para os clientes (% redução custo/prazo)?",
            "Quantas obras/projetos ativos utilizam a plataforma?",
            "A solução integra com ERPs e sistemas existentes das construtoras?",
            "Qual o ciclo de vendas médio e como é a adoção em grandes construtoras?",
            "A startup tem cases com construtoras de grande porte?",
            "Como a solução ajuda no compliance de segurança e normas técnicas?"
        ],
        "benchmarks": {
            "reducao_custo_obra_bom": 0.15,
            "reducao_prazo_obra_bom": 0.20,
            "nps_construtoras_bom": 50,
            "ciclo_vendas_meses": 6
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AGROTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "agrotech": {
        "nome_display": "AgroTech",
        "descricao": "Tecnologia para agronegócio - agricultura de precisão, gestão rural, marketplace",
        "kpis_principais": [
            "Área Monitorada (hectares)",
            "Aumento de Produtividade (%)",
            "Redução de Custos Agrícolas (%)",
            "Número de Fazendas/Produtores",
            "ARR (Receita Recorrente)",
            "CAC por Produtor",
            "Taxa de Retenção de Safra",
            "ROI do Produtor",
            "Volume de Commodities Transacionado",
            "Economia de Insumos (%)"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema agrícola resolvido, ROI para o produtor",
            "proposta_valor": "Aumento de produtividade, redução de custos, sustentabilidade",
            "concorrencia": "Diferenciação vs métodos tradicionais e outras agrotechs",
            "mercado_alvo": "Segmentação (pequenos/médios/grandes produtores, cooperativas, traders)",
            "canais_distribuicao": "Vendas diretas, cooperativas, revendas agrícolas, associações",
            "relacionamento_clientes": "Suporte agronômico, treinamento, consultoria técnica",
            "fontes_receita": "Modelo (SaaS por hectare, marketplace, consultoria)",
            "recursos_principais": "Tecnologia IoT/satélite, expertise agronômica, dados climáticos",
            "atividades_chave": "Desenvolvimento de sensores/software, vendas rurais, suporte técnico",
            "parceiros": "Cooperativas, revendas, traders, indústria de insumos, Embrapa",
            "estrutura_custos": "Hardware IoT, desenvolvimento, equipe comercial rural",
            "referencias_indicacao": "Cases de produtividade, parcerias com cooperativas"
        },
        "perguntas_avaliacao": [
            "Qual o aumento comprovado de produtividade para os produtores?",
            "Quantos hectares/fazendas utilizam a solução ativamente?",
            "A solução funciona offline em áreas rurais sem conectividade?",
            "Qual o ROI médio para o produtor que adota a tecnologia?",
            "A startup tem parcerias com cooperativas ou grandes grupos agrícolas?",
            "Como a solução integra com dados climáticos e satelitais?"
        ],
        "benchmarks": {
            "aumento_produtividade_bom": 0.15,
            "reducao_insumos_bom": 0.20,
            "roi_produtor_ideal": 3.0,
            "area_monitorada_media": 10000
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RETAILTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "retailtech": {
        "nome_display": "RetailTech",
        "descricao": "Tecnologia para varejo - e-commerce, gestão de lojas, omnichannel, logística",
        "kpis_principais": [
            "GMV (Volume Bruto de Mercadorias)",
            "Take Rate (%)",
            "AOV (Average Order Value)",
            "Taxa de Conversão",
            "CAC por Cliente",
            "LTV do Cliente",
            "Taxa de Repeat Purchase",
            "NPS de Clientes",
            "Custo de Fulfillment",
            "Tempo de Entrega Médio"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema do varejo resolvido, diferenciação competitiva",
            "proposta_valor": "Aumento de vendas, redução de custos operacionais, experiência do cliente",
            "concorrencia": "Posicionamento vs marketplaces, varejo tradicional, outras retailtechs",
            "mercado_alvo": "Segmentação (varejistas, marcas, consumidores, nichos específicos)",
            "canais_distribuicao": "Marketing digital, parcerias com varejistas, integrações",
            "relacionamento_clientes": "Experiência omnichannel, suporte, personalização",
            "fontes_receita": "Modelo (SaaS, marketplace, comissão por venda, publicidade)",
            "recursos_principais": "Plataforma tecnológica, logística, dados de consumo",
            "atividades_chave": "Desenvolvimento de produto, operações logísticas, marketing",
            "parceiros": "Varejistas, transportadoras, gateways de pagamento, influenciadores",
            "estrutura_custos": "Tecnologia, logística, marketing, suporte",
            "referencias_indicacao": "Cases de aumento de vendas, parcerias com grandes varejistas"
        },
        "perguntas_avaliacao": [
            "Qual o GMV processado e taxa de crescimento?",
            "Qual a taxa de conversão e como se compara ao mercado?",
            "A solução oferece experiência omnichannel integrada?",
            "Qual o custo de fulfillment e logística por pedido?",
            "Qual a taxa de repeat purchase dos clientes?",
            "Como a plataforma utiliza dados para personalização?"
        ],
        "benchmarks": {
            "taxa_conversao_bom": 0.03,
            "repeat_purchase_bom": 0.30,
            "custo_frete_gmv": 0.10,
            "nps_clientes_bom": 50
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LOGTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "logtech": {
        "nome_display": "LogTech",
        "descricao": "Tecnologia para logística - gestão de frota, last mile, supply chain, fulfillment",
        "kpis_principais": [
            "Volume de Entregas",
            "Custo por Entrega",
            "Taxa de Entregas no Prazo (OTD)",
            "Taxa de Avarias/Extravios",
            "Utilização de Frota (%)",
            "Custo por Km Rodado",
            "NPS de Clientes/Embarcadores",
            "Tempo Médio de Entrega",
            "ARR (Receita Recorrente)",
            "GMV Transportado"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema logístico resolvido, eficiência operacional",
            "proposta_valor": "Redução de custos logísticos, velocidade, rastreabilidade, confiabilidade",
            "concorrencia": "Diferenciação vs operadores tradicionais e outras logtechs",
            "mercado_alvo": "Segmentação (e-commerces, indústrias, transportadoras, last mile)",
            "canais_distribuicao": "Vendas B2B, parcerias com e-commerces, integrações",
            "relacionamento_clientes": "Rastreamento em tempo real, suporte, SLA garantido",
            "fontes_receita": "Modelo (por entrega, SaaS, comissão sobre frete)",
            "recursos_principais": "Tecnologia de roteirização, rede de entregadores, integrações",
            "atividades_chave": "Operações logísticas, otimização de rotas, gestão de entregas",
            "parceiros": "Transportadoras, motoristas autônomos, e-commerces, armazéns",
            "estrutura_custos": "Operações, tecnologia, rede de entregadores, combustível",
            "referencias_indicacao": "Cases de eficiência logística, parcerias com grandes e-commerces"
        },
        "perguntas_avaliacao": [
            "Qual a taxa de entregas no prazo (OTD) e meta de SLA?",
            "Qual o custo médio por entrega e como se compara ao mercado?",
            "A solução oferece rastreamento em tempo real para o cliente final?",
            "Qual a cobertura geográfica e capilaridade da rede?",
            "Como a tecnologia otimiza rotas e reduz custos?",
            "Qual a taxa de avarias e extravios?"
        ],
        "benchmarks": {
            "otd_bom": 0.95,
            "taxa_avarias_aceitavel": 0.02,
            "utilizacao_frota_bom": 0.80,
            "custo_por_km_competitivo": True
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HRTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "hrtech": {
        "nome_display": "HRTech",
        "descricao": "Tecnologia para RH - recrutamento, gestão de pessoas, folha, benefícios",
        "kpis_principais": [
            "Tempo de Contratação (Time to Hire)",
            "Custo por Contratação",
            "Taxa de Retenção de Funcionários",
            "NPS de Funcionários (eNPS)",
            "ARR (Receita Recorrente)",
            "Número de Funcionários Gerenciados",
            "Taxa de Adoção da Plataforma",
            "Custo por Funcionário/Mês",
            "Taxa de Engajamento",
            "Redução de Turnover"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema de RH resolvido, ROI para empresas",
            "proposta_valor": "Eficiência em recrutamento, engajamento, redução de turnover",
            "concorrencia": "Diferenciação vs soluções tradicionais de RH e outras hrtechs",
            "mercado_alvo": "Segmentação (PMEs, enterprises, setores específicos)",
            "canais_distribuicao": "Vendas B2B, parcerias com consultorias, eventos de RH",
            "relacionamento_clientes": "Suporte dedicado, treinamento, consultoria de implementação",
            "fontes_receita": "Modelo (SaaS per seat, por transação, marketplace de talentos)",
            "recursos_principais": "Plataforma tecnológica, algoritmos de matching, integrações",
            "atividades_chave": "Desenvolvimento de produto, vendas B2B, suporte",
            "parceiros": "Consultorias de RH, empresas de benefícios, universidades",
            "estrutura_custos": "Desenvolvimento, vendas, suporte, marketing B2B",
            "referencias_indicacao": "Cases de redução de turnover, parcerias com grandes empresas"
        },
        "perguntas_avaliacao": [
            "Qual a redução comprovada no tempo de contratação?",
            "Qual o impacto na taxa de turnover dos clientes?",
            "Quantos funcionários são gerenciados na plataforma?",
            "A solução integra com sistemas de folha e ERPs existentes?",
            "Qual o eNPS médio das empresas que utilizam a plataforma?",
            "Como a IA/ML melhora o matching de candidatos?"
        ],
        "benchmarks": {
            "reducao_time_to_hire": 0.40,
            "reducao_turnover": 0.20,
            "enps_bom": 30,
            "adocao_plataforma_bom": 0.80
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # LEGALTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "legaltech": {
        "nome_display": "LegalTech",
        "descricao": "Tecnologia jurídica - automação de contratos, gestão de processos, compliance",
        "kpis_principais": [
            "Número de Contratos/Processos Gerenciados",
            "Tempo de Elaboração de Contrato",
            "Redução de Custos Jurídicos (%)",
            "ARR (Receita Recorrente)",
            "NPS de Advogados/Empresas",
            "Taxa de Erros Reduzida",
            "Número de Advogados/Empresas Ativos",
            "Volume de Documentos Processados",
            "Taxa de Automação",
            "Compliance Score"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema jurídico resolvido, eficiência gerada",
            "proposta_valor": "Automação, redução de custos, agilidade, compliance",
            "concorrencia": "Diferenciação vs escritórios tradicionais e outras legaltechs",
            "mercado_alvo": "Segmentação (escritórios, departamentos jurídicos, PMEs)",
            "canais_distribuicao": "Vendas B2B, parcerias com OAB, eventos jurídicos",
            "relacionamento_clientes": "Suporte jurídico-técnico, treinamento, updates regulatórios",
            "fontes_receita": "Modelo (SaaS, por documento, marketplace de advogados)",
            "recursos_principais": "Tecnologia de automação, expertise jurídica, templates legais",
            "atividades_chave": "Desenvolvimento de produto, vendas B2B, atualização legal",
            "parceiros": "OAB, escritórios de advocacia, cartórios, tribunais",
            "estrutura_custos": "Desenvolvimento, equipe jurídica, compliance, vendas",
            "referencias_indicacao": "Cases de eficiência jurídica, parcerias com grandes escritórios"
        },
        "perguntas_avaliacao": [
            "Qual a redução comprovada no tempo de elaboração de contratos?",
            "A solução está atualizada com as últimas mudanças legislativas?",
            "Quantos contratos/documentos são processados mensalmente?",
            "A plataforma oferece templates validados juridicamente?",
            "Qual o nível de automação vs trabalho manual?",
            "Como a solução auxilia no compliance regulatório?"
        ],
        "benchmarks": {
            "reducao_tempo_contrato": 0.70,
            "reducao_custos_juridicos": 0.50,
            "taxa_automacao_bom": 0.80,
            "nps_advogados_bom": 50
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INSURTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "insurtech": {
        "nome_display": "InsurTech",
        "descricao": "Tecnologia para seguros - distribuição, subscrição, sinistros, embedded insurance",
        "kpis_principais": [
            "GWP (Gross Written Premium)",
            "Loss Ratio",
            "Combined Ratio",
            "CAC por Apólice",
            "LTV do Cliente",
            "Taxa de Renovação",
            "NPS de Segurados",
            "Tempo de Cotação",
            "Tempo de Resolução de Sinistro",
            "Taxa de Fraude Detectada"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema de seguros resolvido, proposta de valor",
            "proposta_valor": "Preços competitivos, experiência digital, agilidade em sinistros",
            "concorrencia": "Diferenciação vs seguradoras tradicionais e outras insurtechs",
            "mercado_alvo": "Segmentação (B2C, B2B, embedded, nichos específicos)",
            "canais_distribuicao": "Digital direto, corretores, embedded insurance, parcerias",
            "relacionamento_clientes": "App mobile, sinistros digitais, suporte 24/7",
            "fontes_receita": "Modelo (full stack, MGA, distribuição, SaaS para seguradoras)",
            "recursos_principais": "Licença SUSEP, tecnologia de subscrição, parcerias resseguro",
            "atividades_chave": "Subscrição, gestão de sinistros, prevenção de fraude",
            "parceiros": "Resseguradoras, corretores, empresas para embedded insurance",
            "estrutura_custos": "Sinistros, aquisição, tecnologia, regulatório",
            "referencias_indicacao": "Loss ratio, parcerias, volume de prêmios"
        },
        "perguntas_avaliacao": [
            "A startup possui licença SUSEP ou opera como correspondente?",
            "Qual o Loss Ratio e Combined Ratio atual?",
            "Qual a taxa de renovação de apólices?",
            "Qual o tempo médio de resolução de sinistros?",
            "A startup tem parcerias de resseguro adequadas?",
            "Como a tecnologia auxilia na precificação e detecção de fraudes?"
        ],
        "benchmarks": {
            "loss_ratio_bom": 0.60,
            "combined_ratio_bom": 0.95,
            "taxa_renovacao_bom": 0.80,
            "tempo_sinistro_dias": 15
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROPTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "proptech": {
        "nome_display": "PropTech",
        "descricao": "Tecnologia imobiliária - compra/venda, aluguel, gestão de propriedades",
        "kpis_principais": [
            "VGV (Volume Geral de Vendas)",
            "Número de Imóveis Listados",
            "Taxa de Conversão de Leads",
            "Tempo Médio de Venda/Locação",
            "CAC por Transação",
            "Take Rate/Comissão",
            "NPS de Compradores/Vendedores",
            "GMV de Aluguéis",
            "Taxa de Vacância (gestão)",
            "Inadimplência (aluguel)"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema imobiliário resolvido, diferenciação",
            "proposta_valor": "Agilidade, transparência, redução de custos de transação",
            "concorrencia": "Diferenciação vs imobiliárias tradicionais e outras proptechs",
            "mercado_alvo": "Segmentação (compra/venda, aluguel, comercial, residencial)",
            "canais_distribuicao": "Marketing digital, parcerias com corretores, SEO",
            "relacionamento_clientes": "Atendimento digital, visitas virtuais, suporte pós-venda",
            "fontes_receita": "Modelo (comissão, assinatura, serviços adicionais)",
            "recursos_principais": "Plataforma tecnológica, base de imóveis, integrações",
            "atividades_chave": "Captação de imóveis, marketing, fechamento de negócios",
            "parceiros": "Corretores, bancos (financiamento), cartórios, construtoras",
            "estrutura_custos": "Marketing, tecnologia, equipe comercial, jurídico",
            "referencias_indicacao": "VGV transacionado, parcerias, NPS"
        },
        "perguntas_avaliacao": [
            "Qual o VGV transacionado e taxa de crescimento?",
            "Qual o tempo médio de fechamento de uma transação?",
            "A plataforma oferece tour virtual e documentação digital?",
            "Qual a taxa de conversão de leads em transações?",
            "Como a tecnologia melhora a experiência vs imobiliárias tradicionais?",
            "Qual a estratégia para captação de imóveis de qualidade?"
        ],
        "benchmarks": {
            "tempo_venda_dias_bom": 60,
            "taxa_conversao_lead_bom": 0.05,
            "nps_clientes_bom": 50,
            "inadimplencia_aluguel_aceitavel": 0.05
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FOODTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "foodtech": {
        "nome_display": "FoodTech",
        "descricao": "Tecnologia para alimentação - delivery, dark kitchens, food as a service",
        "kpis_principais": [
            "GMV (Volume de Pedidos)",
            "Take Rate (%)",
            "AOV (Average Order Value)",
            "Taxa de Repeat Orders",
            "CAC por Cliente",
            "LTV do Cliente",
            "NPS de Clientes",
            "Tempo Médio de Entrega",
            "Taxa de Cancelamento",
            "Número de Restaurantes Parceiros"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema de alimentação resolvido, diferenciação",
            "proposta_valor": "Conveniência, variedade, qualidade, preço competitivo",
            "concorrencia": "Diferenciação vs apps de delivery e outras foodtechs",
            "mercado_alvo": "Segmentação (B2C delivery, B2B empresas, dark kitchens)",
            "canais_distribuicao": "App próprio, marketplaces, parcerias corporativas",
            "relacionamento_clientes": "UX do app, programa de fidelidade, atendimento",
            "fontes_receita": "Modelo (comissão, assinatura, publicidade, própria operação)",
            "recursos_principais": "Plataforma tecnológica, rede de restaurantes, logística",
            "atividades_chave": "Operações, marketing, gestão de restaurantes parceiros",
            "parceiros": "Restaurantes, entregadores, empresas para B2B",
            "estrutura_custos": "Marketing, logística, tecnologia, operações",
            "referencias_indicacao": "GMV, parcerias, NPS, tempo de entrega"
        },
        "perguntas_avaliacao": [
            "Qual o GMV mensal e taxa de crescimento?",
            "Qual a taxa de repeat orders e frequência de compra?",
            "Qual o tempo médio de entrega e meta de SLA?",
            "A startup opera dark kitchens próprias ou é marketplace?",
            "Qual a estratégia de aquisição e retenção de restaurantes?",
            "Como a tecnologia otimiza a operação de entrega?"
        ],
        "benchmarks": {
            "repeat_orders_bom": 0.40,
            "tempo_entrega_min_bom": 35,
            "taxa_cancelamento_aceitavel": 0.05,
            "nps_clientes_bom": 40
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MARTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "martech": {
        "nome_display": "MarTech",
        "descricao": "Tecnologia para marketing - automação, analytics, CRM, mídia programática",
        "kpis_principais": [
            "ARR (Receita Recorrente)",
            "NRR (Net Revenue Retention)",
            "Número de Clientes Ativos",
            "CAC por Cliente",
            "LTV do Cliente",
            "Churn Rate",
            "ROI Médio dos Clientes",
            "Volume de Dados Processados",
            "Taxa de Adoção de Features",
            "NPS de Clientes"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema de marketing resolvido, diferenciação",
            "proposta_valor": "Aumento de ROI de marketing, automação, insights acionáveis",
            "concorrencia": "Diferenciação vs ferramentas tradicionais e outras martechs",
            "mercado_alvo": "Segmentação (PMEs, enterprises, agências, setores específicos)",
            "canais_distribuicao": "Vendas B2B, produto self-service, parcerias com agências",
            "relacionamento_clientes": "Onboarding, suporte, treinamento, customer success",
            "fontes_receita": "Modelo (SaaS, por uso, comissão sobre mídia)",
            "recursos_principais": "Plataforma tecnológica, integrações, dados proprietários",
            "atividades_chave": "Desenvolvimento de produto, vendas, customer success",
            "parceiros": "Agências, plataformas de mídia, ERPs, e-commerces",
            "estrutura_custos": "Desenvolvimento, vendas, suporte, infraestrutura de dados",
            "referencias_indicacao": "Cases de ROI, integrações, volume de dados processados"
        },
        "perguntas_avaliacao": [
            "Qual o ROI médio que os clientes obtêm com a plataforma?",
            "Qual o NRR (Net Revenue Retention) da base de clientes?",
            "A plataforma integra com as principais ferramentas de marketing?",
            "Qual a diferenciação tecnológica (IA, dados proprietários)?",
            "Qual o modelo de precificação e unit economics?",
            "Como o produto demonstra valor rapidamente (time to value)?"
        ],
        "benchmarks": {
            "nrr_bom": 1.10,
            "churn_mensal_aceitavel": 0.03,
            "roi_cliente_medio": 5.0,
            "nps_clientes_bom": 50
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CLEANTECH / ENERGYTECH
    # ═══════════════════════════════════════════════════════════════════════════
    "cleantech": {
        "nome_display": "CleanTech/EnergyTech",
        "descricao": "Tecnologia limpa e energia - solar, eficiência energética, mobilidade elétrica",
        "kpis_principais": [
            "MW Instalados/Gerenciados",
            "Redução de Emissões (tCO2)",
            "Economia de Energia (%)",
            "ARR (Receita Recorrente)",
            "CAC por Cliente",
            "LTV do Cliente",
            "Payback do Cliente (meses)",
            "NPS de Clientes",
            "Volume de Energia Transacionado",
            "Créditos de Carbono Gerados"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza no problema ambiental/energético resolvido, impacto",
            "proposta_valor": "Redução de custos energéticos, sustentabilidade, descarbonização",
            "concorrencia": "Diferenciação vs soluções tradicionais e outras cleantechs",
            "mercado_alvo": "Segmentação (residencial, comercial, industrial, utilities)",
            "canais_distribuicao": "Vendas B2B/B2C, parcerias com utilities, integradores",
            "relacionamento_clientes": "Monitoramento contínuo, suporte técnico, garantias",
            "fontes_receita": "Modelo (venda de equipamento, SaaS, PPA, créditos carbono)",
            "recursos_principais": "Tecnologia proprietária, certificações, parcerias",
            "atividades_chave": "Desenvolvimento de produto, instalação, operação e manutenção",
            "parceiros": "Utilities, fabricantes, instaladores, bancos (financiamento)",
            "estrutura_custos": "Hardware, instalação, O&M, desenvolvimento",
            "referencias_indicacao": "MW instalados, economia gerada, créditos de carbono"
        },
        "perguntas_avaliacao": [
            "Qual a economia de energia comprovada para os clientes?",
            "Quantos MW foram instalados ou estão sob gestão?",
            "Qual o payback médio do investimento para o cliente?",
            "A startup tem certificações ambientais (ISO 14001, créditos carbono)?",
            "Qual a estratégia de financiamento para os clientes?",
            "Como a tecnologia se diferencia em eficiência ou custo?"
        ],
        "benchmarks": {
            "economia_energia_bom": 0.25,
            "payback_meses_bom": 48,
            "nps_clientes_bom": 60,
            "reducao_co2_mensuravel": True
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SETOR GENÉRICO (fallback)
    # ═══════════════════════════════════════════════════════════════════════════
    "outro": {
        "nome_display": "Outros Setores",
        "descricao": "Startups de outros setores não categorizados",
        "kpis_principais": [
            "Receita Mensal/Anual",
            "Taxa de Crescimento",
            "CAC (Custo de Aquisição)",
            "LTV (Lifetime Value)",
            "Churn Rate",
            "NPS (Net Promoter Score)",
            "Margem Bruta",
            "Burn Rate",
            "Runway",
            "Número de Clientes Ativos"
        ],
        "criterios_especificos": {
            "sumario_executivo": "Clareza na proposta de valor e diferenciação",
            "proposta_valor": "Benefício claro para o cliente, problema real resolvido",
            "concorrencia": "Análise competitiva e posicionamento",
            "mercado_alvo": "Definição clara de TAM/SAM/SOM",
            "canais_distribuicao": "Estratégia de go-to-market",
            "relacionamento_clientes": "Estratégia de retenção e satisfação",
            "fontes_receita": "Modelo de monetização e unit economics",
            "recursos_principais": "Recursos-chave para entrega de valor",
            "atividades_chave": "Operações essenciais para o negócio",
            "parceiros": "Ecossistema e parcerias estratégicas",
            "estrutura_custos": "Estrutura de custos e eficiência",
            "referencias_indicacao": "Tração e validação de mercado"
        },
        "perguntas_avaliacao": [
            "Qual a proposta de valor única da startup?",
            "O problema resolvido é urgente e frequente para os clientes?",
            "Qual o tamanho do mercado endereçável (TAM/SAM/SOM)?",
            "Qual o unit economics (CAC, LTV, payback)?",
            "A startup tem product-market fit comprovado?",
            "Qual a vantagem competitiva sustentável?"
        ],
        "benchmarks": {
            "ltv_cac_ratio_bom": 3.0,
            "margem_bruta_ideal": 0.50,
            "churn_mensal_aceitavel": 0.05,
            "nps_bom": 40
        }
    }
}


def get_config_setor(setor: str) -> Dict[str, Any]:
    """
    Retorna a configuração de métricas para um setor específico.
    Se o setor não existir, retorna a configuração genérica.
    """
    setor_lower = setor.lower().strip()
    
    # Mapeamento de variações de nome
    mapeamento = {
        "fintech": "fintech",
        "fintechs": "fintech",
        "healthtech": "healthtech",
        "health tech": "healthtech",
        "saúde": "healthtech",
        "edtech": "edtech",
        "educação": "edtech",
        "construtech": "construtech",
        "construtec": "construtech",
        "construção": "construtech",
        "agrotech": "agrotech",
        "agro": "agrotech",
        "agronegócio": "agrotech",
        "retailtech": "retailtech",
        "varejo": "retailtech",
        "logtech": "logtech",
        "logística": "logtech",
        "hrtech": "hrtech",
        "rh": "hrtech",
        "legaltech": "legaltech",
        "jurídico": "legaltech",
        "insurtech": "insurtech",
        "seguros": "insurtech",
        "proptech": "proptech",
        "imobiliário": "proptech",
        "foodtech": "foodtech",
        "alimentação": "foodtech",
        "martech": "martech",
        "marketing": "martech",
        "cleantech": "cleantech",
        "energytech": "cleantech",
        "energia": "cleantech",
    }
    
    setor_normalizado = mapeamento.get(setor_lower, setor_lower)
    
    return METRICAS_POR_SETOR.get(setor_normalizado, METRICAS_POR_SETOR["outro"])


def gerar_prompt_avaliacao(setor: str, dados_empresa: Dict[str, Any]) -> str:
    """
    Gera um prompt de avaliação específico para o setor da empresa.
    """
    config = get_config_setor(setor)
    
    nome_empresa = dados_empresa.get("nome", "Empresa")
    
    prompt = f"""Você é um ANALISTA SÊNIOR DE VENTURE CAPITAL especializado no setor de {config['nome_display']}.

═══════════════════════════════════════════════════════════════════════════════
📋 EMPRESA PARA ANÁLISE
═══════════════════════════════════════════════════════════════════════════════

NOME: {nome_empresa}
SETOR: {config['nome_display']}
DESCRIÇÃO DO SETOR: {config['descricao']}

═══════════════════════════════════════════════════════════════════════════════
📊 KPIs CRÍTICOS PARA {config['nome_display'].upper()}
═══════════════════════════════════════════════════════════════════════════════

Os principais indicadores que você DEVE avaliar para este setor são:
{chr(10).join(f"• {kpi}" for kpi in config['kpis_principais'])}

═══════════════════════════════════════════════════════════════════════════════
🎯 CRITÉRIOS DE AVALIAÇÃO ESPECÍFICOS DO SETOR
═══════════════════════════════════════════════════════════════════════════════

Para cada critério do Business Model Canvas, considere os seguintes aspectos específicos de {config['nome_display']}:

"""
    
    for criterio, descricao in config['criterios_especificos'].items():
        criterio_formatado = criterio.replace("_", " ").title()
        prompt += f"**{criterio_formatado}**: {descricao}\n"
    
    prompt += f"""

═══════════════════════════════════════════════════════════════════════════════
❓ PERGUNTAS-CHAVE PARA AVALIAR {config['nome_display'].upper()}
═══════════════════════════════════════════════════════════════════════════════

{chr(10).join(f"• {pergunta}" for pergunta in config['perguntas_avaliacao'])}

═══════════════════════════════════════════════════════════════════════════════
📈 BENCHMARKS DO SETOR
═══════════════════════════════════════════════════════════════════════════════

Considere os seguintes benchmarks ao avaliar:
"""
    
    for benchmark, valor in config['benchmarks'].items():
        benchmark_formatado = benchmark.replace("_", " ").title()
        if isinstance(valor, float):
            if valor < 1:
                prompt += f"• {benchmark_formatado}: {valor*100:.0f}%\n"
            else:
                prompt += f"• {benchmark_formatado}: {valor}x\n"
        else:
            prompt += f"• {benchmark_formatado}: {valor}\n"
    
    prompt += """

═══════════════════════════════════════════════════════════════════════════════
📝 INSTRUÇÕES DE AVALIAÇÃO
═══════════════════════════════════════════════════════════════════════════════

1. Avalie CADA critério de 0 a 4 pontos considerando:
   - 0: Não mencionado ou muito fraco
   - 1: Básico, precisa melhorar significativamente  
   - 2: Adequado, mas com lacunas importantes
   - 3: Bom, atende às expectativas do setor
   - 4: Excelente, acima da média do mercado

2. Seja RIGOROSO e use os KPIs específicos do setor como referência

3. Considere o ESTÁGIO da startup (MVP, tração inicial, escala)

4. Compare implicitamente com os BENCHMARKS do setor

5. A nota final deve ser a MÉDIA das notas dos 12 critérios

Retorne um JSON com a avaliação completa incluindo notas e justificativas detalhadas para cada critério.
"""
    
    return prompt


# Lista de todos os setores disponíveis
SETORES_DISPONIVEIS = list(METRICAS_POR_SETOR.keys())