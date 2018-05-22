# 携程爬虫(破解eleven, ctrip_ticket)
破解eleven参数后，可以不需要调用selenium便可请求到详细的价格信息。
* 破解了获得房间价格的重要参数eleven生成方法
eleven由一个混淆js文件-"oceanball"生成，该文件具有随机性，需要通过js构建准确的js文件地址
生成方法为ctrip_funcs.py中的"get_oceanball" "get_eleven"两个函数，需要配合js代码和python共同生成
* 获得剩余可订房间需要获得ctrip_ticket这个cookie，生成机制未明，可以用selenium每30分钟提取一次，保证时效
