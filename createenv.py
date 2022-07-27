import os

def main():
    i_ = input("请阅读build.sh, 其存在rm动作，确保可以继续执行输入 Y:\n")
    if i_.lower() == "y":
        os.system("bash build.sh")