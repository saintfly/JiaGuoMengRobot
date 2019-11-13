import pyautogui
import pyrect
import numpy as np
import pytesseract
import cv2.cv2 as cv2
from PIL import Image
from io import StringIO
import pandas as pd
import logging
pytesseract.pytesseract.tesseract_cmd="c:/Program Files/Tesseract-OCR/tesseract.exe"
def win_warp_relative_to_absolute_rect(self,float_rect):
    '''
    添加pyautogui.Windows功能
    窗口内相对浮点矩形转换到屏幕矩形
    '''
    #float_rect=pyrect.Rect(*float_list,enableFloat=True)
    r=pyrect.Rect()
    r.left=int(float_rect.left*self.width+0.5)+self.left
    r.top=int(float_rect.top*self.height+0.5)+self.top
    r.width=int(float_rect.width*self.width+0.5)
    r.height=int(float_rect.height*self.height+0.5)
    return r

def win_warp_relative_to_absolute_point(self,float_point):
    '''
    添加pyautogui.Windows功能
    窗口内相对浮点点转换到屏幕点
    '''
    p=pyrect.Point(int(float_point.x*self.width+0.5)+self.left,\
        int(float_point.y*self.height+0.5)+self.top)
    return p

def win_warp_absolute_to_relative_rect(self,int_rect):
    '''
    添加pyautogui.Windows功能
    屏幕矩形->窗口内相对浮点矩形
    '''
    r=pyrect.Rect(enableFloat=True)
    r.left=(int_rect.left-self.left)/self.width
    r.top=(int_rect.top-self.top)/self.height
    r.width=int_rect.width/self.width
    r.height=int_rect.height/self.height
    return r

def win_warp_absolute_to_relative_point(self,int_point):
    '''
    添加pyautogui.Windows功能
    屏幕点->窗口内相对浮点点
    '''
    p=pyrect.Point((int_point.x-self.left)/self.width,\
        (int_point.y-self.top)/self.height)
    return p

def win_cfg_to_point(self,pos):
    p=pyrect.Point(*pos)
    ap=self.point2absolute(p)
    #print(f"ap{ap},p{p}")
    return ap

def win_cfg_to_rect(self,list_rect):
    p=pyrect.Rect(*list_rect,enableFloat=True)
    ap=self.rect2absolute(p)
    #print(f"ap{ap},p{p}")
    return ap

def win_warp_click(self,pos):
    #print(self.win_cfg_to_point(pos))
    pyautogui.click(self.win_cfg_to_point(pos))

def win_warp_moveTo(self,pos):
    pyautogui.moveTo(self.win_cfg_to_point(pos))

def win_warp_dragTo(self,pos):
    pyautogui.dragTo(self.win_cfg_to_point(pos))

def win_warp_screen(self,list_rect):
    r=self.win_cfg_to_rect(list_rect)
    #print(r,list_rect)
    return pyautogui.screenshot(region=(r.x,r.y,r.w,r.h))

def win_warp_rect_mean_gray(self,list_rect,component='rgb'):
    component_selector={"rgb":slice(3),'r':0,'g':1,'b':2}
    img=self.screenshot(list_rect)
    mat=np.asarray(img)
    slice_mat=mat[:,:,component_selector[component]]
    return slice_mat.sum()/slice_mat.size

def win_warp_rect_mean_color(self,list_rect,color=np.array([255,255,255])):
    import cv2.cv2 as cv2
    img=self.screenshot(list_rect)
    mat=np.asarray(img)    
    mat_bin=cv2.inRange(mat,color,color)
    return mat_bin.sum()/mat_bin.size

def win_wrap_ocr(self,mat_bin,lang='chi_sim'):
    #return pytesseract.image_to_string(Image.fromarray(mat_bin),lang='chi_sim')
    #print(f"lang={lang}")
    data=pytesseract.image_to_data(Image.fromarray(mat_bin),lang=lang,config='--psm 7')
    df=pd.read_csv(StringIO(data),sep='\t',dtype={'text':str})
    min_conf=df.conf[df.conf>=0].min()
    string_list=df.text[df.conf>=0].values.tolist()
    string_code=str.join("",string_list)
    logging.debug(f"识别字符串[{string_code}],最小可信度{min_conf}")
    return string_code

def win_wrap_conf_ocr(self,mat_bin,lang='chi_sim'):
    #return pytesseract.image_to_string(Image.fromarray(mat_bin),lang='chi_sim')
    #print(f"lang={lang}")
    data=pytesseract.image_to_data(Image.fromarray(mat_bin),lang=lang,config='--psm 7')
    df=pd.read_csv(StringIO(data),sep='\t',dtype={'text':str})
    min_conf=df.conf[df.conf>=0].min()
    string_list=df.text[df.conf>=0].values.tolist()
    string_code=str.join("",string_list)
    logging.debug(f"识别字符串[{string_code}],最小可信度{min_conf}")
    return min_conf,string_code

def win_warp_gray_th_ocr(self,img,th=128,inv=False,lang='chi_sim'):
    mat=np.asarray(img)
    mat_gray=cv2.cvtColor(mat,cv2.COLOR_RGB2GRAY)
    if inv:
        mode=cv2.THRESH_BINARY_INV
    else:
        mode=cv2.THRESH_BINARY
    _,mat_bin=cv2.threshold(mat_gray,th,255,mode)

    min_conf,code=win_wrap_conf_ocr(self,mat_bin,lang=lang)
    if min_conf<60:
        logging.warning(f"识别可信度{min_conf}太低，尝试改变灰度门限识别")
        _,mat_bin=cv2.threshold(mat_gray,int(th*0.8),255,mode)
        min_conf1,code1=win_wrap_conf_ocr(self,mat_bin,lang=lang)
        _,mat_bin=cv2.threshold(mat_gray,int(th+(255-th)*0.2),255,mode)
        min_conf2,code2=win_wrap_conf_ocr(self,mat_bin,lang=lang)
        if min_conf1>min_conf2:
            new_code=code1
            new_conf=min_conf1
        else:
            new_code=code2
            new_conf=min_conf2
        if new_conf>60:
            logging.info(f"识别可信度从{min_conf}提高到{new_conf}，使用可信新字符串")
            return new_code
        elif new_conf>min_conf:
            logging.warning(f"识别可信度从{min_conf}提高到{new_conf}，可信度仍不足")
            return new_code
        else:
            logging.warning(f"识别可信度从{min_conf}提升失败{new_conf}，使用原字符串")
            return code
    else:
        logging.debug(f"[{code}]识别可信度{min_conf}")
        return code

def find_perpendicular_param(p0,dir_vect,p_out):
    '''
    line p=p0+k(dir_vect), find p_out's perpendicular's k
    reson:
        (k(dir_vect) dot (p_out-(p0+k(dir_vect))))=0
        dir_vect dot p_out - dir_vect dot p0 = k(dir_vect)dot(dir_vect)
        k=((dir_vect) dot (p_out-p0))/((dir_vect)dot(dir_vect))
    参数方程直线外一点的垂足的方程系数k，利用垂直向量点积为0推导计算
    点到直线距离为直线上任意点到直线外点的向量与直线方向单位向量叉乘的模
    '''
    d=dir_vect.astype(np.float)
    p=p0.astype(np.float)
    out=p_out.astype(np.float)
    k=np.dot(d,(out-p))/np.dot(d,d)
    dist=np.linalg.norm(np.cross(dir_vect,(out-p)))
    return k,dist

def find_perpendicular_param_pp(p1,p2,p_out):
    '''
    line p=p1+k*(p2-p1)/norm(p2-p1) transfer to 
    line p=p0+k(dir_vect), find p_out's perpendicular's k
    reson:
        (k(dir_vect) dot (p_out-(p0+k(dir_vect))))=0
        dir_vect dot p_out - dir_vect dot p0 = k(dir_vect)dot(dir_vect)
        k=((dir_vect) dot (p_out-p0))/((dir_vect)dot(dir_vect))
    参数方程直线外一点的垂足的方程系数k，利用垂直向量点积为0推导计算
    点到直线距离为直线上任意点到直线外点的向量与直线方向单位向量叉乘的模
    '''
    p0=p1
    dir_vect=(p2-p1)/np.linalg.norm(p2-p1)
    return find_perpendicular_param(p0,dir_vect,p_out)

def win_warp_color_space_ana_orc(self,img,bg_color=None,lang='chi_sim'):
    mat=np.asarray(img)
    if bg_color is None:
        bg_color=mat[0,0,:]
    mat=np.asarray(img)
    
    matgray=cv2.cvtColor(mat,cv2.COLOR_RGB2GRAY)
    min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(matgray)
    _=min_val
    _=max_val
    dark_point=mat[min_loc[1],min_loc[0]]
    light_point=mat[max_loc[1],max_loc[0]]
    p1=dark_point.astype(np.float)
    p2=light_point.astype(np.float)
    p3=bg_color.astype(np.float)
    mat_bin=np.zeros(mat.shape,dtype=np.uint8)
    _=p3
    half_len=np.linalg.norm(p2-p1)/2
    for row in range(mat.shape[0]):
        for col in range(mat.shape[1]):
            p=mat[row,col,:].astype(np.float)
            k1,d1=find_perpendicular_param_pp(p2,p1,p)
            #k2,d2=find_perpendicular_param_pp(p1,p3,p)
            d3=np.linalg.norm(p2-p)
            _=k1
            th=5
            if(d1<th and d3<half_len):
                mat_bin[row,col]=np.array([0,0,0],dtype=np.uint8)
                
            else:
                mat_bin[row,col]=np.array([255,255,255],dtype=np.uint8)
                
    return self.ocr(mat_bin,lang=lang)
#增加相对坐标转屏幕坐标的功能
pyautogui.Window.rect2relative=win_warp_absolute_to_relative_rect
pyautogui.Window.rect2absolute=win_warp_relative_to_absolute_rect

pyautogui.Window.point2relative=win_warp_absolute_to_relative_point
pyautogui.Window.point2absolute=win_warp_relative_to_absolute_point

#配置相对坐标转换到绝对坐标和鼠标的绝对坐标操作
pyautogui.Window.win_cfg_to_point=win_cfg_to_point
pyautogui.Window.win_cfg_to_rect=win_cfg_to_rect
pyautogui.Window.click=win_warp_click
pyautogui.Window.moveTo=win_warp_moveTo
pyautogui.Window.dragTo=win_warp_dragTo

#根据配置中定义的浮点矩形进行截图功能
pyautogui.Window.screenshot=win_warp_screen

#根据配置中定义的浮点矩形进行截图，计算平均灰度
pyautogui.Window.rect_mean_gray=win_warp_rect_mean_gray
pyautogui.Window.rect_mean_color=win_warp_rect_mean_color

#文字识别
pyautogui.Window.ocr=win_wrap_ocr
pyautogui.Window.gray_th_ocr=win_warp_gray_th_ocr
pyautogui.Window.color_ana_ocr=win_warp_color_space_ana_orc
