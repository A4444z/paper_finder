# app.py

from flask import Flask, render_template, request, jsonify, session
import os
import json
from config import Config
import uuid # 用于生成唯一的缓存ID
from datetime import datetime, timedelta

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

# --- 解决方案：服务器端缓存 ---
# 使用一个简单的字典作为服务器端缓存来存储搜索结果
SEARCH_CACHE = {}
CACHE_EXPIRATION = timedelta(minutes=30) # 搜索结果在服务器上保留30分钟

# 初始化组件
db = Database(Config.DATABASE_PATH)
pubmed_api = PubMedAPI(Config.PUBMED_BASE_URL, Config.PUBMED_API_KEY)
scopus_api = ScopusAPI(Config.SCOPUS_BASE_URL, Config.SCOPUS_API_KEY)
biorxiv_api = BioRxivAPI(Config.BIORXIV_BASE_URL)
info_extractor = InfoExtractor(Config.NLP_MODEL)
qa_system = QuestionAnswering(Config.QA_MODEL)

def init_db():
    db.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keywords = request.form.get('keywords', '')
        sources = request.form.getlist('sources')
        max_results = int(request.form.get('max_results', Config.MAX_RESULTS_PER_SOURCE))
        
        # 执行搜索
        all_results = {}
        if 'pubmed' in sources:
            all_results['pubmed'] = pubmed_api.search(keywords, max_results=max_results)
        if 'scopus' in sources:
            all_results['scopus'] = scopus_api.search(keywords, max_results=max_results)
        if 'biorxiv' in sources:
            all_results['biorxiv'] = biorxiv_api.search(keywords, max_results=max_results)
        
        # --- 关键改动：不再将结果存入session ---
        # 1. 生成一个唯一的ID来标识这次搜索结果
        search_id = str(uuid.uuid4())
        
        # 2. 将巨大的搜索结果存入服务器端的缓存中
        SEARCH_CACHE[search_id] = {
            "timestamp": datetime.now(),
            "results": all_results
        }
        
        # 3. 只将这个简短、唯一的ID存入session
        session['search_id'] = search_id
        
        db.save_search_history(keywords, sources, sum(len(v) for v in all_results.values()))
        
        # 将 search_id 传递给模板，以便后续操作可以引用它
        return render_template('search.html', keywords=keywords, results=all_results, search_id=search_id)
    
    return render_template('search.html')

@app.route('/extract', methods=['POST'])
def extract_info():
    paper_ids = request.form.getlist('paper_ids')
    source = request.form.get('source')
    
    # --- 关键改动：从服务器缓存中读取结果 ---
    # 1. 从session中获取search_id
    search_id = session.get('search_id')
    if not search_id or search_id not in SEARCH_CACHE:
        return "搜索会话已过期，请重新搜索。", 400

    # 2. 检查缓存是否过期
    cache_entry = SEARCH_CACHE[search_id]
    if datetime.now() - cache_entry["timestamp"] > CACHE_EXPIRATION:
        del SEARCH_CACHE[search_id]
        return "搜索会话已过期，请重新搜索。", 400
        
    # 3. 从缓存中安全地获取结果
    results = cache_entry.get("results", {})
    source_results = results.get(source, [])
    
    selected_papers = [paper for paper in source_results if paper['id'] in paper_ids]
    
    extracted_info = []
    if selected_papers:
        extracted_info = info_extractor.extract_batch(selected_papers)
    
    # 将提取的信息也存入缓存，与本次搜索关联
    SEARCH_CACHE[search_id]['extracted_info'] = extracted_info
    
    return render_template('result.html', papers=selected_papers, extracted_info=extracted_info)

@app.route('/answer', methods=['POST'])
def answer_question():
    question = request.form.get('question', '')
    
    # --- 关键改动：同样从服务器缓存中读取 ---
    search_id = session.get('search_id')
    if not search_id or search_id not in SEARCH_CACHE:
        return jsonify({'error': '会话已过期'}), 400
        
    cache_entry = SEARCH_CACHE[search_id]
    extracted_info = cache_entry.get('extracted_info', [])
    
    if not extracted_info:
        return jsonify({'question': question, 'answer': "没有可供问答的文献信息，请先提取。"})

    answer = qa_system.answer(question, extracted_info)
    
    return jsonify({
        'question': question,
        'answer': answer
    })

@app.route('/history')
def view_history():
    history = db.get_search_history()
    return render_template('history.html', history=history)

# ... download_paper 和 main 部分保持不变 ...
if __name__ == '__main__':
    os.makedirs(Config.CACHE_DIR, exist_ok=True)
    db.init_db()
    app.run(debug=Config.DEBUG)