# Agents

Reusable agent implementations built on the Academy framework.

## PI_Calculator

A simple agent that uses the Monte Carlo method for calculating Pi ([Ref](https://en.wikipedia.org/wiki/Monte_Carlo_method))

### Usage

```python
from academy.manager import Manager
from agentic_blueprint_catalog.agents import PI_Calculator

async with manager:
    handle = await manager.launch(PI_Calculator)
    pi_estimate = await handle.simulate_pi(rounds=1000)
    print(f"Pi estimate: {pi_estimate}")
```

## Director

An orchestration agent for running molecular dynamics (MD) simulations in parallel using Parsl.
The `Director` uses Parsl's `HighThroughputExecutor` to provision and launch functions
on Aurora GPUs.

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

### Actions

| Action | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `md_sim` | None | `str` | Run a single MD simulation, returns hostname |
| `md_sim_batch` | `iterations=4` | `str` | Run multiple simulations in parallel |

### Lifecycle Hooks

- **`agent_on_startup`**: Initializes Parsl executor with the batch job configuration
- **`agent_on_shutdown`**: Cleans up Parsl resources
