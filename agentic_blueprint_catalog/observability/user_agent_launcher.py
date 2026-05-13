"""Launch the User Agent in local threads and wait."""

from __future__ import annotations

import argparse
import asyncio
import pickle
from concurrent.futures import ThreadPoolExecutor

from academy.exchange.cloud.client import HttpExchangeFactory
from academy.logging import init_logging
from academy.manager import Manager

from agentic_blueprint_catalog.observability.user_agent import UserAgent


async def launch(port: int) -> None:
    """Launch UserAgent in ThreadPoolExecutor and write handle info to file."""
    init_logging()

    async with await Manager.from_exchange_factory(
        factory=HttpExchangeFactory(),
        executors=ThreadPoolExecutor(max_workers=4),
    ) as manager:
        agent_hdl = await manager.launch(UserAgent, kwargs={'port': port})
        print(f'User Agent Handle >>>> {agent_hdl.agent_id.uid!s}')

        with open('user_agent_handle.pkl', 'wb') as f:
            pickle.dump(agent_hdl.agent_id, f)
        await manager.wait([agent_hdl], raise_error=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='Port at which the flask service is listening')
    parser.add_argument('-u', '--user_agent_id', help='User Agent will use this ID if specified')
    args = parser.parse_args()
    asyncio.run(launch(port=args.port))
