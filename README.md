# Paper Finder

一个用于生物学文献调研的工具，可以根据关键词搜索相关文献，并提取信息回答特定问题。

## 功能特点

1. 根据关键词或句子在可靠的生物学数据库中搜索英文文献
2. 提取文献中的关键信息
3. 回答用户特定问题，如多肽binder设计中常用的靶蛋白模式及其表达与纯化方法
4. 用户友好的界面，便于操作和查看结果

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd paper_finder

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

```bash
# 启动Web界面
python app.py
```

然后在浏览器中访问 `http://localhost:5000` 即可使用。

## 项目结构

```
paper_finder/
├── app.py                 # 主程序入口
├── requirements.txt       # 项目依赖
├── README.md              # 项目说明
├── config.py              # 配置文件
├── database/              # 数据库相关
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   └── db.py              # 数据库操作
├── api/                   # API相关
│   ├── __init__.py
│   ├── pubmed.py          # PubMed API
│   ├── scopus.py          # Scopus API
│   └── biorxiv.py         # bioRxiv API
├── nlp/                   # 自然语言处理
│   ├── __init__.py
│   ├── extractor.py       # 信息提取
│   └── qa.py              # 问答系统
├── static/                # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
└── templates/             # 前端模板
    ├── index.html
    ├── search.html
    └── result.html
```

## 支持的数据库

- PubMed
- Scopus (waiting fot API)
- bioRxiv
- Web of Science

## 许可证

MIT
