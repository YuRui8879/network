from bs4 import BeautifulSoup
import tkinter as tk
import re
import time
from apscheduler.schedulers.background import BackgroundScheduler
from submit import *
import datetime

class netdata:

    def __init__(self):
        self.flow = 0
        self.fee = 0
        self.old_flow = 0
        self.old_fee = 0
        self.rc_flag = 0
        self.stage = 0
        self.warn_flag = 0
        self.ir = 0
        self.temp_list = [0] * 60

    def check_stage(self):
        url = 'https://lgn.bjut.edu.cn/'
        strhtml = requests.get(url)
        soup = BeautifulSoup(strhtml.text, features='lxml')
        title = soup.title.text
        if '北京工业大学上网信息窗' in title:
            return 1
        else:
            return 0

    def reset_ir(self):
        self.ir = 0

    def get_stage(self):
        self.stage = self.check_stage()
        return self.stage

    def set_stage(self,stage):
        self.stage = stage

    def get_warn_flag(self):
        return self.warn_flag

    def set_warn_flag(self,warn_flag):
        self.warn_flag = warn_flag

    def set_rc_flag(self,flag):
        self.rc_flag = flag

    def get_rc_flag(self):
        return self.rc_flag

    def get_flow(self):
        return self.norm_flow(self.flow)

    def get_fee(self):
        return self.norm_fee(self.fee)

    def set_flow(self):
        self.old_flow = self.flow

    def set_fee(self):
        self.old_fee = self.fee

    def get_internal_flow(self):
        internal_flow = self.flow - self.old_flow
        return self.norm_flow(internal_flow)

    def get_internal_fee(self):
        internal_fee = (self.flow - self.old_flow)/1024*0.002
        return 'RMB ' + str(round(internal_fee,3))

    def norm_flow(self,flow_num):
        flow0 = flow_num % 1024
        flow1 = flow_num - flow0
        flow0 = flow0 * 1000
        flow0 = flow0 - flow0 % 1024
        flow3 = '.'
        if flow0 / 1024 < 10:
            flow3 = '.00'
        else:
            if flow0 / 1024 < 100:
                flow3 = '.0'

        return str(int(flow1 / 1024)) + flow3 + str(int(flow0 / 1024)) + ' MByte'

    def norm_fee(self,fee_num):
        fee1 = fee_num - fee_num % 100
        return 'RMB ' + str(fee1 / 10000)

    def get_data(self,name,password,msg = None,threshold = 1024,exe = 1):
        url = 'https://lgn.bjut.edu.cn/'
        strhtml = requests.get(url)
        soup = BeautifulSoup(strhtml.text, features='lxml')
        title = soup.title.text
        if '北京工业大学上网信息窗' in title:
            data = soup.select('script')
            flow = re.compile('flow=\'\s*[0-9]*\s*\'')
            fee = re.compile('fee=\'\s*[0-9]*\s*\'')
            fee_data = fee.findall(str(data))
            flow_data = flow.findall(str(data))
            num_mode = re.compile('[0-9]+')
            fee_num = int(num_mode.findall(str(fee_data))[0])
            flow_num = int(num_mode.findall(str(flow_data))[0])
            self.flow = flow_num
            self.fee = fee_num
            if self.warn_flag == 1:
                if self.ir < 60:
                    self.temp_list[self.ir%60] = self.flow
                else:
                    if self.flow - self.temp_list[self.ir%60] >= threshold:
                        if exe == 1:
                            msg.insert('end','60s内流量超过阈值\n')
                        else:
                            self.deconnect()
                    else:
                        self.temp_list[self.ir%60] = self.flow
                        self.ir += 1

            #print(self.flow)
            #print(self.fee)
        else:
            if self.rc_flag == 1:
                while not self.re_connect(name,password):
                    time.sleep(3)

    def re_connect(self,name,password):
        url = 'https://lgn.bjut.edu.cn/'
        header = {
            'Host':'lgn.bjut.edu.cn',
            'Connection':'keep-alive',
            'Content-Length':'77',
            'Cache-Control':'max-age=0',
            'Upgrade-Insecure-Requests':'1',
            'Origin':'https://lgn.bjut.edu.cn',
            'Content-Type':'application/x-www-form-urlencoded',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site':'same-origin',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-User':'?1',
            'Sec-Fetch-Dest':'document',
            'Referer':'https://lgn.bjut.edu.cn/',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9'
        }
        post_data = {
            'DDDDD':str(name),
            'upass':str(password),
            'v46s':'1',
            'v6ip':'',
            'f4serip':'172.30.201.10',
            '0MKKey':''
        }
        strhtml = requests.post(url,data=post_data,headers=header)
        soup = BeautifulSoup(strhtml.text,features='lxml')
        title = soup.title.text
        if '登录成功窗' in title:
            return 1
        else:
            return 0

    def deconnect(self):
        url = 'https://lgn.bjut.edu.cn/F.html'
        strhtml = requests.get(url)
        soup = BeautifulSoup(strhtml.text,features='lxml')
        title = soup.title.text
        if '信息返回窗' in title:
            return 1
        else:
            return 0

    def set_meal(self,meal,name,password):
        login_url = 'https://jfself.bjut.edu.cn/LoginAction.action'
        url = 'https://jfself.bjut.edu.cn/selfservicebookAction'
        header = self.set_header('88','https://jfself.bjut.edu.cn/LogoutAction.action')
        post_data = {
            'account':name,
            'password':password,
            'checkcode':'2651',
            'Submit':'%E7%99%BB+%E5%BD%95'
        }
        requests.post(login_url,data=post_data,headers=header)

        header = self.set_header('8','https://jfself.bjut.edu.cn/nav_servicedefaultbook')
        post_data = {
            'serid': str(meal)
        }
        requests.post(url, data=post_data, headers=header)


    def set_header(self,length,referer):
        header = {
            'Host': 'jfself.bjut.edu.cn',
            'Connection': 'keep-alive',
            'Content-Length': length,
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'https://jfself.bjut.edu.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': referer,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        return header


class gui:

    def __init__(self):
        with open('.\\config.txt','r') as f:
            self.name = f.readline().strip()
            self.password = f.readline().strip()

        self.flag = 0
        self.time_to_connect_flag = 0
        self.warn_flag = 0
        self.card_flag = 0
        self.old_flow = ''
        self.old_fee = ''
        self.begin_hour = 9
        self.begin_minute = 0
        self.end_hour = 9
        self.end_minute = 1
        self.exe_selection = 1
        self.fre_refresh = 1
        self.warn_flow_num = 1000
        self.sched = BackgroundScheduler()
        self.sched.start()

        self.top = tk.Tk()
        self.net_data = netdata()
        self.net_data.get_data(self.name,self.password)
        self.top.title('校园网监控')
        #self.top.geometry('500x300')

        text_msgbox_frame = tk.Frame(self.top)
        text_frame = tk.Frame(text_msgbox_frame,height = 100,width = 20)
        flow_tag = tk.Label(text_frame, text='已使用流量：', width=12, height=1)
        flow_tag.pack(side = tk.TOP)
        self.flow_text = tk.StringVar()
        flow = tk.Label(text_frame, textvariable=self.flow_text, width=20, height=1)
        flow.pack(side = tk.TOP)

        fee_tag = tk.Label(text_frame, text='余额：', width=12, height=1)
        fee_tag.pack(side = tk.TOP)
        self.fee_text = tk.StringVar()
        fee = tk.Label(text_frame, textvariable=self.fee_text, width=20, height=1)
        fee.pack(side = tk.TOP)

        internal_flow_tag = tk.Label(text_frame, text='区间流量：', width=12, height=1)
        internal_flow_tag.pack(side = tk.TOP)
        self.internal_flow_text = tk.StringVar()
        internal_flow = tk.Label(text_frame, textvariable=self.internal_flow_text, width=20, height=1)
        internal_flow.pack(side = tk.TOP)

        internal_fee_tag = tk.Label(text_frame, text='区间费用：', width=12, height=1)
        internal_fee_tag.pack(side = tk.TOP)
        self.internal_fee_text = tk.StringVar()
        internal_fee = tk.Label(text_frame, textvariable=self.internal_fee_text, width=12, height=1)
        internal_fee.pack(side = tk.TOP)

        text_frame.pack(side = tk.LEFT)

        msgbox_frame = tk.Frame(text_msgbox_frame,height = 100,width = 28)
        self.msgbox = tk.Text(msgbox_frame,height = 20,width = 28)
        self.msgbox.pack(side = tk.TOP)

        msgbox_frame.pack(side = tk.LEFT)

        text_msgbox_frame.pack(side = tk.TOP)

        button_frame = tk.Frame(self.top,height = 20)

        self.connectb = tk.Button(button_frame, text = '连接校园网', width = 10, height = 1, command=self.connect)
        self.connectb.pack(side=tk.LEFT,padx=5)
        if self.net_data.get_stage() == 0:
            self.connectb['text'] = '连接校园网'
            self.net_data.set_stage(1)
        else:
            self.connectb['text'] = '断开连接'
            self.net_data.set_stage(0)
        begin = tk.Button(button_frame, text='开始记录', width=10, height=1, command=self.begin_click)
        begin.pack(side=tk.LEFT,padx = 5)
        end = tk.Button(button_frame, text='停止记录', width=10, height=1, command=self.end_click)
        end.pack(side=tk.LEFT,padx = 5)
        self.reconnectb = tk.Button(button_frame, text = '自动重连：关',width = 10,height = 1,command=self.reconnect)
        self.reconnectb.pack(side = tk.LEFT,padx = 5)

        button_frame.pack(side=tk.TOP,pady = 10)

        button_frame2 = tk.Frame(self.top,height = 20)

        self.time_to_connectb = tk.Button(button_frame2,text = '定时联网：关',width = 10, height = 1, command=self.time_to_connect)
        self.time_to_connectb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')
        self.warnb = tk.Button(button_frame2,text = '流量预警：关',width = 10 ,height = 1,command = self.warn)
        self.warnb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')
        self.cardb = tk.Button(button_frame2,text = '自动打卡：关',width = 10, height = 1,command = self.card)
        self.cardb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')
        aboutb = tk.Button(button_frame2,text = '设置',width = 10, height = 1,command = self.setting)
        aboutb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')

        button_frame2.pack(side = tk.TOP)

        self.top.after(self.fre_refresh*1000, self.refresh_data)
        self.top.attributes("-topmost", True)
        self.top.mainloop()

    def about(self):
        self.msgbox.insert('end','如遇问题，可以联系yurui03@163.com\n')

    def card(self):
        if self.card_flag == 0:
            self.card_flag = 1
            self.cardb['text'] = '自动打卡：开'
            self.msgbox.insert('end','自动打卡已开启\n')
            if self.net_data.get_stage() == 0:
                self.net_data.re_connect(self.name,self.password)
            self.sched.add_job(self.submit_func,'cron',month = '1-12',day = '*',hour = 9,id = 'card')
            self.sched.print_jobs()
        else:
            self.card_flag = 0
            self.cardb['text'] = '自动打卡：关'
            self.msgbox.insert('end','自动打卡已关闭\n')
            self.sched.remove_job('card')
            self.sched.print_jobs()

    def submit_func(self):
        submit_obj = submit()
        submit_obj.login(self.name,self.password)
        res = submit_obj.submit(submit_obj.get_yesterday())
        self.msgbox.insert('end',res+'\n')

    def warn(self):
        if self.warn_flag == 0:
            self.warn_flag = 1
            self.net_data.reset_ir()
            self.warnb['text'] = '流量预警：开'
            self.msgbox.insert('end','流量预警已开启\n')
            self.net_data.set_warn_flag(1)
        else:
            self.warn_flag = 0
            self.warnb['text'] = '流量预警：关'
            self.msgbox.insert('end','流量预警已关闭\n')
            self.net_data.set_warn_flag(0)


    def time_to_connect(self):

        if self.time_to_connect_flag == 0:
            self.time_to_connect_flag = 1
            self.time_to_connectb['text'] = '定时联网：开'
            self.msgbox.insert('end','定时联网已开启\n时间区间为每日%s时%s分到%s时%s分\n' %(self.begin_hour,self.begin_minute,self.end_hour,self.end_minute))
            self.sched.add_job(self.time_to_connect_job_begin,'cron',month = '1-12',day = '*',hour = int(self.begin_hour),minute = int(self.begin_minute),id = 'begin_task')
            self.sched.add_job(self.time_to_connect_job_end,'cron',month = '1-12',day = '*',hour = int(self.end_hour),minute = int(self.end_minute),id = 'end_task')
            self.sched.print_jobs()
        else:
            self.time_to_connect_flag = 0
            self.time_to_connectb['text'] = '定时联网：关'
            self.msgbox.insert('end','定时联网已关闭\n')
            self.sched.remove_job(job_id='begin_task')
            self.sched.remove_job(job_id='end_task')
            self.sched.print_jobs()

    def time_to_connect_job_begin(self):
        self.net_data.re_connect(self.name,self.password)
        self.net_data.set_stage(1)

    def time_to_connect_job_end(self):
        self.net_data.deconnect()
        self.net_data.set_stage(0)

    def setting(self):
        self.middle = tk.Tk()
        self.middle.title('设置')

        name_title = tk.Label(self.middle,text = '配置账号密码',width = 10,height = 1)
        name_title.pack(fill = 'x',anchor = 'e',pady = 5)

        top_frame = tk.Frame(self.middle)

        name_tag = tk.Label(top_frame,text = '账号：',width = 6,height = 1)
        name_tag.pack(side = tk.LEFT)
        self.name_entry = tk.Entry(top_frame,width = 30)
        self.name_entry.pack(side = tk.LEFT)
        self.name_entry.insert(0,self.name)

        top_frame.pack(side = tk.TOP)
        middle_frame = tk.Frame(self.middle)

        password_tag = tk.Label(middle_frame,text = '密码：',width = 6,height = 1)
        password_tag.pack(side = tk.LEFT)
        self.password_entry = tk.Entry(middle_frame,width = 30)
        self.password_entry.pack(side = tk.LEFT)
        self.password_entry.insert(0,self.password)

        middle_frame.pack(side = tk.TOP)

        time_to_connect_title = tk.Label(self.middle,text = '定时联网配置（每日）',width = 10,height = 1)
        time_to_connect_title.pack(fill = 'x',pady = 5)

        time_begin_frame = tk.Frame(self.middle)

        begin_text = tk.Label(time_begin_frame,text = '开始时间',width = 6,height = 1)
        begin_text.pack(side = tk.LEFT,padx = 5)

        self.begin_hour_sp = tk.Spinbox(time_begin_frame,from_ = 0,to = 23,width = 4)
        self.begin_hour_sp.pack(side = tk.LEFT)
        self.begin_hour_sp.insert('end',self.begin_hour)
        hour = tk.Label(time_begin_frame,text = '时',width = 4,height = 1)
        hour.pack(side = tk.LEFT)
        self.begin_minute_sp = tk.Spinbox(time_begin_frame,from_ = 0, to = 60,width = 4)
        self.begin_minute_sp.pack(side = tk.LEFT)
        self.begin_minute_sp.insert('end',self.begin_minute)
        minute = tk.Label(time_begin_frame,text = '分',width = 4,height = 1)
        minute.pack(side = tk.LEFT)

        time_begin_frame.pack(side = tk.TOP)

        time_end_frame = tk.Frame(self.middle)

        end_text = tk.Label(time_end_frame, text='断开时间', width=6, height=1)
        end_text.pack(side=tk.LEFT, padx=5)

        self.end_hour_sp = tk.Spinbox(time_end_frame, from_=0, to=23, width=4)
        self.end_hour_sp.pack(side=tk.LEFT)
        self.end_hour_sp.insert('end',self.end_hour)
        hour = tk.Label(time_end_frame, text='时', width=4, height=1)
        hour.pack(side=tk.LEFT)
        self.end_minute_sp = tk.Spinbox(time_end_frame, from_=0, to=60, width=4)
        self.end_minute_sp.pack(side=tk.LEFT)
        self.end_minute_sp.insert('end',self.end_minute)
        minute = tk.Label(time_end_frame, text='分', width=4, height=1)
        minute.pack(side=tk.LEFT)

        time_end_frame.pack(side = tk.TOP)

        warn_title = tk.Label(self.middle,text = '流量预警配置',width = 10,height = 1)
        warn_title.pack(fill = 'x',pady = 5)

        warn_top_frame = tk.Frame(self.middle)

        warn_flow_text = tk.Label(warn_top_frame,text = '流量阈值',width = 6,height = 1)
        warn_flow_text.pack(side = tk.LEFT)
        self.warn_flow = tk.Spinbox(warn_top_frame,from_ = 1,to = 4096,width = 10)
        self.warn_flow.pack(side = tk.LEFT)
        self.warn_flow.insert('end','000')
        MB_text = tk.Label(warn_top_frame,text = ' MB',width = 4,height = 1)
        MB_text.pack(side = tk.LEFT)

        warn_top_frame.pack(side = tk.TOP)

        warn_middle_frame = tk.Frame(self.middle)

        exe_text = tk.Label(warn_middle_frame,text = '执行操作',width = 6,height = 1)
        exe_text.pack(side = tk.LEFT)

        self.exe_selection = tk.IntVar()
        self.exe_selection.set(1)

        tk.Radiobutton(warn_middle_frame,text = '仅提醒',variable = self.exe_selection,value = 1).pack(side = tk.LEFT)
        tk.Radiobutton(warn_middle_frame,text = '断开连接',variable = self.exe_selection,value = 2).pack(side = tk.LEFT)

        warn_middle_frame.pack(side = tk.TOP)

        fre_title = tk.Label(self.middle,text = '刷新频率(s)',width = 10,height = 1)
        fre_title.pack(fill = 'x',pady = 5)

        fre_frame = tk.Frame(self.middle)

        self.fre_selection = tk.IntVar()
        self.fre_selection.set(1)
        fre1 = tk.Radiobutton(fre_frame,text = '1',variable = self.fre_selection,value = 1,command = self.set_fre1)
        fre1.pack(side = tk.LEFT)
        fre3 = tk.Radiobutton(fre_frame,text = '3',variable = self.fre_selection,value = 5,command = self.set_fre3)
        fre3.pack(side = tk.LEFT)
        fre5 = tk.Radiobutton(fre_frame, text='5', variable=self.fre_selection, value=10,command = self.set_fre3)
        fre5.pack(side=tk.LEFT)
        fre10 = tk.Radiobutton(fre_frame, text='10', variable=self.fre_selection, value=60,command = self.set_fre3)
        fre10.pack(side=tk.LEFT)

        fre_frame.pack(side = tk.TOP)

        manu_card_text = tk.Label(self.middle,text = '打卡配置',width = 6,height = 1)
        manu_card_text.pack(fill = 'x',pady = 5)
        manu_cardb = tk.Button(self.middle,text = '手动打卡',width = 6,height = 1,command = self.submit_func)
        manu_cardb.pack(side = tk.TOP)

        ok_button = tk.Button(self.middle,text = 'OK',width = 6,height = 1,command = self.ok)
        ok_button.pack(side = tk.TOP,pady = 10)

    def set_fre1(self):
        self.fre_selection.set(1)

    def set_fre3(self):
        self.fre_selection.set(5)

    def set_fre5(self):
        self.fre_selection.set(10)

    def set_fre10(self):
        self.fre_selection.set(60)

    def ok(self):
        self.name = self.name_entry.get()
        self.password = self.password_entry.get()
        self.warn_flow_num = self.warn_flow.get()
        self.begin_hour = self.begin_hour_sp.get()
        self.begin_minute = self.begin_minute_sp.get()
        self.end_hour = self.end_hour_sp.get()
        self.end_minute = self.end_minute_sp.get()
        self.fre_refresh = self.fre_selection.get()
        with open('.\\config.txt','w') as f:
            f.write(self.name + '\n')
            f.write(self.password)
        self.middle.destroy()


    def reconnect(self):
        if self.net_data.get_stage() == 0:
            self.msgbox.insert('end','请先连接校园网\n')
        else:
            if self.net_data.get_rc_flag() == 0:
                self.net_data.set_rc_flag(1)
                self.msgbox.insert('end','自动重连已开启\n')
                self.reconnectb['text'] = '自动重连：开'
            else:
                self.net_data.set_rc_flag(0)
                self.msgbox.insert('end','自动重连已关闭\n')
                self.reconnectb['text'] = '自动重连：关'


    def connect(self):
        if self.net_data.get_stage() == 0:
            res = self.net_data.re_connect(self.name,self.password)
            if res == 0:
                self.msgbox.insert('end','请检查网络连接及账号密码\n')
            else:
                self.msgbox.insert('end','网络连接成功，开始计费\n')
                self.refresh_data()
                self.connectb['text'] = '断开连接'
                self.net_data.set_stage(1)
        else:
            if self.net_data.get_rc_flag() == 1:
                self.msgbox.insert('end', '请先关闭自动重连功能\n')
            else:
                res = self.net_data.deconnect()
                if res == 1:
                    self.msgbox.insert('end', '注销成功\n')
                    self.connectb['text'] = '连接校园网'
                    self.net_data.set_stage(0)
                else:
                    self.msgbox.insert('end', '注销失败\n')



    def begin_click(self):
        self.net_data.set_flow()
        self.net_data.set_fee()
        self.flag = 1
        self.msgbox.insert('end','记录开始\n')

    def end_click(self):
        self.flag = 2
        self.msgbox.insert('end','记录结束\n')
        self.msgbox.insert('end','本次记录已使用流量：'+self.net_data.get_internal_flow()+'\n')
        self.msgbox.insert('end','本次记录已使用费用：'+self.net_data.get_internal_fee()+'\n')

    def refresh_data(self):
        self.net_data.get_data(self.name,self.password,self.msgbox,self.warn_flow_num,self.exe_selection)
        self.flow_text.set(self.net_data.get_flow())
        self.fee_text.set(self.net_data.get_fee())

        if self.net_data.get_stage() == 0:
            self.connectb['text'] = '连接校园网'
        else:
            self.connectb['text'] = '断开连接'

        if self.flag == 0:
            self.internal_flow_text.set('0.00 MByte')
            self.internal_fee_text.set('RMB 0')
        elif self.flag == 1:
            self.old_flow = self.net_data.get_internal_flow()
            self.old_fee = self.net_data.get_internal_fee()
            self.internal_flow_text.set(self.old_flow)
            self.internal_fee_text.set(self.old_fee)
        else:
            self.internal_flow_text.set(self.old_flow)
            self.internal_fee_text.set(self.old_fee)
        self.top.after(self.fre_refresh*1000,self.refresh_data)

if __name__ == '__main__':
    g = gui()
    #net_data = netdata()
