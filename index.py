#!/usr/bin/env python

import asyncio

agent_url = "http://localhost:3052"

from PowerMaster import PowerMaster

async def print_values():
    pm = PowerMaster(agent_url)

    async for change in pm.subscribe():
        print(change)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_values())

