# PubMed API模块

import requests
import xml.etree.ElementTree as ET
import time
from . import BaseAPI

class PubMedAPI(BaseAPI):
    """PubMed API接口"""
    
    def __init__(self, base_url, api_key=None):
        """初始化PubMed API
        
        Args:
            base_url (str): PubMed API基础URL
            api_key (str, optional): PubMed API密钥
        """
        super().__init__(base_url, api_key)
        
    def search(self, query, max_results=20, **kwargs):
        """搜索PubMed文献
        
        Args:
            query (str): 搜索关键词
            max_results (int, optional): 最大结果数量
            **kwargs: 其他搜索参数
            
        Returns:
            list: 搜索结果列表
        """
        # 构建搜索URL
        search_url = f"{self.base_url}esearch.fcgi"
        
        # 构建参数
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        # 添加API密钥（如果有）
        if self.api_key:
            params['api_key'] = self.api_key
            
        # 添加其他参数
        params.update(kwargs)
        
        # 发送请求
        response = requests.get(search_url, params=params)
        
        if response.status_code != 200:
            return []
        
        # 解析结果
        data = response.json()
        id_list = data.get('esearchresult', {}).get('idlist', [])
        
        if not id_list:
            return []
        
        # 获取文献详情
        return self._fetch_papers(id_list)
    
    def _fetch_papers(self, id_list):
        """获取多篇文献详情
        
        Args:
            id_list (list): 文献ID列表
            
        Returns:
            list: 文献详情列表
        """
        # 构建获取详情URL
        fetch_url = f"{self.base_url}efetch.fcgi"
        
        # 构建参数
        params = {
            'db': 'pubmed',
            'id': ','.join(id_list),
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        # 添加API密钥（如果有）
        if self.api_key:
            params['api_key'] = self.api_key
            
        # 发送请求
        response = requests.get(fetch_url, params=params)
        
        if response.status_code != 200:
            return []
        
        # 解析XML结果
        return self._parse_xml_response(response.text)
    
    def _parse_xml_response(self, xml_text):
        """解析XML响应
        
        Args:
            xml_text (str): XML文本
            
        Returns:
            list: 解析后的文献列表
        """
        try:
            root = ET.fromstring(xml_text)
            articles = []
            
            # 遍历所有PubmedArticle元素
            for article_elem in root.findall('.//PubmedArticle'):
                article = {}
                
                # 获取PMID
                pmid_elem = article_elem.find('.//PMID')
                if pmid_elem is not None:
                    article['id'] = pmid_elem.text
                
                # 获取标题
                title_elem = article_elem.find('.//ArticleTitle')
                if title_elem is not None:
                    article['title'] = title_elem.text
                
                # 获取摘要
                abstract_elems = article_elem.findall('.//AbstractText')
                if abstract_elems:
                    article['abstract'] = ' '.join([elem.text for elem in abstract_elems if elem.text])
                
                # 获取作者
                authors = []
                author_elems = article_elem.findall('.//Author')
                for author_elem in author_elems:
                    last_name = author_elem.find('LastName')
                    fore_name = author_elem.find('ForeName')
                    if last_name is not None and fore_name is not None:
                        authors.append(f"{fore_name.text} {last_name.text}")
                article['authors'] = authors
                
                # 获取期刊信息
                journal_elem = article_elem.find('.//Journal')
                if journal_elem is not None:
                    journal_title = journal_elem.find('Title')
                    if journal_title is not None:
                        article['journal'] = journal_title.text
                
                # 获取发布日期
                pub_date_elem = article_elem.find('.//PubDate')
                if pub_date_elem is not None:
                    year = pub_date_elem.find('Year')
                    month = pub_date_elem.find('Month')
                    day = pub_date_elem.find('Day')
                    
                    date_parts = []
                    if year is not None:
                        date_parts.append(year.text)
                    if month is not None:
                        date_parts.append(month.text)
                    if day is not None:
                        date_parts.append(day.text)
                    
                    article['pub_date'] = '-'.join(date_parts)
                
                # 获取关键词
                keywords = []
                keyword_elems = article_elem.findall('.//Keyword')
                for keyword_elem in keyword_elems:
                    if keyword_elem.text:
                        keywords.append(keyword_elem.text)
                article['keywords'] = keywords
                
                # 获取DOI
                article_id_elems = article_elem.findall('.//ArticleId')
                for article_id_elem in article_id_elems:
                    if article_id_elem.get('IdType') == 'doi':
                        article['doi'] = article_id_elem.text
                
                # 添加来源信息
                article['source'] = 'pubmed'
                
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"解析XML时出错: {e}")
            return []
    
    def get_paper(self, paper_id):
        """获取单篇文献详情
        
        Args:
            paper_id (str): 文献ID
            
        Returns:
            dict: 文献详情
        """
        papers = self._fetch_papers([paper_id])
        return papers[0] if papers else None
    
    def download_paper(self, paper_id, save_path):
        """下载文献（如果可用）
        
        Args:
            paper_id (str): 文献ID
            save_path (str): 保存路径
            
        Returns:
            bool: 是否下载成功
        """
        # 获取文献详情
        paper = self.get_paper(paper_id)
        
        if not paper or 'doi' not in paper:
            return False
        
        # 尝试通过DOI下载
        doi = paper['doi']
        download_url = f"https://doi.org/{doi}"
        
        try:
            response = requests.get(download_url, allow_redirects=True)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                return False
        except Exception:
            return False