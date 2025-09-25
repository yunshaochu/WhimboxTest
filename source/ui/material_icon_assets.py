from source.common.path_lib import ASSETS_PATH
from source.ui.template.img_manager import GameImg

import os
import json

material_icon_dict = {}

material_json_filepath = os.path.join(ASSETS_PATH, 'material.json')
with open(material_json_filepath, 'r', encoding='utf-8') as f:
    material_json = json.load(f)
    for material_name, value in material_json.items():
        material_icon_dict[material_name] = {
            "icon": GameImg(name=value['game_img']),
            "type": value['type']
        }
