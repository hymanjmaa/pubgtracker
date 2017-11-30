from time import sleep
from slackclient import SlackClient

import requests
import json


class PUBGPlayerMonitor:
    def __init__(self, api_key, players_monitored, slack_token):
        self.api_key = api_key
        self.pubg_url = "https://api.pubgtracker.com/v2/profile/pc/"
        self.headers = {
            'content-type': "application/json",
            'trn-api-key': api_key,
        }
        self.slack_token = slack_token
        self.players_monitored = players_monitored
        self.player_agg_stats = self.collect_player_agg_stats()
        self.slack_message("#pubgtrackerbot", "Starting monitoring of players: {0}".format(
            ','.join(self.players_monitored)))

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

    def player_stats(self, player_handle):
        """Returns the full set of data on a player, no filtering"""
        try:
            url = self.pubg_url + player_handle
            response = requests.request("GET", url, headers=self.headers)
            return json.loads(response.text)
        except BaseException as error:
            print('Unhandled exception: ' + str(error))
            raise

    def collect_player_agg_stats(self):
        """
        Collect statistics for all players defined in settings.
        :return:
        """
        player_wins = []
        for player in self.players_monitored:
            player_stat_collection = {'player': player}
            sleep(2)
            stats = self.get_player_agg_stats(player)
            player_stat_collection['stats'] = stats
            player_wins.append(player_stat_collection)
        return player_wins

    def get_player_agg_stats(self, player_handle):
        try:
            player = self.player_stats(player_handle)
            if player:
                stats = player.get('stats')
                if stats:
                    stat_collection = {
                        'wins': dict(),
                        'kills': dict(),
                    }
                    for region_stat in stats:
                        if region_stat['region'] == 'agg':
                            for stat in region_stat['stats']:
                                if stat['field'] == 'Wins':
                                    stat_collection['wins'][region_stat['mode']] = stat
                                if stat['field'] == 'Kills':
                                    stat_collection['kills'][region_stat['mode']] = stat
                    return stat_collection
            else:
                print("No win stats for player: {0}".format(player_handle))
                return None
        except json.JSONDecodeError:
            print("JSON Decoding error")
        except Exception as e:
            print("Error getting player wins: {0}".format(str(e)))

    def check_player_agg_stats(self):
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
                        mode_win_diff = recent_stats['wins'][mode].get('valueInt', 0) - old_stats['wins'][mode].get(
                            'valueInt', 0)
                        kills_diff = recent_stats['kills'][mode].get('valueInt', 0) - old_stats['kills'][mode].get(
                            'valueInt', 0)
                        if mode_win_diff > 0:
                            self.slack_message("#pubg", "{0} new win(s) detected for player {1}!\n"
                                                        "Mode: {2}\n"
                                                        "Match kills: {3}\n"
                                                        "Total mode kill count: {4}\n"
                                                        "Total mode win count: {5}".format(
                                                            mode_win_diff,
                                                            player['player'],
                                                            mode,
                                                            kills_diff,
                                                            recent_stats['kills'][mode].get('valueInt', 0),
                                                            recent_stats['wins'][mode].get('valueInt', 0)))
                        elif kills_diff > 0:
                            self.slack_message("#pubgtrackerbot",
                                               "{0} new kill(s) detected for player {1}!\n"
                                               "Mode: {2}\n"
                                               "Total mode kill count: {3}".format(
                                                   kills_diff,
                                                   player['player'],
                                                   mode,
                                                   recent_stats['kills'][mode].get('valueInt', 0)))
                    except Exception as e:
                        print("Exception from trying to parse new wins/stats: {0}".format(str(e)))
                player['stats'] = recent_stats
