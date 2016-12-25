#QA系统#
基于维基语料的中文问答系统

###作者###
朱兆成 高俊

###项目结构###
questions目录下包含样例数据和测试数据。

results目录下包含运行结果，由于每个问题需要1分钟左右的时间运行，受限于时间关系，只对大部分题目做了开放测试，封闭测试没能来的及做。样例数据上开放测试能达到25%的准确率。

code下包含系统的所有代码，其中release.py为主程序。

###代码###
- data.py 维基语料载入及预处理
- debugger.py 调试辅助函数
- embedding.py 向量空间模型
- graph.py 图模型（最终模型中未使用）
- method.py 算法抽象类
- question.py 模板抽取
- search.py 检索和搜索
- timer.py 计时函数
- web.py 搜索引擎
- release.py 主程序
- test 调试用的一些程序，以及文件比较程序

####第三方库####
- wikipedia-extractor bz2格式维基语料处理库
- langconv 简繁转换库