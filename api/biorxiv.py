# bioRxiv API模块

import requests
import json
from datetime import datetime, timedelta
from . import BaseAPI
import urllib.parse

class BioRxivAPI(BaseAPI):
    """bioRxiv API接口，用于获取预印本论文"""
    
    def __init__(self, base_url):
        """初始化bioRxiv API
        
        Args:
            base_url (str): bioRxiv API基础URL
        """
        super().__init__(base_url)
    
    def search(self, query, max_results=20, **kwargs):
        """搜索bioRxiv文献
        
        Fetches papers from the last 90 days and filters them by the query term
        because the official API does not support direct keyword searching.
        
        Args:
            query (str): 搜索关键词
            max_results (int, optional): 最大结果数量
            **kwargs: 其他搜索参数
            
        Returns:
            list: 搜索结果列表
        """
        # The bioRxiv API doesn't have a keyword search.
        # We fetch the latest preprints and filter them client-side.
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        # Format the URL for fetching details of publications in a date range
        search_url = f"{self.base_url}/details/biorxiv/{start_date}/{end_date}/0"
        
        print(f"Fetching bioRxiv articles from: {search_url}")
        
        try:
            response = requests.get(search_url)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            
            collection = data.get('collection', [])
            
            # Filter the results based on the query
            filtered_results = []
            search_query = query.lower()
            for item in collection:
                title = item.get('title', '').lower()
                abstract = item.get('abstract', '').lower()
                
                if search_query in title or search_query in abstract:
                    filtered_results.append(item)
            
            # Limit the number of results
            final_results = filtered_results[:max_results]
            
            return self._parse_response(final_results)
            
        except requests.exceptions.RequestException as e:
            print(f"bioRxiv API请求出错: {e}")
            return []
        except json.JSONDecodeError:
            print("Failed to decode JSON from bioRxiv API response.")
            return []

    def _parse_response(self, collection):
        """解析bioRxiv API响应
        
        Args:
            collection (list): API响应数据
            
        Returns:
            list: 解析后的文献列表
        """
        results = []
        
        for item in collection:
            # Handle authors, which can be a string or list
            authors_raw = item.get('authors', '')
            if isinstance(authors_raw, list):
                author_names = [author.get('name', '') for author in authors_raw if 'name' in author]
            else:
                author_names = [name.strip() for name in authors_raw.split(';')]

            paper = {
                'id': item.get('doi', '').replace('10.1101/', ''),
                'title': item.get('title', 'No Title Available'),
                'abstract': item.get('abstract', ''),
                'authors': author_names,
                'doi': item.get('doi', ''),
                'pub_date': item.get('date', ''),
                'journal': 'bioRxiv',
                'source': 'biorxiv',
                'url': f"https://www.biorxiv.org/content/{item.get('doi', '')}"
            }
            paper['keywords'] = [] # bioRxiv API does not provide keywords
            
            results.append(paper)
        
        return results