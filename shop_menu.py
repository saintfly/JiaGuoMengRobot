#%%
import pyautogui
import numpy as np
import pyrect
import cv2.cv2 as cv2
import json
import pyautogui_ext
import time
import logging
import datetime

class red_packet:
    def __init__(self,win,config,parent):
        self.win=win
        self.config=config
        self.parent=parent
        self.last_collect=datetime.datetime.now()
    def check_free(self,rp_name):
        cfg=self.config["商店菜单"]["红包"][rp_name]["个数"]["矩形"]
        logging.debug(f"检测{rp_name}的数字区域")
        return self.parent.check_free(cfg)
        
    def collect(self,rp_name):
        cfg=self.config["商店菜单"]["红包"][rp_name]["个数"]["矩形"]
        p=self.win.win_cfg_to_point(cfg[:2])
        th=self.config["商店菜单"]["背景检测区"]["门限"]
        cfg_rect=self.config["商店菜单"]["背景检测区"]["矩形"]
        max_splash_count=self.config["商店菜单"]["背景检测区"]["最大闪屏点击"]
        mean_gray_before=self.win.rect_mean_gray(cfg_rect)   
        logging.debug(f"点击后首次检测区平均灰度{mean_gray_before}")
        for count in range(max_splash_count):
            pyautogui.click(p)
            shadow_mean_gray=self.win.rect_mean_gray(cfg_rect)
            logging.debug(f"点击后阴影检测区平均灰度{shadow_mean_gray}")
            if(mean_gray_before*0.75>shadow_mean_gray):
                break
            else:
                pass
        if(count>=max_splash_count-1):
            logging.error(f"在一个{rp_name}收集前点击{count}次未恢复，疑似出错。")
        else:
            logging.info(f"收集{rp_name}中。。。")
        for count in range(max_splash_count):
            pyautogui.click(p)
            mean_gray_after=self.win.rect_mean_gray(cfg_rect)
            logging.debug(f"点击后恢复检测区平均灰度{mean_gray_after}")
            if(mean_gray_after*th>shadow_mean_gray):
                break
            else:
                pass
        if(count>=max_splash_count-1):
            logging.error(f"在一个{rp_name}收集后点击{count}次未恢复，疑似出错。")
        else:
            logging.info(f"在一个{rp_name}中收集中点击{count+1}次")
        time.sleep(1)

    def conti_collect(self,rp_name):
        while(self.check_free(rp_name)):
            self.collect(rp_name)

    def get_blue_coin_num(self):
        cfg=self.config["商店菜单"]["蓝星币"]["矩形"]
        th =self.config["商店菜单"]["蓝星币"]["灰度门限"]
        img=self.win.screenshot(cfg)
        code=self.win.gray_th_ocr(img,th=th)
        if(code.isdigit()):
            logging.info(f"有{int(code)}个蓝星币")
            return int(code)
        else:
            logging.error(f"没有识别到蓝星币.识别为[{code}]")
            return 0
    def run(self):
        for rp_name in self.config["商店菜单"]["红包"]["红包列表"]:
            logging.info(f"开始收集{rp_name}")
            self.conti_collect(rp_name)
        while(self.get_blue_coin_num()>=500):
            logging.info(f"收集一次满福红包")
            self.collect("满福红包")
        #记录本次收集时刻
        self.last_collect=datetime.datetime.now()

class album:
    def __init__(self,win,config,parent):
        self.win=win
        self.config=config
        self.parent=parent
    def click(self):
        cfg=self.config["商店菜单"]["相册"]["个数"]["矩形"]
        p=self.win.win_cfg_to_point(cfg[:2])
        pyautogui.click(p)
    
    def check_get_gold(self):
        cfg_rect=self.config["商店菜单"]["相册"]["金币检测区"]["矩形"]
        th=self.config["商店菜单"]["相册"]["金币检测区"]["门限"]
        return self.win.rect_mean_gray(cfg_rect)<th
    def check_free(self):
        cfg=self.config["商店菜单"]["相册"]["个数"]["矩形"]
        return self.parent.check_free(cfg)
    def collect(self):
        th=self.config["商店菜单"]["背景检测区"]["门限"]
        cfg_rect=self.config["商店菜单"]["背景检测区"]["矩形"]
        max_splash_count=self.config["商店菜单"]["背景检测区"]["最大闪屏点击"]
        mean_gray_before=self.win.rect_mean_gray(cfg_rect)   
        logging.debug(f"点击后首次检测区平均灰度{mean_gray_before}")
        for count in range(max_splash_count):
            self.click()
            shadow_mean_gray=self.win.rect_mean_gray(cfg_rect)
            logging.debug(f"点击后阴影检测区平均灰度{shadow_mean_gray}")
            if(mean_gray_before*0.75>shadow_mean_gray):
                break
            else:
                pass
        time.sleep(2)
        if(self.check_get_gold()):
            logging.info(f"在一个相册中收集到金币，退出。")
            return "金币"
        else:
            logging.info(f"在一个相册中收集到相册，继续。")
        if(count>=max_splash_count-1):
            logging.error(f"在相册收集前点击{count}次未恢复，疑似出错。")
        else:
            logging.info(f"收集相册中。。。")
        for count in range(max_splash_count):
            self.click()
            mean_gray_after=self.win.rect_mean_gray(cfg_rect)
            logging.debug(f"点击后恢复检测区平均灰度{mean_gray_after}")
            if(mean_gray_after*th>shadow_mean_gray):
                break
            else:
                pass
        if(count>=max_splash_count-1):
            logging.error(f"在相册收集后点击{count}次未恢复，疑似出错。")
        else:
            logging.info(f"在相册中收集中点击{count+1}次")
        time.sleep(1)
    def collect1(self):
        self.click()
        if(self.check_get_gold()):
            logging.info(f"在一个相册中收集到金币，退出。")
            return "金币"
        th=self.config["商店菜单"]["背景检测区"]["门限"]
        cfg_rect=self.config["商店菜单"]["背景检测区"]["矩形"]
        max_splash_count=self.config["商店菜单"]["背景检测区"]["最大闪屏点击"]
        shadow_mean_gray=self.win.rect_mean_gray(cfg_rect)

        for count in range(max_splash_count):
            self.click()
            if(self.win.rect_mean_gray(cfg_rect)>shadow_mean_gray*th):
                break
            else:
                pass
        if(count>=max_splash_count-1):
            logging.error(f"在一个相册收集中点击超过{count}次，疑似出错。")
        else:
            logging.info(f"在一个相册收集中点击{count}次。")
        time.sleep(1)
        return "相片"
    def run(self):
        while True:
            while self.check_free():
                if(self.collect()=="金币"):
                    self.parent.select()
                    self.parent.select()
                    return
            check1=self.check_free()
            time.sleep(1)
            check2=self.check_free()
            if(check1 or check2):
                logging.info(f"动画干扰数字检测。")
            else:
                logging.info(f"无相册，退出。")
                break
        self.parent.select()
        self.parent.select()
        

class shop_menu:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.rp=red_packet(win,config,self)
        self.alb=album(win,config,self)
    def click(self):
        self.win.click(self.config["商店菜单"]["位置"])
    def select(self):
        # 两次点击，确保在商店菜单下。
        # 第一次点击消除弹窗，第二次点击切换菜单
        self.click()
        self.click()
    def check_free(self,cfg):
        r=self.win.rect_mean_gray(cfg,'r')
        g=self.win.rect_mean_gray(cfg,'g')
        b=self.win.rect_mean_gray(cfg,'b')
        r_lth=self.config["商店菜单"]["数字存在门限"]["红色下限"]
        g_uth=self.config["商店菜单"]["数字存在门限"]["绿色上限"]
        b_uth=self.config["商店菜单"]["数字存在门限"]["蓝色上限"]
        logging.debug(f"数字区域平均色彩分量{r},{g},{b}")
        return r>r_lth and g<g_uth and b<b_uth

    def run(self):
        self.select()
        self.rp.run()
        
        self.alb.run()
        
        
        


#%%
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
    sm=shop_menu(app_win,config)
    sm.run()
