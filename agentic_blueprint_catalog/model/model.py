# Load model based on configuration set in the .env file at the project root
import os

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
import logging

load_dotenv(find_dotenv("agents.env"))
logger = logging.getLogger(__name__)

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Use this for any arithmetic."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

class ToolEnabledFakeChatModel(GenericFakeChatModel):
    """A fake model that implements bind_tools."""
    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, Callable, BaseTool]],
        **kwargs: Any
    ) -> Any:
        return self

def get_llm() -> BaseChatModel:
    """Load a chat model based on OpenAI API configs, failing that load a fake model"""

    if os.environ.get("OPENAI_API_BASE_URL"):
        model = os.environ["OPENAI_API_MODEL"]
        api_key = os.environ["OPENAI_API_KEY"]
        base_url = os.environ["OPENAI_BASE_URL"]
        chat_model = ChatOpenAI(model=model,
                           api_key=api_key,
                           base_url=base_url)
        logger.info(f"Loading {model=} from {base_url}")
    else:
        responses = [
            AIMessage(content="", tool_calls=[
                {"name": "calculate", "args": {"expression": "347 * 892"},
                 "id": "call_1"}]),
            AIMessage(content="347 * 892 is 309,524."),
            AIMessage(content="", tool_calls=[
                {"name": "calculate", "args": {"expression": "1500 - 847"},
                 "id": "call_2"}]),
            AIMessage(content="You have 653 left.")

        ]
        chat_model = ToolEnabledFakeChatModel(messages=iter(responses))
        logger.info("Loading a fake model for testing")

    return chat_model
