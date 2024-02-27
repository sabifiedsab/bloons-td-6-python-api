import requests
import time
import logging

""" Uncomment to enable logging for debugging purposes
with open('api_log.log', 'w'): pass # Clear Log File
logging.basicConfig(filename='api_log.log', level=logging.DEBUG, format= '[%(levelname)s] %(asctime)s - %(message)s') # Logging
"""

"""
ERRORS
"""
class InvalidLinkError(Exception):
    def __init__(self, message):
        super().__init__(message)

class TooBigTeamSize(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidFilterType(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidRaceID(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidBossID(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidBossType(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidTeamSize(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidUserID(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidChallengeID(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidCTID(Exception):
    def __init__(self, message):
        super().__init__(message)

class NoScoresAvailable(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidGuildID(Exception):
    def __init__(self, message):
        super().__init__(message)

"""
EVENTS
"""
class BTD6SubmissionEntry:
    """
    A submission entry for a BTD6 event. For example a time in a race event, or a score in a ranked boss event
    :param displayName: The display name of the submission owner
    :param score: Score of the submission
    :param submissionTime: The epoch time in milliseconds when the score was submitted (-1 when not available)
    :param profile: URL to the players public profile
    """

    def __init__(self, displayName, score, scoreParts, submissionTime, profile):
        self.displayName = displayName
        self.score = score
        self.scoreParts = scoreParts
        self.submissionTime = submissionTime
        self.profile = profile

        logging.debug(f"Created Submission Entry Variable, Display Name: {self.displayName}")

    @classmethod
    def from_dict(cls, data_dict):
        return cls(**data_dict)

class BTD6EventLeaderboard:
    """
    A list of Submission Entries

    :param body: The body of the API response JSON object. Example: response['body']
    """

    def __init__(self, body: list):
        self.leaderboardList = body
        self.leaderboard = []

        for elem in self.leaderboardList:
            entry = BTD6SubmissionEntry.from_dict(elem)
            self.leaderboard.append(entry)

        logging.debug("Created Event Leaderboard")

    def get_leaderboard(self):
        return self.leaderboard

class Event:
    """
    Event class

    :param id_: ID of the event, gotten from the response
    :param name: Name of the event
    :param start: Starting time of the event in epoch time
    :param end: Ending time of the event in epoch time
    """

    def __init__(self, id_, name, start, end):
        self.id = id_
        self.name = name
        self.start = start
        self.end = end

        logging.debug(f"Created Event: {self.name}")

"""
RACES
"""
class BTD6RaceEvent(Event):
    def __init__(self, id_, name, start, end, totalScores, leaderboard, metadata, api_instance=None):
        super().__init__(id_, name, start, end)
        self.totalScores = totalScores
        self.leaderboardURL = leaderboard
        self.metadataURL = metadata

        self.api_instance = api_instance

        self.leaderboard = self.get_leaderboard() if api_instance else None
        self.metadata = self.get_metadata() if api_instance else None

        logging.debug(f"Created Race Event: {self.name}")

    def get_leaderboard(self):
        """
        Gets leaderboard for the respective mode
        :return: A BTD6EventLeaderboard object with all the top 100 entries of this event
        """
        logging.debug(f"Get: '{self.name}' leaderboard")
        leaderboard_data = self.api_instance.get_response(self.leaderboardURL, raw=True)['body']
        leaderboard = BTD6EventLeaderboard(leaderboard_data)
        return leaderboard.get_leaderboard()

    def get_metadata(self):
        """
        Get rules of the map you're playing on
        :return: A BTD6ChallengeDocument object with all the rules and details
        """
        logging.debug(f"Get: '{self.name}' metadata")
        metadata_data = self.api_instance.get_response(self.metadataURL, raw=True)['body']
        metadata = BTD6ChallengeDocument.from_dict(metadata_data)
        return metadata

    @classmethod
    def from_dict(cls, data_dict):
        # Adjust the dictionary key for id
        data_dict['id_'] = data_dict.pop('id')
        return cls(**data_dict)

"""
BOSSES
"""
class BTD6BossEvent(Event):
    def __init__(self, id_, name, start, end, bossType, bossTypeURL, totalScores_standard, totalScores_elite,
                 leaderboard_standard_players_1, leaderboard_elite_players_1, metadataStandard, metadataElite,
                 scoringType, api_instance=None):
        super().__init__(id_, name, start, end)
        self.bossType = bossType
        self.bossTypeURL = bossTypeURL
        self.totalScores_standard = totalScores_standard
        self.totalScores_elite = totalScores_elite
        self.leaderboard_standard_players_1_URL = leaderboard_standard_players_1
        self.leaderboard_elite_players_1_URL = leaderboard_elite_players_1
        self.metadataStandardURL = metadataStandard
        self.metadataEliteURL = metadataElite
        self.scoringType = scoringType

        self.api_instance = api_instance

        self.leaderboard_standard_players_1 = self.get_leaderboard_one_player("standard") if api_instance else None
        self.leaderboard_elite_players_1 = self.get_leaderboard_one_player("elite") if api_instance else None

        self.metadataStandard = self.get_metadata("standard") if api_instance else None
        self.metadataElite = self.get_metadata("elite") if api_instance else None

        logging.debug(f"Created Boss Event: {self.name}")

    def get_leaderboard_one_player(self, mode: str):
        """
        Gets leaderboard for the respective mode
        :param mode: Either standard or elite mode
        :return: A BTD6EventLeaderboard object with all the top 100 entries of this event
        """
        logging.debug(f"Get: {mode} boss leaderboard")
        if mode == "standard":
            leaderboard_data = self.api_instance.get_response(self.leaderboard_standard_players_1_URL, raw=True)['body']
        elif mode == "elite":
            leaderboard_data = self.api_instance.get_response(self.leaderboard_elite_players_1_URL, raw=True)['body']
        else:
            logging.error(f"Leaderboard type '{mode}' isn't valid!")
            raise ValueError("Invalid Mode!")

        leaderboard = BTD6EventLeaderboard(leaderboard_data)
        return leaderboard.get_leaderboard()

    def get_metadata(self, mode: str):
        """
        Get rules of the map you're playing on
        :param mode: Either standard or elite mode
        :return: A BTD6ChallengeDocument object with all the rules and details
        """
        logging.debug(f"Get: {mode} boss metadata")
        if mode == "standard":
            metadata_data = self.api_instance.get_response(self.metadataStandard, raw=True)['body']
        elif mode == "elite":
            metadata_data = self.api_instance.get_response(self.metadataEliteURL, raw=True)['body']
        else:
            logging.error(f"Metadata type '{mode}' isn't valid!")
            raise ValueError("Invalid Mode!")

        metadata = BTD6ChallengeDocument.from_dict(metadata_data)
        return metadata

    @classmethod
    def from_dict(cls, data_dict):
        # Adjust the dictionary key for id
        data_dict['id_'] = data_dict.pop('id')
        return cls(**data_dict)

"""
USER
"""
class BTD6UserProfile:
    def __init__(self, displayName, rank, veteranRank, achievements, mostExperiencedMonkey,
                 avatar, banner, avatarURL, bannerURL, followers, bloonsPopped, gameplay,
                 heroesPlaced, _medalsSinglePlayer, _medalsMultiplayer, _medalsBoss,
                 _medalsBossElite, _medalsCTLocal, _medalsCTGlobal, _medalsRace):
        self.displayName = displayName
        self.rank = rank
        self.veteranRank = veteranRank
        self.achievements = achievements
        self.mostExperiencedMonkey = mostExperiencedMonkey
        self.avatar = avatar
        self.banner = banner
        self.avatarURL = avatarURL
        self.bannerURL = bannerURL
        self.followers = followers
        self.bloonsPopped = bloonsPopped
        self.gameplay = gameplay
        self.heroesPlaced = heroesPlaced
        self._medalsSinglePlayer = _medalsSinglePlayer
        self._medalsMultiplayer = _medalsMultiplayer
        self._medalsBoss = _medalsBoss
        self._medalsBossElite = _medalsBossElite
        self._medalsCTLocal = _medalsCTLocal
        self._medalsCTGlobal = _medalsCTGlobal
        self._medalsRace = _medalsRace

    @classmethod
    def from_dict(cls, data_dict):
        return cls(**data_dict)

"""
CHALLENGES
"""
class BTD6ChallengeDocument:
    """
    An object containing all detailed debugrmation of a challenge/map
    """
    def __init__(
            self, name, createdAt, id_, creator, gameVersion, map_, mapURL, mode, difficulty,
            disableDoubleCash, disableInstas, disableMK, disablePowers, disableSelling, startingCash,
            lives, maxLives, maxTowers, maxParagons, startRound, endRound, plays, wins, losses, upvotes,
            playsUnique, restarts, winsUnique, lossesUnique, abilityCooldownReductionMultiplier,
            leastCashUsed, leastTiersUsed, noContinues, seed, removeableCostMultiplier, roundSets,
            _powers, _bloonModifiers, _towers
    ):
        self.name = name
        self.createdAt = createdAt
        self.id_ = id_
        self.creator = creator
        self.gameVersion = gameVersion
        self.map_ = map_
        self.mapURL = mapURL
        self.mode = mode
        self.difficulty = difficulty
        self.disableDoubleCash = disableDoubleCash
        self.disableInstas = disableInstas
        self.disableMK = disableMK
        self.disablePowers = disablePowers
        self.disableSelling = disableSelling
        self.startingCash = startingCash
        self.lives = lives
        self.maxLives = maxLives
        self.maxTowers = maxTowers
        self.maxParagons = maxParagons
        self.startRound = startRound
        self.endRound = endRound
        self.plays = plays
        self.wins = wins
        self.losses = losses
        self.upvotes = upvotes
        self.playsUnique = playsUnique
        self.restarts = restarts
        self.winsUnique = winsUnique
        self.lossesUnique = lossesUnique
        self.abilityCooldownReductionMultiplier = abilityCooldownReductionMultiplier
        self.leastCashUsed = leastCashUsed
        self.leastTiersUsed = leastTiersUsed
        self.noContinues = noContinues
        self.seed = seed
        self.removeableCostMultiplier = removeableCostMultiplier
        self.roundSets = roundSets
        self.powers = _powers
        self.bloonModifiers = _bloonModifiers
        self.towers = _towers

        logging.debug(f"Created Challenge Document: {self.name}")

    @classmethod
    def from_dict(cls, data_dict):
        # Adjust the dictionary key for id and map
        data_dict['id_'] = data_dict.pop('id')
        data_dict['map_'] = data_dict.pop('map')
        return cls(**data_dict)

class BTD6Challenge:
    def __init__(self, name, createdAt, id_, creator, metadata, api_instance=None):
        self.name = name
        self.createdAt = createdAt
        self.id_ = id_
        self.creatorURL = creator
        self.metadataURL = metadata

        self.api_instance = api_instance

        self.creator = self.get_creator() if api_instance else None
        self.metadata = self.get_metadata() if api_instance else None

    def get_creator(self):
        """
        Get creator profile debugrmation
        :return: A BTD6ChallengeDocument object with all the rules and details
        """
        logging.debug(f"Get: '{self.name}' creator")
        creator_data = self.api_instance.get_response(self.creatorURL, raw=True)['body']
        creator = BTD6UserProfile.from_dict(creator_data)
        return creator

    def get_metadata(self):
        """
        Get rules of the map you're playing on
        :return: A BTD6ChallengeDocument object with all the rules and details
        """
        logging.debug(f"Get: '{self.name}' metadata")
        metadata_data = self.api_instance.get_response(self.metadataURL, raw=True)['body']
        metadata = BTD6ChallengeDocument.from_dict(metadata_data)
        return metadata

    @classmethod
    def from_dict(cls, data_dict):
        # Adjust the dictionary key for id
        data_dict['id_'] = data_dict.pop('id')
        return cls(**data_dict)

"""
API
"""
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class BTD6API(metaclass=SingletonMeta):
    def __init__(self, api_token: str = None):
        self.url_prefix = "https://data.ninjakiwi.com"
        self.api_token = api_token

    def get_response(self, link: str, raw=False) -> dict | None:
        """
        Tries to access the API
        :param link: The link to the API
        :param raw: If you input the whole link, or just the suffix
        :return: A JSON object of the debugrmation
        """
        logging.debug("Get response from API")
        l: str = link if raw else f"{self.url_prefix}{link}"
        if not l.startswith("https://data.ninjakiwi.com"):
            raise InvalidLinkError("You're trying to access another website/api!")
        try:
            response = requests.get(l)
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error ocurred: {http_err}")
        except Exception as err:
            print(f"Other exception occurred: {err}")
        else:
            response_json = response.json()

            if not response_json['success']: # if the request wasn't successfull, error in request
                self.get_error(response_json['error'])
                return None

            return response_json
        logging.warning("An error occured with get reponse function from API")
        return None

    @staticmethod
    def get_error(err: str):
        match err.lower():
            case "no race with that id exists":
                raise InvalidRaceID(err)
            case "no boss with that id exists":
                raise InvalidBossID(err)
            case "invalid boss type":
                raise InvalidBossType(err)
            case "invalid team size":
                raise InvalidTeamSize(err)
            case "invalid boss difficulty":
                raise InvalidBossType(err)
            case "invalid user id / player does not play this game":
                raise InvalidUserID(err)
            case "invalid filter type":
                raise InvalidFilterType(err)
            case "no challenge with that id exists":
                raise InvalidChallengeID(err)
            case "no ct with that id exists":
                raise InvalidCTID(err)
            case "no scores available":
                raise NoScoresAvailable(err)
            case "invalid guild id":
                raise InvalidGuildID(err)


    def get_available_race_events(self) -> list:
        """
        Gives you a list of recent race events
        :return: List of BTD6RaceEvent objects
        """
        endpoint = "/btd6/races"

        responses = self.get_response(endpoint)['body']
        races = []

        for elem in responses:
            race = BTD6RaceEvent.from_dict(elem)
            race.api_instance = self
            races.append(race)

        logging.debug(f"Get: Available races, latest is '{races[0].name}'")
        return races

    def get_latest_race(self) -> BTD6RaceEvent:
        """
        Gives you the latest Race Event
        :return: A BTD6RaceEvent
        """
        races = self.get_available_race_events()
        latest_race = max(races, key=lambda r: r.start)
        latest_race.api_instance = self
        logging.debug(f"Get: Latest race: '{latest_race.name}'")
        return latest_race

    def get_race_leaderboard(self, race_id) -> BTD6EventLeaderboard:
        """
        Gives you the leaderboard of a specific race event
        :param race_id: The id of the race event
        :return: A BTD6EventLeaderboard of the race event provided
        """
        endpoint = f"/btd6/races/{race_id}/leaderboard"

        response = self.get_response(endpoint)
        leaderboard = BTD6EventLeaderboard(response['body'])
        logging.debug(f"Get: Race Leaderboard")
        return leaderboard

    def get_race_metadata(self, race_id) -> BTD6ChallengeDocument:
        """
        Gives you the metadata (map debugrmation) of a race event
        :param race_id: The id of the race event
        :return: A BTD6ChallengeDocument of the race event provided
        """
        endpoint = f"/btd6/races/{race_id}/metadata"

        response = self.get_response(endpoint)
        metadata = BTD6ChallengeDocument.from_dict(response['body'])
        logging.debug(f"Get: Race ({metadata.name}) Metadata")
        return metadata

    @staticmethod
    def race_event_is_ongoing(race: BTD6RaceEvent) -> bool:
        """
        Tells you if a race event is ongoing
        :param race: The race event you want to test for
        :return: Bool that says if the provided race event is ongoing respectively
        """
        logging.debug(f"Get: Race event ({race}) is ongoing")
        return True if time.time() - race.end < 0 else False

    def get_available_boss_events(self) -> list:
        """
        Gives you a list of recent boss events
        :return: List of recent boss events
        """
        endpoint = "/btd6/bosses"

        responses = self.get_response(endpoint)['body']
        bosses = []

        for elem in responses:
            boss = BTD6BossEvent.from_dict(elem)
            boss.api_instance = self
            bosses.append(boss)

        logging.debug(f"Get: Available bosses, latest is '{bosses[0].name}'")
        return bosses

    def get_boss_leaderboard(self, boss_id, type_, teamSize) -> BTD6EventLeaderboard:
        """
        Gives you a boss leaderboard
        :param boss_id: The id of the boss event
        :param type_: Difficulty, either standard or elite
        :param teamSize: The size of the time. Keep in mind that no teams bigger than 1 is supported
        :return: A BTD6EventLeaderboard for the boss event provided
        """
        endpoint = f"/btd6/bosses/{boss_id}/leaderboard/{type_}/{teamSize}"

        if teamSize > 1:
            raise TooBigTeamSize("Team Sizes bigger than 1 aren't supported")

        response = self.get_response(endpoint)
        leaderboard = BTD6EventLeaderboard(response['body'])
        logging.debug(f"Get: Boss Leaderboard")
        return leaderboard

    def get_boss_metadata(self, boss_id, difficulty) -> BTD6ChallengeDocument:
        """
        Gives you the metadata (map debugrmation) of a boss event
        :param boss_id: The id of the boss event
        :param difficulty: Difficulty, standard or elite
        :return: A BTD6EventLeaderboard for the boss event provided
        """
        endpoint = f"/btd6/bosses/{boss_id}/metadata/{difficulty}"

        response = self.get_response(endpoint)
        metadata = BTD6ChallengeDocument.from_dict(response['body'])
        logging.debug(f"Get: Boss ({metadata.name}) Metadata")
        return metadata

    def get_user_profile(self, user_id) -> BTD6UserProfile:
        """
        Gives you debugrmation about a user
        :param user_id: The id of the user
        :return: A BTD6UserProfile of the id provided
        """
        endpoint = f"/btd6/users/{user_id}"

        response = self.get_response(endpoint)
        user = BTD6UserProfile.from_dict(response)
        logging.debug(f"Get: User Profile Information, Display Name: {user.displayName}")
        return user

    def get_challenges_with_filter(self, filter_) -> list:
        """
        Gives you a list of recent challenges with the filter provided
        :param filter_: Either newest, trending or daily
        :return: List with BTD6Challenge objects
        """
        endpoint = f"/btd6/challenges/filter/{filter_}"
        if filter_ not in ['newest', 'trending', 'daily']:
            logging.error(f"'{filter_}' isn't a valid filter for challenges!")
            raise InvalidFilterType("Filter can either be 'newest', 'trending' or 'daily'")

        responses = self.get_response(endpoint)['body']
        challenges = []

        for elem in responses:
            challenge = BTD6Challenge.from_dict(elem)
            challenge.api_instance = self
            challenges.append(challenge)

        logging.debug(f"Get: Challenges with filter '{filter_}', first is '{challenges[0].name}'")
        return challenges

    def get_challenge_metadata(self, challenge_id) -> BTD6ChallengeDocument:
        """
        Gives you the metadata (map debugrmation) of a challenge
        :param challenge_id: The id of the challenge
        :return: A BTD6ChallengeDocument of the id provided
        """
        endpoint = f"/btd6/challenges/challenge/{challenge_id}"

        response = self.get_response(endpoint)['body']
        challenge = BTD6ChallengeDocument.from_dict(response)

        return challenge
