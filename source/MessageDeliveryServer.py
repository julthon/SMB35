from nintendo.nex import messaging, common


class MessageDeliveryServer(messaging.MessageDeliveryServer):
    def __init__(self, clients, matchmaker):
        super().__init__()
        self.clients = clients
        self.matchmaker = matchmaker

    async def deliver_message(self, client, message):
        message.sender = client.pid()
        message.sender_name = str(client.pid())
        message.reception_time = common.DateTime.now()
        if message.recipient.type == messaging.RecipientType.PRINCIPAL:
            await self.clients.send_message(message.recipient.pid)
        elif message.recipient.type == messaging.RecipientType.GATHERING:
            session = self.matchmaker.get_joined(message.recipient.gid, client.pid())
            for participant in session.participants:
                await self.clients.send_message(participant, message)
