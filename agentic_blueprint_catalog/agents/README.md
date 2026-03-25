# Agents

Reusable agent implementations built on the Academy framework.

## PI_Calculator

A simple agent demonstrating Monte Carlo simulation for estimating Pi.

### How It Works

The agent uses the random point-in-circle method:
1. Generate random (x, y) points in a 2x2 square centered at origin
2. Count points that fall inside the unit circle (x² + y² ≤ 1)
3. Estimate π ≈ 4 × (points inside circle / total points)

### Usage

```python
from academy.manager import Manager
from agentic_blueprint_catalog.agents import PI_Calculator

async with manager:
    handle = await manager.launch(PI_Calculator)
    pi_estimate = await handle.simulate_pi(rounds=1000)
    print(f"Pi estimate: {pi_estimate}")
```

### Actions

| Action | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `simulate_pi` | `rounds=100` | `float` | Estimate Pi using Monte Carlo simulation |

---

## Director

An orchestration agent for running molecular dynamics (MD) simulations in parallel using Parsl.

### How It Works

The Director agent:
1. On startup, configures a Parsl `HighThroughputExecutor` across allocated batch job nodes
2. Exposes actions to run MD simulation tools either individually or in batches
3. Uses `MpiExecLauncher` to distribute workers across nodes
4. Manages GPU tile binding (12 workers per node for Aurora's Intel GPUs)

### Usage

```python
from agentic_blueprint_catalog.agents.director import Director

# Initialize with run directory and PBS nodefile
director = Director(
    run_dir="/path/to/run/directory",
    nodefile="/path/to/pbs/nodefile"
)

# Within a manager context
handle = await manager.launch(Director, args=(run_dir, nodefile))

# Run a single simulation
result = await handle.md_sim()

# Run a batch of simulations in parallel
results = await handle.md_sim_batch(iterations=4)
```

### Configuration

The Director reads the PBS nodefile to determine available nodes and configures Parsl accordingly:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_workers_per_node` | 12 | Workers per node (matches GPU tiles on Aurora) |
| `available_accelerators` | 12 | GPU tiles available per node |
| `nodes_per_block` | Auto | Read from nodefile |
| `initialize_logging` | False | Disabled for performance at scale |

### Actions

| Action | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `md_sim` | None | `str` | Run a single MD simulation, returns hostname |
| `md_sim_batch` | `iterations=4` | `str` | Run multiple simulations in parallel |

### Lifecycle Hooks

- **`agent_on_startup`**: Initializes Parsl executor with the batch job configuration
- **`agent_on_shutdown`**: Cleans up Parsl resources

### Requirements

- Running within a PBS batch job with allocated nodes
- PBS_NODEFILE environment variable or explicit nodefile path
- Parsl and MPI available in the environment
