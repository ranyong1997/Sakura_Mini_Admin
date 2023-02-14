 <h1 align="center">Sakura_Mini_Admin后台管理系统</h1>
<h4 align="center">🚀快速开发、✅后台多端自适应</h4> 
<p align="center">
<a href="https://www.java.com/zh-CN/download/"><img src="https://img.shields.io/badge/Python-3.8-fadf6f"> </a> 
<a href="#"> <img src="https://img.shields.io/badge/FastAPI-0.88.0-46968a"> </a>
<a target="_blank" href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker--139cff"> </a>
</p>

# 👨‍💻‍简介 Sakura_Mini_Admin

## 👻介绍
>欢迎来到Sakura_Mini_Admin后台管理系统，一个简洁轻快的后台管理框架.支持拥有多用户组的RBAC管理后台 🚀

<h1 align="center">
    <a>
        <img src="https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=春暖花开，百事可乐.;console.log(%22Hello%EF%BC%8CSakuta_MiNi_Admin%22)">  
    </a>
</h1>

## 🧐💻‍目录
```shell
├─📂 Sakura_MiNi_Admin          //服务端根目录（管理后台、接口）
│  ├─📂 back                    //后端应用
│  │  ├─📂 app                  //后台应用
│  │  │  │  ├─📄 __init__.py
│  │  │  │  ├─📄 config.py      //配置文件
│  │  │  │  ├─📄 database.py    //数据库以及连接的配置
│  │  │  ├─📂 conf              //环境应用
│  │  │  │  ├─📄 dev.env        //开发环境
│  │  │  │  ├─📄 pro.env        //线上环境
│  │  │  ├─📂 crud              //API应用
│  │  │  │  ├─📄 __init__.py
│  │  │  │  ├─📄 services.py    //接口增删改查
│  │  │  ├─📂 logs              //日志层
│  │  │  ├─📂 models            //数据库模型
│  │  │  ├─📂 router            //模块路由
│  │  │  ├─📂 schemas           //数据模型
│  │  │  ├─📂 utils             //工具目录
│  │  │  │  ├─📄 __init__.py
│  │  │  │  ├─📄 casbin.py      //权限工具
│  │  │  │  ├─ 📄 lark_test_report.py   //飞书机器人工具
│  │  │  │  ├─ 📄 logger.py     //日志工具
│  │  │  │  ├─ 📄 password.py   //哈希密码加密/解密工具
│  │  │  │  ├─ 📄 token.py      //鉴权工具
│  │  ├─📄 main.py              //项目入口文件
│  │  ├─📄 rbac_model.conf      //角色权限设计
│  ├─📂 static                  //静态目录（暂未接入）
│  ├─📂 migrations              //数据迁移（暂未接入）
│  ├─📂 tests                   //测试用例（暂未使用）
│  ├─📄 .gitignore              //gitcommit忽略文件
│  ├─📄 docker-compose.yml      //docker-compose编排
│  ├─📄 Dockerfile              //Dockerfile编排
│  ├─📄 README.md               //使用文档
│  ├─📄 requirements.txt        //项目依赖文件
│  ├─📄 start.sh                //项目运行脚本
```

## 💽部署(方式一 本地)
Git克隆或是下载压缩包。
```git
git clone https://github.com/ranyong1997/Sakura_Mini_Admin.git
```
## 环境要求
🧰服务端

| 运行环境 | 要求版本 | 推荐版本 |
| -------- | :------: | -------: |
| Python   |  >=3.8   |   3.8.10 |
| Mysql    |  >=8.0   |   8.0.24 |
| Redis    |  >=8.0   |    7.0.4 |

🧰前端

| 运行环境    |   要求版本    |    推荐版本 |
|---------|:---------:|--------:|
| Node.js | >=16.17.0 |  18.9.1 |
创建虚拟环境(win)
```python
python - m venv venv
```
![image-20230109105555094](https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202301091056655.png)

激活虚拟环境（win）
```shell
>>>cd .\venv\Scripts\
>>> .\activate
```

激活虚拟环境（Mac）
```shell
#python3默认安装virtualenv环境
>>>pip3 install virtualenv
#安装完成检测版本是否安装成功
>>>virtualenv --version
#创建虚拟环境
>>>virtualenv venv
#进入虚拟环境
>>>cd venv 
#查看当前路径
>>>pwd
eg:/Users/ranyong/Desktop/gitpush/Sakura_Mini_Admin/venv
#激活虚拟环境
>>source /Users/ranyong/Desktop/gitpush/Sakura_Mini_Admin/venv/bin/activate
#退出虚拟环境
deactivate
```

终端进入程序的根目录：
```
pip3 install -r requirements.txt
cd back
python3 main.py
```

## 💽部署(方式二 Docker)
```docker
docker-compose up -d
```
>📢注意事项：部署前请检查本地mysql端口3306是否开启，如果开启，请关闭。否则更改3306映射端口

## 🤦‍待办清单：
- [ ] 完善README文档
- [ ] 数据迁移、定时备份
- [ ] 替换异步mysql
- [ ] 日志优化输出控制台
- [ ] 引入APScheduler


## 🤦‍已办清单：
- [X] 使用Dockerfile进行构建
- [X] 使用Mysql接替sqlite
- [X] 封装mysql账号密码到config.py里面
- [X] 接入Redis
- [X] redis接入Dockerfile里

##  📢开发提交规范:
```text
✨ feat:  新增
🐞Fix: 修复
📃 docs: 文档
🦄 refactor: 重构
🎈 perf: 优化
```
## 🛰️API文档
***API文档：***
本地：[http://localhost:8000/docs](http://localhost:8000/docs)
生成
## 📸截图
***项目界面***
<details><summary>🔎点击展开截图</summary>
<div align="center">
  <img  width="80%"  src="图片地址" /><br>
</div>
</details>
<hr>