import json
import requests
import time
import re
import random
import os

session = requests.session()


def is_set_account():
    if os.path.exists("daka.json"):
        return True
    else:
        return False


def set_account():

    print("第一次运行程序，请填写下面的打卡必要信息")
    jkzk = input(r'请输入个人健康状况，仅数字("正常":"1", "发热", "2", "咳嗽":"3", "头疼":"4", "乏力":"5", "胸闷":"6", "厌食":"11", "腹泻":"8", "呼吸困难":"7", "新冠肺炎疑似病例":"10", "新冠肺炎确诊病例":"9", "新冠肺炎无症状感染者":"12"): ')
    xrywz = input(
        r'请输入现人员位置，仅数字("在校 ":"1", "在苏州":"2", "江苏省其他地区":"5", "在境外、在中高风险地区":"37", "在中高风险地区所在城市":"39", "在其他地区":"38"): ')
    username = input("请输入学号: ")
    pwd = input("请输入密码: ")

    print("--------以下内容为填报上传的地址信息，按打卡网站填写即可--------")
    sheng = input("请输入所在省: ")
    shi = input("请输入所在市: ")
    qu = input("请输入所在区: ")
    jtdz = input("请输入具体地址: ")
    account = {"jkzk": jkzk, "xrywz": xrywz,
               "username": username, "password": pwd, "dz": {"sheng": sheng, "shi": shi, "qu": qu, "jtdz": jtdz}}
    account_file = open("daka.json", "w")
    account_file.write(json.dumps(account))
    account_file.close()
    print("设置成功！\n账号:{:}\n密码:{:}".format(
        username, pwd))


def read_account():
    account_file = open("daka.json", "r")
    account_data = json.load(account_file)
    account_file.close()
    return account_data


if not is_set_account():
    set_account()

config = read_account()

###### 登录 ######

# 第一轮跳转
url1 = "http://dk.suda.edu.cn/default/work/suda/jkxxtb/dkjl.jsp"
headers1 = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36 Edg/97.0.1072.76",
    "Host": "dk.suda.edu.cn",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
response1 = session.get(url1, headers=headers1,
                        verify=False, allow_redirects=False)

# 跳转到登录页面
url2 = "http://auth.suda.edu.cn/cas/login?service=http%3A%2F%2Fdk.suda.edu.cn%2Fdefault%2Fwork%2Fsuda%2Fjkxxtb%2Fdkjl.jsp%3Bdefault%3D" + \
    response1.cookies.get('default')
response2 = session.get(url2, headers=headers1,
                        verify=False, allow_redirects=False)

# 发送登录POST
headers3 = headers1
headers3['Referer'] = "http://auth.suda.edu.cn/cas/login?service=http%3A%2F%2Fdk.suda.edu.cn%2Fdefault%2Fwork%2Fsuda%2Fjkxxtb%2Fdkjl.jsp"
headers3['Origin'] = "http://auth.suda.edu.cn"
headers3['Content-Length'] = "143"
headers3['Content-Type'] = "application/x-www-form-urlencoded"
pid = re.findall(r'value="CAS_.+"', response2.text)[0][7:-1]
lt = re.findall(r'value="LT-.+"', response2.text)[0][7:-1]
execution = re.findall(r'"execution" value="(.+)"', response2.text)[0]
data_packet = {
    "username": config.get('username'),
    "password": config.get('password'),
    "pid": pid,
    "source": "cas",
    "execution": execution,
    "_eventId": "submit",
    "lt": lt
}
response = session.post(url2, data=data_packet, headers=headers3, verify=False)
if response.text.find("打卡记录") != -1:
    print("登录成功！")
else:
    print("登录失败，请检查学号密码是否正确")
    exit()


###### 打卡 ######

urlBase = "http://dk.suda.edu.cn/default/work/suda/jkxxtb/com.sudytech.work.suda.jkxxtb.jkxxcj.queryNear.biz.ext"
HeadersBase = {"Host": "dk.suda.edu.cn",
               "Connection": "keep-alive",
               "Cache-Control": "max-age=0",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Mobile Safari/537.36 Edg/98.0.1108.43",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"}
responseBase = session.get(urlBase, headers=HeadersBase)
near_data = json.loads(responseBase.text).get('list')[0]

url = "http://dk.suda.edu.cn/default/work/suda/jkxxtb/com.sudytech.work.suda.jkxxtb.jkxxcj.saveOrUpdate.biz.ext"
Headers = {"Host": "dk.suda.edu.cn",
           "Connection": "keep-alive",
           "Origin": "http://dk.suda.edu.cn",
           "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36 Edg/97.0.1072.76",
           "X-Requested-With": "XMLHttpRequest",
           'Content-Type': 'text/json'}

Post_Data = {"params":
             {"sqrid": near_data.get('SQRID'),
              "sqbmid": near_data.get('SQBMID'), "rysf": near_data.get('RYSF'), "sqrmc": near_data.get('SQRMC'), "gh": near_data.get('GH'),
              "sfzh": near_data.get('SFZH'),
              "sqbmmc": near_data.get('SQBMMC'),
              "xb": near_data.get('XB'),
              "jgshen": near_data.get('JGSHEN'),
              "jgshi": near_data.get('JGSHI'),
              "jgqu": near_data.get('JGQU'),
              "xhjshen": near_data.get('XHJSHEN'),
              "xhjshi": near_data.get('XHJSHI'),
              "xhjqu": near_data.get('XHJQU'),
              "nl": near_data.get('NL'),
              "lxdh": near_data.get('LXDH'),
              "xjzdz": near_data.get('XJZDZ'),
              "xq": near_data.get('XQ'),
              "xxss": "",
              "hcrq": "",
              "hccc": "",
              "ljqk": "",
              # 填报日期
              "tbrq": time.strftime("%Y-%m-%d", time.localtime(time.time())),
              # 腋测法体温正常值是36-37℃，口测法体温正常值是36.3-37.2℃，而肛测法体温的正常值是36.5-37.7℃
              # 这里取腋测法的保守值36.2-36.8℃
              "swtw": str(round(random.uniform(36.2, 36.8), 1)),
              "xwtw": str(round(random.uniform(36.2, 36.8), 1)),
              "jkzk": "[\""+config.get("jkzk", 1)+"\"]",
              "xrywz": config.get("xrywz", 5),
              # jtdzshen=具体地址省？省不是后鼻音吗...这里要吐槽下命名变量的程序员的语文水平
              "jtdzshen": config["dz"].get('sheng'),
              "jtdzshi": config["dz"].get('shi'),
              "jtdzqu": config["dz"].get('qu'),
              "jtdz": config["dz"].get('jtdz'),
              "sfyxglz": "否",  # 是否医学隔离中
              "yxgcts": "",
              "glfs": "",
              "zzjc": "",
              "tw": "",
              "mrxz": "",
              "ycqkhb": "",
              "sfywc": "否",  # 是否有外出
              "sfywcdq": "",
              "sfywcjtgj": "",
              "sfygrzjcg": "否",  # 是否与新冠确诊病例/无症状感染者接触过
              "sfygrzjcgjtdd": "",
              "sfyxcgjjc": "否",  # 是否与新冠确诊病例/无症状感染者有行程轨迹交叉
              "sfyxcgjjcgj": "",
              "sfyzgfxljs": "否",  # 是否有中高风险地区旅居史（包括途径中高风险地区）
              "sfyzgfxljsjtdd": "",
              "sfyzgfxryjc": "否",  # 是否与中高风险地区人员接触
              "sfyzgfxryjcsj": "",
              "sfyzgfxryjcdd": "",
              "bz": "",
              "_ext": "{}",
              # 这里填打卡时间，但实测乱填也可以...会按照服务器时间打卡，但是日期必须填当天的
              "tjsj": time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())),
              "fxsj": "",
              "yjzt": 0}}
reply = session.post(url, data=json.dumps(Post_Data), headers=Headers)
if reply.text.find(r'"success":true') != -1:
    print("打卡成功！时间：", time.strftime(
        "%Y-%m-%d %H:%M", time.localtime(time.time())))
elif reply.text.find(r'rollback-only') != -1:
    print("今天已经打过卡了，请勿重复打卡")
else:
    print("打卡失败")
    print(reply.text)

input("按回车键退出程序")
