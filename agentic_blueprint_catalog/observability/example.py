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
from concurrent.futures import ProcessPoolExecutor

from academy.agent import action
from academy.agent import loop
from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.logging import init_logging
from academy.manager import Manager

from agentic_blueprint_catalog.observability.monitored_agent import MonitoredAgent
from agentic_blueprint_catalog.observability.user_agent import UserAgent


class Spinner(MonitoredAgent):
    """A concrete MonitoredAgent that does some work and reports progress."""

    def __init__(self, user_agent_handle: Handle[UserAgent]) -> None:
        super().__init__(user_agent_handle=user_agent_handle)
        print('Spinner init done')

    @action
    async def run(self, iterations: int = 3) -> str:
        """Simulate work and emit log messages that are forwarded to UserAgent."""
        logging.info('Starting run!')
        for i in range(iterations):
            logging.info(
                f'{self.agent_name} iteration %d/%d',
                i + 1,
                iterations,
            )
            await asyncio.sleep(10)
        logging.warning('Finishing run!')
        return f'Finished {iterations} iterations'

    @action
    async def poke(self) -> int:
        """Mock action that emits a log."""
        logging.warning('I just got Poked!')
        return 4

    @action
    async def trigger_user_query(self) -> None:
        """Trigger a user query."""
        logging.info('Triggering user query!')
        response = await self.prompt_user_agent(
            'Should I continue?',
            responses=['Yes', 'No'],
        )
        try:
            _ = 5 / 0
        except ZeroDivisionError:
            logging.exception('Something went wrong!')
        logging.info(f'Got response: {response} from user query')


class Sleeper(MonitoredAgent):
    """An Agent that sleeps."""

    def __init__(self, user_agent_handle: Handle[UserAgent]) -> None:
        super().__init__(user_agent_handle=user_agent_handle)
        print('Spinner init done')

    @loop
    async def cycle(self, shutdown: asyncio.Event) -> None:
        """Log and sleep in loop."""
        counter = 0
        while not shutdown.is_set():
            await asyncio.sleep(30)
            logging.info('Sleeper iteration %d', counter)
            counter += 1
        logging.info('Sleeper exiting!!!! ')


async def main(user_agent_id: str) -> None:
    """Launch MonitoredAgents."""
    init_logging(logging.INFO)

    async with await Manager.from_exchange_factory(
        factory=HttpExchangeFactory(),
        executors=ProcessPoolExecutor(max_workers=8),
    ) as manager:
        # 1. Launch UserAgent first so its handle can be passed to the worker.
        user_agent_handle = manager.get_handle(user_agent_id)

        # 2. Launch a few agents:
        spinner = await manager.launch(
            Spinner,
            kwargs={'user_agent_handle': user_agent_handle},
        )
        sleeper1 = await manager.launch(
            Sleeper,
            kwargs={'user_agent_handle': user_agent_handle},
        )
        sleeper2 = await manager.launch(
            Sleeper,
            kwargs={'user_agent_handle': user_agent_handle},
        )

        await spinner.trigger_user_query()
        handles = [spinner, sleeper1, sleeper2]

        # 3. Trigger work on the worker — log messages are forwarded automatically.
        await spinner.run(iterations=5)
        [handle.shutdown() for handle in handles]
        logging.info('All done!')


if __name__ == '__main__':
    with open('user_agent_handle.pkl', 'rb') as f:
        user_agent_id = pickle.load(f)
        raise SystemExit(asyncio.run(main(user_agent_id)))
