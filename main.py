"""
Script principal - Orquestração do sistema de Banco de Talentos
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
from utils.logger import LoggerSetup
logger = LoggerSetup.setup()

# Importar módulos
from modules.email_reader import process_emails
from modules.email_reader import EmailReader
from modules.whatsapp_reader import process_whatsapp_messages
from modules.gemini_extractor import extract_cv_data
from modules.deduplication import process_candidate_data
from utils.file_handler import FileHandler
from modules.mongodb_handler import get_mongodb_handler

class BancoTalentosOrchestrator:
    """Orquestra o fluxo completo do sistema"""
    
    def __init__(self):
        """Inicializa o orquestrador"""
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'emails_processados': 0,
            'whatsapp_processados': 0,
            'arquivos_baixados': 0,
            'arquivos_processados': 0,
            'novos_candidatos': 0,
            'candidatos_atualizados': 0,
            'sem_mudancas': 0,
            'erros': 0
        }
    
    def run(self):
        """Executa o fluxo completo"""
        try:
            email_reader = EmailReader()
            Folder_Mail_Sucesso = 'CVs_Processados'
            Folder_Mail_Erro = 'CVs_Processados_Erro'
            self.logger.info("=" * 80)
            self.logger.info(" INICIANDO BANCO DE TALENTOS")
            self.logger.info("=" * 80)
            
            # Etapa 1: Capturar arquivos
            self.logger.info("\nETAPA 1: CAPTURANDO ARQUIVOS")
            self.logger.info("-" * 80)
            
            all_files = []
            
            # Processar e-mails
            self.logger.info("\nProcessando e-mails...")
            email_files = process_emails()
            all_files.extend(email_files)
            self.stats['emails_processados'] = len(email_files)
            
            # Processar WhatsApp
            # self.logger.info("\nProcessando mensagens WhatsApp...")
            # whatsapp_files = process_whatsapp_messages()
            # all_files.extend(whatsapp_files)
            # self.stats['whatsapp_processados'] = len(whatsapp_files)
            
            self.stats['arquivos_baixados'] = len(all_files)
            self.logger.info(f"\nTotal de arquivos capturados: {len(all_files)}")
            
            if not all_files:
                self.logger.warning("Nenhum arquivo foi capturado")
                self._print_summary()
                return
            
            # Etapa 2: Processar arquivos
            self.logger.info("\nETAPA 2: PROCESSANDO ARQUIVOS")
            self.logger.info("-" * 80)
            
            for file_info in all_files:
                try:
                    file_path = file_info['path']
                    filename = file_info['filename']
                    source = file_info['source']
                    
                    self.logger.info(f"\nProcessando: {filename}")
                    
                    # Gerar hash do arquivo
                    document_hash = FileHandler.generate_file_hash(file_path)
                    
                    if not document_hash:
                        self.logger.error(f" Não foi possível gerar hash para {filename}")
                        self.stats['erros'] += 1
                        continue
                    
                    # Extrair dados com Gemini
                    self.logger.info(f" Extraindo dados com Gemini...")
                    candidate_data = extract_cv_data(file_path)
                    
                    if not candidate_data:
                        self.logger.error(f" Não foi possível extrair dados de {filename}")
                        self.stats['erros'] += 1
                        continue
                    
                    self.logger.info(f" Dados extraídos: {candidate_data.get('Nome', 'Desconhecido')}")
                    
                    # Processar candidato (inserir ou atualizar)
                    source_date = file_info.get('email_date') or file_info.get('message_date')
                    
                    result = process_candidate_data(
                        candidate_data,
                        document_hash,
                        source,
                        source_date
                    )
                    
                    # Atualizar estatísticas
                    Move_Folder = Folder_Mail_Sucesso
                    if result['status'] == 'novo':
                        self.stats['novos_candidatos'] += 1
                        self.logger.info(f" Novo candidato: {result['nome']}")
                    elif result['status'] == 'atualizado':
                        self.stats['candidatos_atualizados'] += 1
                        self.logger.info(f" Candidato atualizado: {result['nome']}")
                    elif result['status'] == 'sem_mudancas':
                        self.stats['sem_mudancas'] += 1
                        self.logger.info(f"Sem mudanças: {result['nome']}")
                    else:
                        self.stats['erros'] += 1
                        self.logger.error(f" Erro ao processar: {result.get('mensagem')}")
                        Move_Folder = Folder_Mail_Erro

                    # Move Mail Folder
                    if file_info.get("source") == "email" and file_info.get("email_id"):
                        email_reader.move_email(
                            file_info["email_id"],
                            Move_Folder
                        )

                    self.stats['arquivos_processados'] += 1
                    
                except Exception as e:
                    # Move Mail Folder
                    if file_info.get("source") == "email" and file_info.get("email_id"):
                        email_reader.move_email(
                            file_info["email_id"],
                            Folder_Mail_Erro)

                    self.logger.error(f" Erro ao processar arquivo: {e}")
                    self.stats['erros'] += 1
                    continue
            
            # Etapa 3: Gerar relatório
            self.logger.info("\n ETAPA 3: GERANDO RELATÓRIO")
            self.logger.info("-" * 80)
            
            self._print_summary()
            
            # Limpar arquivos temporários
            self.logger.info("\nLimpando arquivos temporários...")
            FileHandler.cleanup_temp_files()
            
            self.logger.info("\n" + "=" * 80)
            self.logger.info(" PROCESSO CONCLUÍDO COM SUCESSO")
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f" Erro crítico no orquestrador: {e}")
            self._print_summary()
    
    def _print_summary(self):
        """Imprime resumo das operações"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info(" RESUMO DA EXECUÇÃO")
        self.logger.info("=" * 80)
        self.logger.info(f" E-mails processados: {self.stats['emails_processados']}")
        self.logger.info(f" Mensagens WhatsApp processadas: {self.stats['whatsapp_processados']}")
        self.logger.info(f" Total de arquivos baixados: {self.stats['arquivos_baixados']}")
        self.logger.info(f" Arquivos processados: {self.stats['arquivos_processados']}")
        self.logger.info(f" Novos candidatos: {self.stats['novos_candidatos']}")
        self.logger.info(f" Candidatos atualizados: {self.stats['candidatos_atualizados']}")
        self.logger.info(f"Sem mudanças: {self.stats['sem_mudancas']}")
        self.logger.info(f" Erros: {self.stats['erros']}")
        
        # Estatísticas do MongoDB
        try:
            handler = get_mongodb_handler()
            db_stats = handler.get_statistics()
            self.logger.info("\n Estatísticas do MongoDB:")
            self.logger.info(f"  Total de candidatos: {db_stats.get('total_candidatos', 0)}")
            self.logger.info(f"  Origem E-mail: {db_stats.get('origem_email', 0)}")
            self.logger.info(f"  Origem WhatsApp: {db_stats.get('origem_whatsapp', 0)}")
            self.logger.info(f"  Com E-mail: {db_stats.get('com_email', 0)}")
            self.logger.info(f"  Com Telefone: {db_stats.get('com_telefone', 0)}")
        except Exception as e:
            self.logger.warning(f"Não foi possível obter estatísticas do MongoDB: {e}")
        
        self.logger.info("=" * 80)


def main():
    """Função principal"""
    try:
        orchestrator = BancoTalentosOrchestrator()
        orchestrator.run()
    except Exception as e:
        logger.error(f" Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
