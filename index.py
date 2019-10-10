#!/usr/bin/env python

import asyncio
from datetime import datetime, timezone
from influxdb import InfluxDBClient

agent_url = "http://localhost:3052"

from PowerMaster import PowerMaster
from util import deep_update

def log(text):
    print(f"{datetime.now().isoformat()} {text}")

def create_measurements(status):
    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    runtime = int(status['battery']['runtimeHour'])*60 + int(status['battery']['runtimeMinute'])

    return [
        {
            "time": timestamp,
            "measurement": "utility",
            "fields": {
                "frequency": float(status['utility']['frequency']),
                "voltage": float(status['utility']['voltage']),
                "warning": status['utility']['stateWarning'],
            },
            "tags": {
                "state": status['utility']['state'],
            },
        },
        {
            "time": timestamp,
            "measurement": "output",
            "fields": {
                "voltage": float(status['output']['voltage']),
                "frequency": float(status['output']['frequency']),
                "load": int(status['output']['load']),
                "watt": int(status['output']['watt']),
                "warning": status['output']['stateWarning'],
                "loadWarning": status['output']['outputLoadWarning'],
            },
            "tags": {
                "state": status['output']['state'],
            },
        },
        {
            "time": timestamp,
            "measurement": "battery",
            "fields": {
                "voltage": float(status['battery']['voltage']),
                "runtime": runtime,
                "capacity": int(status['battery']['capacity']),
                "warning": status['battery']['stateWarning'],
            },
            "tags": {
                "state": status['battery']['state'],
            },
        },
    ]

async def publish_values():
    db = None
    while True:
        try:
            pm = PowerMaster(agent_url)
            db = InfluxDBClient(database = "ups")
            active = False

            data = {}

            async for change in pm.subscribe():
                if not active:
                    active = True
                    log("connected")

                data = deep_update(data, change)
                log(data)
                measurements = create_measurements(data['status'])
                db.write_points(measurements)
        except Exception as e:
            print(type(e))
            print(e)
            try:
                db.close()
            except:
                pass
            await asyncio.sleep(3)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish_values())

