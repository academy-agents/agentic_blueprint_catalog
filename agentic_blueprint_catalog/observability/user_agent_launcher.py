"""Launch the User Agent in local threads and wait"""

from __future__ import annotations

import asyncio
import pickle
from concurrent.futures import ThreadPoolExecutor

from academy.exchange.cloud.client import HttpExchangeFactory
from academy.logging import init_logging
from academy.manager import Manager

from agentic_blueprint_catalog.observability.user_agent import UserAgent


async def launch() -> None:
    init_logging()

    async with await Manager.from_exchange_factory(
        factory=HttpExchangeFactory(),
        executors=ThreadPoolExecutor(max_workers=4),
    ) as manager:
        agent_hdl = await manager.launch(UserAgent)
        print(f'User Agent Handle >>>> {agent_hdl.agent_id.uid!s}')

        with open('user_agent_handle.pkl', 'wb') as f:
            pickle.dump(agent_hdl.agent_id, f)
        await manager.wait([agent_hdl], raise_error=True)


if __name__ == '__main__':
    asyncio.run(launch())
