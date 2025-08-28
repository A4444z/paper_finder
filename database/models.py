# 数据模型模块

class Paper:
    """文献数据模型"""
    
    def __init__(self, id, title, abstract=None, authors=None, journal=None, 
                 pub_date=None, doi=None, source=None, keywords=None, url=None):
        """初始化文献对象
        
        Args:
            id (str): 文献ID
            title (str): 标题
            abstract (str, optional): 摘要
            authors (list, optional): 作者列表
            journal (str, optional): 期刊名称
            pub_date (str, optional): 发布日期
            doi (str, optional): DOI
            source (str, optional): 来源（pubmed, scopus, biorxiv等）
            keywords (list, optional): 关键词列表
            url (str, optional): 文献URL
        """
        self.id = id
        self.title = title
        self.abstract = abstract
        self.authors = authors or []
        self.journal = journal
        self.pub_date = pub_date
        self.doi = doi
        self.source = source
        self.keywords = keywords or []
        self.url = url
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建文献对象
        
        Args:
            data (dict): 文献数据字典
            
        Returns:
            Paper: 文献对象
        """
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            abstract=data.get('abstract'),
            authors=data.get('authors'),
            journal=data.get('journal'),
            pub_date=data.get('pub_date'),
            doi=data.get('doi'),
            source=data.get('source'),
            keywords=data.get('keywords'),
            url=data.get('url')
        )
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 文献数据字典
        """
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'authors': self.authors,
            'journal': self.journal,
            'pub_date': self.pub_date,
            'doi': self.doi,
            'source': self.source,
            'keywords': self.keywords,
            'url': self.url
        }

class SearchHistory:
    """搜索历史数据模型"""
    
    def __init__(self, id, keywords, sources, result_count, search_time):
        """初始化搜索历史对象
        
        Args:
            id (int): 历史记录ID
            keywords (str): 搜索关键词
            sources (list): 搜索来源列表
            result_count (int): 结果数量
            search_time (str): 搜索时间
        """
        self.id = id
        self.keywords = keywords
        self.sources = sources
        self.result_count = result_count
        self.search_time = search_time
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建搜索历史对象
        
        Args:
            data (dict): 搜索历史数据字典
            
        Returns:
            SearchHistory: 搜索历史对象
        """
        return cls(
            id=data.get('id'),
            keywords=data.get('keywords'),
            sources=data.get('sources'),
            result_count=data.get('result_count'),
            search_time=data.get('search_time')
        )
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 搜索历史数据字典
        """
        return {
            'id': self.id,
            'keywords': self.keywords,
            'sources': self.sources,
            'result_count': self.result_count,
            'search_time': self.search_time
        }

class UserQuestion:
    """用户问题数据模型"""
    
    def __init__(self, id, question, answer, related_papers, question_time):
        """初始化用户问题对象
        
        Args:
            id (int): 问题ID
            question (str): 问题内容
            answer (str): 回答内容
            related_papers (list): 相关文献ID列表
            question_time (str): 提问时间
        """
        self.id = id
        self.question = question
        self.answer = answer
        self.related_papers = related_papers
        self.question_time = question_time
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建用户问题对象
        
        Args:
            data (dict): 用户问题数据字典
            
        Returns:
            UserQuestion: 用户问题对象
        """
        return cls(
            id=data.get('id'),
            question=data.get('question'),
            answer=data.get('answer'),
            related_papers=data.get('related_papers'),
            question_time=data.get('question_time')
        )
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 用户问题数据字典
        """
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'related_papers': self.related_papers,
            'question_time': self.question_time
        }