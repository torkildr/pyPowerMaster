#!/usr/bin/env python

import asyncio
from datetime import datetime

agent_url = "http://localhost:3052"

from PowerMaster import PowerMaster

def log(text):
    print(f"{datetime.now().isoformat()} {text}")

async def print_values():
    while True:
        try:
            log("connecting")
            pm = PowerMaster(agent_url)

            async for change in pm.subscribe():
                log(change)
        except:
            log("failed")
            await asyncio.sleep(3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_values())

