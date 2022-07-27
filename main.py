from createenv import main as c_main
from dumpdata import main as d_main
from builddb import main as b_main
from api import main as a_main

print("确保adb仅接1台手机; 确保手机已ROOT (当前仅支持登录一个账号备份的场景)")
choose_ = input("[1]初始化环境 [2]导出手机数据并解码与解密 [3]重构本地数据库 [4]拉起聊天查看服务器:\n")

if choose_ == "1":
    c_main()
elif choose_ == "2":
    d_main()
elif choose_ == "3":
    b_main()
elif choose_ == "4":
    a_main()
