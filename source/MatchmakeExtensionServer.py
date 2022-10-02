import random

from nintendo.nex import settings, kerberos, common, prudp, rmc, \
    authentication, secure, utility, notification, messaging, \
    ranking2_eagle as ranking2, matchmaking_eagle as matchmaking


class MatchmakeExtensionServer(matchmaking.MatchmakeExtensionServer):
    def __init__(self, matchmaker):
        super().__init__()
        self.matchmaker = matchmaker

    async def logout(self, client):
        await self.matchmaker.disconnect(client.pid())

    async def close_participation(self, client, gid):
        session = self.matchmaker.get_joined(gid, client.pid())
        session.session.open_participation = False

    async def auto_matchmake_with_param_postpone(self, client, param):
        if param.session.max_participants < param.num_participants:
            raise common.RMCError("Core::InvalidArgument")

        sessions = []
        for crit in param.search_criteria:
            sessions += self.matchmaker.browse(crit)

        if sessions:
            session = random.choice(sessions)
        else:
            await self.matchmaker.create(param.session, client.pid())
            session = param.session

        await self.matchmaker.join(session.id, client.pid(), param.join_message, param.num_participants)
        return session
