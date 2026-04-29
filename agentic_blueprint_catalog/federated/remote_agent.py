"""Federated Agents example

This example demonstrates how to deploy an agent to a remote system using Globus Compute.
In this model, the Orchestrator and Simulator(s) are all launched onto an HPC system's
compute nodes via Globus Compute. In this model:

1. Client launches the orchestrator and simulator agents

    +--------+      +----HPC System-----+
    | Client |----+-|--> Orchestrator   |
    +--------+    +-|--> Simulator      |
                  + |      ...          |
                  +-|--> Simulator      |
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

from academy.agent import action
from academy.agent import Agent
from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.manager import Manager
from globus_compute_sdk import Executor as GlobusComputeExecutor

from agentic_blueprint_catalog.agents.pi_calculator import PiCalculator

EXCHANGE_ADDRESS = 'https://exchange.academy-agents.org'
logger = logging.getLogger(__name__)


class Orchestrator(Agent):
    def __init__(
        self,
        simulators: list[Handle[PiCalculator]],
    ) -> None:
        super().__init__()
        self.simulators = simulators

    @action
    async def process(self) -> float:
        """Average results from calls to multiple PiSimulators."""
        estimates = []
        for sim_handle in self.simulators:
            estimate = await sim_handle.simulate_pi()
            estimates.append(estimate)

        return sum(estimates) / len(estimates)


'''
class Simulator(Agent):
    @action
    async def simulate_pi(self, rounds: int = 100) -> float:
        """Simulate pi using monte carlo simulation"""
        inside_circle = 0
        for _ in range(rounds):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            if x * x + y * y <= 1:
                inside_circle += 1

        return 4 * (inside_circle / rounds)
'''


async def main() -> None:
    """Launch Orchestrator and Simulator agents."""
    endpoint_uuid = 'bf06ab80-794a-4cb6-93f6-d5c71fb632d8'

    with GlobusComputeExecutor(endpoint_id=endpoint_uuid) as remote_exec:
        # Create manager with agents and their assigned executors
        async with await Manager.from_exchange_factory(
            factory=HttpExchangeFactory(),
            executors=remote_exec,
        ) as manager:
            # Launch orchestrator and simulators. Each Orchestrator could link
            # with any number of simulators. To simplify a single simulator is used.
            handle_sims = [await manager.launch(PiCalculator), await manager.launch(PiCalculator)]
            handle_orc = await manager.launch(
                Orchestrator,
                args=(handle_sims,),
            )

            pi_estimate = await handle_orc.process()
            print(f'Orchestrator: pi_estimate: {pi_estimate}')
        remote_exec.shutdown(wait=True)


if __name__ == '__main__':
    print('Starting main')
    raise SystemExit(asyncio.run(main()))
