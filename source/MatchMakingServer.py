from nintendo.nex import matchmaking


class MatchMakingServer(matchmaking.MatchMakingServer):
    def __init__(self, matchmaker):
        super().__init__()
        self.matchmaker = matchmaker

    async def get_detailed_participants(self, client, gid):
        session = self.matchmaker.get_joined(gid, client.pid())

        participants = []
        for participant in session.participants.values():
            details = matchmaking.ParticipantDetails()
            details.pid = participant.pid
            details.name = str(participant.pid)
            details.message = participant.message
            details.participants = participant.participants
            participants.append(details)
        return participants


class MatchMakingServerExt(matchmaking.MatchMakingServerExt):
    def __init__(self, matchmaker):
        super().__init__()
        self.matchmaker = matchmaker

    async def end_participation(self, client, gid, message):
        await self.matchmaker.leave(gid, client.pid(), message)
        return True
