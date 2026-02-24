"""Director agent that runs MD sim tools in parallel."""
from __future__ import annotations

import asyncio
import os
import time

import parsl
from academy.agent import action
from academy.agent import Agent
from parsl import Config
from parsl import python_app
from parsl.executors import HighThroughputExecutor
from parsl.launchers import MpiExecLauncher
from parsl.providers import LocalProvider


@python_app
def md_sim_tool(duration: int = 10):
    """Simulate call to a Molecular Dynamics tool."""
    import platform  # noqa: PLC0415
    time.sleep(duration)
    return platform.uname().node


class Director(Agent):
    """Director agent that runs MD sim tools in parallel."""

    def __init__(self, run_dir: str, nodefile: str) -> None:
        """Initialize director."""
        super().__init__()
        self.run_dir = run_dir
        self.nodefile = nodefile
        self.executor = None

    async def agent_on_startup(self) -> None:
        """On startup, use Parsl as a task executor."""
        os.environ['PBS_NODEFILE'] = self.nodefile
        with open(self.nodefile) as f:
            nodes = f.readlines()
            num_nodes = len(nodes)

        config = Config(
            executors=[
                HighThroughputExecutor(
                    # Launch 12 workers per node each binding to a GPU tile
                    max_workers_per_node=12,
                    available_accelerators=12,

                    # Use local provider since we are running parsl inside
                    # provisioned batch job
                    provider=LocalProvider(
                        # Use mpiexec to launch workers across multiple node
                        launcher=MpiExecLauncher(
                            bind_cmd='--cpu-bind', overrides='--ppn 1',
                        ),
                        # Number of nodes per PBS job, setting to 2 in debug
                        nodes_per_block=num_nodes,
                        min_blocks=0,
                        max_blocks=1,
                    ),
                ),
            ],
            retries=1,
            run_dir=self.run_dir,
            # Disable logging for higher performance at >128 node scale
            initialize_logging=False,
        )
        self.dfk = parsl.load(config)

    @action
    async def md_sim(self):
        """md_sim is a blocking call executed by Parsl."""
        return await asyncio.wrap_future(md_sim_tool())

    @action
    async def md_sim_batch(self, iterations: int = 4):
        """Execute a batch of MD calls in parallel with parsl."""
        futures = [md_sim_tool() for _ in range(iterations)]
        # Wrap futures with asyncio
        wrapped_futures = [asyncio.wrap_future(fu) for fu in futures]
        results = await asyncio.gather(*wrapped_futures)
        return 'SIMS \n' + '\n'.join(results)

    async def agent_on_shutdown(self) -> None:
        """Cleanup parsl."""
        self.dfk.cleanup()
        self.dfk = None
        parsl.clear()
