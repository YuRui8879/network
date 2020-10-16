import requests
from bs4 import BeautifulSoup
import tkinter as tk
import re
import time

class netdata:

    def __init__(self):
        self.flow = 0
        self.fee = 0
        self.old_flow = 0
        self.old_fee = 0
        self.rc_flag = 0

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

    def get_data(self,name,password):
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
        with open('config.txt','r') as f:
            self.name = f.readline()
            self.password = f.readline()

        self.flag = 0
        self.old_flow = ''
        self.old_fee = ''
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

        msgbox_frame = tk.Frame(text_msgbox_frame,height = 100,width = 20)
        self.msgbox = tk.Text(msgbox_frame,height = 20,width = 20)
        self.msgbox.pack(side = tk.TOP)

        msgbox_frame.pack(side = tk.LEFT)

        text_msgbox_frame.pack(side = tk.TOP)

        button_frame = tk.Frame(self.top,height = 20)

        connect = tk.Button(button_frame, text = '连接校园网', width = 8, height = 1, command=self.connect)
        connect.pack(side=tk.LEFT,padx=5)
        begin = tk.Button(button_frame, text='开始记录', width=8, height=1, command=self.begin_click)
        begin.pack(side=tk.LEFT,padx = 5)
        end = tk.Button(button_frame, text='停止记录', width=8, height=1, command=self.end_click)
        end.pack(side=tk.LEFT,padx = 5)
        reconnectb = tk.Button(button_frame, text = '自动重连',width = 8,height = 1,command=self.reconnect)
        reconnectb.pack(side = tk.LEFT,padx = 5)

        button_frame.pack(side=tk.TOP,pady = 10)

        button_frame2 = tk.Frame(self.top,height = 20)

        deconnectb = tk.Button(button_frame2,text = '断开连接',width = 8, height = 1, command=self.deconnect)
        deconnectb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')
        settingb = tk.Button(button_frame2,text = '配置账号',width = 8 ,height = 1,command = self.setting)
        settingb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')
        mealb = tk.Button(button_frame2,text = '空',width = 8, height = 1,command = self.set_meal)
        mealb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')
        aboutb = tk.Button(button_frame2,text = '关于',width = 8, height = 1,command = self.about)
        aboutb.pack(side = tk.LEFT,padx = 5,pady = 5,anchor = 'e')

        button_frame2.pack(side = tk.TOP)

        self.top.after(1000, self.refresh_data)
        self.top.attributes("-topmost", True)
        self.top.mainloop()

    def about(self):
        self.msgbox.insert('end','如遇问题，可以联系yurui03@163.com\n')

    def set_meal(self):
        pass
        '''
        self.meal_tk = tk.Tk()
        self.meal_tk.title('设置套餐')

        self.v = tk.IntVar()

        tk.Radiobutton(self.meal_tk,text = '免费30G套餐',variable = self.v,value = 1).pack(side = tk.TOP)
        tk.Radiobutton(self.meal_tk,text = '20元45G套餐',variable = self.v,value = 2).pack(side = tk.TOP)
        tk.Radiobutton(self.meal_tk,text = '25元55G套餐',variable = self.v,value = 3).pack(side = tk.TOP)

        tk.Button(self.meal_tk,text = 'OK',width = 8,height = 1,command = self.meal_ok).pack(side = tk.TOP)
        '''


    def meal_ok(self):
        pass
        '''
        if self.v == 1:
            self.net_data.set_meal(9,self.name,self.password)
            self.msgbox.insert('end','您已选择30G流量套餐\n')
        elif self.v == 2:
            self.net_data.set_meal(32,self.name,self.password)
            self.msgbox.insert('end','您已选择45G流量套餐\n')
        else:
            self.net_data.set_meal(33,self.name,self.password)
            self.msgbox.insert('end','您已选择55G流量套餐\n')
        self.meal_tk.destroy()
        '''

    def setting(self):
        self.middle = tk.Tk()
        self.middle.title('账号密码配置')
        top_frame = tk.Frame(self.middle)

        name_tag = tk.Label(top_frame,text = '账号：',width = 6,height = 1)
        name_tag.pack(side = tk.LEFT)
        self.name_entry = tk.Entry(top_frame,width = 30)
        self.name_entry.pack(side = tk.LEFT)

        top_frame.pack(side = tk.TOP)
        middle_frame = tk.Frame(self.middle)

        password_tag = tk.Label(middle_frame,text = '密码：',width = 6,height = 1)
        password_tag.pack(side = tk.LEFT)
        self.password_entry = tk.Entry(middle_frame,width = 30)
        self.password_entry.pack(side = tk.LEFT)

        middle_frame.pack(side = tk.TOP)

        ok_button = tk.Button(self.middle,text = 'OK',width = 6,height = 1,command = self.ok)
        ok_button.pack(side = tk.TOP,pady = 10)

    def ok(self):
        self.name = self.name_entry.get()
        self.password = self.password_entry.get()
        with open('config.txt','w') as f:
            f.write(self.name + '\n')
            f.write(self.password)
        self.middle.destroy()

    def deconnect(self):
        if self.net_data.get_rc_flag() == 1:
            self.msgbox.insert('end','请先关闭自动重连功能\n')
        else:
            res = self.net_data.deconnect()
            if res == 1:
                self.msgbox.insert('end','注销成功\n')
            else:
                self.msgbox.insert('end','注销失败\n')

    def reconnect(self):

        if self.net_data.get_rc_flag() == 0:
            self.net_data.set_rc_flag(1)
            self.msgbox.insert('end','自动重连已开启\n')
        else:
            self.net_data.set_rc_flag(0)
            self.msgbox.insert('end','自动重连已关闭\n')


    def connect(self):
        res = self.net_data.re_connect(self.name,self.password)
        if res == 0:
            self.msgbox.insert('end','请检查网络连接及账号密码\n')
        else:
            self.msgbox.insert('end','网络连接成功，开始计费\n')
            self.refresh_data()


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
        self.net_data.get_data(self.name,self.password)
        self.flow_text.set(self.net_data.get_flow())
        self.fee_text.set(self.net_data.get_fee())
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
        self.top.after(1000,self.refresh_data)

if __name__ == '__main__':
    g = gui()
    #net_data = netdata()
