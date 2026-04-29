from __future__ import annotations

import random

from academy.agent import action
from academy.agent import Agent


class PiCalculator(Agent):
    """Pi Calculator Agent."""

    @action
    async def simulate_pi(self, rounds: int = 100) -> float:
        """Run monte-carlo simulation to estimate PI."""
        inside_circle = 0
        for _ in range(rounds):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            if x * x + y * y <= 1:
                inside_circle += 1

        return 4 * (inside_circle / rounds)
