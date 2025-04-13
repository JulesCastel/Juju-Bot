import random
import requests
import json


def cnf_gif(fake_command, key) -> str:
    while True:
        try:
            response = requests.get(f"https://tenor.googleapis.com/v2/search?q={fake_command}&key={key}&random=true&limit=1&media_filter=gif")
        except requests.RequestException:
            return "Tenor API failed :(\nsee: " + str(requests.RequestException)
        if response.status_code == 200:
            return response.json()["results"][0]["itemurl"]

def hello(name: str) -> str:
    return f"hello there, {name}"


# modified the example dice roller function from the official Discord.py GitHub repo
def roll(dice: str) -> str:
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
        if rolls > 10000000 or limit > 10000000:
            raise ValueError
    except ValueError:
        return "value error! did you try to put in a decimal dice or a word? (idiot)"
    except Exception:
        return "'roll' format has to be in NdN! (e.g. 'roll 2d20') and less than 1,000,000"

    rolled = list(random.randint(1, limit) for _ in range(rolls))
    result = str(rolled)[1:-1] + f"\nSum: {sum(rolled)}"
    if len(result) > 2000:
        return f"result is too long to send on Discord, so this is all u get\nSum: {sum(rolled)}"
    else:
        return result


def cat() -> str:
    try:
        response = requests.get("https://api.thecatapi.com/v1/images/search")
    except requests.RequestException:
        return "cat API failed :(\nsee: " + str(requests.RequestException)
    return response.json()[0]["url"]


def insult(name: str) -> str:
    try:
        response = requests.get("https://evilinsult.com/generate_insult.php")
    except requests.RequestException:
        return "insults API failed :(\nsee: " + str(requests.RequestException)
    return f"Dear {name},\n\n***{response.text}***\n\nLove,\nMe"


def riddle() -> str:
    try:
        response = requests.get("https://riddles-api.vercel.app/random")
    except requests.RequestException:
        return "riddle API failed :(\nsee: " + str(requests.RequestException)
    o = response.json()
    return f"**{o['riddle']}**\nAnswer: ||__{o['answer']}__||"


def dadjoke() -> str:
    try:
        response = requests.get("https://icanhazdadjoke.com", headers={"Accept": "text/plain"})
    except requests.RequestException:
        return "dad joke API failed :(\nsee: " + str(requests.RequestException)
    return f"**{response.text}**"


def haiku() -> str:
    with open("haikus.txt") as haikus:
        return "*" + random.choice(haikus.read().split('\n\n')) + "*"


def flirt(name: str) -> str:
    try:
        response = requests.get("https://vinuxd.vercel.app/api/pickup")
    except requests.RequestException:
        return "pickup line API failed :(\nsee: " + str(requests.RequestException)
    line = response.json()["pickup"]
    return f"Hey {name},\n*{line}*\n😘"

def hammer(key) -> str:
    # putting this in a while loop bc for some reason, it won't accept my API key sometimes and i'll have to refresh to get it to work
    while True:
        try:
            response = requests.get(f"https://tenor.googleapis.com/v2/search?q=hammer&key={key}&random=true&limit=1&media_filter=gif")
        except requests.RequestException:
            return "Tenor API failed :(\nsee: " + str(requests.RequestException)
        if response.status_code == 200:
            return response.json()["results"][0]["itemurl"]
     
def fursona(user_id: int) -> str:
    with open("animals.txt") as file:
        animals = file.read().split("\n")
        random.seed(user_id)
        return random.choice(animals)