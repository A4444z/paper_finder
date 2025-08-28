# 配置文件

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基本配置
class Config:
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    DEBUG = os.environ.get('DEBUG') or False
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'paper_finder.db')
    
    # API密钥
    PUBMED_API_KEY = "0f2d9637e5192173f5f09079e922f0ba1908"
    SCOPUS_API_KEY = "6d0bc60f9f5ade60e9cd250f41b4c06a"
    WOS_API_KEY = os.environ.get('WOS_API_KEY')
    
    # API配置
    PUBMED_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    SCOPUS_BASE_URL = 'https://api.elsevier.com/content/search/scopus'
    BIORXIV_BASE_URL = 'https://api.biorxiv.org'
    
    # 搜索配置
    MAX_RESULTS_PER_SOURCE = 50
    DEFAULT_SEARCH_FIELDS = ['title', 'abstract', 'keywords']
    
    # NLP配置
    NLP_MODEL = 'en_core_web_lg'  # SpaCy模型
    QA_MODEL = 'bert-large-uncased-whole-word-masking-finetuned-squad'  # Transformers QA模型
    
    # 缓存配置
    CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
    CACHE_EXPIRATION = 86400  # 24小时，单位：秒