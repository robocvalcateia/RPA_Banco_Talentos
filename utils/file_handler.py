"""
Manipulação de arquivos e conversões
"""
import os
import hashlib
import shutil
from pathlib import Path
import logging
from docx import Document
from pdf2image import convert_from_path
from PIL import Image
import PyPDF2

from utils.config import *

logger = logging.getLogger(__name__)

class FileHandler:
    """Gerencia operações com arquivos"""
    
    @staticmethod
    def get_temp_folder():
        """Retorna a pasta temporária"""
        os.makedirs(TEMP_FOLDER, exist_ok=True)
        return TEMP_FOLDER
    
    @staticmethod
    def generate_file_hash(file_path):
        """Gera hash SHA256 de um arquivo"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f" Erro ao gerar hash do arquivo: {e}")
            return None
    
    @staticmethod
    def save_file(file_content, filename, subfolder=''):
        """Salva um arquivo na pasta temporária"""
        try:
            temp_folder = FileHandler.get_temp_folder()
            
            if subfolder:
                temp_folder = os.path.join(temp_folder, subfolder)
                os.makedirs(temp_folder, exist_ok=True)
            
            file_path = os.path.join(temp_folder, filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f" Arquivo salvo: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f" Erro ao salvar arquivo: {e}")
            return None
    
    @staticmethod
    def convert_docx_to_pdf(docx_path):
        """Converte arquivo DOCX para PDF"""
        try:
            # Usar LibreOffice para conversão
            import subprocess
            
            temp_folder = FileHandler.get_temp_folder()
            pdf_path = os.path.join(temp_folder, Path(docx_path).stem + '.pdf')
            
            # Comando para converter com LibreOffice
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_folder,
                docx_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                logger.info(f" DOCX convertido para PDF: {pdf_path}")
                return pdf_path
            else:
                logger.warning(f"Erro ao converter DOCX: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f" Erro ao converter DOCX para PDF: {e}")
            return None
    
    @staticmethod
    def convert_doc_to_pdf(doc_path):
        """Converte arquivo DOC para PDF"""
        try:
            # Usar LibreOffice para conversão
            import subprocess
            
            temp_folder = FileHandler.get_temp_folder()
            pdf_path = os.path.join(temp_folder, Path(doc_path).stem + '.pdf')
            
            # Comando para converter com LibreOffice
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_folder,
                doc_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                logger.info(f" DOC convertido para PDF: {pdf_path}")
                return pdf_path
            else:
                logger.warning(f"Erro ao converter DOC: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f" Erro ao converter DOC para PDF: {e}")
            return None
    
    @staticmethod
    def ensure_pdf(file_path):
        """Garante que o arquivo seja PDF, convertendo se necessário"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return file_path
            elif file_ext == '.docx':
                return FileHandler.convert_docx_to_pdf(file_path)
            elif file_ext == '.doc':
                return FileHandler.convert_doc_to_pdf(file_path)
            else:
                logger.warning(f"Formato não suportado: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f" Erro ao garantir PDF: {e}")
            return None
    
    @staticmethod
    def cleanup_temp_files():
        """Limpa arquivos temporários"""
        try:
            temp_folder = FileHandler.get_temp_folder()
            
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
                os.makedirs(temp_folder, exist_ok=True)
                logger.info(" Arquivos temporários limpos")
                
        except Exception as e:
            logger.error(f" Erro ao limpar arquivos temporários: {e}")
    
    @staticmethod
    def delete_file(file_path):
        """Deleta um arquivo específico"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f" Arquivo deletado: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f" Erro ao deletar arquivo: {e}")
            return False
