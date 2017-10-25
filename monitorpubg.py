from pypubg import core
from time import sleep
from slackclient import SlackClient
import json


class PUBGPlayerMonitor:
    """
    PUBG Player Monitor
    """
    def __init__(self, pubg_api_key=None, players_monitored=None, slack_token=None, slack_channel=None):
        try:
            self.pubg_api_key = pubg_api_key
            self.players_monitored = players_monitored
            self.slack_token = slack_token
            self.slack_channel = slack_channel
        except AttributeError as e:
            print("Variable not defined: {0}".format(e))
            raise

        self.api = core.PUBGAPI(pubg_api_key)
        # self.player_match_history = self.collect_player_match_history()
        self.player_wins = self.collect_player_wins()
        self.player_agg_stats = self.collect_player_agg_stats()

    def get_player_match_history(self, player_handle):
        """
        Retrieve all match history for a given player handle
        :param player_handle:
        :return: List of match history dictionaries
        """
        try:
            stats = self.api.player(player_handle)
            if stats:
                if stats.get('MatchHistory'):
                    return stats.get('MatchHistory')
                else:
                    print('Error getting stats for player: {0}. This player will be ignored\n{1}'.format(player_handle, stats))
                    return None
            else:
                print("No match history for player: {0}".format(player_handle))
                return None
        except json.JSONDecodeError:
            print("JSON Decoding error")

    def get_player_wins(self, player_handle):
        """
        Retrieve aggregate match mode win statistics for a given player handle
        :param player_handle:
        :return: Dictionary
        """
        try:
            player = self.api.player(player_handle)
            if player:
                stats = player.get('Stats')
                season = player.get('defaultSeason')
                if stats:
                    win_collection = dict()
                    for region_stat in stats:
                        if region_stat['Region'] == 'agg' and region_stat['Season'] == season:
                            for stat in region_stat['Stats']:
                                if stat['field'] == 'Wins':
                                    win_collection[region_stat['Match']] = stat
                    return win_collection
            else:
                print("No win stats for player: {0}".format(player_handle))
                return None
        except json.JSONDecodeError:
            print("JSON Decoding error")
        except Exception as e:
            print("Error getting player wins: {0}".format(str(e)))

    def get_player_agg_stats(self, player_handle):
        """
        Retrieve aggregate match mode win statistics for a given player handle
        :param player_handle:
        :return: Dictionary
        """
        try:
            player = self.api.player(player_handle)
            if player:
                stats = player.get('Stats')
                season = player.get('defaultSeason')
                if stats:
                    stat_collection = {
                        'wins': dict(),
                        'kills': dict(),
                    }
                    for region_stat in stats:
                        if region_stat['Region'] == 'agg' and region_stat['Season'] == season:
                            for stat in region_stat['Stats']:
                                if stat['field'] == 'Wins':
                                    stat_collection['wins'][region_stat['Match']] = stat
                                if stat['field'] == 'Kills':
                                    stat_collection['kills'][region_stat['Match']] = stat
                    return stat_collection
            else:
                print("No win stats for player: {0}".format(player_handle))
                return None
        except json.JSONDecodeError:
            print("JSON Decoding error")
        except Exception as e:
            print("Error getting player wins: {0}".format(str(e)))

    def slack_message(self, channel, message):
        """
        Send a generic slack message
        :param channel:
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
                     "Mode: {2}\n"
                     "Win Count: {3}\n"
                     "Latest Rank: {4}".format(mode_win_diff, player, mode, new_win['ValueInt'], new_win['rank'])
            )
        except Exception as e:
            print("Error making Slack call: {0}".format(e))
            raise

    def slack_new_agg_wins(self, new_wins=None, player=None, mode=None, win_count=None, kills=None, kill_count=None):
        """
        Update slack with new wins.
        :param new_wins:
        :param player:
        :param mode:
        :param win_count:
        :param kills:
        :return:
        """
        try:
            sc = SlackClient(self.slack_token)
            sc.api_call(
                "chat.postMessage",
                channel=self.slack_channel,
                text="{0} new win(s) detected for player {1}!\n"
                     "Kills: {4}\n"
                     "Mode: {2}\n"
                     "Total Win Count: {3}\n"
                     "Total Kill Count:{5}".format(new_wins, player, mode, win_count, kills, kill_count)
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
                channel='#pubgtrackerbot',
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
            sleep(5)
            match_history = self.get_player_match_history(player)
            if match_history:
                player_match_collection['match_history'] = match_history
                player_match_history.append(player_match_collection)
            else:
                self.players_monitored.remove(player)
        return player_match_history

    def check_match_history(self):
        """
        Check if there are any new match histories avaialable for all players defined in settings.
        :return:
        """
        for player in self.player_match_history:
            old_history = player['match_history']
            sleep(5)
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

    def collect_player_agg_stats(self):
        """
        Collect statistics for all players defined in settings.
        :return:
        """
        player_wins = []
        for player in self.players_monitored:
            player_stat_collection = {'player': player}
            sleep(1)
            stats = self.get_player_agg_stats(player)
            player_stat_collection['stats'] = stats
            player_wins.append(player_stat_collection)
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

    def check_player_agg_wins(self):
        """
        Check if there are any new wins updated for all players defined in settings.
        :return:
        """
        for player in self.player_agg_stats:
            old_stats = player['stats']
            sleep(1)
            recent_stats = self.get_player_agg_stats(player['player'])
            if recent_stats:
                for mode in recent_stats['wins']:
                    try:
                        if old_stats['wins'][mode].get('ValueInt', 0) < recent_stats['wins'][mode].get('ValueInt', 0):
                            mode_win_diff = recent_stats['wins'][mode].get('ValueInt', 0) - old_stats['wins'][mode].get('ValueInt', 0)
                            kills_diff = recent_stats['kills'][mode].get('ValueInt', 0) - old_stats['kills'][mode].get('ValueInt', 0)
                            self.slack_new_agg_wins(
                                new_wins=mode_win_diff,
                                player=player['player'],
                                mode=mode,
                                win_count=recent_stats['wins'][mode].get('ValueInt', 0),
                                kills=kills_diff,
                                kill_count=recent_stats['kills'][mode].get('ValueInt', 0)
                            )
                    except Exception as e:
                        print("Exception from trying to parse new wins/stats: {0}".format(str(e)))
                player['stats'] = recent_stats
