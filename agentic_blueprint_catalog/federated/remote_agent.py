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
from academy.manager import Manager
from academy.agent import Agent, action
from academy.handle import Handle

from globus_compute_sdk import Executor as GlobusComputeExecutor
from academy.exchange.cloud import HttpExchangeFactory


EXCHANGE_ADDRESS = 'https://exchange.academy-agents.org'
logger = logging.getLogger(__name__)


class Orchestrator(Agent):
    def __init__(
        self,
        simulators: list[Handle[Simulator]],
    ) -> None:
        super().__init__()
        self.simulators = simulators

    @action
    async def process(self) -> float:
        estimates = []
        for sim_handle in self.simulators:
            estimate = await sim_handle.simulate_pi()
            estimates.append(estimate)

        return sum(estimates) / len(estimates)


class Simulator(Agent):
    @action
    async def simulate_pi(self, rounds=100) -> int:
        import random

        inside_circle = 0
        for _ in range(rounds):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            if x * x + y * y <= 1:
                inside_circle += 1

        return 4 * (inside_circle / rounds)


async def main():

    endpoint_uuid = 'bf06ab80-794a-4cb6-93f6-d5c71fb632d8'

    # Set up exchange for messaging between client and agents
    exchange = HttpExchangeFactory(
        url=EXCHANGE_ADDRESS,
        auth_method='globus',
    )

    with GlobusComputeExecutor(endpoint_id=endpoint_uuid) as remote_exec:
        # Create manager with agents and their assigned executors
        async with await Manager.from_exchange_factory(
            factory=exchange,
            executors=remote_exec,
        ) as manager:
            # Launch orchestrator and simulators. Each Orchestrator could link
            # with any number of simulators. To simplify a single simulator is used.
            handle_sim = await manager.launch(Simulator)
            handle_orc = await manager.launch(
                Orchestrator, args=([handle_sim],)
            )

            pi_estimate = await handle_orc.process()
            print(f'Orchestrator: pi_estimate: {pi_estimate}')
        remote_exec.shutdown(wait=True)


if __name__ == '__main__':
    print('Starting main')
    raise SystemExit(asyncio.run(main()))
