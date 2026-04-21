import os
import requests
from config.microsoft_graph import get_microsoft_graph

def enviar_email_resumo_graph(stats, total_candidatos):
    graph_config = get_microsoft_graph()
    headers = graph_config.get_headers()
    email_from = graph_config.get_email()
    emails_to = os.getenv("GRAPH_EMAIL_TO", email_from)

    url = f"https://graph.microsoft.com/v1.0/users/{email_from}/sendMail"

    corpo_html = f"""
    <h2>Resumo do Processamento</h2>
    <ul>
        <li>E-mails processados: {stats['emails_processados']}</li>
        <li>Arquivos processados: {stats['arquivos_processados']}</li>
        <li>Novos candidatos: {stats['novos_candidatos']}</li>
        <li>Atualizados: {stats['candidatos_atualizados']}</li>
        <li>Sem mudanças: {stats['sem_mudancas']}</li>
        <li>Erros: {stats['erros']}</li>
    </ul>
    <hr>
    <h3>Total geral: {total_candidatos}</h3>
    """
    to_recipients = [
        {"emailAddress": {"address": e.strip()}}
        for e in emails_to.split(",")
    ]
    payload = {
        "message": {
            "subject": "📊 Relatório Diário - Banco de Talentos",
            "body": {
                "contentType": "HTML",
                "content": corpo_html
            },
            "toRecipients": to_recipients
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 202:
        raise Exception(f"Erro ao enviar email: {response.text}")