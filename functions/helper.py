import random


async def random_win():
    win = random.randint(0, 1)
    if win == 0:
        if random.randint(0, 2) == 0:
            return random.randrange(20000, 120000, 10000), 0
        else:
            return random.randrange(1000, 2200, 200), 0

    else:
        if random.randint(0, 2) == 0:
            return random.randrange(1500, 16500, 1500), 1
        else:
            return random.randrange(150, 900, 150), 1

    # else:
    #     if random.randint(0, 2) == 0:
    #         return random.randint(5, 16), 2
    #     else:
    #         return random.randint(3, 5), 2


async def promo_win():
    win = random.choice([True, False])
    if win:
        if random.choice([True, False]):
            return random.randrange(200000, 1200000, 200000), 0
        else:
            return random.randrange(20000, 220000, 20000), 0

    else:
        if random.choice([True, False]):
            return random.randrange(15000, 22500, 1500), 1
        else:
            return random.randrange(15000, 90000, 1500), 1
