

# python "C:\RPA\RPA_Banco_Talentos\api.py"
# cd C:\RPA\RPA_Banco_Talentos\web\banco_talentos_web
# npm install --legacy-peer-deps
# npm run dev
from flask import Flask, jsonify, request
from flask_cors import CORS
from bson import ObjectId
from modules.mongodb_handler import get_mongodb_handler
from auth_utils import generate_token, verify_token, token_required
import os
from dotenv import load_dotenv
from modules.word_generator import WordGenerator
from flask import send_file

word_gen = WordGenerator("templates")

load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================
# BANCO DE DADOS DE USUÁRIOS
# ============================================
# Em produção, armazene no MongoDB com senhas hasheadas

USERS_DB = {
    "admin@alcateia.com.br": {
        "password": "admin123",
        "name": "Administrador",
        "role": "admin"
    },
    "user@alcateia.com.br": {
        "password": "user123",
        "name": "Usuário",
        "role": "user"
    },
    "test@test.com": {
        "password": "test123",
        "name": "Teste",
        "role": "user"
    }
}

# ============================================
# ENDPOINTS DE AUTENTICAÇÃO
# ============================================

@app.route('/api/candidatos/<id>/gerar-documento', methods=['POST'])
@token_required
def gerar_documento(id):
    """
    Gera documento Word com dados do candidato
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Esperado:
    {
        "template_id": "cv"  // ou "carta", "perfil_linkedin"
    }
    
    Retorna:
    Arquivo Word para download
    """
    try:
        handler = get_mongodb_handler()
        candidato = handler.get_candidate_by_id(id)
        
        if not candidato:
            return jsonify({
                'success': False,
                'error': 'Candidato não encontrado'
            }), 404
        
        data = request.get_json()
        template_id = data.get('template_id', 'cv')
        
        # Gerar documento
        output_path, filename = word_gen.generate_document(
            template_id,
            serialize_doc(candidato)
        )
        
        # Retornar arquivo
        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except Exception as e:
        print(f"❌ Erro ao gerar documento: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/templates', methods=['GET'])
@token_required
def list_templates():
    """
    Retorna lista de templates disponíveis
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Retorna:
    {
        "success": true,
        "templates": [
            {"id": "cv", "nome": "Currículo Padrão"},
            {"id": "carta", "nome": "Carta de Apresentação"}
        ]
    }
    """
    try:
        templates = word_gen.list_templates()
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
    
    except Exception as e:
        print(f"❌ Erro ao listar templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def serialize_doc(doc):
    """Serializa documento do MongoDB para JSON"""
    return {
        "_id": str(doc.get("_id", "")),
        "nome": doc.get("nome", ""),
        "email": doc.get("email", ""),
        "telefone": doc.get("telefone", ""),
        "endereco": doc.get("endereco", ""),
        "nacionalidade": doc.get("nacionalidade", ""),
        "idade": doc.get("idade", ""),
        "linkedin": doc.get("linkedin", ""),
        "skills": doc.get("skills", ""),
        "formacao_academica": doc.get("formacao_academica", ""),
        "nivel_ingles": doc.get("nivel_ingles", ""),
        "nivel_espanhol": doc.get("nivel_espanhol", ""),
        "cursos_certificacoes": doc.get("cursos_certificacoes", ""),
        "conhecimento_tecnico": doc.get("conhecimento_tecnico", ""),
        "experiencia_profissional": doc.get("experiencia_profissional", ""),
        "fonte": doc.get("fonte", "email"),
        "data_criacao": doc.get("data_criacao", ""),
        "data_atualizacao": doc.get("data_atualizacao", ""),
    }
@app.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint de login
    
    Esperado:
    {
        "email": "admin@alcateia.com.br",
        "password": "admin123"
    }
    
    Retorna:
    {
        "success": true,
        "token": "jwt_token_aqui",
        "user": {
            "email": "admin@alcateia.com.br",
            "name": "Administrador"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Nenhum dado fornecido"
            }), 400
        
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        # Validação
        if not email or not password:
            return jsonify({
                "success": False,
                "error": "E-mail e senha são obrigatórios"
            }), 400
        
        if "@" not in email:
            return jsonify({
                "success": False,
                "error": "E-mail inválido"
            }), 400
        
        # Verificar credenciais
        if email not in USERS_DB:
            return jsonify({
                "success": False,
                "error": "E-mail ou senha incorretos"
            }), 401
        
        user_data = USERS_DB[email]
        if user_data["password"] != password:
            return jsonify({
                "success": False,
                "error": "E-mail ou senha incorretos"
            }), 401
        
        # Gerar token JWT
        token = generate_token(email)
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "email": email,
                "name": user_data["name"]
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Erro no login: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Erro ao processar login"
        }), 500

@app.route('/api/verify-token', methods=['POST'])
def verify():
    """
    Verifica se um token é válido
    
    Esperado:
    {
        "token": "jwt_token_aqui"
    }
    
    Retorna:
    {
        "success": true,
        "valid": true,
        "email": "admin@alcateia.com.br"
    }
    """
    try:
        data = request.get_json()
        token = data.get("token", "")
        
        if not token:
            return jsonify({
                "success": False,
                "valid": False
            }), 400
        
        payload = verify_token(token)
        
        if payload:
            return jsonify({
                "success": True,
                "valid": True,
                "email": payload.get("email")
            }), 200
        else:
            return jsonify({
                "success": False,
                "valid": False
            }), 401
    
    except Exception as e:
        print(f"❌ Erro ao verificar token: {str(e)}")
        return jsonify({
            "success": False,
            "valid": False
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Logout do usuário (apenas para limpeza no frontend)
    
    Retorna:
    {
        "success": true,
        "message": "Logout realizado com sucesso"
    }
    """
    return jsonify({
        "success": True,
        "message": "Logout realizado com sucesso"
    }), 200

# ============================================
# ENDPOINTS DE CANDIDATOS (PROTEGIDOS)
# ============================================

@app.route('/api/candidatos', methods=['GET'])
@token_required
def get_candidatos():
    """
    Retorna lista de candidatos
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Query parameters opcionais:
    - nome: Filtrar por nome
    - skill: Filtrar por skill
    
    Retorna:
    {
        "success": true,
        "data": [...],
        "total": 10
    }
    """
    try:
        handler = get_mongodb_handler()
        
        # Filtros opcionais
        nome = request.args.get('nome', '')
        skill = request.args.get('skill', '')
        


        # Buscar candidatos
        candidatos = handler.search_candidates(nome, skill)
        candidatos_serializados = [serialize_doc(c) for c in candidatos]
        
        return jsonify({
            'success': True,
            'data': candidatos_serializados,
            'total': len(candidatos_serializados)
        }), 200
    
    except Exception as e:
        print(f"❌ Erro ao buscar candidatos: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/estatisticas', methods=['GET'])
@token_required
def get_estatisticas():
    """
    Retorna estatísticas dos candidatos
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Retorna:
    {
        "success": true,
        "data": {
            "total": 10,
            "email": 7,
            "whatsapp": 3
        }
    }
    """
    try:
        handler = get_mongodb_handler()
        stats = handler.get_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    """
    Verifica se a API está funcionando
    
    Retorna:
    {
        "status": "ok",
        "message": "API Banco de Talentos está funcionando"
    }
    """
    return jsonify({
        "status": "ok",
        "message": "API Banco de Talentos está funcionando"
    }), 200

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Tratamento para rota não encontrada"""
    return jsonify({
        "success": False,
        "error": "Rota não encontrada"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Tratamento para erro interno do servidor"""
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor"
    }), 500

# ============================================
# INICIALIZAÇÃO
# ============================================

@app.route('/api/candidatos/<id>', methods=['GET'])
@token_required
def get_candidato_detail(id):
    """
    Retorna detalhes completos de um candidato
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Retorna:
    {
        "success": true,
        "data": {...}
    }
    """
    try:
        handler = get_mongodb_handler()
        candidato = handler.get_candidate_by_id(id)
        
        if candidato:
            return jsonify({
                'success': True,
                'data': serialize_doc(candidato)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Candidato não encontrado'
            }), 404
    
    except Exception as e:
        print(f"❌ Erro ao buscar candidato: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidatos/<id>', methods=['PUT'])
@token_required
def update_candidato(id):
    """
    Atualiza dados de um candidato
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Esperado:
    {
        "nome": "Novo Nome",
        "email": "novo@email.com",
        "telefone": "123456789",
        "endereco": "Novo Endereço",
        "skills": "Python, JavaScript",
        "formacao_academica": "Engenharia",
        "cursos_certificacoes": "Certificações",
        "nivel_ingles": "Fluente",
        "nivel_espanhol": "Intermediário",
        "experiencia_profissional": "10 anos",
        "linkedin": "https://linkedin.com/in/usuario"
    }
    
    Retorna:
    {
        "success": true,
        "message": "Candidato atualizado com sucesso",
        "data": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nenhum dado fornecido'
            }), 400
        
        handler = get_mongodb_handler()
        
        # Validações básicas
        if 'nome' in data and not data['nome'].strip():
            return jsonify({
                'success': False,
                'error': 'Nome não pode estar vazio'
            }), 400
        
        if 'email' in data and data['email'] and '@' not in data['email']:
            return jsonify({
                'success': False,
                'error': 'E-mail inválido'
            }), 400
        
        # Atualizar candidato
        resultado = handler.update_candidate(id, data)
        candidatos_serializados = serialize_doc(resultado)
        if resultado:
            return jsonify({
                'success': True,
                'message': 'Candidato atualizado com sucesso',
                'data': candidatos_serializados
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Candidato não encontrado'
            }), 404
    
    except Exception as e:
        print(f"❌ Erro ao atualizar candidato: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidatos/<id>', methods=['DELETE'])
@token_required
def delete_candidato(id):
    """
    Deleta um candidato
    
    Headers obrigatório:
    Authorization: Bearer <token_jwt>
    
    Retorna:
    {
        "success": true,
        "message": "Candidato deletado com sucesso"
    }
    """
    try:
        handler = get_mongodb_handler()
        resultado = handler.delete_candidate(id)
        
        if resultado:
            return jsonify({
                'success': True,
                'message': 'Candidato deletado com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Candidato não encontrado'
            }), 404
    
    except Exception as e:
        print(f"❌ Erro ao deletar candidato: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 API Banco de Talentos iniciada")
    print("="*60)
    print("\n📝 Endpoints disponíveis:\n")
    print("  🔓 POST /api/login")
    print("     Fazer login e obter token JWT\n")
    print("  🔒 GET /api/candidatos")
    print("     Listar todos os candidatos (requer token)\n")
    print("  🔒 GET /api/candidatos/<id>")
    print("     Detalhes de um candidato (requer token)\n")
    print("  🔒 GET /api/estatisticas")
    print("     Estatísticas dos candidatos (requer token)\n")
    print("  🔓 GET /api/health")
    print("     Health check da API\n")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)