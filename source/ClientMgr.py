from nintendo.nex import settings, kerberos, common, prudp, rmc, \
    authentication, secure, utility, notification, messaging, \
    ranking2_eagle as ranking2, matchmaking_eagle as matchmaking


class ClientMgr:
    def __init__(self):
        self.clients = {}

    def register(self, client):
        self.clients[client.pid()] = client

    def disconnect(self, client):
        pid = client.pid()
        if pid in self.clients:
            del self.clients[pid]

    async def send_message(self, pid, message):
        if pid in self.clients:
            client = messaging.MessageDeliveryClient(self.clients[pid])
            await client.deliver_message(message)

    async def send_notification(self, pid, event):
        if pid in self.clients:
            client = notification.NotificationClient(self.clients[pid])
            await client.process_notification_event(event)
