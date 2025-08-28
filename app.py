# 主程序入口

from flask import Flask, render_template, request, jsonify, session
import os
import json
from config import Config

# 导入自定义模块
from api.pubmed import PubMedAPI
from api.scopus import ScopusAPI
from api.biorxiv import BioRxivAPI
from nlp.extractor import InfoExtractor
from nlp.qa import QuestionAnswering
from database.db import Database

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# 初始化组件
db = Database(Config.DATABASE_PATH)
pubmed_api = PubMedAPI(Config.PUBMED_BASE_URL, Config.PUBMED_API_KEY)
scopus_api = ScopusAPI(Config.SCOPUS_BASE_URL, Config.SCOPUS_API_KEY)
biorxiv_api = BioRxivAPI(Config.BIORXIV_BASE_URL)
info_extractor = InfoExtractor(Config.NLP_MODEL)
qa_system = QuestionAnswering(Config.QA_MODEL)

# 添加数据库初始化函数
def init_db():
    """初始化数据库"""
    db.init_db()

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """搜索页面"""
    if request.method == 'POST':
        # 获取搜索参数
        keywords = request.form.get('keywords', '')
        sources = request.form.getlist('sources')
        max_results = int(request.form.get('max_results', Config.MAX_RESULTS_PER_SOURCE))
        
        # 存储搜索参数到会话
        session['search_params'] = {
            'keywords': keywords,
            'sources': sources,
            'max_results': max_results
        }
        
        # 执行搜索
        results = {}
        if 'pubmed' in sources:
            results['pubmed'] = pubmed_api.search(keywords, max_results=max_results)
        if 'scopus' in sources:
            results['scopus'] = scopus_api.search(keywords, max_results=max_results)
        if 'biorxiv' in sources:
            results['biorxiv'] = biorxiv_api.search(keywords, max_results=max_results)
        
        # 存储结果到会话
        session['search_results'] = results
        
        # 保存搜索历史到数据库
        db.save_search_history(keywords, sources, len(results))
        
        return render_template('search.html', keywords=keywords, results=results)
    
    return render_template('search.html')

@app.route('/extract', methods=['POST'])
def extract_info():
    """提取文献信息"""
    paper_ids = request.form.getlist('paper_ids')
    source = request.form.get('source')
    
    # 获取会话中的搜索结果
    results = session.get('search_results', {})
    source_results = results.get(source, [])
    
    # 筛选选中的文献
    selected_papers = [paper for paper in source_results if paper['id'] in paper_ids]
    
    # 提取信息
    extracted_info = info_extractor.extract_batch(selected_papers)
    
    # 存储提取结果到会话
    session['extracted_info'] = extracted_info
    
    return render_template('result.html', papers=selected_papers, extracted_info=extracted_info)

@app.route('/answer', methods=['POST'])
def answer_question():
    """回答问题"""
    question = request.form.get('question', '')
    
    # 获取会话中的提取信息
    extracted_info = session.get('extracted_info', [])
    
    # 使用问答系统回答问题
    answer = qa_system.answer(question, extracted_info)
    
    return jsonify({
        'question': question,
        'answer': answer
    })

@app.route('/history')
def view_history():
    """查看搜索历史"""
    history = db.get_search_history()
    return render_template('history.html', history=history)

@app.route('/download/<paper_id>')
def download_paper(paper_id):
    """下载文献"""
    # 实现文献下载功能
    pass

if __name__ == '__main__':
    # 确保数据库和缓存目录存在
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    db.init_db()
    
    # 启动应用
    app.run(debug=Config.DEBUG)