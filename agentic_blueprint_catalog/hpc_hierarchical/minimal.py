"""Simplified example of hierarchical Agent+Tool deployment.

This is a simplified example that demonstrates the overall hierarchical pattern
or work distribution.
"""

from __future__ import annotations

import asyncio
import logging
import platform
from concurrent.futures import ProcessPoolExecutor

from academy.agent import action
from academy.agent import Agent
from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.logging import init_logging
from academy.manager import Manager


def md_sim_tool(duration: int = 10):
    """Simulate call to an Molecular Dynamics tool."""
    return platform.uname().node


class Director(Agent):
    """Director agent that runs an MD sim tool."""

    async def agent_on_startup(self) -> None:
        """On startup, use ProcessPoolExecutor."""
        self.executor = ProcessPoolExecutor(max_workers=4)

    @action
    async def md_sim(self, iterations: int = 4):
        """Run expensive MD sim task with Parsl."""
        future = self.executor.submit(md_sim_tool)
        return await asyncio.wrap_future(future)

    async def agent_on_shutdown(self) -> None:
        """Cleanup."""
        self.executor.shutdown()


async def main():
    """Launch agents in a Process Pool."""
    init_logging(logging.INFO)
    exchange = HttpExchangeFactory(
        url='https://exchange.academy-agents.org', auth_method='globus',
    )
    executor = ProcessPoolExecutor(max_workers=2)

    async with await Manager.from_exchange_factory(
        factory=exchange,
        executors=executor,
    ) as manager:
        logging.info('Starting directors')

        director1_handle: Handle = await manager.launch(Director)
        director2_handle: Handle = await manager.launch(Director)

        # Use asyncio.create_task to start the long-running md_sim
        # operations so that each call executes concurrently.
        task1 = asyncio.create_task(director1_handle.md_sim())
        task2 = asyncio.create_task(director2_handle.md_sim())

        # Now await all the results
        results = await asyncio.gather(task1, task2)

        for result in results:
            logging.info(f'Experiment results: {result}')


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
