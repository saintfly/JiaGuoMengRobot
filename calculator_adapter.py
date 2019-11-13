import sys
import pathlib
import os
import re
import pandas as pd
import numpy as np
import json
caclulator_path=(pathlib.Path()/"../JiaGuoMengCalculator").resolve()
sys.path.append(str(caclulator_path))
#sys.path.append(pathlib.Path().resolve())
from config import Config
from algorithm import Calculator

def json_format_convert(cfg,mode='online'):
    org_buildings=cfg['信息总表']['建筑']
    buildings={}

    for key in org_buildings.keys():
        buildings.update(
            {
                key:{
                    "star":org_buildings[key]['星级'],
                    "level":org_buildings[key]['等级'],
                    "buff":0
                }
            })
    city_task=cfg['信息总表']['增益']['城市任务']
    for key in city_task.keys():
        if key in org_buildings.keys():
            buildings[key]['buff']=city_task[key]
    #print(buildings)

    trans_table={
        "所有":"global",
        "供货":"supply",
        "在线":"online",
        "离线":"offline",
        "住宅":"residence",
        "商业":"commerce",
        "工业":"industry",
        "家国之光":"jiaguozhiguang"
        }
    org_policy=cfg['信息总表']['增益']['政策']
    policy={
        "global":0,
        "supply":0,
        "online":0,
        "offline":0,
        "residence":0,
        "commerce":0,
        "industry":0,
        "jiaguozhiguang":0
    }
    for stage in org_policy.keys():
        for buff in org_policy[stage].keys():
            if org_policy[stage][buff]['有效']:
                buff_name=org_policy[stage][buff]['目标']
                policy[trans_table[buff_name]]=policy[trans_table[buff_name]]+org_policy[stage][buff]['数值']
    if '家国之光' in cfg['信息总表']['增益'].keys():
        policy["jiaguozhiguang"]=cfg['信息总表']['增益']['家国之光']["所有"]
    else:
        policy["jiaguozhiguang"]=0
    #print(policy)

    mission={
        "global":0,
        "supply":0,
        "online":0,
        "offline":0,
        "residence":0,
        "commerce":0,
        "industry":0
    }
    org_mission=cfg['信息总表']['增益']['城市任务']
    for buff_name in org_mission.keys():
        if buff_name in trans_table.keys():
            mission[trans_table[buff_name]]=org_mission[buff_name]

    album={
        "global":0,
        "supply":0,
        "online":0,
        "offline":0,
        "residence":0,
        "commerce":0,
        "industry":0
    }
    org_album=cfg['信息总表']['增益']['相册']
    for buff_name in org_album.keys():
        album[trans_table[buff_name]]=org_album[buff_name]
    #%%
    all_config={}
    buffs={}
    all_config.update({"buildings":buildings})
    buffs.update({"policy":policy})
    buffs.update({"album":album})
    buffs.update({"mission":mission})
    all_config.update({"buffs":buffs})
    all_config.update({"blacklist":[]})
    all_config.update({"whitelist":[]})
    all_config.update({"mode":"online"})
    all_config.update({"gold":cfg['信息总表']['金币']})
    all_config.update({"only_current":False})
    return all_config

def calculator_wrap(json_config):
    pwd=pathlib.Path().resolve()
    os.chdir(caclulator_path)
    cfg=Config()
    cfg.init_config_from_json(json_config)
    cal = Calculator(cfg)
    cal.calculate()
    os.chdir(pwd)

def prase_result():
    result_file=caclulator_path/'result.txt'
    with open(result_file,'r',encoding='utf-8') as f:
        lines=[]
        for line in f:
            lines.append(re.sub('\n','',line))
    buildings_layout={}
    for idx in range(1,4):
        parts=lines[idx].split("：")
        builds=parts[1].split("、")
        buildings_layout.update({parts[0][:2]:builds})
    
    upgrade_plan={}
    for idx in range(8,17):
        line=lines[idx]
        name=re.findall(r'(\w+)\s+',line)
        level=re.findall(r'\s+(\d+)',line)
        upgrade_plan.update({name[0]:int(level[0])})
    result={"建筑布局":buildings_layout,"升级方案":upgrade_plan}
    return result

def calc_upgrade_cost(t_lvl,json_config,verbose=False):
    data_path=caclulator_path/"data"
    upgrade_file=data_path/"upgrade.csv"
    baseincome_file=data_path/"baseIncome.csv"
    baseincome = pd.read_csv(baseincome_file, encoding='gb2312')
    upgrade=pd.read_csv(upgrade_file)
    basebuild=baseincome[baseincome.star==5]
    cost_list=[]
    for _,row in basebuild.iterrows():
        r=row['rarity']
        n=row['buildName']
        lvl=json_config['buildings'][n]['level']
        if lvl>=t_lvl:
            cost=0
        else:
            cost=sum(upgrade[(upgrade['rank']>lvl) & (upgrade['rank']<=t_lvl)][r].values)
        cost_list.append(cost)
        if verbose:
            print(f"{n}:{r}从{lvl}升级到{t_lvl}耗费{cost}")
    if verbose:
        print(f"全升级到{t_lvl}耗费{np.array(cost_list).sum()}")
    return np.array(cost_list).sum()

def get_lastest_info(path,glob_pattern):
    import pathlib
    p=pathlib.Path(path)
    return str(sorted(p.glob(glob_pattern),key=lambda x:x.stat().st_ctime)[-1])

def gold_convert(gold):
    from static import UnitDict
    if isinstance(gold,str):
        if re.fullmatch(r'\d+\.*\d*([GKMBT]{0,1}|[abcdefgh]{2})',gold):
            unit=re.findall(r'[GKMBTabcdefgh]+',gold)[0]
            return float(re.findall(r'[\d.]+',gold)[0])*UnitDict[unit]
    elif isinstance(gold,float):
        sorted_keys=sorted(UnitDict,key=lambda x:UnitDict[x],reverse=True)
        for key in sorted_keys:
            if gold>UnitDict[key]:
                number=gold/UnitDict[key]
                return f"{number:3.2f}{key}"

if __name__ == "__main__":
    last_cfg=get_lastest_info("output","cal_cfg_*.json")
    with open(last_cfg,'r',encoding='utf-8') as f:
        cfg=json.load(f)
    cost_gold=calc_upgrade_cost(1425,cfg,True)
    print(f"消耗金币{gold_convert(cost_gold)}")
    print(f"消耗金币{gold_convert(gold_convert(cost_gold))}")
