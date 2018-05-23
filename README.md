# 携程爬虫(破解eleven, 发现ctrip_ticket)
破解eleven参数后，可以不需要调用selenium便可请求到详细的价格信息，提升获取速度、减少资源占用 <br />
该爬虫可爬取：
* 每个酒店名称、评分
* 每个酒店不同预订时间每种房型价格
* 每个酒店不同预订时间每种房型满意度
* 每个酒店不同预订时间每种房型剩余可订数 <br />
**使用时先跑'gen_ticket.py'生成ctrip_ticket，再跑'main.py'**
## 1. 获得房间价格的重要参数"eleven"的生成方法
* "eleven"由一个混淆js文件-"oceanball"生成，该文件具有随机性
* 生成方法:ctrip_funcs.py中的"get_oceanball"、"get_eleven"两个函数，需要配合js代码和python共同生成
## 2. 发现获得剩余可订房间仅需要Cookie: ctrip_ticket
* 生成机制未明，可以用selenium每30分钟提取一次，保证时效
