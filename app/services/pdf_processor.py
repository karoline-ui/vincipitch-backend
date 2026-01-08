"""
Serviço de processamento de PDFs para extração de texto.
Usa PyMuPDF (fitz) como método principal e pdfplumber como fallback.
"""

import re
import io
import logging
from typing import Optional, Tuple
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processa PDFs para extrair e limpar texto."""
    
    # Palavras-chave relevantes para pitch decks
    KEYWORDS_RELEVANTES = [
        "mercado", "market", "receita", "revenue", "cliente", "customer",
        "produto", "product", "serviço", "service", "equipe", "team",
        "investimento", "investment", "crescimento", "growth", "tração",
        "traction", "problema", "problem", "solução", "solution",
        "modelo de negócio", "business model", "competição", "competition",
        "diferencial", "vantagem", "advantage", "patente", "patent",
        "faturamento", "mrr", "arr", "cac", "ltv", "churn", "nps",
        "rodada", "round", "valuation", "runway", "breakeven"
    ]
    
    def __init__(self):
        self.metodo_usado: str = ""
        self.qualidade: float = 0.0
        self.num_paginas: int = 0
    
    async def processar_pdf(self, pdf_bytes: bytes) -> Tuple[str, str, dict]:
        """
        Processa um PDF e retorna o texto extraído.
        
        Args:
            pdf_bytes: Conteúdo do PDF em bytes
            
        Returns:
            Tuple com (texto_extraido, texto_limpo, metadados)
        """
        texto_extraido = ""
        
        # Tenta PyMuPDF primeiro (mais rápido e preciso)
        try:
            texto_extraido = await self._extrair_com_pymupdf(pdf_bytes)
            self.metodo_usado = "pymupdf"
        except Exception as e:
            logger.warning(f"PyMuPDF falhou: {e}, tentando pdfplumber...")
        
        # Fallback para pdfplumber se PyMuPDF falhar ou retornar vazio
        if not texto_extraido or len(texto_extraido.strip()) < 100:
            try:
                texto_extraido = await self._extrair_com_pdfplumber(pdf_bytes)
                self.metodo_usado = "pdfplumber"
            except Exception as e:
                logger.error(f"Ambos métodos falharam: {e}")
                raise ValueError("Não foi possível extrair texto do PDF")
        
        # Limpa o texto
        texto_limpo = self._limpar_texto(texto_extraido)
        
        # Calcula qualidade da extração
        self.qualidade = self._calcular_qualidade(texto_limpo)
        
        metadados = {
            "metodo_extracao": self.metodo_usado,
            "qualidade_extracao": self.qualidade,
            "numero_paginas": self.num_paginas,
            "caracteres_extraidos": len(texto_extraido),
            "caracteres_limpos": len(texto_limpo),
            "palavras": len(texto_limpo.split()),
            "keywords_encontradas": self._contar_keywords(texto_limpo)
        }
        
        return texto_extraido, texto_limpo, metadados
    
    async def _extrair_com_pymupdf(self, pdf_bytes: bytes) -> str:
        """Extrai texto usando PyMuPDF (fitz)."""
        texto_paginas = []
        
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            self.num_paginas = len(doc)
            
            for pagina in doc:
                # Extrai texto com layout preservado
                texto = pagina.get_text("text")
                if texto.strip():
                    texto_paginas.append(texto)
        
        return "\n\n".join(texto_paginas)
    
    async def _extrair_com_pdfplumber(self, pdf_bytes: bytes) -> str:
        """Extrai texto usando pdfplumber (melhor para tabelas)."""
        texto_paginas = []
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            self.num_paginas = len(pdf.pages)
            
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_paginas.append(texto)
                
                # Tenta extrair tabelas também
                tabelas = pagina.extract_tables()
                for tabela in tabelas:
                    if tabela:
                        for linha in tabela:
                            if linha:
                                texto_paginas.append(" | ".join(str(c or "") for c in linha))
        
        return "\n\n".join(texto_paginas)
    
    def _limpar_texto(self, texto: str) -> str:
        """Limpa e normaliza o texto extraído."""
        if not texto:
            return ""
        
        # Remove caracteres de controle
        texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', texto)
        
        # Normaliza espaços e quebras de linha
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        
        # Remove URLs muito longas (mantém curtas para referência)
        texto = re.sub(r'https?://\S{100,}', '[URL]', texto)
        
        # Remove sequências de caracteres repetidos
        texto = re.sub(r'(.)\1{10,}', r'\1\1\1', texto)
        
        # Remove números de página isolados
        texto = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', texto)
        
        # Remove headers/footers comuns
        texto = re.sub(r'(?i)(confidencial|proprietary|all rights reserved|©.*?\d{4})', '', texto)
        
        # Normaliza pontuação
        texto = re.sub(r'\s+([.,;:!?])', r'\1', texto)
        texto = re.sub(r'([.,;:!?])\s*([.,;:!?])+', r'\1', texto)
        
        return texto.strip()
    
    def _calcular_qualidade(self, texto: str) -> float:
        """
        Calcula score de qualidade da extração (0-1).
        Considera: tamanho, keywords, estrutura, etc.
        """
        if not texto:
            return 0.0
        
        score = 0.0
        palavras = len(texto.split())
        
        # Tamanho mínimo esperado para um pitch (~500 palavras)
        if palavras >= 500:
            score += 0.3
        elif palavras >= 200:
            score += 0.15
        elif palavras >= 50:
            score += 0.05
        
        # Keywords encontradas
        keywords_count = self._contar_keywords(texto)
        if keywords_count >= 10:
            score += 0.3
        elif keywords_count >= 5:
            score += 0.2
        elif keywords_count >= 2:
            score += 0.1
        
        # Estrutura (parágrafos, seções)
        paragrafos = texto.count('\n\n')
        if paragrafos >= 5:
            score += 0.2
        elif paragrafos >= 2:
            score += 0.1
        
        # Presença de números (métricas são importantes)
        numeros = len(re.findall(r'\d+[.,]?\d*', texto))
        if numeros >= 20:
            score += 0.2
        elif numeros >= 10:
            score += 0.1
        elif numeros >= 5:
            score += 0.05
        
        return min(1.0, score)
    
    def _contar_keywords(self, texto: str) -> int:
        """Conta quantas keywords relevantes estão no texto."""
        texto_lower = texto.lower()
        return sum(1 for kw in self.KEYWORDS_RELEVANTES if kw.lower() in texto_lower)
    
    def resumir_conteudo(self, texto: str, max_chars: int = 15000) -> str:
        """
        Resume o conteúdo se necessário para caber no contexto da IA.
        Mantém as partes mais relevantes.
        """
        if len(texto) <= max_chars:
            return texto
        
        # Divide em parágrafos
        paragrafos = texto.split('\n\n')
        
        # Pontua cada parágrafo por relevância
        scored_paragrafos = []
        for p in paragrafos:
            score = self._pontuar_paragrafo(p)
            scored_paragrafos.append((score, p))
        
        # Ordena por relevância
        scored_paragrafos.sort(key=lambda x: x[0], reverse=True)
        
        # Reconstrói mantendo os mais relevantes
        resultado = []
        chars_atuais = 0
        
        for score, paragrafo in scored_paragrafos:
            if chars_atuais + len(paragrafo) > max_chars:
                break
            resultado.append(paragrafo)
            chars_atuais += len(paragrafo) + 2  # +2 para \n\n
        
        # Reordena na ordem original aproximada
        resultado_final = []
        for p in paragrafos:
            if p in resultado:
                resultado_final.append(p)
        
        return '\n\n'.join(resultado_final)
    
    def _pontuar_paragrafo(self, paragrafo: str) -> float:
        """Pontua relevância de um parágrafo."""
        score = 0.0
        p_lower = paragrafo.lower()
        
        # Keywords
        for kw in self.KEYWORDS_RELEVANTES:
            if kw.lower() in p_lower:
                score += 1.0
        
        # Números (métricas)
        numeros = len(re.findall(r'\d+[.,]?\d*', paragrafo))
        score += numeros * 0.3
        
        # Valores monetários
        valores = len(re.findall(r'R\$|USD|\$|€|BRL', paragrafo))
        score += valores * 0.5
        
        # Percentuais
        percentuais = len(re.findall(r'\d+%', paragrafo))
        score += percentuais * 0.4
        
        # Penaliza parágrafos muito curtos ou muito longos
        palavras = len(paragrafo.split())
        if palavras < 10:
            score *= 0.5
        elif palavras > 300:
            score *= 0.8
        
        return score


# Função auxiliar para uso direto
async def processar_pdf(pdf_bytes: bytes) -> Tuple[str, str, dict]:
    """Função auxiliar para processar PDF."""
    processor = PDFProcessor()
    return await processor.processar_pdf(pdf_bytes)
