'''自动生成assets下所有图片的索引'''

import os
from whimbox.common.utils.utils import save_json
from whimbox.common.path_lib import ASSETS_PATH


class AssetsIndexGenerator():
    def __init__(self) -> None:
        pass

    def traversal(self):
        index_dict = {}
        folder_path = os.path.join(ASSETS_PATH, "imgs")
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                filename = f.split('.')[0]
                index_dict.setdefault(filename, {})
                rel_path = root.replace(ASSETS_PATH + '\\', "")
                index_dict[filename]['rel_path'] = os.path.join(rel_path, f)
        return index_dict

    def generate(self):
        save_json(self.traversal(), json_name="imgs_index.json", default_path=fr"{ASSETS_PATH}/imgs")

if __name__ == '__main__':
    AssetsIndexGenerator().generate()