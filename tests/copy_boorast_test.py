# -*- coding: utf-8 -*-
from copyboost.macro_revise import RevisorGenerate
from sapperrag.llm.oai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
chatgpt = ChatOpenAI(openai_key, base_url)
revisor = RevisorGenerate(chatgpt)

bad = """
1、科技创新工作 申报人聚焦数据传输与数据安全领域，开展创新性科学研究：（1）以多路径传输协议（如， 多径TCP）为协议基础，突破传统的以“发送端为中心”的数据传输范式，设计新颖的“发送端-接 收端”一体化协同多路径传输理论、机理和模式；（2）研究面向Web 3.0的智能合约安全分析与漏 洞检测全新解决方案，为构建安全可靠可信的Web 3.0智能合约和区块链应用提供技术参考。 2、科研业绩 主持国家自然科学基金2项，以及江西省自然科学基金重点项目、江西省杰出青年基金、江西 省软科学研究计划重点项目等省级课题7项。以第一作者或通讯作者在《IEEE Transactions on In dustrial Informatics》《IEEE Transactions on Network Science and Engineering》《IEEE S ystems Journal》《IEICE Transactions on Information and Systems》《Future Generation C omputer Systems》《Computer Communications》《Wireless Personal Communications》《中国 科学：信息科学》（英文版）、IEEE ICME、IEEE ICC、IEEE GLOBECOM、IEEE WCNC、IEEE ICPADS 等期刊和会议发表论文70余篇。 3、角色分工和发挥领军作用 申报人自2020年7月起担任软件学院学术委员会主任、副院长（分管科研与学科建设），自202 3年8月起，担任计算机信息工程学院党委副书记、副院长（主持工作），期间： (1) 服务江西争创“世界VR中心”目标，组建获批江西师范大学“增强现实与智能网络技术” 校级特色科研团队（担任团队负责人）； (2) 带领团队围绕国家数据安全战略，组建获批“江西省区块链数据安全与治理工程研究中心 ”（担任中心执行主任）； (3) 助推学科科研交叉融合创新发展，带领团队与学校外国语学院联合组建成立“江西师范大 学语言智能研究中心”（担任中心主任）； (4) 搭建学术交流平台服务学术社区，担任10余本国际高水平学术期刊编委、客座主编、客座 编辑，以及3个国际学术会议的共同主席、技术委员会主席等。 
"""

good = """
申报人担任申报单位智能化软件工程学科方向带头人，率先在江西省开展大模型技术的研究，专注 于研究基于大模型的智能软件自动化开发，构建智能体开发理论与技术创新体系，解决大模型通用 智能与领域知识机融合的核心科学问题。其研究包括原创的自然语言原生模型编排方法、范式、体 系、理论、技术、平台及典型应用。重点解决大模型应用效率、技术门槛、推理能力、可控性、可 解释性以及人机交互体验等关键技术挑战，推动AI技术为产业赋能，促进产业数字化发展和升级。 申报人承担或参与多项国家自然科学基金项目（包括面上、青年、地区）和江西省自然科学基金项 目（面上），在ACM/IEEE系列汇刊（如TOSEM、TSE、TKDE、TSC）、中国科学等期刊以及ICSE、ASE 、FSE、ISSTA等国际会议发表论文50余篇，其中有8篇以一作身份在CCF-A类期刊与会议上发表。此 外，申请或授权专利16项，并编写与AI编程相关的“十四五规划”教材3本。 申报人成立江西智能软件工程实验室，并组建智能软件开发理论与技术研究团队。该团队目前拥有 4位教授，7位副教授和5位讲师，成员具备跨学科背景，涵盖软件工程和人工智能等领域。在申报 人的带领下，该团队与国内外高水平大学，如清华大学、北京大学、复旦大学、武汉大学以及澳大 利亚国立大学等开展合作，共同研发支持自然语言编程的一站式AI应用编排平台，使任何人都能够 轻松创建原创AI智能体应用。这一成果在多个场合获得广泛传播，包括江西卫视、知名公众号“机 器之心”、江西省第四届成果对接会、2023年AI+软件研发数字峰会、2023年中国软件大会，甚至 引起知名创业孵化期YC公司的关注和积极反馈。目前，在申报人的带领下，该团队已经发展成为一 支梯队结构合理、研究特色鲜明、在国内外具有一定学术影响力的智能软件开发理论与技术研究团队。 
"""
revisor.contrast_learn(good, bad)
