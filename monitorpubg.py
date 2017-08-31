from pypubg import core
from time import sleep
from slackclient import SlackClient


class PUBGPlayerMonitor:
    """
    PUBG Player Monitor
    """
    def __init__(self, season=None, pubg_api_key=None, players_monitored=None, slack_token=None, slack_channel=None):
        try:
            self.season = season
            self.pubg_api_key = pubg_api_key
            self.players_monitored = players_monitored
            self.slack_token = slack_token
            self.slack_channel = slack_channel
        except AttributeError as e:
            print("Variable not defined: {0}".format(e))
            raise

        self.api = core.PUBGAPI(pubg_api_key)
        self.player_match_history = self.collect_player_match_history()
        self.player_wins = self.collect_player_wins()

    def get_player_match_history(self, player_handle):
        """
        Retrieve all match history for a given player handle
        :param player_handle:
        :return: List of match history dictionaries
        """
        stats = self.api.player(player_handle)
        if stats:
            if stats.get('error'):
                print('Error getting stats for player: {0}. This player will be ignored'.format(player_handle))
                return None
            return stats['MatchHistory']
        else:
            print("No match history for player: {0}".format(player_handle))
            return None

    def get_player_wins(self, player_handle):
        """
        Retrieve aggregate match mode win statistics for a given player handle
        :param player_handle:
        :return: Dictionary
        """
        stats = self.api.player(player_handle).get('Stats')
        win_collection = dict()
        if stats:
            for region_stat in stats:
                if region_stat['Region'] == 'agg' and region_stat['Season'] == self.season:
                    for stat in region_stat['Stats']:
                        if stat['field'] == 'Wins':
                            win_collection[region_stat['Match']] = stat
            return win_collection
        else:
            print("No win stats for player: {0}".format(player_handle))
            return None

    def slack_message(self, channel, message):
        """
        Send a generic slack message
        :param message:
        :return:
        """
        try:
            sc = SlackClient(self.slack_token)
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=message)
        except Exception as e:
            print("Error making Slack call: {0}".format(e))
            raise

    def slack_new_wins(self, player, mode, new_win, mode_win_diff=None):
        """
        Update slack with new wins.
        :param player:
        :param mode:
        :param new_win:
        :param mode_win_diff:
        :return:
        """
        if not mode_win_diff:
            mode_win_diff = new_win.get('ValueInt')
        try:
            sc = SlackClient(self.slack_token)
            sc.api_call(
                "chat.postMessage",
                channel=self.slack_channel,
                text="{0} new win(s) detected for player {1}!\n"
                     "Season: {2}\n"
                     "Mode: {3}\n"
                     "Win Count: {4}\n"
                     "Latest Rank: {5}".format(mode_win_diff, player, self.season, mode, new_win['ValueInt'], new_win['rank'])
            )
        except Exception as e:
            print("Error making Slack call: {0}".format(e))
            raise

    def slack_new_match_history(self, player, match_history):
        """
        Update slack with new match history.
        :param player:
        :param match_history:
        :return:
        """
        try:
            sc = SlackClient(self.slack_token)
            sc.api_call(
                "chat.postMessage",
                channel=self.slack_channel,
                text="New match history detected for player {0}!\n"
                     "Season: {1}\n"
                     "Mode: {2}\n"
                     "Win Count: {3}\n"
                     "Kills: {4}\n"
                     "Top10: {5}\n"
                     "Mode Rating: {6}".format(player,
                                               match_history['SeasonDisplay'],
                                               match_history['MatchDisplay'],
                                               match_history['Wins'],
                                               match_history['Kills'],
                                               match_history['Top10'],
                                               match_history['Rating'])
            )
        except Exception as e:
            print("Error making Slack call: {0}".format(e))
            raise

    @staticmethod
    def _return_new_match_history(old_history, new_history):
        """
        Compare two match history dictionaries and return any new ones.
        :param old_history:
        :param new_history:
        :return:
        """
        new_match_history = []
        max_id = 0
        for old_match in old_history:
            if old_match['Id'] > max_id:
                max_id = old_match['Id']
        for new_match in new_history:
            if new_match['Id'] > max_id:
                new_match_history.append(new_match)
        return new_match_history

    def collect_player_match_history(self):
        """
        Collect match history for all players defined in settings.
        :return:
        """
        player_match_history = []
        for player in self.players_monitored:
            player_match_collection = {'player': player}
            sleep(1)
            match_history = self.get_player_match_history(player)
            if match_history:
                player_match_collection['match_history'] = match_history
                player_match_history.append(player_match_collection)
            else:
                print("")
                self.players_monitored.remove(player)
        return player_match_history

    def check_match_history(self):
        """
        Check if there are any new match histories avaialable for all players defined in settings.
        :return:
        """
        for player in self.player_match_history:
            old_history = player['match_history']
            sleep(1)
            new_history = self.get_player_match_history(player['player'])
            if not old_history == new_history and new_history:
                new_matches = self._return_new_match_history(old_history, new_history)
                for match in new_matches:
                    self.slack_new_match_history(player['player'], match)
                player['match_history'] = new_history

    def collect_player_wins(self):
        """
        Collect win statistics for all players defined in settings.
        :return:
        """
        player_wins = []
        for player in self.players_monitored:
            player_win_collection = {'player': player}
            sleep(1)
            wins = self.get_player_wins(player)
            if wins:
                player_win_collection['wins'] = wins
                player_wins.append(player_win_collection)
        return player_wins

    def check_player_wins(self):
        """
        Check if there are any new wins updated for all players defined in settings.
        :return:
        """
        for player in self.player_wins:
            old_wins = player['wins']
            sleep(1)
            recent_wins = self.get_player_wins(player['player'])
            if recent_wins:
                for mode in recent_wins:
                    try:
                        if old_wins[mode].get('ValueInt', 0) < recent_wins[mode].get('ValueInt', 0):
                            mode_win_diff = recent_wins[mode].get('ValueInt') - old_wins[mode].get('ValueInt')
                            self.slack_new_wins(player['player'], mode, recent_wins[mode], mode_win_diff=mode_win_diff)
                    except:
                        self.slack_new_wins(player['player'], mode, recent_wins[mode])
                player['wins'] = recent_wins
