# WordWise
import os
import platform
import shutil
import subprocess
import tkinter
import tkinter.ttk
from tkinter import filedialog
from tkinter import messagebox

import jieba

fileNameDic = {}  # file 文件夹下的文件名作为键；jieba 分词结果作为值
themeName = ["化学", "英语", "语文", "数学", "解题", "审题", "自学", "计划", "错题", "家长"]  # 主题名称的值
themeNameJieba = {}  # 主题名称的分词结果
fileClassify = {}  # 分类结果：主题名称作为键；文件名列表作为值
file_dir = "./file/"  # 被分类文件所在位置

# 对当前已有主题进行分词处理
for theme in themeName:
    temp = []
    for i in range(len(theme) - 1):
        temp.append(theme[i:i + 2])
    themeNameJieba[theme] = temp


def classify(name):  # 对指定文件进行分词与分类
    words = jieba.lcut(open(file_dir + name, "r", encoding="utf-8").read())
    fileNameDic[name] = words
    for key in themeNameJieba.keys():
        for value in themeNameJieba[key]:
            count = 0
            for i in words:
                if value == i:
                    count += 1
            if count >= 2:
                try:
                    temp_list = fileClassify[key]
                    temp_list.append(name)
                    fileClassify[key] = temp_list
                except KeyError:
                    temp_list = [name]
                    fileClassify[key] = temp_list


def classify_all():  # 对当前所有文件进行分词处理
    global fileClassify
    fileClassify = {}
    for _, _, files in os.walk(file_dir):
        for name in files:
            classify(name)


classify_all()

top = tkinter.Tk()
top.title("WordWise")  # 窗体标题
top.configure(bg="#282C34")  # 窗体颜色
top.iconphoto(False, tkinter.PhotoImage(file='icon.png'))  # 窗体图标
top.resizable(0, 0) #Don't allow resizing in the x or y direction

title = tkinter.Label(top, text="文本内容归档辅助系统", font=("微软雅黑", 40), justify="center")
title.grid(row=0, columnspan=2, sticky=tkinter.NSEW)

themeList = tkinter.LabelFrame(top, relief="groove", text="主题列表", labelanchor="n")
themeList.grid(row=1, column=0, sticky=tkinter.NSEW)


def open_file(event=None):
    file_name = fileList.get(tkinter.ACTIVE)
    file_path = file_dir + file_name

    if platform.system() == 'Darwin':  # macOS
        subprocess.call(('open', file_path))
    elif platform.system() == 'Windows':  # Windows
        os.startfile(file_path)
    else:  # linux variants
        subprocess.call(('xdg-open', file_path))


fileFrame = tkinter.LabelFrame(top, relief="groove", text="主题内容列表", labelanchor="n")
fileFrame.grid(row=2, columnspan=2, sticky=tkinter.NSEW)

listScrollbar = tkinter.Scrollbar(fileFrame)
listScrollbar.grid(row=0, column=1, sticky=tkinter.N + tkinter.S + tkinter.W)
fileList = tkinter.Listbox(fileFrame, width=60)
fileList.bind("<Double-Button-1>", open_file)
fileList.configure(yscrollcommand=listScrollbar.set)
listScrollbar.config(command=fileList.yview)
fileList.grid(row=0, column=0, sticky=tkinter.NSEW)


def show_list(name):  # 更新列表显示当前选中主题
    fileList.delete(0, "end")
    for item in fileClassify.get(name, []):
        fileList.insert("end", item)


class ThemeButton:  # 定义主题按钮
    def __init__(self, name, row, column):
        self.button = tkinter.ttk.Button(themeList,
                                         text=name,
                                         command=lambda: show_list(name))
        self.button.configure()
        self.button.grid(row=row, column=column)


buttonList = [
    ThemeButton(name=themeName[i], row=i // 5, column=i - (i // 5) * 5)
    for i in range(10)
]
buttonRow, buttonColumn = 2, 4


def add_theme():  # 新增主题
    class MyCollectApp(tkinter.Toplevel):  # 获取输入
        def __init__(self):
            super().__init__()  # 重点
            self.title("新增主题")
            self.setupUI()

        @staticmethod
        def classify_new_theme(new_theme):
            themeName.append(new_theme)
            # 对新主题进行分词处理
            temp = []
            for i in range(len(new_theme) - 1):
                temp.append(new_theme[i:i + 2])
            themeNameJieba[new_theme] = temp
            # 添加按钮
            global buttonRow, buttonColumn, buttonList, ThemeButton
            buttonColumn = buttonColumn + 1
            if buttonColumn == 5:
                buttonColumn = 0
                buttonRow += 1
            buttonList.append(
                ThemeButton(name=new_theme, row=buttonRow, column=buttonColumn))
            # 遍历所有文件进行分词
            classify_all()

        def setupUI(self):
            row1 = tkinter.Frame(self)
            row1.grid(row=0)
            l1 = tkinter.Label(row1, text="新增主题名:", height=2, width=10)
            l1.grid(row=0, column=0)
            self.xls_text = tkinter.StringVar()
            tkinter.Entry(row1,
                          textvariable=self.xls_text).grid(row=0,
                                                           column=1,
                                                           sticky=tkinter.EW)
            row2 = tkinter.Frame(self)
            row2.grid()
            tkinter.Button(row2, text="点击确认",
                           command=self.on_click).grid(row=1)

        def on_click(self):
            global newTheme
            newTheme = self.xls_text.get().lstrip()
            if len(newTheme) == 0:
                messagebox.showwarning(title='系统提示', message="请输入新增主题名!")
                self.quit()
                self.destroy()
                return False
            try:
                themeName.index(newTheme)
                messagebox.showwarning(title='系统提示', message="已存在该主题!")
                self.quit()
                self.destroy()
            except ValueError:
                self.classify_new_theme(newTheme)
                self.quit()
                self.destroy()

    var_box = tkinter.messagebox.askyesno(
        title='系统提示', message="是否需要新增主题")  # 返回'True','False'
    if var_box:
        app = MyCollectApp()
        app.mainloop()


def add_file():
    choose_file = tkinter.Tk()
    choose_file.withdraw()
    filepath = filedialog.askopenfilename()  # 获得选择好的文件
    print('Filepath:', filepath)

    def mycopyfile(srcfile, dstpath):  # 复制函数
        # srcfile 需要复制、移动的文件
        # dstpath 目的地址
        _, fname = os.path.split(srcfile)  # 分离文件名和路径
        shutil.copy(srcfile, dstpath + fname)  # 复制文件
        print("copy %s -> %s" % (srcfile, dstpath + fname))
        classify(fname)  # 直接进行分词分类

    mycopyfile(filepath, file_dir)  # 复制文件


fileFunction = tkinter.LabelFrame(top, relief="groove", text="功能", labelanchor="n")
fileFunction.grid(row=1, column=1, sticky=tkinter.NSEW)

addThemeButton = tkinter.ttk.Button(fileFunction, text="新增主题", command=add_theme)
addThemeButton.grid(row=0, column=0)
addFileButton = tkinter.ttk.Button(fileFunction, text="添加文件", command=add_file)
addFileButton.grid(row=1, column=0)

top.mainloop()
