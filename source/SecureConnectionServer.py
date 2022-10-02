import itertools

from nintendo.nex import secure, rmc, common


class SecureConnectionServer(secure.SecureConnectionServer):
    def __init__(self, clients):
        super().__init__()
        self.clients = clients

        self.connection_id = itertools.count(1)

    async def logout(self, client):
        self.clients.disconnect(client)

    async def register(self, client, urls):
        address, port = client.remote_address()

        response = rmc.RMCResponse()
        response.result = common.Result.success()
        response.connection_id = next(self.connection_id)
        response.public_station = common.StationURL(
            scheme="prudp", address=address, port=port,
            natf=0, natm=0, pmp=0, upnp=0, Tpt=2,
            type=11, sid=client.remote_sid()
        )

        self.clients.register(client)
        return response
