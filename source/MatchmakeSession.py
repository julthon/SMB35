from nintendo.nex import common

from MatchmakeParticipant import MatchmakeParticipant


class MatchmakeSession:
    def __init__(self, session):
        self.session = session
        self.participants = {}

    def __check_value(self, value, check):
        if not check: return True

        if "," in check:
            start, end = check.split(",")
            return int(start) <= value <= int(end)

        values = [int(v) for v in check.split("|")]
        return value in values

    def __check_search_criteria(self, session, crit):
        for i in range(6):
            if not self.__check_value(session.attribs[i], crit.attribs[i]):
                return False
        if not self.__check_value(session.game_mode, crit.game_mode): return False
        if not self.__check_value(session.min_participants, crit.min_participants): return False
        if not self.__check_value(session.max_participants, crit.max_participants): return False
        if not self.__check_value(session.matchmake_system, crit.matchmake_system): return False
        if crit.vacant_only:
            if session.max_participants - session.num_participants < crit.vacant_participants:
                return False
        if crit.exclude_locked and not session.open_participation: return False
        if crit.exclude_user_password and session.user_password_enabled: return False
        if crit.exclude_system_password and session.system_password_enabled: return False
        if crit.codeword and session.codeword != crit.codeword: return False
        return True

    def check(self, crit):
        return self.__check_search_criteria(self.session, crit)

    def join(self, pid, message, participants):
        if pid in self.participants:
            raise common.RMCError("RendezVous::AlreadyParticipatedGathering")
        if not self.session.open_participation:
            raise common.RMCError("RendezVous::SessionClosed")
        if self.session.max_participants - self.session.num_participants < participants:
            raise common.RMCError("RendezVous::SessionFull")

        self.session.num_participants += participants

        participant = MatchmakeParticipant(pid, message, participants)
        self.participants[pid] = participant

    def leave(self, pid):
        if pid not in self.participants:
            raise common.RMCError("RendezVous::PermissionDenied")

        participant = self.participants.pop(pid)
        self.session.num_participants -= participant.participants
