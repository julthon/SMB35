from nintendo.nex import settings, kerberos, common, prudp, rmc, \
    authentication, secure, utility, notification, messaging, \
    ranking2_eagle as ranking2, matchmaking_eagle as matchmaking
import itertools
import secrets
import config

class AuthenticationServer(authentication.AuthenticationServerNX):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.pid = itertools.count(1)

    async def validate_and_request_ticket_with_param(self, client, param):
        pid = next(self.pid)

        key = secrets.token_bytes(16)

        result = authentication.ValidateAndRequestTicketResult()
        result.pid = pid
        result.ticket = self.generate_ticket(pid, config.SERVER_PID, key, config.SERVER_KEY)
        result.server_url = common.StationURL(
            scheme="prudps", address="0.0.0.1", port=1,
            PID=config.SERVER_PID, CID=1, type=2,
            sid=2, stream=10
        )
        result.server_time = common.DateTime.now()
        result.server_name = "Super Mario Bros. 35"
        result.source_key = key.hex()
        return result

    def generate_ticket(self, user_pid, server_pid, user_key, server_key):
        session_key = secrets.token_bytes(32)

        internal = kerberos.ServerTicket()
        internal.timestamp = common.DateTime.now()
        internal.source = user_pid
        internal.session_key = session_key

        ticket = kerberos.ClientTicket()
        ticket.session_key = session_key
        ticket.target = server_pid
        ticket.internal = internal.encrypt(server_key, self.settings)
        return ticket.encrypt(user_key, self.settings)
