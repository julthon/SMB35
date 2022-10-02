import itertools

from nintendo.nex import matchmaking, common, notification


class MatchmakeRefereeServer(matchmaking.MatchmakeRefereeServer):
    def __init__(self, clients, matchmaker):
        super().__init__()
        self.clients = clients
        self.matchmaker = matchmaker

        self.round_id = itertools.count(1)
        self.rounds = {}

    async def start_round(self, client, param):
        if not param.pids: raise common.RMCError("Core::InvalidArgument")

        gathering = self.matchmaker.get(param.gid)
        if not gathering:
            raise common.RMCError("MatchmakeReferee::NotParticipatedGathering")

        for pid in param.pids:
            if pid not in gathering.participants:
                raise common.RMCError("MatchmakeReferee::NotParticipatedGathering")

        round_id = next(self.round_id)
        self.rounds[round_id] = param

        event = notification.NotificationEvent()
        event.pid = client.pid()
        event.type = 116000
        event.param1 = round_id
        for pid in param.pids:
            await self.clients.send_notification(pid, event)

        return round_id

    async def get_start_round_param(self, client, round_id):
        if round_id not in self.rounds:
            raise common.RMCError("MatchmakeReferee::RoundNotFound")
        return self.rounds[round_id]

    async def end_round(self, client, param):
        if param.round_id not in self.rounds:
            raise common.RMCError("MatchmakeReferee::RoundNotFound")

    async def end_round_with_partial_report(self, client, param):
        if param.round_id not in self.rounds:
            raise common.RMCError("MatchmakeReferee::RoundNotFound")
