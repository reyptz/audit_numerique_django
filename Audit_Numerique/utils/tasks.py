from celery import shared_task
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from Audit_Numerique.models import Transaction, Audit


@shared_task
def audit_transactions():
    # Configurer le modèle LangChain
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-3.5-turbo")

    transactions_to_audit = Transaction.objects.all().values()  # Exemple d'extraction
    prompt = ChatPromptTemplate.from_template("""
        Analyse ces transactions : {transactions} et détecte les anomalies.
    """)
    message = prompt.format(transactions=transactions_to_audit)
    anomalies = llm.predict(message)

    # Enregistrez les anomalies trouvées
    Audit.objects.create(details=anomalies)
    return anomalies