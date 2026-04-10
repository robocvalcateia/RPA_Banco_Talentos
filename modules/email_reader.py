"""
Mdulo para leitura de e-mails via Microsoft Graph
"""
import requests
import os
from datetime import datetime, timedelta
import logging
from config.microsoft_graph import get_microsoft_graph
from utils.file_handler import FileHandler
from utils.validators import Validators

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
import os

load_dotenv()
class EmailReader:
    """L e-mails e baixa anexos"""
    
    def __init__(self):
        """Inicializa o leitor de e-mails"""
        self.graph_config = get_microsoft_graph()
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.email = self.graph_config.get_email()
        self.dias_atras = int(os.getenv('DIAS_ATRAS', 730))
    
    def get_emails(self):
        """Obtm lista de e-mails dos ltimos 2 anos"""
        try:
            logger.info(" Iniciando leitura de e-mails...")
            
            # Calcular data limite
            date_limit = datetime.now() - timedelta(days=self.dias_atras)
            date_filter = date_limit.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Construir URL com filtro de data
            url = f"{self.base_url}/users/{self.email}/mailFolders/inbox/messages"
            params = {
                '$filter': f"receivedDateTime ge {date_filter}",
                '$select': 'id,subject,from,receivedDateTime,hasAttachments',
                '$top': 999
            }
            
            headers = self.graph_config.get_headers()
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            emails = response.json().get('value', [])
            logger.info(f" {len(emails)} e-mails encontrados")
            
            return emails
            
        except Exception as e:
            logger.error(f" Erro ao obter e-mails: {e}")
            return []
    
    def get_email_attachments(self, email_id):
        """Obtm anexos de um e-mail especfico"""
        try:
            url = f"{self.base_url}/users/{self.email}/messages/{email_id}/attachments"
            headers = self.graph_config.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            attachments = response.json().get('value', [])
            return attachments
            
        except Exception as e:
            logger.error(f" Erro ao obter anexos do e-mail {email_id}: {e}")
            return []
    
    def download_attachment(self, email_id, attachment_id, filename):
        """Baixa um anexo especfico"""
        try:
            url = f"{self.base_url}/users/{self.email}/messages/{email_id}/attachments/{attachment_id}"
            headers = self.graph_config.get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            attachment_data = response.json()
            
            # Verificar se  um arquivo com contedo
            if '@odata.type' in attachment_data and '#microsoft.graph.fileAttachment' in attachment_data['@odata.type']:
                # Decodificar o contedo base64
                import base64
                content = base64.b64decode(attachment_data.get('contentBytes', ''))
                
                # Salvar arquivo
                file_path = FileHandler.save_file(content, filename, subfolder='email')
                logger.info(f" Anexo baixado: {filename}")
                return file_path
            
            return None
            
        except Exception as e:
            logger.error(f" Erro ao baixar anexo {attachment_id}: {e}")
            return None
    
    def process_emails(self):
        """Processa todos os e-mails e baixa anexos vlidos"""
        try:
            emails = self.get_emails()
            downloaded_files = []
            
            for email in emails:
                email_id = email.get('id')
                subject = email.get('subject', 'Sem assunto')
                has_attachments = email.get('hasAttachments', False)
                received_date = email.get('receivedDateTime')
                
                # Validar data
                if not Validators.is_within_date_range(received_date, self.dias_atras):
                    continue
                
                if has_attachments:
                    logger.info(f" Processando e-mail: {subject}")
                    
                    attachments = self.get_email_attachments(email_id)
                    
                    for attachment in attachments:
                        filename = attachment.get('name', 'arquivo')
                        attachment_id = attachment.get('id')
                        
                        # Verificar extenso
                        if self._is_valid_file_extension(filename):
                            file_path = self.download_attachment(email_id, attachment_id, filename)
                            
                            if file_path:
                                downloaded_files.append({
                                    'path': file_path,
                                    'filename': filename,
                                    'source': 'email',
                                    'email_id': email_id,
                                    'email_subject': subject,
                                    'email_date': received_date
                                })
            
            logger.info(f" Total de arquivos baixados do e-mail: {len(downloaded_files)}")
            return downloaded_files
            
        except Exception as e:
            logger.error(f" Erro ao processar e-mails: {e}")
            return []
    
    @staticmethod
    def _is_valid_file_extension(filename):
        """Verifica se o arquivo tem extenso vlida"""
        valid_extensions = ['.pdf', '.doc', '.docx']
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in valid_extensions


    def move_email(self, email_id, destination_folder_name):
        """Move e-mail para uma pasta específica"""
        try:
            headers = self.graph_config.get_headers()

            # buscar pasta destino
            folders_url = f"{self.base_url}/users/{self.email}/mailFolders"
            response = requests.get(folders_url, headers=headers)
            response.raise_for_status()

            folders = response.json().get("value", [])

            destination_folder = next(
                (f for f in folders if f["displayName"] == destination_folder_name),
                None
            )

            if not destination_folder:
                logger.error(f"Pasta não encontrada: {destination_folder_name}")
                return False

            move_url = f"{self.base_url}/users/{self.email}/messages/{email_id}/move"

            payload = {
                "destinationId": destination_folder["id"]
            }

            response = requests.post(move_url, headers=headers, json=payload)
            response.raise_for_status()

            logger.info(f"E-mail movido para {destination_folder_name}")
            return True

        except Exception as e:
            logger.error(f"Erro ao mover e-mail: {e}")
            return False

def process_emails():
    """Funo auxiliar para processar e-mails"""
    reader = EmailReader()
    return reader.process_emails()
