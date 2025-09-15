import json
from source.map.convert import *
from pydantic import BaseModel
import typing
import os
from source.common.path_lib import SOURCE_PATH

DICT_TELEPORTER ={}

class TeleporterModel(BaseModel):
    id: int
    region: str
    province: str
    tp: str
    item_id: int
    name: str
    position: typing.Tuple[float, float]

checkpoint_filepath = os.path.join(SOURCE_PATH, 'map', 'data', 'checkpoints.json')
with open(checkpoint_filepath, 'r', encoding='utf-8') as f:
    checkpoints = json.load(f)
    for checkpoint in checkpoints:
        pos = convert_gameLoc_to_mapPx([checkpoint['position']['x'], checkpoint['position']['y']])
        DICT_TELEPORTER[checkpoint['checkpointID']] = TeleporterModel(
            id=checkpoint['checkpointID'],
            tp='Teleporter',
            item_id=660,
            name=checkpoint['name'],
            region=checkpoint['region'],
            province=checkpoint['province'],
            position=(pos[0], pos[1])
        )

