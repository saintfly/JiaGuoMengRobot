import re
import Levenshtein
import logging
import numpy as np
class buff_praser:
    def __init__(self,config):
        self.single_buff_target=config["增益解析"]["单体增益"]
        self.buff_type=config["增益解析"]["增益类别"]
        self.multi_buff_target=config["增益解析"]["群体增益"]
    def match_unit(self,line):
        result=re.findall(r'[\d\.]+([GKMBT]{0,1}|[abcdefgh]{2})/',line)
        if result:
            return result[0]
        else:
            logging.info(f"[{line}]中没有匹配到金币单位。")
            return 0
    def match_head(self,line,keywords):
        dist_list=[]
        len_list=[]
        for target in keywords:
            t_len=min(len(target),len(line))
            dist=Levenshtein.hamming(line[:t_len],target[:t_len])
            dist_list.append(dist)
            len_list.append(t_len)
        npdist=np.array(dist_list)
        min_idx=np.array(dist_list).argmin()     
        if(dist_list[min_idx]<=1):
            if(dist_list[min_idx]==1):
                nplen=np.array(len_list)
                min_val=np.array(dist_list).min()   
                min_idx_list=np.where(npdist==min_val)
                if min_idx_list[0].size>1:
                    min_len_list=nplen[list(min_idx_list[0])]
                    min_idx=min_idx_list[0][min_len_list.argmax()]
            if(dist_list[min_idx]>0):
                logging.warning(f"将[{line}]开头纠正为[{keywords[min_idx]}]，距离{dist_list[min_idx]}")
            return keywords[min_idx]
        else:
            return None
    def match_grade(self,line):
        result=re.findall(r"等级(\d+):\s*",line)
        if result:
            return int(result[0])
        else:
            logging.error(f"[{line}]中没有等级信息。")
            return 0
    def strip_grade(self,line):
        return re.sub(r"等级\d+:\s*","",line)

    def match_percent(self,line):
        result=re.findall(r"增加(\d+)%",line)
        if result:
            return int(result[0])
        else:
            logging.error(f"[{line}]中没有增益值信息。")
            return 0
    def match_number(self,line):
        result=re.findall(r"(\d+)",line)
        if result:
            return int(result[0])
        else:
            logging.error(f"[{line}]中没有数字。")
            return 0
    def type_praser(self,line):
        for bt in self.buff_type:
            if re.findall(bt,line):
                return bt
        logging.error(f"[{line}]中没有增益类型")
        return None
    def buff_praser(self,line):
        if len(line)<10:
            logging.error(f"[{line}]太短（{len(line)}）无法解析增益信息")
            return None,0
        sbt=self.match_head(line,self.single_buff_target)
        mbt=self.match_head(line,self.multi_buff_target)
        value=self.match_percent(line)
        if sbt:
            bt=sbt
            logging.debug(f"[{line}]中解析出对[{sbt}]的单体增益{value}%")
        elif mbt:
            bt=mbt
            logging.debug(f"[{line}]中解析出对[{mbt}]的群体增益{value}%")
        else:
            bt=None
            logging.error(f"[{line}]中无法解析增益类型信息。")
        return bt,value

if __name__=="__main__":
    import json
    
    fp=open('config.json', 'r',encoding='utf-8')
    config=json.load(fp)

    fmt_string='%(asctime)s %(filename)s[line:%(lineno)d] [%(name)s] [%(funcName)s] %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,format=fmt_string)
    bp=buff_praser(config)
    lines=['民食高的收入增加100%', '企药机械的收入增加200%']
    bp.buff_praser(lines[0])
    bp.buff_praser(lines[1])

