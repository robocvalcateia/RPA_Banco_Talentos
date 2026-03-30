"""
Configurao e conexo com MongoDB
"""
import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class MongoDBConfig:
    """Gerencia a conexo com MongoDB"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa a configurao do MongoDB"""
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Conecta ao MongoDB"""
        try:
            url = os.getenv('MONGODB_URL')
            db_name = os.getenv('MONGODB_DB', 'Banco_de_Talentos')
            
            if not url:
                raise ValueError("MONGODB_URL no configurada no arquivo .env")
            
            self._client = MongoClient(url, serverSelectionTimeoutMS=5000)
            
            # Testa a conexo
            self._client.admin.command('ping')
            
            self._db = self._client[db_name]
            logger.info(f" Conectado ao MongoDB: {db_name}")
            
            # Criar ndices
            self._create_indexes()
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f" Erro ao conectar ao MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f" Erro inesperado: {e}")
            raise
    
    def _create_indexes(self):
        """Cria ndices na coleo de candidatos"""
        try:
            collection = self._db['candidatos']
            
            # ndice nico para email
            collection.create_index('email', unique=True, sparse=True)
            
            # ndice nico para hash do documento
            collection.create_index('hash_documento', unique=True, sparse=True)
            
            # ndices para busca
            collection.create_index('nome')
            collection.create_index('telefone')
            collection.create_index('skills')
            collection.create_index('data_criacao')
            collection.create_index('data_atualizacao')
            
            logger.info(" ndices criados/verificados no MongoDB")
            
        except Exception as e:
            logger.warning(f" Erro ao criar ndices: {e}")
    
    def get_db(self):
        """Retorna a instncia do banco de dados"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name='candidatos'):
        """Retorna uma coleo especfica"""
        return self.get_db()[collection_name]
    
    def close(self):
        """Fecha a conexo com MongoDB"""
        if self._client:
            self._client.close()
            logger.info(" Conexo com MongoDB fechada")
    
    def __del__(self):
        """Garante que a conexo seja fechada"""
        self.close()


def get_mongodb():
    """Funo auxiliar para obter a instncia do MongoDB"""
    return MongoDBConfig()
