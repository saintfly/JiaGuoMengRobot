import pyautogui
import pyrect
import json
import numpy as np

import pyautogui_ext
from construct_menu import construct_menu
from shop_menu import shop_menu
from home_nation_light import home_nation_light
import logging
import datetime

from calculator_adapter import json_format_convert
from calculator_adapter import calculator_wrap
from calculator_adapter import prase_result
from calculator_adapter import get_lastest_info

__now=datetime.datetime.now()
__ts=__now.strftime("%Y%m%d%H%M%S")
info_file=f'output/org_info_{__ts}.json'
cal_cfg_file=f'output/cal_cfg_{__ts}.json'
cal_layout_file=f'output/cal_layout_{__ts}.json'
log_file=f'output/jgm_{__ts}.log'


def init_log():
    fmt_string='%(asctime)s %(filename)s[line:%(lineno)d] [%(name)s] [%(funcName)s] %(levelname)s %(message)s'
    logger=logging.getLogger()
    logging.basicConfig(level=logging.INFO,\
        format=fmt_string)
    handler=logging.FileHandler(filename=log_file,encoding='utf-8')
    handler.setFormatter(logging.Formatter(fmt_string))
    logger.addHandler(handler)

def init_click(win,config):
        cfg=config["建设菜单"]["位置"]
        win.click(cfg)
        win.click(cfg)
        # 在附近点几下，消除弹窗。
        cfg=config["建设菜单"]["城市任务"]["弹窗"]["完成按钮"]["位置"]
        for ofs in range(-3,3):
            win.click([cfg[0],cfg[1]+ofs*0.02])

def save_dict_as_json(filename,json_dict):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(json_dict,f,indent=4,ensure_ascii=False)

def calc_best_layout(json_cfg):
    if isinstance(json_cfg,dict):
        dict_cfg=json_cfg
    elif isinstance(json_cfg,str):
        with open(json_cfg,'r',encoding='utf-8') as f:
            dict_cfg=json.load(f)
    else:
        logging.error("计算配置参数错误，必须是dict或者json文件名。")
    calculator_wrap(dict_cfg)
    cal_result=prase_result()
    logging.info(f"最佳布局和升级方案解析结果：\n{cal_result}")
    return cal_result

def grab_info(cm,hnl):
    cm.select()
    gold_num=cm.get_gold_num()
    building_df=cm.bc.grab_info()
    building_dict=building_df.set_index(building_df.columns[0]).T.to_dict('dict')
    cm.select()
    task_light_buff=cm.tl.grab_info()
    cm.select()
    policy_buff=cm.pc.grab_info()
    hnl.select()
    album_buff=hnl.ct.grab_info()
    

    all_buff={}
    all_buff.update(task_light_buff)
    all_buff.update({"相册":album_buff})
    all_buff.update({"政策":policy_buff})
    all_dict={
        "信息总表":{
            "建筑":building_dict,
            "增益":all_buff,
            "金币":gold_num
        }
    }

    return all_dict
    
def relogin():
    exit_cfg=config["退出图标"]["位置"]
    comfirm_cfg=config["退出确认"]["位置"]
    icon_cfg=config["程序图标"]["位置"]
    app_win.click(exit_cfg)
    app_win.click(comfirm_cfg)
    while app_win.height>app_win.width:
        pyautogui.sleep(1)
    pyautogui.sleep(3)
    app_win.click(icon_cfg)
    while app_win.height<app_win.width:
        pyautogui.sleep(1)

def relogin_check():
    now=datetime.datetime.now()
    if(now.hour>=23 and now.minute>=55):
        return True
    else:
        return False
if "__main__"==__name__:

    import pyautogui_ext
    
    #找窗口，激活
    txwin_title='腾讯手游助手【极速傲引擎】'
    txwin=pyautogui.getWindowsWithTitle(txwin_title)
    if txwin == []:
        pyautogui.pymsgbox.alert("No windows named %s"%txwin_title)
        exit(-1)
    pyautogui.PAUSE=0.5

    app_win=txwin[0]
    app_win.activate()

    #读取配置
    fp=open('config.json', 'r',encoding='utf-8')
    config=json.load(fp)

    #初始化自动化对象
    # 建设菜单
    cm=construct_menu(app_win,config)
    # 商店菜单
    sm=shop_menu(app_win,config)
    # 家国之光菜单
    hnl=home_nation_light(app_win,config)

    #日志
    init_log()
    test=False
    if test:
        '''
        org_info=grab_info(cm,hnl)
        logging.info(f"收集的信息使用json格式保存{info_file}")
        save_dict_as_json(info_file,org_info)
        logging.info(f"收集信息：\n{json.dumps(org_info,indent=4,ensure_ascii=False)}")
        '''
        org_file=get_lastest_info("output","org_info_*.json")
        logging.info(f"读取保存的信息{org_file}")
        with open(org_file,'r',encoding='utf-8') as f:
            org_info=json.load(f)
        json_cfg=json_format_convert(org_info)
        logging.info(f"布局计算器配置使用json格式保存{cal_cfg_file}")
        save_dict_as_json(cal_cfg_file,json_cfg)
        calc_best_layout(json_cfg)
        exit(0)
    #
    # 开始循环
    cfg_train_timeout=config["建设菜单"]["火车"]["超时"]
    train_timeout=datetime.timedelta(0,cfg_train_timeout)
    while True:
        if relogin_check():
            logging.warning("定时重启。。。")
            relogin()
            sleep_time=300
            logging.warning(f"定时重启完成，等待{sleep_time}秒")
            pyautogui.sleep(sleep_time)
            logging.warning(f"等待完毕，开始自动点击")

        init_click(app_win,config)
        cm.run()
        now=datetime.datetime.now()
        # 现在火车超时（最后火车过去300秒，5分钟）并且超时后没有收集过红包，
        # 就收下红包，顺便收下相册。可能浪费一次相册。
        # 但相册周期四天出新，每天收入100+，影响不大。
        logging.debug(f"火车最近收集时间{cm.trs.last_train}")
        logging.debug(f"火车超时时间{cm.trs.last_train+train_timeout}")
        logging.debug(f"红包最近收集时间{sm.rp.last_collect}")
        if(cm.trs.last_train+train_timeout<now and\
            cm.trs.last_train+train_timeout>sm.rp.last_collect):
            sm.run()
            cm.select()
            #开始收集增益信息，尝试自动升级
            org_info=grab_info(cm,hnl)
            logging.info(f"收集的信息使用json格式保存{info_file}")
            save_dict_as_json(info_file,org_info)
            logging.info(f"收集信息：\n{json.dumps(org_info,indent=4,ensure_ascii=False)}")
            '''
            org_file=get_lastest_info("output","org_info_*.json")
            logging.info(f"读取保存的信息{org_file}")
            with open(org_file,'r',encoding='utf-8') as f:
                org_info=json.load(f)
            '''
            json_cfg=json_format_convert(org_info)
            logging.info(f"布局计算器配置使用json格式保存{cal_cfg_file}")
            save_dict_as_json(cal_cfg_file,json_cfg)
            cal_result=calc_best_layout(json_cfg)
            logging.info(f"布局计算器结果使用json格式保存{cal_layout_file}")
            save_dict_as_json(cal_layout_file,cal_result)
                
            

