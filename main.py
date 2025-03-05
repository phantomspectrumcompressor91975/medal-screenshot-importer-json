import filecmp
import glob
import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import TypedDict
from PIL import Image

STORE_PATH = Path(os.path.expandvars("%appdata%/Medal/store"))
# Enter Your Medal Clip Path
MEDAL_PATH = Path("C:\\Medal")
EXTRA_NAMES = {"Minecraft": ["Minecraft Java"]}

class Screenshot(TypedDict):
    uuid: str
    clipID: str
    Status: str
    Image: str
    SaveType: int
    GameTitle: str
    TimeCreated: float
    GameCategory: str
    Flag: int
    encoded: bool
    fileSource: str
    clipType: str
    userId: str
    origin: str
    Size: int
    sourceWidth: int
    sourceHeight: int
    videoLengthSeconds: int
    parent: int
    client: str
    clientId: str
    clientVersion: str


class Categories:
    categories: dict[str, list[str]]

    def __init__(self):
        self.USER_ID = 0
        self.clientVersion = 0
        self.clientId = 0
        self.categories = {}

    def load(self):
        with open(STORE_PATH / "game.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for game in data["games"]:
                if game["isGame"]:
                    self.categories[game["categoryId"]] = [
                        game["categoryName"],
                        game["alternativeName"],
                        *EXTRA_NAMES.get(game["categoryName"], []),
                        *EXTRA_NAMES.get(game["alternativeName"], []),
                    ]

    def game_id(self, game_name: str):
        for game_id, game in self.categories.items():
            if any(name.lower() == game_name.lower() for name in game):
                return game_id
        return None


# just shortens a uuid to 17 characters
def generateClipID():
    result = []
    for i, value in enumerate(str(uuid.uuid4())):
        if value != "-":
            if i > 17:
                break

            result.append(value)
    
    return ''.join(result)

class Clips:
    clips: dict[str, Screenshot]
    categories: Categories

    def __init__(self):
        self.clips = {}
        self.USER_ID = 0
        self.clientId = ""
        self.clientVersion = ""
        self.categories = Categories()

    def load(self):
        self.categories.load()
        with open(STORE_PATH / "clips.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for clip in data.values():
                self.USER_ID = clip["userId"]
                try:
                    data2 = json.loads(clip)
                    self.clientId = data2["clientId"]
                    self.clientVersion = data2["clientVersion"]
                except: pass

                self.clips[clip["uuid"]] = clip

    def save(self):
        with open(STORE_PATH / "clips.json", "w", encoding="utf-8") as f:
            json.dump(self.clips, f, indent=2)
    
    def insert(self, clip: Path):
        game = clip.name.split("_")[0]
        timestamp = datetime.now().timestamp()
        game_id = self.categories.game_id(game)
        if game_id is None:
            raise ValueError(f"Game {game} not found for clip {clip}")
        
        Screenshots = Path(f"{MEDAL_PATH}\\Screenshots")
        if Screenshots.exists() == False:
            Screenshots.mkdir()
        else:
            GamePath = Path(f"{Screenshots}\\{game}")
            if GamePath.exists() == False:
                GamePath.mkdir()
            else:
                time = datetime.fromtimestamp(timestamp)
                fileName = "MedalTV" + game + time.strftime("%m%d%Y%H%M%S") + ".png"
                
                copy = Path(shutil.copy(clip.name, fileName))
                imagePath = Path(shutil.move(copy, GamePath))
                img = Image.open(imagePath)

                clip_info: Screenshot = {
                    "uuid": str(uuid.uuid4()),
                    "clipID": generateClipID(),
                    "Status": "local",
                    "Image": str(imagePath.absolute()),
                    "SaveType": "1",
                    "GameTitle": game
                    + " "
                    + time.strftime("%m/%d/%Y %H:%M:%S"),
                    "TimeCreated": timestamp,
                    "userId": str(self.USER_ID),
                    "GameCategory": game_id,
                    "Flag": 0,
                    "encoded": True,
                    "fileSource": "medal",
                    "clipType": "clip",
                    "contentType": 29,
                    "origin": "Recorder",
                    "Size": os.path.getsize(imagePath),
                    "unseenCount": 0,
                    "sourceWidth": img.width,
                    "sourceHeight": img.height,
                    "videoLengthSeconds": 0,
                    "parent": -1,
                    "client": "Electron",
                    "clientId": str(self.clientId),
                    "clientVersion": str(self.clientVersion),
                }

                self.clips[clip_info["uuid"]] = clip_info

# So I Can Test
def main():
    clips = Clips()
    clips.load()

    for file in os.listdir():
        split = file.split(".")
        if split[len(split)-1].lower() == "png":
            clips.insert(Path(file))
            break
        
    clips.save()

if __name__ == "__main__":
    if MEDAL_PATH.exists() == False:
        Exception("Medal Path Doesn't Exist")
    else: main()