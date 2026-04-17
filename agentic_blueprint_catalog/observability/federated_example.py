"""Example: launch a UserAgent and a MonitoredAgent and exchange messages.

Architecture:

    +---------------+        messages        +------------+
    | MonitoredAgent| ---------------------->| UserAgent  |
    |  (worker)     |   receive_message()    |            |
    +---------------+                        +------------+
          |                                        |
          | logging.info / agent.log()             | get_messages()
          v                                        v
     forwarded automatically              inspect from client

Both agents run inside a local ProcessPoolExecutor so no remote
infrastructure is required to run this example.
"""

from __future__ import annotations

import asyncio
import logging
import pickle

# from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

from academy.agent import action
from academy.agent import loop
from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.logging import init_logging
from academy.manager import Manager

from globus_compute_sdk import Executor as GlobusExecutor
from agentic_blueprint_catalog.observability.example import Spinner
from agentic_blueprint_catalog.observability.example import Sleeper


async def main(user_agent_id: str) -> None:
    init_logging(logging.INFO)

    nersc = GlobusExecutor(endpoint_id="07b73b75-d534-428f-acd8-003b01a166f5")
    local = ProcessPoolExecutor(max_workers=4)

    async with await Manager.from_exchange_factory(
        factory=HttpExchangeFactory(),
        executors={
            'nersc': nersc,
            'local': local
        }
    ) as manager:
        # 1. Launch UserAgent first so its handle can be passed to the worker.
        user_agent_handle = manager.get_handle(user_agent_id)

        # 2. Launch a few agents:
        spinner = await manager.launch(
            Spinner,
            kwargs={'user_agent_handle': user_agent_handle},
            executor='nersc',
        )
        sleeper = await manager.launch(
            Sleeper,
            kwargs={'user_agent_handle': user_agent_handle},
            executor='local',
        )

        await spinner.trigger_user_query()
        handles = [spinner, sleeper]

        # 3. Trigger work on the worker — log messages are forwarded automatically.
        await spinner.run(iterations=5)
        logging.info('All done!')


if __name__ == '__main__':
    with open('user_agent_handle.pkl', 'rb') as f:
        user_agent_id = pickle.load(f)
        raise SystemExit(asyncio.run(main(user_agent_id)))
