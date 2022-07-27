# 微信聊天数据备份

**感谢项目[wechat-backup](https://github.com/greycodee/wechat-backup)实现的前端与接口逻辑，本项目大量参考并引用.**

一款微信备份工具，自动、高效、完整的备份微信聊天数据于本地，支持增量备份、聊天预览。解决空间占用过多，历史数据担心丢失或无处存放的问题。



## 一、环境准备

* Ubuntu 22 (虚拟机、实体机)
* 已ROOT的安卓手机(参考文章: <a href="https://mp.weixin.qq.com/s/Dvb16jWPX-SuJhhfkBGwmg" target="_blank">[AOH 004] 便携式Frida环境-附某考勤任意定位</a> ， 不到300RMB，搭建ROOT的Kali手机, cool~)



## 二、adb调试

ROOT手机：开发者 - 开启USB调试， 连接WIFI

PC电脑:

```
adb shell 'ip a'
adb tcpip 5555
```

Ubuntu 22(vmware):

```
adb connect ipaddress:5555
```



## 三、数据迁移

日用手机A :  设置 - 聊天 - 迁移 -  另一台设备 - 选择要迁移的聊天 - 出现二维码

ROOT手机： 登录微信账号

ROOT手机 扫码 手机A的二维码， 即可完成迁移 ， 此时A手机会退出登录



## 四、数据备份并预览

1. 初始化环境

   ```
   python3 main.py
   >> 1
   ```

2. 导出手机数据并解码与解密

   ```
   python3 main.py
   >> 2
   ```

3. 重构本地数据库

   ```
   python3 main.py
   >> 3
   ```

4. 拉起聊天查看服务器

   ```
   python3 main.py
   >> 4
   ```



## 五、增量备份

> 危险： 此功能暂未进行完整测试，先保留历史EnMicroMsg.db 勿删除

迁移进新的聊天数据后，执行'重构本地数据库'动作，新的聊天数据及资源映射关系会保存到weixin_decrypt.db中。开启新的聊天预览即可。



## 六、Video Demo

待补充



## 参考

* https://github.com/greycodee/wechat-backup/issues/11
* https://www.bilibili.com/video/BV1jQ4y1X7rP?spm_id_from=333.999.0.0&vd_source=8ce308e411dbd86b131c421595170291
* https://github.com/greycodee/wechat-backup
