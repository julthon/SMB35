from nintendo.nex import ranking2, common


class Ranking2Server(ranking2.Ranking2Server):
    def __init__(self):
        super().__init__()
        self.common_data = {}

    async def get_common_data(self, client, flags, pid, unique_id):
        data = self.common_data.get(pid, {})
        if unique_id not in data:
            raise common.RMCError("Ranking2::InvalidArgument")
        return data[unique_id]

    async def put_common_data(self, client, data, unique_id):
        pid = client.pid()
        if pid not in self.common_data:
            self.common_data[pid] = {}
        self.common_data[pid][unique_id] = data

    async def get_ranking(self, client, param):
        info = ranking2.Ranking2Info()
        info.data = []
        info.lowest_rank = 10000
        info.num_entries = 0
        info.season = 0
        return info

    async def get_category_setting(self, client, category):
        setting = ranking2.Ranking2CategorySetting()
        setting.min_score = 0
        setting.max_score = 999999999
        setting.lowest_rank = 10000
        setting.reset_month = 4095
        setting.reset_day = 0
        setting.reset_hour = 0
        setting.reset_mode = 2
        setting.max_seasons_to_go_back = 3
        setting.score_order = 1
        return setting

    async def get_estimate_my_score_rank(self, client, input):
        output = ranking2.Ranking2EstimateScoreRankOutput()
        output.rank = 0
        output.length = 0
        output.score = 0
        output.category = input.category
        output.season = 0
        output.sampling_rate = 0
        return output
