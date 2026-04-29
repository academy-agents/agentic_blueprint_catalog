"""Federated Spawning Agents example.

This example builds on the Federated Remote agents example to demonstrate a case
where the remote agent is capable of spawning further agents.

In this model:

1. Client launches the orchestrator which then launches simulator agents.
   Client is unaware of simulator agents.

    Step 1.
    +--------+      +----HPC System-----+
    | Client |------|--> Orchestrator   |
    +--------+      +------------------ /

    Step 2.
    +--------+      +----HPC System-----+
    | Client |      | +  Orchestrator   |
    +--------+      | +->Simulator      |
                    | +     ...         |
                    | +->Simulator      |
                    +------------------ /

2. Client interacts with the Orchestrator which in turn interacts with the simulators
   to compute results

    +--------+      +----HPC System-----+
    | Client | <----|--> Orchestrator   |
    +--------+      |    +- ->Simulator |
                    |    +      ...     |
                    |    +--->Simulator |
                    +------------------ /
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor

from academy.agent import action
from academy.agent import Agent
from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.logging import init_logging
from academy.manager import Manager
from globus_compute_sdk import Executor as GlobusComputeExecutor

from agentic_blueprint_catalog.agents import PiCalculator

logger = logging.getLogger(__name__)


class Orchestrator(Agent):
    """An Orchestrator agent that launches and manages agents."""

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.simulators: list[Handle] = []

    async def agent_on_startup(self) -> None:
        """Spawn agents in own context."""
        # Using the ProcessPoolExecutor, the manager launches agents in separate processes
        # To launch agents across compute nodes in a batch job, or to interface
        # with the batch system consider using Parsl's ParlsExecutor
        self._manager = await Manager.from_exchange_factory(
            executors=ProcessPoolExecutor(max_workers=4),
            factory=HttpExchangeFactory(
                'https://exchange.academy-agents.org',
                auth_method='globus',
            ),
        )

        self.simulators = [
            await self._manager.launch(PiCalculator),
            await self._manager.launch(PiCalculator),
        ]

    async def agent_on_shutdown(self) -> None:
        """Shutdown agent."""
        await self._manager.close()

    @action
    async def process(self) -> float:
        """Call launched simulator agents to calculate pi."""
        estimates = []

        for sim_handle in self.simulators:
            estimate = await sim_handle.simulate_pi()
            estimates.append(estimate)

        return sum(estimates) / len(estimates)


async def main() -> None:
    """Launch Orchestrator agent."""
    init_logging(logging.INFO)
    endpoint_uuid = '0a6b732b-71ff-43b8-9537-017ad80eaadb'
    # endpoint_uuid = "0f0ab4d4-6878-4f2a-8106-e84fac7daa73"

    # Set up exchange for messaging between client and agents
    exchange = HttpExchangeFactory()

    # Globus Compute Executor for Polaris@ALCF
    remote_executor = GlobusComputeExecutor(endpoint_id=endpoint_uuid)

    # Create manager with agents and their assigned executors
    async with await Manager.from_exchange_factory(
        factory=exchange,
        executors=remote_executor,
    ) as manager:
        # Launch orchestrator and simulators. Each Orchestrator could link
        # with any number of simulators. To simplify a single simulator is used.
        handle_orc = await manager.launch(Orchestrator)

        pi_estimate = await handle_orc.process()
        logging.info(f'Pi Estimate from the orchestration: {pi_estimate}')

    remote_executor.shutdown()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
