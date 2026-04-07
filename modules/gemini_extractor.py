"""
Módulo para extração de dados de CVs usando Gemini API
"""
import json
import time
import logging
from google.genai import types
from config.gemini import get_gemini
from utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class GeminiExtractor:
    """Extrai dados de CVs usando Gemini API"""
    
    PROMPT_TEMPLATE = """Extraia os dados de um currículo a partir do documento fornecido.

RETORNE APENAS UM JSON VÁLIDO, SEM TEXTO ADICIONAL, SEM EXPLICAÇÕES, SEM MARKDOWN.

O JSON DEVE CONTER EXATAMENTE AS SEGUINTES CHAVES (todas obrigatórias):
- Nome
- Nacionalidade
- Idade
- Endereco
- Telefone
- Email
- Link_Linkedin
- Skil
- Formacao_Academica
- Nivel_Idioma_Ingles
- Nivel_Idioma_Espanhol
- Cursos_Certificacoes
- Conhecimento_Tecnico
- Experiencia_Profissional

REGRAS IMPORTANTES:

1. O retorno deve ser um objeto JSON (dict), nunca lista.
2. Todas as chaves devem existir, mesmo que vazias.
3. Se não encontrar um valor, retornar "" (string vazia).
4. Cada chave deve conter apenas um valor do tipo string.
5. Não incluir listas, objetos aninhados ou múltiplos valores.
6. Não incluir quebras de linha no JSON.
7. Não incluir ```json ou ```.

CRITÉRIOS DE EXTRAÇÃO:

Nome:
- Nome completo do candidato
- Localizado no topo do currículo

Nacionalidade:
- Nacionalidade do Canditado, caso não tenha nada considerar Brasileiro

Idade:
- Caso não exista, calcular a partir da data de nascimento

Endereco:
- Cidade, estado ou endereço completo

Telefone:
- Numero de Telefone no formato ddd-xxxxx-xxxx

Email:
- Email
- Caso não exista, deixar em branco

Link_Linkedin:
- Link_Linkedin
- Caso não exista o que for encontrado não corresponder a uma url, deixar em branco

Skil:
- Resumo das qualificações profissionais

Formacao_Academica:
- Formação principal (graduação, pós, etc.)
- Maior nível (Ensino Médio, Superior, Pós, MBA, etc.)

Nivel_Idioma_Ingles:
- Nivel_Idioma_Ingles
- Caso não exista, deixar em branco

Nivel_Idioma_Espanhol:
- Nivel_Idioma_Espanhol
- Caso não exista, deixar em branco

Cursos_Certificacoes:
- Cursos complementares separados por vírgula

Conhecimento_Tecnico:
- Lista de conhecimento técnico profissional

Experiencia_Profissional
- Resumo das experiências no formato:
- Empresa - Cargo (Período) | Empresa - Cargo (Período)

FORMATO FINAL OBRIGATÓRIO:
{{
  "Nome": "",
  "Nacionalidade": "",
  "Idade": "",
  "Endereco": "",
  "Telefone": "",
  "Email": "",
  "Link_Linkedin": "",
  "Skil": "",
  "Formacao_Academica": "",
  "Nivel_Idioma_Ingles": "",
  "Nivel_Idioma_Espanhol": "",
  "Cursos_Certificacoes": "",
  "Conhecimento_Tecnico": "",
  "Experiencia_Profissional": ""
}}"""
    
    def __init__(self):
        """Inicializa o extrator Gemini"""
        self.gemini_config = get_gemini()
        self.client = self.gemini_config.get_client()
        self.model = self.gemini_config.get_model()
    
    def _normalize_json_response(self, dados):
        """Normaliza a resposta do modelo Gemini"""
        if isinstance(dados, list):
            if len(dados) == 1 and isinstance(dados[0], dict):
                return dados[0]
            else:
                return dados
        elif isinstance(dados, dict):
            return dados
        else:
            raise ValueError("Formato inesperado de dados retornados.")
    
    def extract_from_pdf(self, pdf_path, max_tentativas=4, delay_retry=3):
        """
        Extrai dados de um PDF usando Gemini
        
        Args:
            pdf_path (str): Caminho do arquivo PDF
            max_tentativas (int): Número máximo de tentativas
            delay_retry (int): Tempo entre tentativas em segundos
            
        Returns:
            dict: Dados extraídos ou None em caso de erro
        """
        
        for tentativa in range(1, max_tentativas + 1):
            try:
                logger.info(f" Processando PDF (tentativa {tentativa}/{max_tentativas}): {pdf_path}")
                
                # Fazer upload do PDF
                uploaded_file = self.client.files.upload(file=pdf_path)
                logger.info(f" PDF enviado para Gemini")
                
                # Chamar o modelo Gemini
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[uploaded_file, self.PROMPT_TEMPLATE],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                
                # Parsear a resposta
                dados_brutos = response.text.strip()
                
                # Limpar bordas de markdown se existirem
                dados_limpos = dados_brutos.strip('```json').strip('```').strip()
                
                # Converter para JSON
                json_dados = json.loads(dados_limpos)
                dados = self._normalize_json_response(json_dados)
                
                logger.info(f" Dados extraídos com sucesso")
                return dados
                
            except Exception as e:
                logger.error(f" Erro na tentativa {tentativa}: {e}")
                
                if tentativa < max_tentativas:
                    logger.info(f" Tentando novamente em {delay_retry}s...")
                    time.sleep(delay_retry)
                else:
                    logger.error(f" Limite de tentativas atingido para {pdf_path}")
                    return None
    
    def extract_from_file(self, file_path):
        """
        Extrai dados de um arquivo (PDF, DOC ou DOCX)
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            dict: Dados extraídos ou None em caso de erro
        """
        
        try:
            # Garantir que seja PDF
            pdf_path = FileHandler.ensure_pdf(file_path)
            
            if not pdf_path:
                logger.error(f" Não foi possível converter arquivo para PDF: {file_path}")
                return None
            
            # Extrair dados
            dados = self.extract_from_pdf(pdf_path)
            
            # Limpar arquivo temporário se foi convertido
            if pdf_path != file_path:
                FileHandler.delete_file(pdf_path)
            
            return dados
            
        except Exception as e:
            logger.error(f" Erro ao extrair dados do arquivo: {e}")
            return None


def extract_cv_data(file_path):
    """Função auxiliar para extrair dados de CV"""
    extractor = GeminiExtractor()
    return extractor.extract_from_file(file_path)
