
# ai_server/bot_graph.py

import os
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger("GraphDispatcher")
provider = os.getenv("LLM_PROVIDER", "local").lower()

logger.info(f"Loading Graph for provider: {provider}")

if provider == "gemini":
    from gemini_bot_graph import app_graph
elif provider == "local":
    from local_bot_graph import app_graph
else:
    logger.warning(f"Unknown provider '{provider}', falling back to Local Graph")
    from local_bot_graph import app_graph
