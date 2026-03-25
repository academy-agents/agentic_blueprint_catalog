# Federated Deployment Patterns

Patterns for deploying agents to remote HPC systems using Globus Compute.

## Overview

These patterns demonstrate how to deploy agents from a local client to remote HPC resources. Both patterns use:

- **Globus Compute**: For remote function execution on HPC systems
- **Academy HttpExchange**: For message passing between client and remote agents
- **Globus Authentication**: For secure access to compute endpoints

## Pattern 1: Remote Agent (`remote_agent.py`)

The client explicitly launches both orchestrator and simulator agents to the remote system.

### Architecture

```
Step 1: Client launches all agents
+--------+      +----HPC System-----+
| Client |----+-|--> Orchestrator   |
+--------+    +-|--> Simulator      |
              + |      ...          |
              +-|--> Simulator      |
                +-------------------+

Step 2: Client interacts via Orchestrator
+--------+      +----HPC System-----+
| Client | <----|--> Orchestrator   |
+--------+      |    +-->Simulator  |
                |    +     ...      |
                |    +-->Simulator  |
                +-------------------+
```

### Key Characteristics

- Client has visibility into all agents
- Client manages the full agent topology
- Suitable when you need fine-grained control over agent deployment

### Usage

```python
from globus_compute_sdk import Executor as GlobusComputeExecutor
from academy.exchange.cloud import HttpExchangeFactory
from academy.manager import Manager

endpoint_uuid = 'your-endpoint-uuid'

exchange = HttpExchangeFactory(
    url='https://exchange.academy-agents.org',
    auth_method='globus',
)

with GlobusComputeExecutor(endpoint_id=endpoint_uuid) as remote_exec:
    async with await Manager.from_exchange_factory(
        factory=exchange,
        executors=remote_exec,
    ) as manager:
        # Launch simulator and orchestrator
        sim_handle = await manager.launch(Simulator)
        orc_handle = await manager.launch(Orchestrator, args=([sim_handle],))

        # Interact with orchestrator
        result = await orc_handle.process()
```

---

## Pattern 2: Remote Spawning Agent (`remote_spawning_agent.py`)

The client launches only an orchestrator, which then spawns its own sub-agents on startup.

### Architecture

```
Step 1: Client launches Orchestrator only
+--------+      +----HPC System-----+
| Client |------|--> Orchestrator   |
+--------+      +-------------------+

Step 2: Orchestrator spawns Simulators
+--------+      +----HPC System-----+
| Client |      | +  Orchestrator   |
+--------+      | +->Simulator      |
                | +     ...         |
                | +->Simulator      |
                +-------------------+

Step 3: Client interacts via Orchestrator
+--------+      +----HPC System-----+
| Client | <----|--> Orchestrator   |
+--------+      |    +-->Simulator  |
                |    +     ...      |
                |    +-->Simulator  |
                +-------------------+
```

### Key Characteristics

- Client only knows about the top-level orchestrator
- Sub-agents are an implementation detail hidden from the client
- Orchestrator manages its own worker pool
- Suitable for encapsulated, self-contained workflows

### Usage

```python
from globus_compute_sdk import Executor as GlobusComputeExecutor
from academy.exchange.cloud import HttpExchangeFactory
from academy.manager import Manager

endpoint_uuid = 'your-endpoint-uuid'

exchange = HttpExchangeFactory(
    url='https://exchange.academy-agents.org',
    auth_method='globus',
)

remote_executor = GlobusComputeExecutor(endpoint_id=endpoint_uuid)

async with await Manager.from_exchange_factory(
    factory=exchange,
    executors=remote_executor,
) as manager:
    # Launch only the orchestrator - it spawns its own simulators
    orc_handle = await manager.launch(Orchestrator)

    # Interact with orchestrator
    result = await orc_handle.process()

remote_executor.shutdown()
```

### Orchestrator Implementation

The spawning orchestrator creates its own manager and launches sub-agents in `agent_on_startup`:

```python
class Orchestrator(Agent):
    async def agent_on_startup(self) -> None:
        self._manager = await Manager.from_exchange_factory(
            executors=ProcessPoolExecutor(max_workers=4),
            factory=HttpExchangeFactory(
                'https://exchange.academy-agents.org',
                auth_method='globus'
            )
        )

        self.simulators = [
            await self._manager.launch(PI_Calculator),
            await self._manager.launch(PI_Calculator)
        ]

    async def agent_on_shutdown(self) -> None:
        await self._manager.close()
```

---

## Configuration

### Globus Compute Endpoint

You need a configured Globus Compute endpoint on your HPC system. See [Globus Compute documentation](https://globus-compute.readthedocs.io/) for setup instructions.

### Environment Variables

The examples use the Academy cloud exchange which requires Globus authentication:

```bash
# No explicit configuration needed - uses Globus OAuth flow
# First run will prompt for authentication
```

## When to Use Each Pattern

| Pattern | Use When |
|---------|----------|
| Remote Agent | You need visibility into all agents from the client |
| Remote Agent | You want to dynamically adjust the agent topology |
| Remote Agent | Testing/debugging individual agents |
| Remote Spawning | You want encapsulated, self-managing workflows |
| Remote Spawning | The internal agent structure is an implementation detail |
| Remote Spawning | You need simplified client code |
