from academy.agent import Agent
from academy.agent import action


class PI_Calculator(Agent):

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