import tkinter as tk
from tkinter import ttk, messagebox
import requests
import configparser
import os
import threading
from tkinter import font


class LightLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("科文校园网认证助手")
        #顶部图标可自行更换
        #self.root.iconbitmap('kwxy.ico')
        self.root.geometry("350x500")
        self.config_file = 'config.ini'
        # 在这里改你校园网对应的登陆地址
        self.auth_url = "http://10.110.6.251/eportal/?c=ACSetting&a=Login"
        # 在这里对校园网的运营商登陆接口进行配置，可以在网页登陆界面查看源码（这里用的是哆点“广州城市热点”）
        self.operators = {
            '校园用户': '@xyw',
            '校园电信': '@dx',
            '校园联通': '@lt',
            '校园其他': ''
        }

        # 初始化Tk变量
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.operator = tk.StringVar()
        self.remember = tk.BooleanVar()

        # 设置界面
        self.create_widgets()
        self.load_config()
        self.check_network_status()

    def create_widgets(self):
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=25, pady=20, fill=tk.BOTH, expand=True)

        # 标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=15, fill=tk.X)
        ttk.Label(title_frame,
                  text="科文校园网络认证系统",
                  font=font.Font(family="微软雅黑", size=14, weight="bold"),
                  foreground="#2196F3").pack()

        # 网络状态面板
        status_frame = ttk.LabelFrame(main_frame, text="网络状态监测")
        status_frame.pack(pady=10, fill=tk.X)

        self.status_icons = {
            "intranet": {"text": "内网连接", "label": ttk.Label(status_frame)},
            "internet": {"text": "外网连接", "label": ttk.Label(status_frame)},
        }

        for i, (key, value) in enumerate(self.status_icons.items()):
            ttk.Label(status_frame,
                      text=value["text"],
                      font=font.Font(family="微软雅黑", size=10)).grid(row=0, column=i * 3, padx=5)
            value["label"].grid(row=0, column=i * 3 + 1, padx=5)
            value["label"].config(text="⏳ 检测中...",
                                  foreground="#9E9E9E",
                                  font=font.Font(family="微软雅黑", size=10))

        # 登录表单
        form_frame = ttk.LabelFrame(main_frame, text="认证信息")
        form_frame.pack(pady=15, fill=tk.X)

        form_elements = [
            ("账号", self.username, False),
            ("密码", self.password, True),
            ("运营商", self.operator, False)
        ]

        for label_text, tk_var, is_password in form_elements:
            row_frame = ttk.Frame(form_frame)
            row_frame.pack(pady=8, fill=tk.X)

            ttk.Label(row_frame,
                      text=label_text,
                      width=8,
                      font=font.Font(family="微软雅黑", size=10)).pack(side=tk.LEFT)

            if label_text == "密码":
                entry = ttk.Entry(row_frame, show="*", textvariable=tk_var)
            elif label_text == "运营商":
                entry = ttk.Combobox(row_frame,
                                     textvariable=tk_var,
                                     values=list(self.operators.keys()))
                entry.current(0)
            else:
                entry = ttk.Entry(row_frame, textvariable=tk_var)

            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 记住密码
        ttk.Checkbutton(form_frame,
                        text="记住登录信息",
                        variable=self.remember).pack(pady=8)

        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame,
                   text="立即登录",
                   command=self.start_login,
                   width=12).pack(side=tk.LEFT, padx=8)

        ttk.Button(btn_frame,
                   text="断开连接",
                   command=self.logout,
                   width=12).pack(side=tk.LEFT, padx=8)

        # 状态栏
        self.status_bar = ttk.Frame(self.root, height=28)
        self.status_text = ttk.Label(self.status_bar,
                                     text="就绪"
                                          "        本项目完全开源，编译时可删去此段",
                                     anchor=tk.W,
                                     font=font.Font(family="微软雅黑", size=10),
                                     foreground="#616161")
        self.status_text.pack(fill=tk.X, padx=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file)
                self.username.set(config.get('DEFAULT', 'username', fallback=''))
                self.password.set(config.get('DEFAULT', 'password', fallback=''))
                self.operator.set(config.get('DEFAULT', 'operator', fallback='校园用户'))
                self.remember.set(config.getboolean('DEFAULT', 'remember', fallback=False))
            except Exception as e:
                messagebox.showerror("配置错误", f"读取配置文件失败: {str(e)}")

    def save_config(self):
        try:
            config = configparser.ConfigParser()
            config['DEFAULT'] = {
                'username': self.username.get() if self.remember.get() else '',
                'password': self.password.get() if self.remember.get() else '',
                'operator': self.operator.get(),
                'remember': str(self.remember.get())
            }
            with open(self.config_file, 'w') as f:
                config.write(f)
        except Exception as e:
            messagebox.showerror("保存错误", f"无法保存配置: {str(e)}")

    def check_network_status(self):
        def check():
            try:
                requests.get("http://10.110.6.251", timeout=1)
                self.status_icons["intranet"]["label"].config(
                    text="✓ 已连接",
                    foreground="#4CAF50")
            except:
                self.status_icons["intranet"]["label"].config(
                    text="✗ 未连接",
                    foreground="#F44336")

            try:
                requests.get("https://www.baidu.com", timeout=1)
                self.status_icons["internet"]["label"].config(
                    text="✓ 已连接",
                    foreground="#4CAF50")
            except:
                self.status_icons["internet"]["label"].config(
                    text="✗ 未连接",
                    foreground="#F44336")
            try:
                requests.get("http://10.110.222.1", timeout=1)
                self.status_icons["intranet"]["label"].config(
                    text="✓ 已连接",
                    foreground="#4CAF50")
            except:
                self.status_icons["intranet"]["label"].config(
                    text="✗ 未连接",
                    foreground="#F44336")

        threading.Thread(target=check).start()

    def start_login(self):
        username = self.username.get()
        password = self.password.get()
        operator = self.operators[self.operator.get()]

        if not username or not password:
            messagebox.showerror("输入错误", "请填写完整的登录信息")
            return

        self.update_status("正在连接认证服务器...", "#2196F3")
        threading.Thread(target=self.do_login, args=(username, password, operator)).start()

    def do_login(self, username, password, operator):
        try:
            full_username = f"{username}{operator}"
            data = {
                'DDDDD': full_username,
                'upass': password,
                '0MKKey': '123456',
                'R1': '0',
                'R2': '',
                'R3': operator,
                'R6': '0',
                'para': '00',
                'terminal_type': '1',
                'lang': 'zh-cn'
            }

            response = requests.post(self.auth_url, data=data)
            if "认证成功" in response.text:
                self.save_config()
                self.update_status("认证成功！网络已连接", "#4CAF50")
                messagebox.showinfo("认证成功", "您已成功接入校园网络")
            else:
                self.update_status("认证失败，请检查信息", "#F44336")
                messagebox.showerror("认证失败", "请检查账号密码或运营商选择")
        except Exception as e:
            self.update_status(f"连接失败：{str(e)}", "#F44336")
            messagebox.showerror("网络错误", "无法连接到认证服务器")

    def logout(self):
        try:
            requests.get("http://10.110.6.251/eportal/?c=ACSetting&a=Logout")
            self.update_status("已断开网络连接", "#616161")
            messagebox.showinfo("断开成功", "您已退出校园网络")
        except Exception as e:
            messagebox.showerror("操作失败", f"注销失败：{str(e)}")
        # 这里可以改成你自己的，本项目完全开源，你可以随意使用，切记不可商用
        self.update_status("Built By ZYF       zyfup@foxmail.com", "#616161")

    def update_status(self, message, color=None):
        self.status_text.config(text=message, foreground=color or "#37474F")


if __name__ == "__main__":
    root = tk.Tk()
    app = LightLoginApp(root)
    root.mainloop()