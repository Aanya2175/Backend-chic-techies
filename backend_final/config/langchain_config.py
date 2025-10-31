import os, logging
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
LLM_AVAILABLE = False

def init_app():
    global LLM_AVAILABLE
    if OPENAI_KEY:
        try:
            from langchain import OpenAI
            LLM_AVAILABLE = True
            logging.info("LLM configured (OpenAI key found).")
        except Exception as e:
            logging.warning("LangChain/OpenAI not fully available: %s", e)
            LLM_AVAILABLE = False
    else:
        logging.info("No OPENAI_API_KEY found - LLM in MOCK mode.")
        LLM_AVAILABLE = False
