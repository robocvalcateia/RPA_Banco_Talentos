"""
Mdulo para leitura de mensagens WhatsApp via Ultramsg
"""
import requests
import os
from datetime import datetime, timedelta
import logging
from config.ultramsg import get_ultramsg
from utils.file_handler import FileHandler
from utils.validators import Validators

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
import os

load_dotenv()

class WhatsAppReader:
    """L mensagens WhatsApp e baixa anexos"""
    
    def __init__(self):
        """Inicializa o leitor de WhatsApp"""
        self.ultramsg_config = get_ultramsg()
        self.dias_atras = int(os.getenv('DIAS_ATRAS', 730))
        
        if not self.ultramsg_config.is_enabled():
            logger.warning(" Ultramsg no est configurado. WhatsApp ser desabilitado.")
    
    def get_messages(self):
        """Obtm lista de mensagens dos ltimos 2 anos"""
        try:
            if not self.ultramsg_config.is_enabled():
                logger.warning(" Ultramsg no habilitado")
                return []
            
            logger.info(" Iniciando leitura de mensagens WhatsApp...")
            
            token = self.ultramsg_config.get_token()
            instance_id = self.ultramsg_config.get_instance_id()
            base_url = self.ultramsg_config.get_base_url()
            
            # Calcular data limite
            date_limit = datetime.now() - timedelta(days=self.dias_atras)
            
            # Construir URL
            url = f"{base_url}/{instance_id}/messages"
            
            params = {
                'token': token,
                'limit': 1000
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                messages = data.get('data', [])
                
                # Filtrar mensagens dentro do intervalo de data
                filtered_messages = []
                for msg in messages:
                    try:
                        msg_date = datetime.fromtimestamp(msg.get('timestamp', 0))
                        if msg_date >= date_limit:
                            filtered_messages.append(msg)
                    except:
                        continue
                
                logger.info(f" {len(filtered_messages)} mensagens encontradas")
                return filtered_messages
            else:
                logger.warning(f" Erro na resposta da API: {data.get('message', 'Erro desconhecido')}")
                return []
            
        except Exception as e:
            logger.error(f" Erro ao obter mensagens WhatsApp: {e}")
            return []
    
    def download_media(self, media_url, filename):
        """Baixa mdia de uma mensagem"""
        try:
            response = requests.get(media_url, timeout=30)
            response.raise_for_status()
            
            # Salvar arquivo
            file_path = FileHandler.save_file(response.content, filename, subfolder='whatsapp')
            logger.info(f" Mdia baixada: {filename}")
            return file_path
            
        except Exception as e:
            logger.error(f" Erro ao baixar mdia: {e}")
            return None
    
    def process_messages(self):
        """Processa todas as mensagens e baixa anexos vlidos"""
        try:
            if not self.ultramsg_config.is_enabled():
                logger.warning(" Ultramsg no habilitado")
                return []
            
            messages = self.get_messages()
            downloaded_files = []
            
            for message in messages:
                msg_id = message.get('id')
                msg_type = message.get('type', '')
                timestamp = message.get('timestamp', 0)
                
                # Validar data
                try:
                    msg_date = datetime.fromtimestamp(timestamp)
                    if not Validators.is_within_date_range(msg_date.isoformat(), self.dias_atras):
                        continue
                except:
                    continue
                
                # Verificar se tem anexo
                if msg_type == 'document' or msg_type == 'file':
                    media_url = message.get('media', '')
                    filename = message.get('fileName', f"documento_{msg_id}")
                    
                    # Verificar extenso
                    if self._is_valid_file_extension(filename):
                        logger.info(f" Processando mensagem: {filename}")
                        
                        file_path = self.download_media(media_url, filename)
                        
                        if file_path:
                            downloaded_files.append({
                                'path': file_path,
                                'filename': filename,
                                'source': 'whatsapp',
                                'message_id': msg_id,
                                'message_date': datetime.fromtimestamp(timestamp).isoformat()
                            })
            
            logger.info(f" Total de arquivos baixados do WhatsApp: {len(downloaded_files)}")
            return downloaded_files
            
        except Exception as e:
            logger.error(f" Erro ao processar mensagens WhatsApp: {e}")
            return []
    
    @staticmethod
    def _is_valid_file_extension(filename):
        """Verifica se o arquivo tem extenso vlida"""
        valid_extensions = ['.pdf', '.doc', '.docx']
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in valid_extensions


def process_whatsapp_messages():
    """Funo auxiliar para processar mensagens WhatsApp"""
    reader = WhatsAppReader()
    return reader.process_messages()
