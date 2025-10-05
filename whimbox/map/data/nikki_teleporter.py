import json
from pydantic import BaseModel
import typing
import os
from whimbox.common.path_lib import ASSETS_PATH

DICT_TELEPORTER ={}

class TeleporterModel(BaseModel):
    region: str
    province: str
    map: str
    type: str
    name: str
    position: typing.Tuple[float, float]

checkpoint_filepath = os.path.join(ASSETS_PATH, 'checkpoints.json')
with open(checkpoint_filepath, 'r', encoding='utf-8') as f:
    checkpoints_dict = json.load(f)
    for map_name in checkpoints_dict:
        DICT_TELEPORTER[map_name] = []
        checkpoints = checkpoints_dict[map_name]
        for checkpoint in checkpoints:
            t = TeleporterModel(
                region=checkpoint['region'],
                province=checkpoint['province'],
                map=checkpoint['map'],
                type=checkpoint['type'],
                name=checkpoint['name'],
                position=(checkpoint['position'][0], checkpoint['position'][1])
            )
            DICT_TELEPORTER[map_name].append(t)
