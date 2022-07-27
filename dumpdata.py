import os
import hashlib
import subprocess

def md5_(content):
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()

def checkadbconnect():
    osresult = os.popen("adb root").read().strip()
    if osresult == "restarting adbd as root" or osresult == "adbd is already running as root":
        return True
    else:
        return False

def getpassword():
    osresult = os.popen("adb shell 'cat /data/data/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml'").read()
    uin = osresult.split('<int name="_auth_uin" value="',1)[1].split('"',1)[0]

    IMEI = ["1234567890ABCDEF"]

    osresult = os.popen("""adb shell 'service call iphonesubinfo 1 | cut -c 52-66 | tr -d ".[:space:]"'""").read().strip()
    if "iphonesubinfo does not exist" not in osresult:
        IMEI.append(osresult)
    
    result_ = []
    for oneIEMI in IMEI:
        result_.append(md5_("{}{}".format(oneIEMI,uin).encode())[:7])
    
    inputpassword = input("给出你手工计算得到的密码(无需补充可不填):\n")
    inputpassword = inputpassword.strip()
    if inputpassword != "":
        result_.append(inputpassword)
    return result_

def get32bits(pathlist):
    result_ = []
    for onepath in pathlist:
        osresult = os.popen("adb shell 'ls -a {}'".format(onepath)).read()
        for oneflodername in osresult.split("\n"):
            if len(oneflodername) == 32 and oneflodername.isascii() and oneflodername == oneflodername.lower():
                result_.append(oneflodername)
    return result_

def decrypt_db(passwords):
	# https://gist.github.com/greycodee/255e5adcc06f698cdb1ded6166d5607a
    dbname = "EnMicroMsg.db"
    fn = dbname.split(".")[0]
    fpn = "EnMicroMsg_plain.db"
    for onepass in passwords:
        command = """
        PRAGMA key = '{}';\r\n
        PRAGMA cipher_use_hmac = off;\r\n
        PRAGMA kdf_iter = 4000;\r\n
        PRAGMA cipher_page_size = 1024;\r\n
        PRAGMA cipher_hmac_algorithm = HMAC_SHA1;\r\n
        PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;\r\n
        ATTACH DATABASE '{}' AS {} KEY '';\r\n
        SELECT sqlcipher_export('{}');\r\n
        DETACH DATABASE {};\r\n
        .exit\r\n
        """.format(onepass, fpn , fn+"plain" ,fn+"plain", fn+"plain")
        program = subprocess.Popen(["/usr/bin/sqlcipher",dbname], stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        [out,err] = program.communicate((command).encode())
        if b'file is encrypted or is not a database' in err:
            continue
        else:
            return onepass
    return False

def decompress_voice(floderpath):
	# https://github.com/greycodee/wechat-backup/edit/master/silkV3-decoder.dockerfile
    for (root,dirs,files) in os.walk(floderpath, topdown=True):
        for file_ in files:
            thisfile = root+"/"+file_
            if thisfile[-4:] != ".mp3":
                os.system("bash converter.sh {} mp3".format(thisfile))


def main():
    path1 = "/data/data/com.tencent.mm/MicroMsg/"
    path2 = "/data/media/0/Android/data/com.tencent.mm/MicroMsg/"
    pathlist = [path1, path2]

    if checkadbconnect() == False:
        print("adb not connect; adb connect multi; adb root failed")
        exit()

    floder32 = get32bits(pathlist)
    passwords = getpassword()

    to_clone = [
        "image2",
        "video",
        "avatar",
        "voice2",
        "EnMicroMsg.db",
        "WxFileIndex.db"
    ]
    try:
        os.mkdir("./tmp")
    except:
        pass
    os.chdir("./tmp")
    for oneclone in to_clone:
        for onefloder in floder32:
            for path in pathlist:
                # (已测试)说明：同名目录，若是本地已有，是新增到目录中而非覆盖，除非重复目录下有重名文件才会覆盖
                os.system("adb pull {}/{}/{} .".format(path,onefloder,oneclone))
    os.system("adb pull /sdcard/Android/data/com.tencent.mm/MicroMsg/Download .")

    # 解密数据库
    realpass = decrypt_db(passwords)
    if realpass == False:
        print("No GOOD Password")
        exit()
    else:
        print("password is {}".format(realpass))
    os.chdir("..")

    # 解码语音
    decompress_voice("./tmp/voice2/")