# High Performance Tool Calling

Patterns for deploying agents within HPC batch jobs with hierarchical task distribution.

## Overview

This example demonstrates agents sharing nodes within a batch job to drive expensive MD simulations via tool calling. The focus is on infrastructure setup for resource sharing rather than the simulation logic itself.

## Files

| File | Description |
|------|-------------|
| `minimal.py` | Simplified example using `ProcessPoolExecutor` |
| `complete.py` | Production example for Aurora@ALCF with Globus Compute |
| `aurora.yaml.j2` | Globus Compute endpoint config template |
| `../agents/director.py` | Director agent with Parsl-based task execution |

## Architecture

The pattern uses a hierarchical approach:

1. **Two Director agents** launched via Globus Compute to the lead node of a 4-node batch job
2. **Logical partitioning** divides the 4 nodes into 2 partitions of 2 nodes each
3. **Each Director** owns one partition and uses Parsl for parallel task execution

### Step 1: Launch Directors onto Lead Node

```
+-----------------------------AURORA@ANL------------------------------+
+   +------------+   +---------------BATCH JOB-(4 Nodes)----------+   |
+   | GCompute --+-->+  +-------Node0------+ +-------Node1------+ |   |
+   +------------+   |  | Director1        | |                  | |   |
+                    |  | Director2        | |                  | |   |
+                    |  +------------------+ +------------------+ |   |
+                    |                                            |   |
+                    |  +-------Node2------+ +-------Node3------+ |   |
+                    |  |                  | |                  | |   |
+                    |  |                  | |                  | |   |
+                    |  +------------------+ +------------------+ |   |
+-----------------------------AURORA@ANL------------------------------+
```

### Step 2: Each Director Manages a Parsl Pool

```
+-----------------------------AURORA@ANL------------------------------+
+   +------------+   +---------------BATCH JOB-(4 Nodes)----------+   |
+   | GCompute --+-->+  +-------Node0------+ +-------Node1------+ |   |
+   +------------+   |  | D1---> +------PARSL POOL 1--------+   | |   |
+                    |  | D2     +--------------------------+   | |   |
+                    |  +--+---------------+ +------------------+ |   |
+                    |     |                                      |   |
+                    |  +--+----Node2------+ +-------Node3------+ |   |
+                    |  |  +---> +------PARSL POOL 2--------+   | |   |
+                    |  |        +--------------------------+   | |   |
+                    |  +------------------+ +------------------+ |   |
+-----------------------------AURORA@ANL------------------------------+
```

## Usage

### Minimal Example

The simplified example uses `ProcessPoolExecutor` locally:

```bash
python -m agentic_blueprint_catalog.hpc_hierarchical.minimal
```

```python
from concurrent.futures import ProcessPoolExecutor
from academy.manager import Manager

executor = ProcessPoolExecutor(max_workers=2)

async with await Manager.from_exchange_factory(
    factory=exchange,
    executors=executor,
) as manager:
    director1 = await manager.launch(Director)
    director2 = await manager.launch(Director)

    # Run simulations concurrently
    task1 = asyncio.create_task(director1.md_sim())
    task2 = asyncio.create_task(director2.md_sim())
    results = await asyncio.gather(task1, task2)
```

### Production Example (Aurora)

The complete example uses Globus Compute with a 4-node batch job:

```bash
python -m agentic_blueprint_catalog.hpc_hierarchical.complete
```

```python
from globus_compute_sdk import Executor
from agentic_blueprint_catalog.agents.director import Director

executor = Executor(
    endpoint_id='your-endpoint-uuid',
    user_endpoint_config={'nodes_per_block': 4},
)

async with await Manager.from_exchange_factory(
    factory=exchange,
    executors=executor,
) as manager:
    # Each director gets a nodefile pointing to its partition
    director1 = await manager.launch(
        Director, args=(run_dir_1, '/tmp/node_slice.00')
    )
    director2 = await manager.launch(
        Director, args=(run_dir_2, '/tmp/node_slice.01')
    )

    # Run batch simulations on each partition
    results = await asyncio.gather(
        director1.md_sim_batch(iterations=4),
        director2.md_sim_batch(iterations=4),
    )
```

## Globus Compute Endpoint Configuration

The `aurora.yaml.j2` template configures a Multi-Endpoint (MEP) for Aurora@ALCF:

```bash
# Copy to your endpoint config directory
cp aurora.yaml.j2 ~/.globus_compute/<MEP>/user_config_template.yaml.j2
```

Key configuration points:
- Uses PBS scheduler with `qsub` commands
- Requests nodes with Intel GPUs
- Sets up the appropriate conda environment
- Configures node partitioning for multiple Directors

## Prerequisites

- Globus Compute endpoint configured on your HPC system
- Academy exchange access (uses Globus authentication)
- For Aurora: access to ALCF and appropriate allocations

## Key Concepts

### Node Partitioning

The nodefile is split to give each Director exclusive access to a subset of nodes:

```python
# Director 1 gets nodes 0-1
# Director 2 gets nodes 2-3
```

### Parsl Configuration

Each Director configures Parsl's `HighThroughputExecutor`:
- 12 workers per node (matching Aurora's GPU tiles)
- `MpiExecLauncher` for cross-node worker distribution
- Logging disabled for performance at scale (>128 nodes)

### Concurrent Execution

Use `asyncio.create_task()` to run Director operations concurrently:

```python
task1 = asyncio.create_task(director1.md_sim_batch())
task2 = asyncio.create_task(director2.md_sim_batch())
results = await asyncio.gather(task1, task2)
```

