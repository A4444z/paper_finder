# Scopus API模块

import requests
import json
from . import BaseAPI

class ScopusAPI(BaseAPI):
    """Scopus API接口"""
    
    def __init__(self, base_url, api_key=None):
        """初始化Scopus API
        
        Args:
            base_url (str): Scopus API基础URL
            api_key (str): Scopus API密钥（必需）
        """
        super().__init__(base_url, api_key)
        if not api_key:
            raise ValueError("Scopus API需要API密钥")
    
    def search(self, query, max_results=20, **kwargs):
        """搜索Scopus文献
        
        Args:
            query (str): 搜索关键词
            max_results (int, optional): 最大结果数量
            **kwargs: 其他搜索参数
            
        Returns:
            list: 搜索结果列表
        """
        params = {
            'query': query,
            'count': max_results,
            'sort': 'relevancy',
            'field': 'dc:title,dc:description,dc:creator,prism:publicationName,prism:doi,prism:coverDate,citedby-count,authkeywords'
        }
        params.update(kwargs)
        
        headers = {
            'X-ELS-APIKey': self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return self._parse_response(data)
        except requests.exceptions.RequestException as e:
            print(f"Scopus API请求出错: {e}")
            return []

    def _parse_response(self, data):
        """解析Scopus API响应
        
        Args:
            data (dict): API响应数据
            
        Returns:
            list: 解析后的文献列表
        """
        results = []
        entries = data.get('search-results', {}).get('entry', [])
        
        for entry in entries:
            paper = {
                'id': entry.get('dc:identifier', '').replace('SCOPUS_ID:', ''),
                'title': entry.get('dc:title', 'No title available'),
                'abstract': entry.get('dc:description', ''),
                'journal': entry.get('prism:publicationName', ''),
                'pub_date': entry.get('prism:coverDate', ''),
                'doi': entry.get('prism:doi', ''),
                'source': 'scopus',
                'citation_count': entry.get('citedby-count', '0'),
                'authors': [author.get('$', '') for author in entry.get('dc:creator', []) if '$' in author],
                'keywords': entry.get('authkeywords', '').split(' | ')
            }
            results.append(paper)
            
        return results