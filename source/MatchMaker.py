import base64
import hashlib
import hmac
import itertools
import json
import random
import time

from nintendo.nex import common, notification

import config
import eagle
from MatchmakeSession import MatchmakeSession


class MatchMaker:
    def __init__(self, clients, eagle):
        self.clients = clients
        self.eagle = eagle

        self.session_id = itertools.count(1)
        self.sessions = {}

    def get(self, gid):
        if gid not in self.sessions:
            raise common.RMCError("RendezVous::SessionVoid")
        return self.sessions[gid]

    def get_joined(self, gid, pid):
        session = self.get(gid)
        if pid not in session.participants:
            raise common.RMCError("RendezVous::PermissionDenied")
        return session

    async def send_notification(self, session, event):
        for pid in session.participants:
            await self.clients.send_notification(pid, event)

    async def create(self, session, pid):
        session.id = next(self.session_id)
        session.host = pid
        session.owner = pid
        session.started_time = common.DateTime.now()

        self.sessions[session.id] = MatchmakeSession(session)

        await self.eagle.start(session.id)

    async def destroy(self, session, pid):
        event = notification.NotificationEvent()
        event.pid = pid
        event.type = 109000
        event.param1 = session.session.id
        await self.send_notification(session, event)

        del self.sessions[session.session.id]
        await self.eagle.stop(session.session.id)

    async def join(self, gid, pid, message, participants):
        session = self.get(gid)
        session.join(pid, message, participants)

        event = notification.NotificationEvent()
        event.pid = pid
        event.type = 3001
        event.param1 = gid
        event.param2 = pid
        event.param3 = participants
        event.text = message

        await self.clients.send_notification(session.session.owner, event)

        payload = {
            "expires_at": "%i" % (time.time() + 10800),
            "server_env": "lp1",
            "server_id": "%i" % gid,
            "user_id": "%016x" % pid
        }

        signature = hmac.digest(
            eagle.SIGNATURE_KEY, json.dumps(payload).encode(),
            hashlib.sha256
        )

        token = json.dumps({
            "payload": payload,
            "signature": base64.b64encode(signature).decode(),
            "version": 1
        })

        event = notification.NotificationEvent()
        event.pid = config.SERVER_PID
        event.type = 200000
        event.param1 = gid
        event.map = {
            "url": "wss://smb35.ymar.dev:20001/%i" % gid,
            "token": base64.b64encode(token.encode()).decode()
        }

        await self.clients.send_notification(pid, event)

    async def leave(self, gid, pid, message="", disconnected=False):
        session = self.get(gid)
        session.leave(pid)

        if pid == session.session.owner:
            if session.session.flags & 0x10 and session.participants:
                await self.migrate(session)
            else:
                await self.destroy(session, pid)
        else:
            event = notification.NotificationEvent()
            event.pid = pid
            event.type = 3007 if disconnected else 3008
            event.param1 = session.session.id
            event.param2 = pid
            event.text = message

            await self.clients.send_notification(session.session.owner, event)

    async def migrate(self, session):
        new_owner = random.choice(list(session.participants))

        event = notification.NotificationEvent()
        event.type = 4000
        event.pid = session.session.owner
        event.param1 = session.session.id
        event.param2 = new_owner

        session.session.owner = new_owner

        await self.send_notification(session, event)

    async def disconnect(self, pid):
        for session in list(self.sessions.values()):
            if pid in session.participants:
                await self.leave(session.session.id, pid)

    def browse(self, search_criteria):
        sessions = []
        for session in self.sessions.values():
            if session.check(search_criteria):
                sessions.append(session.session)

        offset = search_criteria.range.offset
        if offset == 0xFFFFFFFF:
            offset = 0

        size = search_criteria.range.size
        return sessions[offset:offset + size]
