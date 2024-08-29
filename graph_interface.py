import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog, ttk
import subprocess
import sys
import neo
import single_library
from tkinter.messagebox import showinfo, showwarning


# todo 多个项目读取
def check_condition():
    level = spinbox.get()
    path = file_entry.get()
    if path == '':
        showwarning("", "请输入项目路径或项目名")
        return False
    if combo_box.get() == '':
        # window.withdraw()
        showwarning("", "未选择语编程言")
        return False
    if level == '':
        showwarning("", "最高组件层数不能为空")
        return False
    return True, level


def open_folder():
    folder_path = filedialog.askdirectory()  # 使用askdirectory()方法选择文件夹
    file_entry.delete(0, tk.END)
    file_entry.insert(tk.END, folder_path)  # 将选择的路径插入到Entry控件中


def button_upp_clicked():
    check, level = check_condition()
    if check:
        language = combo_box.get()
        project_name = file_entry.get()
        print('project_name:', project_name)
        project_name = project_name.split('/')[-1]
        neo.find_all_relationships(project_name, label_name_covert(language), level=level)
        open_page()


def button_low_clicked():
    check, level = check_condition()
    if check:
        check_condition()
        language = combo_box.get()
        project_name = file_entry.get()
        project_name = project_name.split('/')[-1]
        neo.find_all_relationships(project_name, label_name_covert(language), relation='LOW',level=level)
        open_page()


def read_project():
    path = file_entry.get()
    if path == '':
        showwarning("", "项目路径不能为空")
        return
    res,language=single_library.parse_library(path, check_upper_relationship=False)
    if res:
        showinfo("", "读取成功")
    else:
        showwarning("", "读取失败")
    if language == 'java':
        combo_box.set('Java')
    elif language == 'python':
        combo_box.set('Python')
    elif language == 'cpp':
        combo_box.set('C++')
    elif language == 'c':
        combo_box.set('C')

def label_name_covert(language):
    if language == 'Java':
        return 'java'
    elif language == 'Python':
        return 'python'
    elif language == 'C++':
        return 'cpp'
    elif language == 'C':
        return 'c'


# 当文本框失去焦点时，改变背景色为灰色
def on_focus_out(event):
    file_entry.config(bg='gray')


def open_page(file_path='/Users/john/PycharmProjects/code_clones/network.html'):  # todo windows测试
    sys_type = sys.platform
    print(sys_type)
    if sys_type == 'win32':  # Windows
        subprocess.Popen(['start', '', file_path], shell=True)  # Windows 上打开文件的命令为 'start'
    elif sys_type.startswith('linux'):
        print('当前系统是 Linux')
    elif sys_type == 'darwin':  # Mac OS X
        subprocess.Popen(['open', file_path])  # macOS 上打开文件的命令为 'open'
    else:
        print('无法识别当前系统')

path = ''
# 创建窗口
window = tk.Tk()

# 设置窗口标题
window.title("代码组件关系图谱展示")

# 设置窗口大小为400x300像素
window.geometry("550x250")

# 设置窗口最大值为600x700像素
# window.maxsize(600, 700)

# 设置窗口最小值为200x100像素
# window.minsize(200, 100)


# 创建按钮
button_upp = tk.Button(window, text="上层组件", command=button_upp_clicked)
button_low = tk.Button(window, text="下层组件", command=button_low_clicked)
button_read = tk.Button(window, text="读取项目", command=read_project)

# 创建标签用于显示选中文件名
file_label = tk.Label(window, text="项目路径")
language_label = tk.Label(window, text="编程语言")
level_label = tk.Label(window, text="组件层数")

# 创建文本框，并应用样式配置
style = ttk.Style()
style.configure('My.TEntry', bg='white', fg='black', font=('courier', 15, 'bold'))
file_entry = ttk.Entry(window, style='My.TEntry',width=40)

# 绑定 <FocusOut> 事件到文本框
# file_entry.bind('<FocusOut>', on_focus_out)
# file_entry.pack()

# 创建文件选择按钮
file_button = tk.Button(window, text="选择", command=open_folder)
# file_button.pack()

# 下拉框
# 创建一个字符串列表，用于填充下拉框选项
options = ["Python", "Java", "C++", "C"]

# 设置下拉框默认选项
# selected_option = StringVar(window)
# selected_option.set(options[1])

# 创建下拉框
combo_box = Combobox(window, values=options,width=10)

# 数字选择框
spinbox = tk.Spinbox(window, width=2, from_=0, to=10)  # 设置数值范围为0到10


file_entry.grid(row=2, column=1, columnspan=3)
file_button.grid(row=2, column=4)

file_label.grid(row=2, column=0)
language_label.grid(row=4, column=0)
level_label.grid(row=4, column=2)

combo_box.grid(row=4, column=1)
spinbox.grid(row=4, column=3)


button_read.grid(row=3, column=2, columnspan=1)
button_upp.grid(row=8, column=1)
button_low.grid(row=8, column=3)

# 运行窗口主循环
window.mainloop()
print(path)

# /Users/john/miniforge3/envs/pytorch/lib/python3.10/site-packages
