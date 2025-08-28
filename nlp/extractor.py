# 信息提取模块

import spacy
import re
from collections import Counter

class InfoExtractor:
    """文献信息提取器"""
    
    def __init__(self, model_name):
        """初始化信息提取器
        
        Args:
            model_name (str): SpaCy模型名称
        """
        self.nlp = spacy.load(model_name)
        
        # 生物学相关实体类型
        self.bio_entity_types = [
            'GENE', 'PROTEIN', 'CHEMICAL', 'DISEASE', 'SPECIES', 'CELL_TYPE', 'CELL_LINE'
        ]
        
        # 实验方法相关关键词
        self.method_keywords = [
            'express', 'purif', 'crystalli', 'clone', 'mutat', 'transfect',
            'culture', 'incubat', 'centrifug', 'elut', 'dialys', 'chromatograph',
            'electrophoresis', 'assay', 'pcr', 'sequenc', 'amplif', 'digest',
            'ligat', 'transform', 'plate', 'screen', 'select', 'wash', 'stain',
            'microscop', 'imaging', 'analys', 'quantif', 'measur', 'detect'
        ]
        
    def extract(self, paper):
        """从单篇文献中提取信息
        
        Args:
            paper (dict): 文献信息
            
        Returns:
            dict: 提取的信息
        """
        if not paper or 'abstract' not in paper or not paper['abstract']:
            return {}
        
        # 提取的信息
        extracted_info = {
            'paper_id': paper.get('id', ''),
            'entities': {},
            'methods': [],
            'key_findings': [],
            'protein_info': {}
        }
        
        # 处理摘要
        abstract = paper['abstract']
        doc = self.nlp(abstract)
        
        # 提取命名实体
        entities = {}
        for ent in doc.ents:
            ent_type = ent.label_
            if ent_type not in entities:
                entities[ent_type] = []
            if ent.text not in entities[ent_type]:
                entities[ent_type].append(ent.text)
        
        extracted_info['entities'] = entities
        
        # 提取实验方法
        methods = self._extract_methods(abstract)
        extracted_info['methods'] = methods
        
        # 提取关键发现
        key_findings = self._extract_key_findings(abstract)
        extracted_info['key_findings'] = key_findings
        
        # 提取蛋白质信息（如果文章涉及蛋白质）
        protein_info = self._extract_protein_info(abstract)
        if protein_info:
            extracted_info['protein_info'] = protein_info
        
        return extracted_info
    
    def extract_batch(self, papers):
        """批量提取多篇文献的信息
        
        Args:
            papers (list): 文献列表
            
        Returns:
            list: 提取的信息列表
        """
        results = []
        for paper in papers:
            extracted = self.extract(paper)
            if extracted:
                results.append({
                    'paper': paper,
                    'extracted_info': extracted
                })
        return results
    
    def _extract_methods(self, text):
        """提取实验方法
        
        Args:
            text (str): 文本内容
            
        Returns:
            list: 提取的方法列表
        """
        methods = []
        text_lower = text.lower()
        
        # 查找方法关键词
        for keyword in self.method_keywords:
            pattern = r'\b' + keyword + r'[a-z]*\b'
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                # 获取关键词上下文
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text_lower[start:end]
                
                # 提取完整句子
                sentence = self._extract_sentence(text, match.start())
                
                if sentence and sentence not in methods:
                    methods.append(sentence)
        
        return methods[:5]  # 限制返回的方法数量
    
    def _extract_key_findings(self, text):
        """提取关键发现
        
        Args:
            text (str): 文本内容
            
        Returns:
            list: 关键发现列表
        """
        findings = []
        
        # 查找表示发现的关键短语
        finding_phrases = [
            'we found', 'we show', 'we demonstrate', 'we report', 'we identify',
            'we discover', 'we observe', 'we present', 'we reveal', 'we determine',
            'results show', 'results indicate', 'results demonstrate', 'results reveal',
            'our findings', 'this study shows', 'this study demonstrates'
        ]
        
        text_lower = text.lower()
        for phrase in finding_phrases:
            pos = text_lower.find(phrase)
            if pos >= 0:
                # 提取包含关键短语的句子
                sentence = self._extract_sentence(text, pos)
                if sentence and sentence not in findings:
                    findings.append(sentence)
        
        # 如果没有找到明确的发现句，尝试提取结论句
        if not findings:
            conclusion_phrases = [
                'in conclusion', 'to conclude', 'we conclude', 'thus', 'therefore',
                'in summary', 'taken together', 'overall', 'collectively', 'in brief'
            ]
            
            for phrase in conclusion_phrases:
                pos = text_lower.find(phrase)
                if pos >= 0:
                    # 提取包含结论短语的句子
                    sentence = self._extract_sentence(text, pos)
                    if sentence and sentence not in findings:
                        findings.append(sentence)
        
        return findings[:3]  # 限制返回的发现数量
    
    def _extract_protein_info(self, text):
        """提取蛋白质相关信息
        
        Args:
            text (str): 文本内容
            
        Returns:
            dict: 蛋白质信息
        """
        protein_info = {
            'names': [],
            'expression_methods': [],
            'purification_methods': []
        }
        
        # 查找蛋白质名称
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'PROTEIN' or ent.label_ == 'GENE':
                if ent.text not in protein_info['names']:
                    protein_info['names'].append(ent.text)
        
        # 查找表达方法
        expression_keywords = [
            'express', 'overexpress', 'produce', 'construct', 'clone', 'transfect',
            'transform', 'induce', 'IPTG', 'vector', 'plasmid', 'E. coli', 'HEK',
            'CHO cells', 'baculovirus', 'yeast', 'mammalian cells'
        ]
        
        for keyword in expression_keywords:
            pattern = r'\b' + re.escape(keyword) + r'[a-z]*\b'
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                # 提取包含关键词的句子
                sentence = self._extract_sentence(text, match.start())
                if sentence and sentence not in protein_info['expression_methods']:
                    protein_info['expression_methods'].append(sentence)
        
        # 查找纯化方法
        purification_keywords = [
            'purif', 'chromatograph', 'column', 'elut', 'dialys', 'filtrat',
            'centrifug', 'precipitat', 'pellet', 'supernatant', 'wash', 'buffer',
            'resin', 'beads', 'affinity', 'his-tag', 'gst', 'imidazole', 'gel filtration',
            'size exclusion', 'ion exchange', 'hplc', 'fplc'
        ]
        
        for keyword in purification_keywords:
            pattern = r'\b' + re.escape(keyword) + r'[a-z]*\b'
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                # 提取包含关键词的句子
                sentence = self._extract_sentence(text, match.start())
                if sentence and sentence not in protein_info['purification_methods']:
                    protein_info['purification_methods'].append(sentence)
        
        # 限制返回的方法数量
        protein_info['expression_methods'] = protein_info['expression_methods'][:3]
        protein_info['purification_methods'] = protein_info['purification_methods'][:3]
        
        return protein_info
    
    def _extract_sentence(self, text, pos):
        """提取包含指定位置的完整句子
        
        Args:
            text (str): 文本内容
            pos (int): 位置
            
        Returns:
            str: 提取的句子
        """
        # 查找句子的开始和结束
        start = text.rfind('.', 0, pos) + 1
        if start == 0:  # 没有找到句点，可能是第一个句子
            start = 0
        
        end = text.find('.', pos)
        if end == -1:  # 没有找到句点，可能是最后一个句子
            end = len(text)
        
        # 提取并清理句子
        sentence = text[start:end].strip()
        return sentence