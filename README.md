# JiaGuoMeng
家国梦自动机器人，基本实现无人值守运行

拜访计算源于：https://github.com/WANGPeisheng1997/JiaGuoMengCalculator
修改了几个BUG，请使用fork版本https://github.com/saintfly/JiaGuoMengCalculator

## 特性
- 计算优化布局，调整布局并升级建筑。
- 自动收集金币
- 自动升级政策，完成任务

## 使用方法

- 搭建python环境
	1. 访问[python官网](https://www.python.org/downloads/windows/)
	2. 在导航栏中依次点击Downloads----Windows
	3. 在Stable Releases条目下选择最新版的windows安装程序（后缀executable installer）下载（32位64位自行选择）
	4. 安装首页勾选 Add Python to Path 点击Install Now（推荐）或自定义路径
	5. 打开cmd，输入python -V，出现版本号为安装成功
	6. 安装依赖模块numpy scipy tqdm pandas pytesseract等，缺啥装啥。

- 问题
　　出现其他类似:`ModuleNotFoundError: No module named 'numpy'`的提示，参照环境搭建第六条输入`python -m pip install --user 模块名`并回车

- 运行环境
	使用PC下windows环境，安装腾讯手游助手https://syzs.qq.com/，分辨率1024x576，DPI 160。代码做了分辨率适配，但其他分辨率情况未测试。
	安装文字识别工具tesseract和汉字识别数据https://github.com/tesseract-ocr/tesseract，注意修改pyautogui_ext.py中的路径或者删除前述路径，添加PATH。在5.0alpha版本下，安装在C盘测试过。
	屏保请设置启动时间大于5分钟。为避免火车刷不出来，凌晨会重启模拟器，运行会停止5分钟，此时若出现屏保程序会出错。

- 运行方法
	克隆本项目和增加修改补丁的摆放计算器https://github.com/saintfly/JiaGuoMengCalculator，放到同一个目录下。在本项目目录下执行python auto_jgm.py

## 更新记录
2019/11/15 首次公开发布

