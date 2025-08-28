# API模块初始化

class BaseAPI:
    """API基类，定义通用方法"""
    
    def __init__(self, base_url, api_key=None):
        """初始化API
        
        Args:
            base_url (str): API基础URL
            api_key (str, optional): API密钥
        """
        self.base_url = base_url
        self.api_key = api_key
        
    def search(self, query, **kwargs):
        """搜索文献
        
        Args:
            query (str): 搜索关键词
            **kwargs: 其他搜索参数
            
        Returns:
            list: 搜索结果列表
        """
        raise NotImplementedError("子类必须实现search方法")
    
    def get_paper(self, paper_id):
        """获取单篇文献详情
        
        Args:
            paper_id (str): 文献ID
            
        Returns:
            dict: 文献详情
        """
        raise NotImplementedError("子类必须实现get_paper方法")
    
    def download_paper(self, paper_id, save_path):
        """下载文献
        
        Args:
            paper_id (str): 文献ID
            save_path (str): 保存路径
            
        Returns:
            bool: 是否下载成功
        """
        raise NotImplementedError("子类必须实现download_paper方法")