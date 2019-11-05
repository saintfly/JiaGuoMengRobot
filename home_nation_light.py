import pyautogui
import numpy as np
import pyrect
import cv2.cv2 as cv2
import json
import pyautogui_ext
import time
import logging
import datetime
from buff_praser import buff_praser

class china_travelog:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.bp=buff_praser(config)
    
    def click(self):
        self.win.click(self.config["国家之光菜单"]["相册增益"]["位置"])

    def grab_info(self):
        self.win.click(self.config["国家之光菜单"]["相册增益"]["位置"])
        cfg=self.config["国家之光菜单"]["相册增益"]["弹窗"]["矩形"]
        line_height=self.config["国家之光菜单"]["相册增益"]["弹窗"]["行高"]
        line_num=int(cfg[3]/line_height+0.5)
        buff_dict={}
        for line_idx in range(line_num):
            line_cfg=[cfg[0],\
                cfg[1]+line_idx*line_height,\
                cfg[2],line_height]
            
            img=self.win.screenshot(line_cfg)

            line=self.win.gray_th_ocr(img,th=160,inv=False)
            target,value=self.bp.buff_praser(line)
            if target:
                logging.info(f"从[{line}]分析出[{target}]的增益百分比{value}")
                buff_dict.update({target:value})
            else:
                logging.info(f"从[{line}]什么都没分析出来，丢弃。")
        self.win.click(self.config["国家之光菜单"]["位置"])
        return buff_dict
class home_nation_light:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.ct=china_travelog(win,config)
    def click(self):
        self.win.click(self.config["国家之光菜单"]["位置"])
    def select(self):
        # 两次点击，确保在建设菜单下。
        # 第一次点击消除弹窗，第二次点击切换菜单
        self.click()
        self.click()
    
if __name__=="__main__":
    txwin_title='腾讯手游助手【极速傲引擎】'
    txwin=pyautogui.getWindowsWithTitle(txwin_title)
    if txwin == []:
        pyautogui.pymsgbox.alert("No windows named %s"%txwin_title)
        exit(-1)
    pyautogui.PAUSE=0.5

    app_win=txwin[0]
    app_win.activate()
    fp=open('config.json', 'r',encoding='utf-8')
    config=json.load(fp)
    fmt_string='%(asctime)s %(filename)s[line:%(lineno)d] [%(name)s] [%(funcName)s] %(levelname)s %(message)s'
    logger=logging.getLogger()
    logging.basicConfig(level=logging.DEBUG, format=fmt_string)
    handler=logging.FileHandler(filename="jgm.log",encoding='utf-8')
    handler.setLevel(logging.NOTSET)
    handler.setFormatter(logging.Formatter(fmt_string))
    logger.addHandler(handler)
    logging.info("开始商店菜单点击")

    hnl=home_nation_light(app_win,config)

    hnl.select()
    buff_list=hnl.ct.grab_info()
    print(buff_list)