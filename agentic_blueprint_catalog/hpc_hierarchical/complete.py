"""Demonstrate HPC scale Agent+Tool deployment on Aurora.

This example uses GlobusCompute on Aurora to launch Director agents on
the lead node of a 4 node batch job. The Directors partition the batch job
into even splits of 2 nodes each. Each Director uses Parsl to run a mock
md_sim_tool to tasks on.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime

from academy.exchange.cloud import HttpExchangeFactory
from academy.handle import Handle
from academy.logging import init_logging
from academy.manager import Manager
from globus_compute_sdk import Executor

from agentic_blueprint_catalog.agents.director import Director


async def main():
    """Use GlobusCompute to two Director agents onto a batch job."""
    init_logging(logging.INFO)
    exchange = HttpExchangeFactory(
        url='https://exchange.academy-agents.org', auth_method='globus',
    )
    executor = Executor(
        endpoint_id='9bfbd7a8-296e-4b57-8e7f-90e75ae581e7',
        user_endpoint_config={
            'nodes_per_block': 4,
        },
    )

    async with await Manager.from_exchange_factory(
        factory=exchange,
        executors=executor,
    ) as manager:
        logging.info('Starting directors')

        current_time = datetime.now()
        director1_handle: Handle = await manager.launch(
            Director, args=(
                os.path.abspath(f"{current_time.strftime('%H.%M.%S')}.00"),
                os.path.abspath('/tmp/node_slice.00'),
            ),
        )
        director2_handle: Handle = await manager.launch(
            Director, args=(
                os.path.abspath(f"{current_time.strftime('%H.%M.%S')}.01"),
                os.path.abspath('/tmp/node_slice.01'),
            ),
        )

        # Launch md_sim experiment campaigns over each director
        d1_task = asyncio.create_task(
            director1_handle.md_sim_batch(iterations=4),
        )
        d2_task = asyncio.create_task(
            director2_handle.md_sim_batch(iterations=4),
        )

        # Wait for all the results
        results = await asyncio.gather(d1_task, d2_task)

        # Now await the result
        for result in results:
            logging.warning(f'Experiment results: {result}')


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
