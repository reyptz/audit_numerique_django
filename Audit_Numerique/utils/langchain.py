from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import os
from django.conf import settings

from Audit_Numerique.models import Transaction

# Configurer LangChain avec OpenAI
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

def chatbot_response(user_message):
    # Initialiser le modèle
    llm = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo')

    # Décrire le prompt
    prompt = ChatPromptTemplate.from_template(
        "Vous êtes un assistant utile. Répondez à l'utilisateur : {user_message}"
    )

    # Générer la réponse
    formatted_prompt = prompt.format(user_message=user_message)
    response = llm.predict(formatted_prompt)

    return response

def explain_anomaly(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    prompt = ChatPromptTemplate.from_template("""
        Voici les détails d'une transaction anormale : {transaction}.
        Explique pourquoi elle est marquée comme anormale et propose des recommandations.
    """)
    formatted_prompt = prompt.format(transaction=transaction)
    response = ChatOpenAI().predict(formatted_prompt)
    return response