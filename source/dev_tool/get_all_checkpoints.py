'''
根据解包游戏获得的传送点数据，不太靠谱，仅用于测试
正式发布时，需要手动录入一遍真实的传送点数据
'''
import json
import os
from source.common.path_lib import SOURCE_PATH

province_replace_dict = {
    '大愿望镇': '心愿原野',
    '活动地图1': '心愿原野',
    "无忧岛": '心愿原野',

}

region_replace_dict = {
    '愿望镇': '花愿镇',
    '石树田': '石树田无人区',
    '心愿树林': '祈愿树林',
    '心愿树龄': '祈愿树林',
    
}

checkpoint_pos_filepath = 'D:\workspaces\python\in-config-decoder\cfg\config_output\map\TbCheckPoints.json'
checkpoint_info_filepath = 'D:\workspaces\\reverse\\tools\FModel\Output\Exports\X6Game\Content\Config\DesignerConfigs\CheckPoint\DT_CheckpointList.json'
checkpoint_info_dict = {}
with open (checkpoint_info_filepath, 'r', encoding='utf-8') as f:
    json_obj = json.load(f)
    for checkpoint_id, value in json_obj[0]['Rows'].items():
        name_obj = value['CheckpointName_25_620EB1A34749C207A34B66886372C213[4]']
        if 'SourceString' in name_obj:
            name = name_obj['SourceString']
        else:
            continue
        province = value["KingdomTag_5_2534C1B0461F1506F77E9ABA9CA55446[2]"]
        if province in province_replace_dict:
            province = province_replace_dict[province]
        region = value["AreaTag_7_96DF79D543FA3C889270E19406D13EB8[3]"]
        if region in region_replace_dict:
            region = region_replace_dict[region]
        
        checkpoint_info_dict[checkpoint_id] = {
            "name": name,
            "province": province,
            "region": region,
        }

res = []
with open(checkpoint_pos_filepath, 'r', encoding='utf-8') as f:
    json_obj = json.load(f)
    checkpoints = json_obj['export']['actors']
    for checkpoint in checkpoints:
        if str(checkpoint['checkpointID']) not in checkpoint_info_dict:
            print(f'{checkpoint["checkpointID"]} not found name')
        else:
            info = checkpoint_info_dict[str(checkpoint['checkpointID'])]
            position = checkpoint['transform']['position']
            res.append({
                'checkpointID': checkpoint['checkpointID'],
                'position': position,
                'world_id': checkpoint['world_id'],
                'teleportTag': checkpoint['teleportTag'],
                'name': info['name'],
                'province': info['province'],
                'region': info['region'],
            })

output_filepath = os.path.join(SOURCE_PATH, 'map', 'data', 'checkpoints.json')
json.dump(res, open(output_filepath, 'w', encoding='utf-8'), ensure_ascii=False)
print(len(res))