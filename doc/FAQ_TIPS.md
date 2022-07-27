## FAQ&TIPS
### 1. adb root报错 'adbd cannot run as root in production builds'
> https://www.cnblogs.com/jeason1997/p/12410537.html

查看 adb shell getprop ro.debuggable 是否为1，不为1，执行;

```
adb shell //adb进入命令行模式
su //切换至超级用户
magisk resetprop ro.debuggable 1  //设置debuggable
stop;start; //一定要通过该方式重启
```

然后再次执行adb root即可

为什么要用到adb root而不是adb shell->su->chmod呢?

因为chmod之后恢复原来的权限很麻烦，且一旦忘记恢复，由于低权限可读，导致存在恶意软件低权限窃取数据的可能。



### 2. VSCODE GUI查看sqlite数据库
Database插件选择 sqlite文件即可



### 3. 全局搜索sqlites数据，输出匹配到特定值的表和列名
eg:
```python
import sqlite3
import os

values = ["微信"]
filename = "EnMicroMsg_plain.db"
with sqlite3.connect(filename) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for tablerow in cursor.fetchall():
        table = tablerow[0]
        cursor.execute("SELECT * FROM {t}".format(t = table))
        for row in cursor:
            for field in row.keys():
                x = row[field]
                for avalue in values:
                    try:
                        avalue_int = int(avalue)
                    except:
                        avalue_int = "luanqibazao@@@"
                    try:
                        if avalue in x:
                            print(table, field, x)
                    except:
                        pass
                    if (x == avalue) or (x==avalue_int):
                        print(table, field, x)
                    else:
                        pass
```

