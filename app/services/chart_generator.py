"""
Serviço de geração de gráficos para análises de startups.
Usa Matplotlib para gráficos estáticos e Plotly para interativos.
"""

import io
import base64
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

# Cores da marca VinciPitch
CORES_MARCA = {
    "verde": "#00E676",
    "verde_escuro": "#00C853",
    "roxo": "#4A148C",
    "roxo_claro": "#6B21A8",
    "roxo_medio": "#7C3AED",
    "cinza": "#64748B",
    "cinza_claro": "#94A3B8",
    "branco": "#FFFFFF",
    "fundo": "#0F172A"
}

# Gradiente de cores para rankings
CORES_RANKING = ["#00E676", "#4ADE80", "#FACC15", "#F97316", "#EF4444"]

# Labels dos 12 critérios
CRITERIOS_LABELS = {
    "sumario_executivo": "Sumário Executivo",
    "proposta_valor": "Proposta de Valor",
    "concorrencia": "Concorrência",
    "mercado_alvo": "Mercado Alvo",
    "canais_distribuicao": "Canais de Distribuição",
    "relacionamento_clientes": "Relacionamento",
    "fontes_receita": "Fontes de Receita",
    "recursos_principais": "Recursos Principais",
    "atividades_chave": "Atividades-Chave",
    "parceiros": "Parceiros",
    "estrutura_custos": "Estrutura de Custos",
    "referencias_indicacao": "Referências"
}


@dataclass
class ConfigGrafico:
    """Configurações de estilo para gráficos."""
    largura: int = 800
    altura: int = 600
    dpi: int = 150
    fonte_titulo: int = 14
    fonte_labels: int = 10
    cor_fundo: str = CORES_MARCA["branco"]
    cor_texto: str = CORES_MARCA["fundo"]
    mostrar_grid: bool = True


class ChartGenerator:
    """Gerador de gráficos para análises de startups."""
    
    def __init__(self, config: Optional[ConfigGrafico] = None):
        self.config = config or ConfigGrafico()
        self._configurar_matplotlib()
    
    def _configurar_matplotlib(self):
        """Configura estilo padrão do Matplotlib."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        plt.rcParams['figure.facecolor'] = self.config.cor_fundo
        plt.rcParams['axes.facecolor'] = self.config.cor_fundo
        plt.rcParams['text.color'] = self.config.cor_texto
        plt.rcParams['axes.labelcolor'] = self.config.cor_texto
        plt.rcParams['xtick.color'] = self.config.cor_texto
        plt.rcParams['ytick.color'] = self.config.cor_texto
    
    # =========================================================================
    # GRÁFICO RADAR - Notas dos 12 Critérios
    # =========================================================================
    
    def gerar_radar_criterios(
        self,
        notas: Dict[str, float],
        titulo: str = "Análise por Critérios",
        incluir_media: bool = True
    ) -> bytes:
        """
        Gera gráfico radar com as notas dos 12 critérios.
        
        Args:
            notas: Dict com critério -> nota (0-4)
            titulo: Título do gráfico
            incluir_media: Se deve incluir linha de média
            
        Returns:
            Imagem PNG em bytes
        """
        # Prepara dados
        criterios = list(CRITERIOS_LABELS.keys())
        labels = [CRITERIOS_LABELS[c] for c in criterios]
        valores = [notas.get(c, 0) for c in criterios]
        
        # Número de variáveis
        N = len(criterios)
        
        # Ângulos para cada critério
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        valores_plot = valores + valores[:1]  # Fecha o polígono
        angles += angles[:1]
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        # Plota área preenchida
        ax.fill(angles, valores_plot, color=CORES_MARCA["verde"], alpha=0.25)
        ax.plot(angles, valores_plot, color=CORES_MARCA["verde"], linewidth=2)
        
        # Adiciona pontos
        ax.scatter(angles[:-1], valores, color=CORES_MARCA["verde"], s=100, zorder=5)
        
        # Linha de média se solicitado
        if incluir_media:
            media = np.mean(valores)
            ax.plot(angles, [media] * len(angles), color=CORES_MARCA["roxo"], 
                   linewidth=1.5, linestyle='--', label=f'Média: {media:.2f}')
            ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))
        
        # Configura eixos
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=9)
        ax.set_ylim(0, 4)
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['1', '2', '3', '4'], size=8)
        
        # Título
        ax.set_title(titulo, size=14, fontweight='bold', pad=20)
        
        # Salva em bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight',
                   facecolor=self.config.cor_fundo, edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    # =========================================================================
    # GRÁFICO DE BARRAS HORIZONTAIS - Ranking
    # =========================================================================
    
    def gerar_barras_ranking(
        self,
        empresas: List[Dict[str, Any]],
        titulo: str = "Ranking de Startups",
        max_empresas: int = 10
    ) -> bytes:
        """
        Gera gráfico de barras horizontais com ranking.
        
        Args:
            empresas: Lista de dicts com 'nome', 'nota_final', 'setor'
            titulo: Título do gráfico
            max_empresas: Máximo de empresas a exibir
            
        Returns:
            Imagem PNG em bytes
        """
        # Limita e ordena
        empresas = sorted(empresas, key=lambda x: x.get('nota_final', 0), reverse=True)[:max_empresas]
        
        # Prepara dados
        nomes = [e.get('nome', 'N/A')[:25] for e in empresas]
        notas = [e.get('nota_final', 0) for e in empresas]
        setores = [e.get('setor', 'outro') for e in empresas]
        
        # Cores baseadas na nota
        cores = [self._cor_por_nota(n) for n in notas]
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(12, max(6, len(empresas) * 0.6)))
        
        # Barras horizontais
        y_pos = np.arange(len(nomes))
        bars = ax.barh(y_pos, notas, color=cores, edgecolor='white', linewidth=0.5)
        
        # Labels nas barras
        for i, (bar, nota) in enumerate(zip(bars, notas)):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                   f'{nota:.2f}', va='center', fontsize=10, fontweight='bold')
        
        # Configura eixos
        ax.set_yticks(y_pos)
        ax.set_yticklabels(nomes)
        ax.set_xlim(0, 4.5)
        ax.set_xlabel('Nota Final (0-4)', fontsize=11)
        ax.invert_yaxis()  # Maior nota no topo
        
        # Grid vertical
        ax.xaxis.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        
        # Título
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
        
        # Legenda de setores
        setores_unicos = list(set(setores))
        if len(setores_unicos) > 1:
            legend_text = "Setores: " + ", ".join(setores_unicos[:5])
            ax.text(0.02, -0.08, legend_text, transform=ax.transAxes, 
                   fontsize=8, color=CORES_MARCA["cinza"])
        
        plt.tight_layout()
        
        # Salva em bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight',
                   facecolor=self.config.cor_fundo)
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    # =========================================================================
    # GRÁFICO COMPARATIVO - Duas Empresas
    # =========================================================================
    
    def gerar_comparativo(
        self,
        empresa_a: Dict[str, Any],
        empresa_b: Dict[str, Any],
        titulo: str = "Comparativo de Startups"
    ) -> bytes:
        """
        Gera gráfico comparativo entre duas empresas.
        
        Args:
            empresa_a: Dict com 'nome' e notas por critério
            empresa_b: Dict com 'nome' e notas por critério
            titulo: Título do gráfico
            
        Returns:
            Imagem PNG em bytes
        """
        criterios = list(CRITERIOS_LABELS.keys())
        labels = [CRITERIOS_LABELS[c] for c in criterios]
        
        notas_a = [empresa_a.get(f'nota_{c}', empresa_a.get(c, 0)) for c in criterios]
        notas_b = [empresa_b.get(f'nota_{c}', empresa_b.get(c, 0)) for c in criterios]
        
        x = np.arange(len(labels))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        bars_a = ax.bar(x - width/2, notas_a, width, label=empresa_a.get('nome', 'Empresa A'),
                       color=CORES_MARCA["verde"], edgecolor='white')
        bars_b = ax.bar(x + width/2, notas_b, width, label=empresa_b.get('nome', 'Empresa B'),
                       color=CORES_MARCA["roxo_medio"], edgecolor='white')
        
        # Labels nas barras
        ax.bar_label(bars_a, fmt='%.1f', padding=3, fontsize=8)
        ax.bar_label(bars_b, fmt='%.1f', padding=3, fontsize=8)
        
        # Configura eixos
        ax.set_ylabel('Nota (0-4)', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.set_ylim(0, 4.5)
        ax.legend(loc='upper right')
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        
        # Título
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
        
        # Médias no rodapé
        media_a = np.mean(notas_a)
        media_b = np.mean(notas_b)
        ax.text(0.02, -0.18, f"Média {empresa_a.get('nome', 'A')}: {media_a:.2f}", 
               transform=ax.transAxes, fontsize=10, color=CORES_MARCA["verde_escuro"])
        ax.text(0.98, -0.18, f"Média {empresa_b.get('nome', 'B')}: {media_b:.2f}",
               transform=ax.transAxes, fontsize=10, color=CORES_MARCA["roxo"], ha='right')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight',
                   facecolor=self.config.cor_fundo)
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    # =========================================================================
    # GRÁFICO DE DISTRIBUIÇÃO - Histograma de Notas
    # =========================================================================
    
    def gerar_distribuicao_notas(
        self,
        notas: List[float],
        titulo: str = "Distribuição de Notas",
        setor: Optional[str] = None
    ) -> bytes:
        """
        Gera histograma com distribuição de notas.
        
        Args:
            notas: Lista de notas finais
            titulo: Título do gráfico
            setor: Nome do setor (opcional)
            
        Returns:
            Imagem PNG em bytes
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histograma
        n, bins, patches = ax.hist(notas, bins=20, range=(0, 4), 
                                   color=CORES_MARCA["verde"], alpha=0.7,
                                   edgecolor='white', linewidth=0.5)
        
        # Colore barras por faixa
        for i, patch in enumerate(patches):
            bin_center = (bins[i] + bins[i+1]) / 2
            patch.set_facecolor(self._cor_por_nota(bin_center))
        
        # Linha de média
        media = np.mean(notas)
        ax.axvline(media, color=CORES_MARCA["roxo"], linestyle='--', linewidth=2,
                  label=f'Média: {media:.2f}')
        
        # Linha de mediana
        mediana = np.median(notas)
        ax.axvline(mediana, color=CORES_MARCA["roxo_medio"], linestyle=':', linewidth=2,
                  label=f'Mediana: {mediana:.2f}')
        
        # Configura eixos
        ax.set_xlabel('Nota Final (0-4)', fontsize=11)
        ax.set_ylabel('Número de Empresas', fontsize=11)
        ax.set_xlim(0, 4)
        ax.legend(loc='upper right')
        
        # Estatísticas no rodapé
        stats_text = f"Total: {len(notas)} empresas | Mín: {min(notas):.2f} | Máx: {max(notas):.2f} | Desvio: {np.std(notas):.2f}"
        ax.text(0.5, -0.12, stats_text, transform=ax.transAxes, fontsize=9,
               ha='center', color=CORES_MARCA["cinza"])
        
        # Título
        titulo_final = f"{titulo}" + (f" - {setor.title()}" if setor else "")
        ax.set_title(titulo_final, fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight',
                   facecolor=self.config.cor_fundo)
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    # =========================================================================
    # GRÁFICO DE EVOLUÇÃO - Linha do Tempo
    # =========================================================================
    
    def gerar_evolucao(
        self,
        dados: List[Dict[str, Any]],
        titulo: str = "Evolução das Análises"
    ) -> bytes:
        """
        Gera gráfico de linha mostrando evolução ao longo do tempo.
        
        Args:
            dados: Lista de dicts com 'data' e 'nota_media'
            titulo: Título do gráfico
            
        Returns:
            Imagem PNG em bytes
        """
        if not dados:
            return self._gerar_grafico_vazio("Sem dados para evolução")
        
        datas = [d.get('data') for d in dados]
        notas = [d.get('nota_media', 0) for d in dados]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Linha principal
        ax.plot(datas, notas, color=CORES_MARCA["verde"], linewidth=2.5, marker='o',
               markersize=8, markerfacecolor=CORES_MARCA["verde_escuro"])
        
        # Área preenchida
        ax.fill_between(datas, notas, alpha=0.2, color=CORES_MARCA["verde"])
        
        # Linha de tendência
        if len(notas) > 2:
            z = np.polyfit(range(len(notas)), notas, 1)
            p = np.poly1d(z)
            ax.plot(datas, p(range(len(notas))), color=CORES_MARCA["roxo"],
                   linestyle='--', linewidth=1.5, alpha=0.7, label='Tendência')
        
        # Configura eixos
        ax.set_xlabel('Data', fontsize=11)
        ax.set_ylabel('Nota Média', fontsize=11)
        ax.set_ylim(0, 4)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left')
        
        # Rotaciona labels do eixo X
        plt.xticks(rotation=45, ha='right')
        
        # Título
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.config.dpi, bbox_inches='tight',
                   facecolor=self.config.cor_fundo)
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    # =========================================================================
    # GRÁFICO INTERATIVO PLOTLY - Radar
    # =========================================================================
    
    def gerar_radar_plotly(
        self,
        notas: Dict[str, float],
        titulo: str = "Análise por Critérios"
    ) -> str:
        """
        Gera gráfico radar interativo com Plotly.
        
        Returns:
            HTML string do gráfico
        """
        criterios = list(CRITERIOS_LABELS.keys())
        labels = [CRITERIOS_LABELS[c] for c in criterios]
        valores = [notas.get(c, 0) for c in criterios]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=valores + [valores[0]],
            theta=labels + [labels[0]],
            fill='toself',
            fillcolor=f'rgba(0, 230, 118, 0.3)',
            line=dict(color=CORES_MARCA["verde"], width=2),
            name='Notas'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 4]),
            ),
            showlegend=False,
            title=dict(text=titulo, font=dict(size=16)),
            paper_bgcolor=CORES_MARCA["branco"],
            plot_bgcolor=CORES_MARCA["branco"]
        )
        
        return fig.to_html(include_plotlyjs='cdn', full_html=False)
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _cor_por_nota(self, nota: float) -> str:
        """Retorna cor baseada na nota (0-4)."""
        if nota >= 3.5:
            return CORES_MARCA["verde"]
        elif nota >= 2.5:
            return "#4ADE80"  # Verde claro
        elif nota >= 1.5:
            return "#FACC15"  # Amarelo
        elif nota >= 0.5:
            return "#F97316"  # Laranja
        else:
            return "#EF4444"  # Vermelho
    
    def _gerar_grafico_vazio(self, mensagem: str) -> bytes:
        """Gera gráfico placeholder com mensagem."""
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, mensagem, ha='center', va='center', fontsize=14,
               color=CORES_MARCA["cinza"])
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                   facecolor=self.config.cor_fundo)
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    def salvar_grafico(self, grafico_bytes: bytes, caminho: str) -> str:
        """Salva gráfico em arquivo local."""
        with open(caminho, 'wb') as f:
            f.write(grafico_bytes)
        return caminho
    
    def grafico_para_base64(self, grafico_bytes: bytes) -> str:
        """Converte gráfico para string base64."""
        return base64.b64encode(grafico_bytes).decode('utf-8')
