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
def init_log():
    fmt_string='%(asctime)s %(filename)s[line:%(lineno)d] [%(name)s] [%(funcName)s] %(levelname)s %(message)s'
    logger=logging.getLogger()
    logging.basicConfig(level=logging.DEBUG,\
        format=fmt_string)
    handler=logging.FileHandler(filename=f"output/jgm.log",encoding='utf-8')
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
    with open('output/info.json','w',encoding='utf-8') as f:
        json.dump(all_dict,f,indent=4,ensure_ascii=False)
    
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
    #sm.run()
    #exit(0)
    grab_info(cm,hnl)
    exit(0)
    #
    # 开始循环
    cfg_train_timeout=config["建设菜单"]["火车"]["超时"]
    train_timeout=datetime.timedelta(0,cfg_train_timeout)
    while True:
        init_click(app_win,config)
        cm.run()
        now=datetime.datetime.now()
        # 现在火车超时（最后火车过去300秒，5分钟）并且超时后没有收集过红包，
        # 就收下红包，顺便收下相册。可能浪费一次相册。
        # 但相册周期四天出新，每天收入100+，影响不大。
        logging.info(f"火车最近收集时间{cm.trs.last_train}")
        logging.info(f"火车超时时间{cm.trs.last_train+train_timeout}")
        logging.info(f"红包最近收集时间{sm.rp.last_collect}")
        if(cm.trs.last_train+train_timeout<now and\
            cm.trs.last_train+train_timeout>sm.rp.last_collect):
            sm.run()
            cm.select()
            #开始收集增益信息
                


            

