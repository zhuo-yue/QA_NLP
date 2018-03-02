#!/usr/bin/env python
# coding=utf-8

import math
import copy
from global_config import *
import extract_sent_trunk as EST

'''处理文本类'''
class ProcessContent:
    """ 处理文本类. 主要实现对文本的各种处理"""

    def  __init__(self):
        pass

    '''判断句子是否完全由标点符号组成'''
    def is_punctuation(self,sentence):
        sentence = unicode(sentence, 'utf-8')
        is_punct = True     # 表示是否全由符号组成Bool值,默认为True
        for my_char in sentence:
            # 判断当前字符是否为中文/英文/数字字符, 若是,则表示不全为标点标号
            if my_char.isalpha() or my_char.isdigit():
                is_punct = False
                break
        return is_punct

    '''对格式化的句法结构中出现的实体符号进行原词替换'''
    def replace_sign_with_entities(self, format_parse_list, replaced_dict):
        dict_keys = replaced_dict.keys()
        for triple in format_parse_list:
            if triple[1] in dict_keys:
                triple[1] = replaced_dict[triple[1]]
            if triple[4] in dict_keys:
                triple[4] = replaced_dict[triple[4]]

        return format_parse_list

'''句法分析类'''
class SyntaxParsing:
    def __init__(self):
        self.est_object = EST.ExtractSentenceTrunk()
        self.process_object = ProcessContent()


    '''获得句法分析元组中支配词与被支配词的词性'''
    def get_pos_tag(self, sent_parse):
        return (sent_parse[3], sent_parse[6])

    '''句法分析'''
    def parse_analysis(self, sentence):
        words = segmentor.segment(sentence)
        postags = postagger.postag(words)
        arcs = parser.parse(words, postags)
        return arcs, words, postags

    '''将依存关系进行格式化表示'''
    def format_child_dict(self, arcs, words, postags):
        word_list=['root']
        postag_list=['root']

        format_parse_list=[]

        for word in words:
            word_list.append(word)

        for postag in postags:
            postag_list.append(postag)
        
        for index in range(len(arcs)):
            word_index=index+1
            format_parse_list.append([arcs[index].relation,word_list[word_index],word_index,postag_list[word_index],word_list[arcs[index].head],arcs[index].head,postag_list[arcs[index].head]])
            
 
        return format_parse_list

    '''处理并获得句子的句法结构的主控函数'''
    def process_parse_structure(self, sentence):
    
        # 对句子中的实体进行符号替换(将实体替换为符号后, 有利于句法分析的准确性)
        sentence, replaced_dict = self.est_object.process_est(sentence)

        # 获取句法分析原始结构
        arcs, words, postags = self.parse_analysis(sentence)

        # 对句法分析结果进行格式化,处理成由(依存关系，词项1，位置1，词性1，词项2，位置2，词性2)元组构成的列表
        format_parse_list = self.format_child_dict(arcs, words, postags)

        # 对格式化句法分析表示中的实体符号进行替换
        format_parse_list = self.process_object.replace_sign_with_entities(format_parse_list, replaced_dict)

        return format_parse_list


def main():
    sentence="今天螺纹行情怎么样"
    parse_object=SyntaxParsing()
    sent_parse_list = parse_object.process_parse_structure(sentence)

    for item in sent_parse_list:
        print ' '.join([str(word) for word in item])

if __name__=='__main__':
    main()
