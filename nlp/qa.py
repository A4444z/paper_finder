# 问答系统模块

import torch
from transformers import AutoModelForQuestionAnswering, AutoTokenizer
import re
import numpy as np
from collections import Counter

class QuestionAnswering:
    """问答系统，用于回答用户关于文献的问题"""
    
    def __init__(self, model_name):
        """初始化问答系统
        
        Args:
            model_name (str): 预训练模型名称
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        
        # 设置设备（GPU或CPU）
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def answer(self, question, extracted_info_list):
        """回答问题
        
        Args:
            question (str): 用户问题
            extracted_info_list (list): 提取的文献信息列表
            
        Returns:
            str: 回答
        """
        # 检查是否有提取的信息
        if not extracted_info_list:
            return "没有找到相关文献信息来回答这个问题。"
        
        # 根据问题类型选择不同的处理方法
        if self._is_protein_question(question):
            return self._answer_protein_question(question, extracted_info_list)
        elif self._is_method_question(question):
            return self._answer_method_question(question, extracted_info_list)
        elif self._is_finding_question(question):
            return self._answer_finding_question(question, extracted_info_list)
        else:
            return self._answer_general_question(question, extracted_info_list)
    
    def _is_protein_question(self, question):
        """判断是否是关于蛋白质的问题
        
        Args:
            question (str): 用户问题
            
        Returns:
            bool: 是否是蛋白质问题
        """
        protein_keywords = [
            '蛋白质', '蛋白', 'protein', '表达', 'expression', '纯化', 'purification',
            '结构', 'structure', '功能', 'function', '序列', 'sequence', '多肽',
            'peptide', 'binder', '靶蛋白', 'target protein'
        ]
        
        return any(keyword.lower() in question.lower() for keyword in protein_keywords)
    
    def _is_method_question(self, question):
        """判断是否是关于方法的问题
        
        Args:
            question (str): 用户问题
            
        Returns:
            bool: 是否是方法问题
        """
        method_keywords = [
            '方法', 'method', '技术', 'technique', '实验', 'experiment', '步骤',
            'procedure', '协议', 'protocol', '如何', 'how to', '怎么', '怎样'
        ]
        
        return any(keyword.lower() in question.lower() for keyword in method_keywords)
    
    def _is_finding_question(self, question):
        """判断是否是关于研究发现的问题
        
        Args:
            question (str): 用户问题
            
        Returns:
            bool: 是否是研究发现问题
        """
        finding_keywords = [
            '发现', 'finding', '结果', 'result', '结论', 'conclusion', '证明',
            'prove', '表明', 'indicate', '显示', 'show', '揭示', 'reveal'
        ]
        
        return any(keyword.lower() in question.lower() for keyword in finding_keywords)
    
    def _answer_protein_question(self, question, extracted_info_list):
        """回答关于蛋白质的问题
        
        Args:
            question (str): 用户问题
            extracted_info_list (list): 提取的文献信息列表
            
        Returns:
            str: 回答
        """
        # 收集所有蛋白质相关信息
        protein_names = []
        expression_methods = []
        purification_methods = []
        
        for item in extracted_info_list:
            paper = item['paper']
            extracted_info = item['extracted_info']
            
            if 'protein_info' in extracted_info and extracted_info['protein_info']:
                protein_info = extracted_info['protein_info']
                
                # 收集蛋白质名称
                if 'names' in protein_info and protein_info['names']:
                    protein_names.extend(protein_info['names'])
                
                # 收集表达方法
                if 'expression_methods' in protein_info and protein_info['expression_methods']:
                    for method in protein_info['expression_methods']:
                        expression_methods.append({
                            'method': method,
                            'paper_title': paper.get('title', ''),
                            'paper_id': paper.get('id', '')
                        })
                
                # 收集纯化方法
                if 'purification_methods' in protein_info and protein_info['purification_methods']:
                    for method in protein_info['purification_methods']:
                        purification_methods.append({
                            'method': method,
                            'paper_title': paper.get('title', ''),
                            'paper_id': paper.get('id', '')
                        })
        
        # 统计最常见的蛋白质
        protein_counter = Counter(protein_names)
        common_proteins = protein_counter.most_common(5)
        
        # 根据问题内容构建回答
        if '表达' in question or 'expression' in question.lower():
            if expression_methods:
                answer = "根据文献，以下是一些蛋白质表达方法：\n\n"
                for i, method_info in enumerate(expression_methods[:5], 1):
                    answer += f"{i}. {method_info['method']} (来源: {method_info['paper_title']})\n"
                return answer
            else:
                return "在提供的文献中没有找到关于蛋白质表达方法的具体信息。"
        
        elif '纯化' in question or 'purification' in question.lower():
            if purification_methods:
                answer = "根据文献，以下是一些蛋白质纯化方法：\n\n"
                for i, method_info in enumerate(purification_methods[:5], 1):
                    answer += f"{i}. {method_info['method']} (来源: {method_info['paper_title']})\n"
                return answer
            else:
                return "在提供的文献中没有找到关于蛋白质纯化方法的具体信息。"
        
        elif '靶蛋白' in question or 'target protein' in question.lower() or 'binder' in question.lower():
            if common_proteins:
                answer = "根据文献，以下是一些常见的靶蛋白：\n\n"
                for i, (protein, count) in enumerate(common_proteins, 1):
                    answer += f"{i}. {protein} (在{count}篇文献中提及)\n"
                return answer
            else:
                return "在提供的文献中没有找到关于靶蛋白的具体信息。"
        
        else:
            # 一般蛋白质问题
            contexts = []
            for item in extracted_info_list:
                paper = item['paper']
                if 'abstract' in paper and paper['abstract']:
                    contexts.append(paper['abstract'])
            
            return self._get_answer_from_context(question, contexts)
    
    def _answer_method_question(self, question, extracted_info_list):
        """回答关于方法的问题
        
        Args:
            question (str): 用户问题
            extracted_info_list (list): 提取的文献信息列表
            
        Returns:
            str: 回答
        """
        # 收集所有方法信息
        all_methods = []
        
        for item in extracted_info_list:
            paper = item['paper']
            extracted_info = item['extracted_info']
            
            if 'methods' in extracted_info and extracted_info['methods']:
                for method in extracted_info['methods']:
                    all_methods.append({
                        'method': method,
                        'paper_title': paper.get('title', ''),
                        'paper_id': paper.get('id', '')
                    })
        
        if all_methods:
            answer = "根据文献，以下是一些相关的实验方法：\n\n"
            for i, method_info in enumerate(all_methods[:7], 1):
                answer += f"{i}. {method_info['method']} (来源: {method_info['paper_title']})\n"
            return answer
        else:
            # 如果没有找到明确的方法，尝试从摘要中回答
            contexts = []
            for item in extracted_info_list:
                paper = item['paper']
                if 'abstract' in paper and paper['abstract']:
                    contexts.append(paper['abstract'])
            
            return self._get_answer_from_context(question, contexts)
    
    def _answer_finding_question(self, question, extracted_info_list):
        """回答关于研究发现的问题
        
        Args:
            question (str): 用户问题
            extracted_info_list (list): 提取的文献信息列表
            
        Returns:
            str: 回答
        """
        # 收集所有关键发现
        all_findings = []
        
        for item in extracted_info_list:
            paper = item['paper']
            extracted_info = item['extracted_info']
            
            if 'key_findings' in extracted_info and extracted_info['key_findings']:
                for finding in extracted_info['key_findings']:
                    all_findings.append({
                        'finding': finding,
                        'paper_title': paper.get('title', ''),
                        'paper_id': paper.get('id', '')
                    })
        
        if all_findings:
            answer = "根据文献，以下是一些关键研究发现：\n\n"
            for i, finding_info in enumerate(all_findings[:5], 1):
                answer += f"{i}. {finding_info['finding']} (来源: {finding_info['paper_title']})\n"
            return answer
        else:
            # 如果没有找到明确的发现，尝试从摘要中回答
            contexts = []
            for item in extracted_info_list:
                paper = item['paper']
                if 'abstract' in paper and paper['abstract']:
                    contexts.append(paper['abstract'])
            
            return self._get_answer_from_context(question, contexts)
    
    def _answer_general_question(self, question, extracted_info_list):
        """回答一般问题
        
        Args:
            question (str): 用户问题
            extracted_info_list (list): 提取的文献信息列表
            
        Returns:
            str: 回答
        """
        # 从摘要中回答一般问题
        contexts = []
        for item in extracted_info_list:
            paper = item['paper']
            if 'abstract' in paper and paper['abstract']:
                contexts.append(paper['abstract'])
        
        return self._get_answer_from_context(question, contexts)
    
    def _get_answer_from_context(self, question, contexts):
        """从上下文中获取问题的答案
        
        Args:
            question (str): 问题
            contexts (list): 上下文列表
            
        Returns:
            str: 答案
        """
        if not contexts:
            return "没有找到相关文献信息来回答这个问题。"
        
        # 合并上下文（限制长度）
        combined_context = ' '.join(contexts)
        if len(combined_context) > 5000:
            combined_context = combined_context[:5000]
        
        # 使用预训练模型回答问题
        inputs = self.tokenizer(question, combined_context, return_tensors='pt')
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        
        # 确保答案范围有效
        if answer_end < answer_start:
            answer_end = answer_start + 10
        
        answer = self.tokenizer.decode(inputs['input_ids'][0][answer_start:answer_end])
        
        # 如果答案太短或无意义，尝试提供一个摘要回答
        if len(answer.split()) < 3 or answer.strip() == '':
            return self._generate_summary_answer(question, contexts)
        
        return answer
    
    def _generate_summary_answer(self, question, contexts):
        """生成摘要回答
        
        Args:
            question (str): 问题
            contexts (list): 上下文列表
            
        Returns:
            str: 摘要回答
        """
        # 简单的摘要生成方法
        relevant_sentences = []
        
        # 将问题分词
        question_words = set(re.findall(r'\w+', question.lower()))
        
        # 从每个上下文中提取相关句子
        for context in contexts:
            sentences = re.split(r'(?<=[.!?])\s+', context)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # 计算句子与问题的相关性
                sentence_words = set(re.findall(r'\w+', sentence.lower()))
                overlap = len(question_words.intersection(sentence_words))
                
                if overlap > 0:
                    relevant_sentences.append((sentence, overlap))
        
        # 按相关性排序
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # 构建回答
        if relevant_sentences:
            top_sentences = [s[0] for s in relevant_sentences[:3]]
            answer = ' '.join(top_sentences)
            return answer
        else:
            return "没有找到足够相关的信息来回答这个问题。"