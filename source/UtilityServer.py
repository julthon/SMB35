import itertools
import secrets

from nintendo.nex import utility, common

import config


class UtilityServer(utility.UtilityServer):
    def __init__(self):
        super().__init__()
        self.unique_id = itertools.count(1)
        self.associated_ids = {}

    async def acquire_nex_unique_id_with_password(self, client):
        info = utility.UniqueIdInfo()
        info.unique_id = next(self.unique_id)
        info.password = secrets.randbits(64)
        return info

    async def associate_nex_unique_id_with_my_principal_id(self, client, info):
        self.associated_ids[client.pid()] = info

    async def get_associated_nex_unique_id_with_my_principal_id(self, client):
        pid = client.pid()
        if pid in self.associated_ids:
            return self.associated_ids[pid]
        return utility.UniqueIdInfo()

    async def get_integer_settings(self, client, index):
        if index == 0: return config.INTEGER_SETTINGS1
        if index == 10: return config.INTEGER_SETTINGS2
        raise common.RMCError("Core::InvalidArgument")
