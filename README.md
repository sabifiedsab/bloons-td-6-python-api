# BTD6 API Support For Python
A library that makes working with the BTD6 API easier

## Installation
1. Download the [BTD6API](/BTD6API.py) script
2. Install the library *requests* with `pip install requests`
3. Make some beautiful creations!

## Features
A user friendly API to get information about the latest race events, boss events, user profile information and more!

For example, this is how you would get the daily challenge info:
```py
from BTD6API import BTD6API, BTD6Challenge, BTD6ChallengeDocument

api = BTD6API()

daily_challenge: BTD6Challenge = api.get_challenges_with_filter('daily')[0] # get the latest daily challenge
metadata: BTD6ChallengeDocument = daily_challenge.get_metadata()
```
Now when you have the metadata, you can get all sorts of things! Like `metadata.name` will give you the name of the challenge, `metadata.startRound` and `metadata.endRound` will give you starting and ending round!

Like this:
```py
print(f"Name: {metadata.name}")
print(f"Starting Round: {metadata.startRound}")
print(f"Ending Round: {metadata.endRound}")
```

Check if there is a race event ongoing with:
```py
from BTD6API import BTD6API, BTD6RaceEvent

api = BTD6API()

latest_race_event: BTD6RaceEvent = api.get_available_race_events()[0]
if api.race_event_is_ongoing(latest_race_event):
    print("Race event is ongoing!")
else:
    print("No race events are currently ongoing..")
```

And so much more! This library is stuffed with classes and functions, and there is more to come!

## License

This project is licensed under the Creative Commons Attribution 4.0 International License - see the [LICENSE](LICENSE) file for details.

### Summary of the License

This license allows others to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

For more information, please visit [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

# Contact
You can add me (Sabified) on discord with `sabifiedsab`
