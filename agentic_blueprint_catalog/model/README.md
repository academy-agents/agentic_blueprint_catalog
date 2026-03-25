# Model Utilities

Utilities for loading and configuring LLM models with LangChain.

## Overview

The `model.py` module provides a factory function for loading OpenAI-compatible chat models. When no API configuration is present, it falls back to a fake model suitable for testing.

## Usage

```python
from agentic_blueprint_catalog.model.model import get_llm

# Returns configured ChatOpenAI or fake model for testing
llm = get_llm()

# Use with LangChain
response = llm.invoke("Hello, world!")
```

## Configuration

Create an `agents.env` file in the project root with your LLM settings:

```bash
# For OpenAI-compatible APIs (OpenAI, local Llama, vLLM, etc.)
OPENAI_API_BASE_URL=http://localhost:8000/v1
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_MODEL=llama-3.1-8b
OPENAI_API_KEY=your-api-key
```

### Supported Configurations

| Provider | Configuration |
|----------|--------------|
| OpenAI | Set `OPENAI_API_BASE_URL` and `OPENAI_API_KEY` |
| Local Llama | Point `OPENAI_BASE_URL` to your local server |
| vLLM | Use vLLM's OpenAI-compatible endpoint |
| Ollama | Use Ollama's OpenAI-compatible endpoint |

## Components

### `get_llm()`

Factory function that returns a LangChain chat model.

**Returns:** `BaseChatModel` - Either a configured `ChatOpenAI` or `ToolEnabledFakeChatModel`

**Behavior:**
- If `OPENAI_API_BASE_URL` is set: Returns `ChatOpenAI` configured with the environment variables
- Otherwise: Returns a fake model with pre-programmed responses for testing

### `ToolEnabledFakeChatModel`

A fake chat model that implements the `bind_tools` interface for testing tool-calling workflows without an actual LLM.

```python
from agentic_blueprint_catalog.model.model import ToolEnabledFakeChatModel

# Create with pre-programmed responses
fake_model = ToolEnabledFakeChatModel(messages=iter([
    AIMessage(content="Response 1"),
    AIMessage(content="Response 2"),
]))

# Supports tool binding (returns self)
bound_model = fake_model.bind_tools([my_tool])
```

### `calculate` Tool

A simple calculator tool included for testing tool-calling:

```python
from agentic_blueprint_catalog.model.model import calculate

result = calculate.invoke({"expression": "2 + 2"})
# Returns: "4"
```

**Security note:** Uses restricted `eval()` with no builtins for safety.

## Testing Without an LLM

When no API configuration is present, `get_llm()` returns a fake model with pre-programmed responses that demonstrate tool calling:

1. First call: Returns tool call for `calculate("347 * 892")`
2. Second call: Returns "347 * 892 is 309,524."
3. Third call: Returns tool call for `calculate("1500 - 847")`
4. Fourth call: Returns "You have 653 left."

This enables testing agent workflows without incurring API costs or requiring network access.
