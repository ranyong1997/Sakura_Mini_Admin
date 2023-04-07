 <h1 align="center">Sakura_Mini_Admin后台管理系统</h1>
<h4 align="center">🚀快速开发、✅后台多端自适应</h4> 
<p align="center">
<a href="https://www.java.com/zh-CN/download/"><img src="https://img.shields.io/badge/Python-3.8-fadf6f"> </a> 
<a href="#"> <img src="https://img.shields.io/badge/FastAPI-0.88.0-46968a"> </a>
<a target="_blank" href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker--139cff"> </a>
</p>

# 👨‍💻‍简介 Sakura_Mini_Admin

## 👻介绍

> 欢迎来到Sakura_Mini_Admin后台管理系统，一个简洁轻快的后台管理框架.支持拥有多用户组的RBAC管理后台 🚀

<h1 align="center">
    <a>
        <img src="https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=春暖花开，百事可乐.;console.log(%22Hello%EF%BC%8CSakuta_MiNi_Admin%22)">  
    </a>
</h1>

## Built with

* [![Python][Python]][python-url] 
* [![FastAPI][FastAPI]][fastapi-url]
* [![Pydantic][Pydantic]][pydantic-url]
* [![Uvicorn][uvicorn]][uvicorn-url]
* [![Redis][redis]][redis-url]
* [![jwt][jwt]][jwt-url]
* [![Pytest][pytest]][pytest-url]
* [![Nginx][Nginx]][Nginx-url]
* [![Pycharm][Pycharm]][Pycharm-url]
* [![Markdown][Markdown]][Markdown-url]
* [![Swagger][Swagger]][Swagger-url]
* ELK
* Mysql
* Casbin
* Httprunner
* Docker

## 🧐💻‍目录

```shell
├─📂 Sakura_MiNi_Admin          //服务端根目录（管理后台、接口）
│  ├─📂 back                    //后端应用
│  │  ├─📂 app                  //后台应用
│  │  │  │  ├─📄 __init__.py
│  │  │  │  ├─📄 config.py      //配置文件
│  │  │  │  ├─📄 mysql.py    //数据库以及连接的配置
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
│  ├─📂 hrun_proj               //httprunner工程
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

| 运行环境   | 要求版本  |   推荐版本 |
|--------|:-----:|-------:|
| Python | >=3.8 | 3.8.10 |
| Mysql  | >=8.0 | 8.0.24 |
| Redis  | >=8.0 |  7.0.4 |

🧰前端

| 运行环境    |   要求版本    |   推荐版本 |
|---------|:---------:|-------:|
| Node.js | >=16.17.0 | 18.9.1 |

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

> 📢注意事项：部署前请检查本地mysql端口3306是否开启，如果开启，请关闭。否则更改3306映射端口

## 🤦‍待办清单：
- [ ] 完善README文档
- [ ] 一个功能单独开一个分支
- [ ] 数据迁移、定时备份
- [ ] 替换异步mysql
- [ ] 日志优化输出控制台
- [ ] 单元测试
- [ ] 增加Jenkinsfile打包
- [ ] 新增修改密码移除redisToken缓存
- [ ] 数据库自定义创建表、字段
- [ ] 接入Scrapy爬虫
- [ ] 测试环境和正式环境一键切换开关
- [ ] 写一个获取菜单的接口
- [ ] 将ELK单独用Docker启动


## 🤦‍已办清单：
- [X] 使用Dockerfile进行构建
- [X] 使用Mysql接替sqlite
- [X] 封装mysql账号密码到config.py里面
- [X] 接入Redis
- [X] redis接入Dockerfile里
- [X] 接入Httprunner
- [X] 增加登录验证码图片接口
- [X] 采用slim打包更小的Docker镜像,包体积从1G+缩小到500M以内
- [X] 实现单点登录功能
- [X] 密码重置功能
- [X] 优化docs文档加载时间
- [X] dev环境下不启动docs调试文档
- [X] 引入APScheduler
- [X] 记录请求日志
- [x] http发送接口,采用aiohttp,并持久化保存
- [x] 涉及到密码的，数据库保留sha256(已实现),前端传输用AES
- [x] 新增分页查询
- [x] 新增websocket
- [x] 重写APScheduler
- [x] 接入ELK日志系统

### ✨Httprunner快速体验

> run_har2case——>"har\requests.har"

> run_har2case 将har文件转化为httprunner用例

> run_subprocess 执行用例,使用pytest的方式执行httprunner用例,得到执行结果

> run_subprocess——>"testcases\requests.json"

> run_debug 在线调试,用于接口调试,使用run_har2case转换后的json内容在线执行,得到接口响应结果


## 📢开发提交规范:

```text
✨ feat:():新增
🐞 Fix:():修复
📃 docs:():文档
🦄 refactor:():重构
🎈 perf:():优化
```

## 🛰️API文档

***API文档：***
本地文档：[http://localhost:8000/docs](http://localhost:8000/docs)


## ⚡API 说明
<details><summary>🔎点击展开</summary>

GET：`/news_api`

### 请求参数

| 参数名           | 位置  | 类型   | 必填 | 示例值 | 说明                                                        |
| :--------------- | ----- | ------ | ---- | ------ | ----------------------------------------------------------- |
| _vercel_no_cache | query |        | 否   | 1      | 说明：`vercel` 强制不缓存                                   |
| cache            | query |        | 否   | 任意值 | 说明：清除缓存用                                            |
| index            | query | number | 否   | 0      | 说明：`0-99` 用来控制天数，`0` 为今天，`1` 为昨天，依次类推 |
| origin           | query | string | 否   | zhihu  | 说明："`zhihu`" 或 "`163`" 切换源                           |
</details>

## 🦄Casbin数据库ER图

![数据库ER图](https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202304041543880.png)

## 📸截图

***项目界面***

<details><summary>🔎点击展开截图</summary>
  <img  width="80%"  src="https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202302150953778.png" /><br>
  <img  width="80%"  src="https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202302150955926.png" /><br>
  <img  width="80%"  src="https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202302150956145.png" /><br>
  <img  width="80%"  src="https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202302150952967.png" /><br>
  <img  width="80%"  src="https://cdn.jsdelivr.net/gh/ranyong1997/image_collect@main/img/202302150951340.png" /><br>
</div>
</details>
<hr>

[Python-docs]: https://docs.python.org/3.8/

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[FastAPI]: https://img.shields.io/badge/FastAPI-FFFFFF?style=for-the-badge&logo=fastapi

[Pydantic]: https://img.shields.io/badge/Pydantic-FF43A1?style=for-the-badge&logo=pydantic&logoColor=white

[Uvicorn]: https://img.shields.io/badge/Uvicorn-2A308B?style=for-the-badge&logo=uvicorn&logoColor=white

[Pytest]: https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white

[Redis]: https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white

[JWT]: https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens

[Nginx]: https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white

[PyCharm]: https://img.shields.io/badge/PyCharm-21D789?style=for-the-badge&logo=pycharm&logoColor=white

[Markdown]: https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white

[Swagger]: https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white

[python-url]: https://www.python.org/

[fastapi-url]: https://fastapi.tiangolo.com

[pydantic-url]: https://docs.pydantic.dev

[uvicorn-url]: https://www.uvicorn.org/

[pytest-url]: https://docs.pytest.org/en/7.2.x/

[redis-url]: https://redis.io/

[jwt-url]: https://jwt.io/

[Pycharm-url]: https://www.jetbrains.com/pycharm/

[Nginx-url]: https://www.nginx.com/

[Markdown-url]: https://daringfireball.net/projects/markdown/

[Swagger-url]: https://swagger.io/