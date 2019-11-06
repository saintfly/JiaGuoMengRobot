
import pyautogui
import numpy as np
import pyrect
import cv2.cv2 as cv2
import logging
import datetime
import math
from buff_praser import buff_praser
import pandas as pd
import time

class policy_center:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.bp=buff_praser(config)

    def get_upgrade_mean_gray(self):
        rect=self.config["建设菜单"]["政策中心"]["升级图标"]["矩形"]
        return self.win.rect_mean_gray(rect)
    def check_upgrade(self):
        gray_th=self.config["建设菜单"]["政策中心"]["升级图标"]["平均灰度下限"]
        return self.get_upgrade_mean_gray()>gray_th
    def click(self):
        self.win.click(self.config["建设菜单"]["政策中心"]["位置"])
    def green_enhance(self,img):
        mat=np.asarray(img)
        lb=np.array([0,255,0])
        ub=np.array([0,255,0])
        matbin=cv2.inRange(mat,lb,ub)   
        return matbin
    def drag_up(self,ratio=1.,duration=2,tween=pyautogui.easeInOutExpo):
        start=self.win.win_cfg_to_point(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["上滚"]["位置"])
        offset=int(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["上滚"]["长度"]*self.win.height*ratio+0.5)
        pyautogui.click(start)
        pyautogui.dragRel(0,-offset,duration,tween)
    def drag_down(self,ratio=1.,duration=2,tween=pyautogui.easeInOutExpo):

        start=self.win.win_cfg_to_point(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["下滚"]["位置"])
        offset=int(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["下滚"]["长度"]*self.win.height*ratio+0.5)
        pyautogui.click(start)
        pyautogui.dragRel(0,offset,duration,tween)
    def find_upgrade_icon(self,tmpl):
        list_rect=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["矩形"]
        match_th=self.config["建设菜单"]["政策中心"]["弹窗"]["匹配门限"]
        img=self.win.screenshot(list_rect)
        canvas=self.green_enhance(img)
        result=cv2.matchTemplate(canvas,tmpl,cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(result)
        if min_val>match_th:
            return None
        else:
            #找到一个升级位置点,计算坐标返回
            r = self.win.win_cfg_to_rect(list_rect)
            p = pyrect.Point(r.left+min_loc[0]+tmpl.shape[1],\
                r.top+min_loc[1]+tmpl.shape[0])
            return p
    def find_and_click_upgrade_icon(self):
        #获取升级图标作为内部匹配图像
        list_rect=self.config["建设菜单"]["政策中心"]["升级图标"]["矩形"]
        img=self.win.screenshot(list_rect)
        tmpl=self.green_enhance(img)
        #点击政策中心，开始升级
        self.win.click(self.config["建设菜单"]["政策中心"]["位置"])
        #点击滚动起始处（无效位置），消除splash screen
        self.win.click(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["下滚"]["位置"])
        #保证初始位置为最开始，先向下滚屏，拉到开头
        max_page_num=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["最大页数"]
        self.scroll_to_begin()
        for page_count in range(max_page_num):
            p=self.find_upgrade_icon(tmpl)

            if p is None:
                #没找到，向上滚屏
                self.drag_up()
            else:
                #找到一个升级位置点
                #点击升级
                pyautogui.click(p)
                logging.info(f"找到可升级政策，滚屏{page_count}次，位置{p}")
                #再点击弹窗的确认按钮
                self.win.click(self.config["建设菜单"]["政策中心"]["弹窗"]["弹窗"]["升级按钮"]["位置"])
                break
        #返回主菜单
        self.win.click(self.config["建设菜单"]["位置"])
        self.win.click(self.config["建设菜单"]["位置"])
        return page_count+1
    def run(self):
        if self.check_upgrade():
            logging.info("政策中心可升级")
            self.find_and_click_upgrade_icon()

    def get_buff_msg(self):
        cfg=self.config["建设菜单"]["政策中心"]["弹窗"]["弹窗"]["增益信息"]["矩形"]
        img=self.win.screenshot(cfg)
        c=self.win.color_ana_ocr(img)
        line=c.encode('UTF-8', 'ignore').decode('UTF-8')  
        #logging.info(f"识别字符串[{code}]")
        grade=self.bp.match_grade(line)
        no_grade_line=self.bp.strip_grade(line)
        target,value=self.bp.buff_praser(no_grade_line)
        return grade,target,value,no_grade_line!=line
    def transerve_stage(self,check_range,last_stage=False):
        if(last_stage):
            base=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["最后阶段基准"]
        else:
            base=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["基准"]
        r_ofs=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["行偏移"]
        c_ofs=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["列偏移"]
        stage_dict={}
        for idx in check_range:
            row=int(idx/2)
            col=idx%2
            cfg_loc=[base[0]+c_ofs*col,base[1]+r_ofs*row]
            self.win.click(cfg_loc)
            grd,tgt,val,valid=self.get_buff_msg()
            logging.info(f"识别增益等级{grd}，目标[{tgt}]，数值{val}，有效标记{valid}")
            self.win.click(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["上滚"]["位置"])
            stage_dict.update({f"第{idx+1}增益":{"级别":grd,"目标":tgt,"数值":val,"有效":valid}})
        return stage_dict
    
    def scroll_to_begin(self):
        for _ in range(3):
            self.drag_down(ratio=1.5,duration=0.5)

    def get_check_point(self,bg_color=np.array([255,255,255],dtype=np.uint8)):
        cfg=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["检测点"]
        ap=self.win.win_cfg_to_point(cfg)
        bbox=[ap[0],ap[1]-1,1,3]
        img=pyautogui.screenshot(region=bbox)
        mat=np.asarray(img)
        p1=mat[0,0,:]
        p2=mat[1,0,:]
        p1_is_bg=(p1==bg_color).all()
        p2_is_bg=(p2==bg_color).all()
        if p1_is_bg and p2_is_bg:
            return "背景"
        elif p1_is_bg and not p2_is_bg:
            return "上边"
        elif not p1_is_bg and not p2_is_bg:
            return "前景"
        else:
            #return "下边"
            return "前景"
    def get_dir_from_current_point(self,current_point,target_point):
        #限制步长场景，不会出现其他移动方向
        move_dir_dict={
            "背景移动到上边":-1,
            "前景移动到上边":1,
            "前景移动到背景":-1,
            "上边移动到背景":-1
        }
        return move_dir_dict[f"{current_point}移动到{target_point}"]

    def up_board_calibration(self):
        cur_cp=self.get_check_point()
        target_cp="上边"
        
        if(cur_cp==target_cp):
            logging.info(f"当前位置[{cur_cp}，无需移动]")
            return
        logging.info(f"校准开始：当前位置[{cur_cp}]")
        max_step=self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["最大移动步长"]
        move_step=int(max_step*self.win.height+0.5)
        
        backup_pause=pyautogui.PAUSE
        pyautogui.PAUSE=0.1
        last_move_dir=self.get_dir_from_current_point(cur_cp,target_cp)
        logging.info(f"开始从[{cur_cp}]向[{target_cp}]移动，方向{last_move_dir}")
        while cur_cp!=target_cp:
            move_dir=self.get_dir_from_current_point(cur_cp,target_cp)
            if(last_move_dir!=move_dir):
                move_step=int(move_step/2)
                move_step=1 if move_step<1 else move_step
            pyautogui.moveRel(0,move_dir*move_step)
            last_move_dir=move_dir
            logging.info(f"从[{cur_cp}]向[{target_cp}]移动{move_dir*move_step}")
            cur_cp=self.get_check_point()
        pyautogui.PAUSE=backup_pause  
        pyautogui.sleep(pyautogui.PAUSE) 
        logging.info(f"校准结束：当前位置[{cur_cp}]")
    def drag_up_stage(self,stage_idx,last_drag=False):
        drag_up_time = self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["阶段滚动时间"]
        
        stage_scroll_up_ratio = self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["阶段位移"][stage_idx]
        start=self.win.win_cfg_to_point(self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["上滚"]["位置"])
        stage_scroll_up_len=int(stage_scroll_up_ratio*self.win.height+0.5)
        pyautogui.click(start)
        pyautogui.mouseDown(start)
        if not last_drag:
            self.up_board_calibration()
            logging.info(f"大位移{-stage_scroll_up_len}")
            pyautogui.moveRel(0,-50)
            pyautogui.moveRel(0,-stage_scroll_up_len,duration=drag_up_time)
            self.up_board_calibration()
        else:
            pyautogui.moveRel(0,-stage_scroll_up_len,duration=drag_up_time)
        pyautogui.mouseUp()
        #self.drag_up(ratio=stage_scroll_up_ratio[stage_idx],duration=drag_up_time)
    
    def grab_info(self):
        self.click()
        self.scroll_to_begin()
        stage_num = self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["阶段数"]
        stage_buff_num = self.config["建设菜单"]["政策中心"]["弹窗"]["滚动区域"]["阶段增益数"]
        buff_dict={}
        for stage_idx in range(stage_num):
            bn=stage_buff_num[stage_idx]
            logging.info(f"政策阶段{stage_idx+1}/{stage_num},增益数量{bn}")
            stage_info=self.transerve_stage(range(bn),last_stage=stage_idx>=stage_num-1)
            buff_dict.update({f"第{stage_idx+1}阶段":stage_info})
            self.drag_up_stage(stage_idx,last_drag=stage_idx>=stage_num-2)
        return buff_dict

class buildings:
    def __init__(self,win,config):
        self.win=win
        self.config=config
    def get_float_rect(self,row,col):
        x_offs=self.config["建设菜单"]["建筑"]["列偏移"]*col
        y_offs=self.config["建设菜单"]["建筑"]["行偏移"]*row+\
            self.config["建设菜单"]["建筑"]["行方向列补偿"]*col
        base_rect=self.win.win_cfg_to_rect(self.config["建设菜单"]["建筑"]["基准"]["矩形"])
        tgt_rect=base_rect
        tgt_rect.left=tgt_rect.left+x_offs
        tgt_rect.top=tgt_rect.top+y_offs
        return tgt_rect
    def get_abs_rect(self,row,col):
        x_offs=self.config["建设菜单"]["建筑"]["列偏移"]*col
        y_offs=self.config["建设菜单"]["建筑"]["行偏移"]*row+\
            self.config["建设菜单"]["建筑"]["行方向列补偿"]*col
        base_rect=self.win.win_cfg_to_rect(self.config["建设菜单"]["建筑"]["基准"]["矩形"])
        tgt_rect=base_rect
        tgt_rect.left=tgt_rect.left+int(x_offs*self.win.width)
        tgt_rect.top=tgt_rect.top+int(y_offs*self.win.height)
        return tgt_rect
    def click(self,row,col):
        abs_rect=self.get_abs_rect(row,col)
        pyautogui.click(abs_rect.center)
    def click_all(self):
        for row in range(self.config["建设菜单"]["建筑"]["行数"]):
            for col in range(self.config["建设菜单"]["建筑"]["列数"]):
                self.click(row,col)
    def get_mean_gray_mat(self):
        #计算建筑图像的绿色分量平均亮度，放入列表
        gray_list=[]
        for row in range(self.config["建设菜单"]["建筑"]["行数"]):
            col_list=[]
            for col in range(self.config["建设菜单"]["建筑"]["列数"]):
                rect=self.get_abs_rect(row,col)
                r=self.win.rect2relative(rect)
                col_list.append(self.win.rect_mean_gray([r.left,r.top,r.width,r.height],'g'))
            gray_list.append(col_list)
        return gray_list
    def run(self):        
        self.click_all()
class train:
    def __init__(self,win,config,tgt):
        self.win=win
        self.config=config
        self.target=tgt
        self.last_train=datetime.datetime.now()
    def check_arrive(self,goods):
        #检测火车货物下的X图像，使用灰度检测
        rect=self.config["建设菜单"]["火车"][goods]["矩形"]
        gray_th=self.config["建设菜单"]["火车"]["平均灰度下限"]
        mg=self.win.rect_mean_color(rect)
        if mg>gray_th:
            logging.info(f"{goods}到达:检测灰度{mg},灰度门限{gray_th}")
            return True
        else:
            #print(f"check arrive fail:{goods},{self.win.rect_mean_color(rect)},{gray_th}")
            return False
    
    
    def find_goods_dest(self,gray_list1,gray_list2):
        cmp_th=self.config["建设菜单"]["火车"]["绿光灰度比值限"]
        #矩阵两两相除
        cmp_mat=np.array(gray_list2)/np.array(gray_list1)
        min_val,max_val,_,max_loc=cv2.minMaxLoc(cmp_mat)
        rect=self.target.get_abs_rect(max_loc[1],max_loc[0])
        mat_std=cmp_mat.std()
        mat_var=cmp_mat.var()
        if max_val>cmp_th:
            logging.info(f"绿光检测成功:最大值 {max_val},最小值 {min_val}, 门限 {cmp_th}")
            logging.info(f"std={mat_std},var={mat_var}")
            return pyrect.Point(rect.centerx,rect.centery)
        else:
            logging.error(f"绿光检测失败:最大值 {max_val},最小值 {min_val}, 门限 {cmp_th}")
            logging.info(f"std={mat_std},var={mat_var}")
            return None
        
    def goods_collect(self,goods):
        '''
        货物下的X上按下鼠标，检测按下鼠标前后的建筑绿光分量平均值查找目标
        然后将货物拖到目标，直到货物下的X消失
        返回值:
        -1表示没有检测到X
        0表示检测到X，但没有看到足够的绿光（按下前比按下后绿光平均灰度比值大于"绿光灰度比值限"）
        其他正整数表示拖动货物次数
        '''
        rect=self.win.win_cfg_to_rect(self.config["建设菜单"]["火车"][goods]["矩形"])
        duration=self.config["建设菜单"]["火车"]["货物拖动时间"]
        if(not self.check_arrive(goods)):
            return -1
        gray_list1=self.target.get_mean_gray_mat()
        #点击触发提示菜单
        pyautogui.click(rect.center)
        #按下查找绿光建筑
        pyautogui.mouseDown(rect.center)
        gray_list2=self.target.get_mean_gray_mat()
        loc=self.find_goods_dest(gray_list1,gray_list2)
        if loc is not None:
            pyautogui.dragTo(loc,duration=duration)
        else:
            return 0
        count = 1
        while(self.check_arrive(goods)):
            pyautogui.moveTo(rect.center)
            pyautogui.dragTo(loc,duration=duration)
            count=count+1
            if(count>10):
                raise Exception("货物拖动次数太多！可能程序未在前台。")
        return count
    def run(self):
        retval=[]
        for goods in self.config["建设菜单"]["火车"]["货物列表"]:
            retval.append(self.goods_collect(goods))
        #检测每个位置是否都检测不到X，即没有货物了
        while(not np.array(list(map(lambda x:x==-1,retval))).all()):
            #记录最后火车时间
            self.last_train=datetime.datetime.now()
            retval=[]
            for goods in self.config["建设菜单"]["火车"]["货物列表"]:
                retval.append(self.goods_collect(goods))
class city_task:
    def __init__(self,win,config):
        self.win=win
        self.config=config
    def click(self):
        self.win.click(self.config["建设菜单"]["城市任务"]["位置"])
    def check_finish(self):
        gray_mean=self.win.rect_mean_gray(self.config["建设菜单"]["城市任务"]["升级图标"]["矩形"])
        gray_th=self.config["建设菜单"]["城市任务"]["升级图标"]["平均灰度下限"]
        return gray_mean>gray_th
    def upgrade(self):
        self.click()
        gray_mean=self.win.rect_mean_gray(self.config["建设菜单"]["城市任务"]["弹窗"]["完成按钮"]["矩形"])
        gray_th=self.config["建设菜单"]["城市任务"]["弹窗"]["完成按钮"]["比较"]["平均灰度下限"]
        if gray_mean>gray_th:
            logging.info("城市任务升级可点击")
            self.win.click(self.config["建设菜单"]["城市任务"]["弹窗"]["完成按钮"]["位置"])
            self.win.click(self.config["建设菜单"]["城市任务"]["弹窗"]["完成按钮"]["第二位置"])
            #等待动画完成。
            time.sleep(1)
        else:
            logging.warning("城市任务升级不可点击")
        self.close()
    def close(self):
        self.win.click(self.config["建设菜单"]["城市任务"]["弹窗"]["关闭按钮"]["位置"])
    def run(self):
        if(self.check_finish()):
            logging.info("城市任务可升级")
            self.upgrade()
        else:
            #print("城市任务不可升级")
            pass

class buildings_center:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.bp=buff_praser(config)
        self.df=pd.DataFrame(columns = ["名称", "等级", "星级"])
    def drag_up(self,ratio=1.,duration=2,tween=pyautogui.easeInOutExpo):
        start=self.win.win_cfg_to_point(self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["上滚"]["位置"])
        offset=int(self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["上滚"]["长度"]*self.win.height*ratio+0.5)
        pyautogui.moveTo(start)
        pyautogui.dragRel(0,-offset,duration,tween)

    def count_star(self,img,th):
        mat=np.asarray(img)
        mat_gray=cv2.cvtColor(mat,cv2.COLOR_RGB2GRAY)
        _,mat_bin=cv2.threshold(mat_gray,200,255,cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        mat_bin_close = cv2.morphologyEx(mat_bin, cv2.MORPH_CLOSE, kernel) 
        cont,_=cv2.findContours(mat_bin_close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return len(cont)-1
    def fix_name(self,name):
        match_name=self.bp.match_head(name,self.bp.single_buff_target)
        if match_name:
            return match_name
        else:
            return name

    def collect_building_info(self,pos):
        pyautogui.click(pos)
        #time.sleep(1)
        th=200
        cfg_rect=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["弹窗"]["名称区"]["矩形"]
        img=self.win.screenshot(cfg_rect)
        name_code=self.win.gray_th_ocr(img,th=th,inv=True)
        cfg_rect=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["弹窗"]["等级区"]["矩形"]
        img=self.win.screenshot(cfg_rect)
        level_code=self.win.gray_th_ocr(img,th=th,inv=True)
        cfg_rect=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["弹窗"]["星级区"]["矩形"]
        img=self.win.screenshot(cfg_rect)
        start_num=self.count_star(img,th)
        logging.info(f"{name_code} {level_code} 星级:{start_num}")
        level=self.bp.match_number(level_code)
        self.win.click(self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["上滚"]["位置"])
        return self.fix_name(name_code),level,start_num
    
    def transerve_page(self,collect_range):
        cfg_pos=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["基准"]["位置"]
        row_num=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["每页行数"]
        col_num=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["每页列数"]
        x_interval=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["列间隔"]
        y_interval=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["行间隔"]
        for row in range(row_num):
            for col in range(col_num):
                if(row*col_num+col in collect_range):
                    x=cfg_pos[0]+col*x_interval
                    y=cfg_pos[1]+row*y_interval
                    pos=self.win.win_cfg_to_point([x,y])
                    info=self.collect_building_info(pos)
                    self.df.loc[len(self.df)]=list(info)
                    
    def select(self):
        cfg_pos=self.config["建设菜单"]["建筑中心"]["位置"]
        self.win.click(cfg_pos)
    def grab_info(self):
        self.select()
        row_num=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["每页行数"]
        col_num=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["每页列数"]
        building_num_in_one_page=row_num*col_num
        all_num=self.config["建设菜单"]["建筑中心"]["弹窗"]["滚动区域"]["总建筑数"]
        page_num=math.ceil(all_num/building_num_in_one_page)
        remaind_building_num = all_num-building_num_in_one_page*(page_num-1)
        logging.info(f"共{all_num}个建筑，每页{building_num_in_one_page}个，"+\
            f"共{page_num}页，最后一页{remaind_building_num}个")
        for page_idx in range(page_num):
            if(page_idx<page_num-1):
                self.transerve_page(range(building_num_in_one_page))
                self.drag_up()
            else:
                self.transerve_page(range(remaind_building_num))

        return self.df
    def save_df(self):
        now=datetime.datetime.now()
        self.df.to_csv(f'bi{now.strftime("%Y%m%d%H%M%S")}.csv')
class task_light:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.bp=buff_praser(config)
    def get_buff_img(self,idx):
        cfg=self.config["建设菜单"]["任务和光增益"]["弹窗"]["矩形"]
        x_offs=self.config["建设菜单"]["任务和光增益"]["图标"]["X偏移"]*idx
        img=self.win.screenshot([cfg[0]+x_offs]+cfg[1:])
        return img
    def get_mat_cut(self,img):
        mat=np.asarray(img)
        for row in range(mat.shape[0]):
            if (mat[row,mat.shape[1]-1]<245).all():
                break
        for col in range(mat.shape[1],0,-1):
            if (mat[0,col-1]<245).all():
                break
        mat_cut=mat[0:row,col-1:]
        return mat_cut
    def get_info_from_mat_cut(self,mat_cut):        
        row_h=int(self.config["建设菜单"]["任务和光增益"]["弹窗"]["行高"]*self.win.height+0.5)
        last_row_h=int(self.config["建设菜单"]["任务和光增益"]["弹窗"]["末行高"]*self.win.height+0.5)
        last_row_ofs=int(self.config["建设菜单"]["任务和光增益"]["弹窗"]["末行偏移"]*self.win.height+0.5)
        h=mat_cut.shape[0]
        w=mat_cut.shape[1]
        line_num=int((h-last_row_h)/row_h+0.5)
        line_list=[]
        if mat_cut.shape[0]<last_row_h:
            return []
        for line_idx in range(line_num):
            mat=mat_cut[row_h*line_idx:row_h*line_idx+row_h,0:w]
            line=self.win.gray_th_ocr(mat,th=190,inv=False)
            line_list.append(line)
        mat=mat_cut[row_h*line_num+last_row_ofs:row_h*(line_num+1)+last_row_ofs,\
            0:w]
        line=self.win.gray_th_ocr(mat,th=190,inv=False)
        line_list.append(line)
        return str.join("\n",line_list)    
    def get_info_from_buff_img(self,img):
        mat_cut=self.get_mat_cut(img)
        return self.get_info_from_mat_cut(mat_cut)
    def ana_info(self,info):
        lines=info.split('\n')
        last_line=lines[-1]

        buff_type=self.bp.type_praser(last_line)

        logging.info(f"从[{last_line}]分析出增益类型[{buff_type}]")
        buff_dict={}
        for line in lines[:-1]:
            target,value=self.bp.buff_praser(line)
            if target:
                logging.info(f"从[{line}]分析出[{target}]的增益百分比{value}")
                buff_dict.update({target:value})
            else:
                logging.info(f"从[{line}]什么都没分析出来，丢弃。")
        return {buff_type:buff_dict}
    def click(self,idx):
        cfg=self.config["建设菜单"]["任务和光增益"]["图标"]["位置"]
        x_offs=self.config["建设菜单"]["任务和光增益"]["图标"]["X偏移"]*idx
        self.win.click([cfg[0]+x_offs,cfg[1]])
    def grab_info(self):
        buff_cluster={}
        for idx in range(5):
            self.click(idx)
            img=self.get_buff_img(idx)
            info=self.get_info_from_buff_img(img)
            if info:
                logging.info(f"右起第{idx}个图标点击获得信息[{info}]")
                buff_dict=self.ana_info(info)
                buff_cluster.update(buff_dict)
                self.win.click(self.config["建设菜单"]["位置"])
            else:
                logging.info(f"右起第{idx}个图标点击没有获得信息")
                self.win.click(self.config["建设菜单"]["位置"])
                break
        return buff_cluster
class construct_menu:
    def __init__(self,win,config):
        self.win=win
        self.config=config
        self.pc=policy_center(win,config)
        self.bds=buildings(win,config)
        self.trs=train(win,config,self.bds)
        self.ct=city_task(win,config)
        self.bc=buildings_center(win,config)
        self.tl=task_light(win,config)
    def get_gold_num(self):
        cfg=self.config["建设菜单"]["金币"]["矩形"]
        img=self.win.screenshot(cfg)
        gn=self.win.gray_th_ocr(img,th=180,inv=False,lang='eng')
        return gn
    def click(self):
        self.win.click(self.config["建设菜单"]["位置"])
    def select(self):
        # 两次点击，确保在建设菜单下。
        # 第一次点击消除弹窗，第二次点击切换菜单
        self.click()
        self.click()
    def run(self):
        self.select()
        self.bds.run()
        self.trs.run()
        self.ct.run()
        self.pc.run()
    
if __name__=="__main__":
    import json
    import pyautogui_ext
    import time
    import datetime
    
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
    
    #cm.run()
    #cm.select()
    #cm.pc.find_and_click_upgrade_icon()
    #cm.pc.run()
    fmt_string='%(asctime)s %(filename)s[line:%(lineno)d] [%(name)s] [%(funcName)s] %(levelname)s %(message)s'
    logger=logging.getLogger()
    logging.basicConfig(level=logging.DEBUG,\
        format=fmt_string)
    handler=logging.FileHandler(filename=f"jgm.log",encoding='utf-8')
    handler.setFormatter(logging.Formatter(fmt_string))
    logger.addHandler(handler)
    cm=construct_menu(app_win,config)
    #bc=buildings_center(app_win,config)
    #cm.run()
    cm.select()
    cm.pc.grab_info()
    cm.select()
    '''
    buff_cluster=cm.tl.grab_info()
    
    print(buff_cluster)
    df=cm.bc.grab_info()
    print(df)
    '''
    
    '''
    logging.info("开始建设菜单点击")
    while True:
        cm.run()
        time.sleep(5)
    '''
