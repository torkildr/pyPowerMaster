#!/usr/bin/env python

import aiohttp
import json
import re

class PowerMaster():
    def __init__(self, base_url, username=None, password=None):
        self.base_url = base_url
        self.username = username
        self.password = password

    # strips down state object to only actual values
    def changed(self, data):
        changed_values = {}

        for key in data:
            if isinstance(data[key], dict):
                values = self.changed(data[key])
                if len(values) > 0:
                    changed_values[key] = values
            elif data[key] is not None:
                changed_values[key] = data[key]

        return changed_values

    async def websocket(self, session):
        async with session.ws_connect(f"{self.base_url}/agent/servlet/status_websocket", protocols=("status_websocket",)) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)['ppbe']['reply']
                    yield self.changed(data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    raise Exception(msg.data)

    async def initial(self, session):
        r = await session.get(f"{self.base_url}/agent/ppbe.js/init_status.js")
        payload = await r.text()

        status = json.loads(re.findall(r'var ppbeJsObj=(.*);', payload)[0])

        return self.changed(status)

    async def login(self, session):
        login_data = {
            "value(action)": "Login",
            "value(username)": self.username,
            "value(password)": self.password,
        }

        async with session.post(f"{self.base_url}/agent/index", data=login_data) as r:
            print(r.status)
            if r.status != 200:
                raise Exception("Login failed")
            return session

    # creates session, fetch initial state then subscribes to websocket
    async def subscribe(self):
        async with aiohttp.ClientSession() as session:
            if self.username and self.password:
                await self.login(session)

            yield await self.initial(session)

            async for state in self.websocket(session):
                yield state

