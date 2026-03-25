# Agentic Blueprint Catalog

A collection of reusable patterns and blueprints for building agentic systems, with a focus on high-performance computing (HPC) and federated deployment scenarios.

## Overview

This catalog provides production-ready examples demonstrating how to deploy AI agents across distributed computing environments using the [Academy](https://github.com/academy-agents/academy-py) agent framework. The blueprints address common challenges in scientific computing workflows, including:

- Deploying agents to remote HPC systems via Globus Compute
- Orchestrating parallel task execution with Parsl
- Coordinating multiple agents across compute nodes
- Hierarchical work distribution patterns

## Installation

```bash
pip install -e .
```

**Requirements:** Python 3.12+

## Catalog Structure

```
agentic_blueprint_catalog/
├── agents/              # Reusable agent implementations
│   ├── pi_calculator.py # Monte Carlo Pi estimation agent
│   └── director.py      # MD simulation orchestration agent
├── federated/           # Remote deployment patterns
│   ├── remote_agent.py          # Client-launched remote agents
│   └── remote_spawning_agent.py # Self-spawning remote agents
├── hpc_hierarchical/    # HPC batch job patterns
│   ├── minimal.py       # Simplified hierarchical example
│   ├── complete.py      # Production Aurora deployment
│   └── aurora.yaml.j2   # Globus Compute endpoint config
└── model/               # LLM integration utilities
    └── model.py         # OpenAI-compatible model loader
```

## Patterns

### 1. Federated Remote Agents

Deploy agents to HPC systems using Globus Compute, with the client orchestrating remote execution.

```
+--------+      +----HPC System-----+
| Client |----+-|--> Orchestrator   |
+--------+    +-|--> Simulator      |
              +-|--> Simulator      |
                +-------------------+
```

See [`federated/README.md`](agentic_blueprint_catalog/federated/README.md)

### 2. Remote Spawning Agents

Agents that dynamically spawn sub-agents on startup, enabling hierarchical orchestration where the client only interacts with a top-level coordinator.

See [`federated/README.md`](agentic_blueprint_catalog/federated/README.md)

### 3. HPC Hierarchical Tool Calling

Run multiple Director agents within a batch job, each managing a partition of compute nodes for parallel tool execution.

```
+---------------BATCH JOB-(4 Nodes)----------+
|  +-------Node0------+  +-------Node1------+|
|  | Director1 -----> PARSL POOL 1          ||
|  | Director2        |  |                  ||
|  +------------------+  +------------------+|
|  +-------Node2------+  +-------Node3------+|
|  |       ---------> PARSL POOL 2          ||
|  +------------------+  +------------------+|
+--------------------------------------------+
```

See [`hpc_hierarchical/README.md`](agentic_blueprint_catalog/hpc_hierarchical/README.md)

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `academy-py` | Agent framework for building and orchestrating agents |
| `globus-compute-sdk` | Remote execution on HPC systems |
| `parsl` | Parallel task execution and resource management |
| `langchain` | LLM integration and tool calling |

## Configuration

Copy and configure the environment file for LLM settings:

```bash
cp agents.env.example agents.env
```

For Globus Compute endpoints, see the configuration templates in `hpc_hierarchical/`.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
mypy .
```

## License

MIT License - see LICENSE for details.

## Authors

ModCon BASE Core Agentic Frameworks Team
