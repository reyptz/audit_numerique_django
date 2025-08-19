import os
import time
import logging
from typing import Optional, Dict, Any

from django.conf import settings

from Audit_Numerique.models import Transaction

# Try the new langchain-openai package first, fall back for compatibility
try:
    # preferred: pip install -U langchain-openai
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:
    try:
        from langchain_community.chat_models import ChatOpenAI  # type: ignore
    except Exception:
        from langchain.chat_models import ChatOpenAI  # type: ignore

from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

# Optional: import openai exceptions to detect quota errors (if openai is installed)
try:
    import openai
    from openai.error import RateLimitError, OpenAIError  # type: ignore
except Exception:
    openai = None
    RateLimitError = Exception
    OpenAIError = Exception

logger = logging.getLogger(__name__)

# Ensure OPENAI_API_KEY available to underlying OpenAI client
if getattr(settings, "OPENAI_API_KEY", None):
    # prefer explicit set so underlying OpenAI client always sees it
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

# LLM cache keyed by (model_name, temperature)
_llm_cache: Dict[tuple, ChatOpenAI] = {}


def get_llm(temperature: float = 0.7, model_name: str = "gpt-3.5-turbo") -> ChatOpenAI:
    """
    Return a cached ChatOpenAI instance for given parameters, creating if needed.
    """
    key = (model_name, float(temperature))
    if key not in _llm_cache:
        logger.debug("Creating new ChatOpenAI instance: model=%s temperature=%s", model_name, temperature)
        _llm_cache[key] = ChatOpenAI(model_name=model_name, temperature=temperature)
    return _llm_cache[key]


def _extract_text_from_response(resp: Any) -> str:
    """
    Accept several possible shapes returned by various langchain versions and extract text.
    """
    # If the model returned a plain string
    if isinstance(resp, str):
        return resp

    # If the model returned a single AI message with .content
    if hasattr(resp, "content"):
        try:
            return resp.content  # type: ignore
        except Exception:
            pass

    # LLMResult with .generations -> nested list objects with .text
    if hasattr(resp, "generations"):
        gen = getattr(resp, "generations")
        try:
            # generations is list[list[Generation]]
            first = gen[0][0]
            if hasattr(first, "text"):
                return first.text  # type: ignore
            # some versions use .message.content
            if hasattr(first, "message") and hasattr(first.message, "content"):
                return first.message.content  # type: ignore
        except Exception:
            pass

    # As a last resort, try str()
    try:
        return str(resp)
    except Exception:
        return ""


def _call_llm_with_retries(llm: ChatOpenAI, messages: list, max_retries: int = 3) -> str:
    """
    Call the LLM with simple exponential backoff for rate-limit/quota errors.
    """
    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            # use the newer __call__ style: pass a list of HumanMessage for chat models
            resp = llm(messages)
            text = _extract_text_from_response(resp)
            return text
        except Exception as exc:
            # Detect common OpenAI rate limit/errors if openai package present
            is_rate_limit = isinstance(exc, RateLimitError) or (hasattr(exc, "code") and getattr(exc, "code") == "insufficient_quota")
            logger.warning("LLM call failed (attempt %s/%s): %s", attempt, max_retries, exc)
            if is_rate_limit:
                # If it's a quota/limit error, don't spam retries — wait and retry a few times
                if attempt == max_retries:
                    logger.exception("Rate limit / quota error after retries.")
                    raise
                time.sleep(backoff)
                backoff *= 2
                continue
            # For other errors, re-raise after logging
            logger.exception("Unexpected error calling LLM")
            raise


def chatbot_response(user_message: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7) -> str:
    """
    Return assistant response for a free-text user_message.
    """
    try:
        llm = get_llm(temperature=temperature, model_name=model_name)

        # build a short chat message — ChatPromptTemplate is fine but simpler here
        messages = [HumanMessage(content=f"Vous êtes un assistant utile. Répondez à l'utilisateur : {user_message}")]
        response_text = _call_llm_with_retries(llm, messages)
        return response_text
    except RateLimitError as rle:
        # Friendly message when quota is exceeded
        logger.exception("OpenAI quota/rate limit error")
        return "Erreur : quota OpenAI dépassé ou problème de facturation. Vérifiez votre clé API et votre plan (https://platform.openai.com/account/billing)."
    except Exception as exc:
        logger.exception("Error while generating chatbot response")
        return f"Une erreur est survenue lors de la génération de la réponse: {exc}"


def _transaction_to_dict(transaction: Transaction) -> Dict[str, Any]:
    """
    Convert a Django model instance to a plain dict (safe for prompts).
    Redacts common sensitive fields.
    """
    SENSITIVE_FIELDS = {"card_number", "pan", "cvv", "ssn", "password", "secret", "token"}
    data: Dict[str, Any] = {}
    for field in transaction._meta.fields:
        name = field.name
        try:
            value = getattr(transaction, name)
        except Exception:
            value = None
        if name.lower() in SENSITIVE_FIELDS:
            data[name] = "<redacted>"
        else:
            data[name] = value
    return data


def explain_anomaly(transaction_id: int, model_name: str = "gpt-3.5-turbo") -> str:
    """
    Ask the LLM to explain why a transaction is anomalous and give recommendations.
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        msg = f"Transaction with id={transaction_id} does not exist."
        logger.warning(msg)
        return msg

    transaction_data = _transaction_to_dict(transaction)

    prompt_template = (
        "Voici les détails d'une transaction anormale :\n\n{transaction}\n\n"
        "Explique pourquoi elle est marquée comme anormale et propose des recommandations pratiques et actionnables."
    )

    try:
        llm = get_llm(model_name=model_name)
        formatted = prompt_template.format(transaction=transaction_data)
        messages = [HumanMessage(content=formatted)]
        response_text = _call_llm_with_retries(llm, messages)
        return response_text
    except RateLimitError:
        logger.exception("OpenAI quota/rate limit error while explaining anomaly %s", transaction_id)
        return "Erreur : quota OpenAI dépassé ou problème de facturation lors de la génération de l'explication. Vérifiez votre clé API et votre plan."
    except Exception as exc:
        logger.exception("Error while explaining anomaly for transaction %s", transaction_id)
        return f"Une erreur est survenue lors de l'explication de l'anomalie: {exc}"