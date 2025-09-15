'''自动生成assets下所有图片的索引'''

import os
from source.common.utils.utils import save_json
from source.common.path_lib import ASSETS_PATH


class AssetsIndexGenerator():
    def __init__(self) -> None:
        pass

    def traversal(self):
        index_dict = {}
        folder_path = os.path.join(ASSETS_PATH, "imgs")
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                index_dict.setdefault(f"{f.split('.')[0]}",{})
                index_dict[f"{f.split('.')[0]}"][root.split('\\')[-1]]=os.path.join(root,f)
        # logger.error(f"SearchPathError:{filename}")
        return index_dict

    def generate(self):
        save_json(self.traversal(), json_name="imgs_index.json", default_path=fr"{ASSETS_PATH}/imgs")

if __name__ == '__main__':
    AssetsIndexGenerator().generate()