#!/usr/bin/env python
# coding=utf-8
import re
import copy
from global_config import *
import entity_recognition as ER




class ExtractSentenceTrunk:
    def __init__(self):
        pass


    def __swap(self,a,b):
        return b,a

    '''去掉括号里的内容'''
    def remove_all_kuohao(self, sentence):
        pattern = r'（.*?）|\(.*\)'
        kuohao_list = re.findall(pattern, sentence)
        for kuohao in kuohao_list:
            sentence = sentence.replace(kuohao, '')
        return sentence


    '''判断两个公司名称是否指向相同公司'''
    def is_same_company(self, cmp1, cmp2):
        '''
        功能: 判断两个公司名称是否指向相同公司
        参数: cmp1: 公司名字符串
             cmp2: 公司名字符串
        返回值: Bool值, 是:True, 否: False
        '''
        result = False    # 结果, 默认为False

        # 令cmp1为cmp1和cmp2字符串中长度较长的一个
        if len(cmp1) < len(cmp2):
            tmp = cmp1
            cmp1 = cmp2
            cmp2 = tmp
        # 判断cmp1是否只比cmp2多出地名表示. 若是,则为相同公司名, 否则为不同公司名
        if cmp2 in cmp1:
            cmp1 = cmp1.replace(cmp2,'')
            if cmp1.endswith('省'):
                cmp1 = cmp1.replace('省','')
            if cmp1.endswith('市'):
                cmp1 = cmp1.replace('市','')
            if CITY_ACTREE.query(cmp1):
                result = True
        return result


    '''替换句子中[公司/政府机构]名为特定符号'''
    def replaceOrgnizationName(self, sentence):
        '''
        功能: 替换句子中[公司/政府机构]名为特定符号[如ORG1,ORG2....]
             (需要判断是否有相似的公司名称,如[北京百度科技有限公司]和[百度科技有限公司], 仅有地名之差)
        参数: sentence: 待处理的句子.
        返回值: 机构名称替换后的句子, 机构名称替换字典
        '''

        replace_orgname_dict = {}   # 机构名称的替换字典, key:符号, value:词项
        flag, orgnize_triples = ER.findAllOrgnization(sentence)  # 查找[机构名称]实体
        cmp_triples = sorted(orgnize_triples, key=lambda x:x[0], reverse=True)   # 按照索引位置从大到小排序
        i = 1
        tmpdict = {}    # 临时记录所有符号和词项的字典
        for cmp in cmp_triples:    #cmp结构为(start, end, word)
            #  当前key与tmpdict中的key完全相同,则可直接使用其符号表示
            if tmpdict.has_key(cmp[2]):
                sign = tmpdict[cmp[2]]
                sentence = sentence[:cmp[0]] + '' + sign + '' + sentence[cmp[1]:]

            # 当前key与tmpdict中的所有key均不相同, 则需要进行去重处理和符号替换
            else:
                curvalue = cmp[2]
                keys = tmpdict.keys()
                key = ''
                flag = False
                for j in range(len(keys)):
                    key = keys[j]
                    flag = self.is_same_company(key, curvalue)   # 判断两个公司名称是否为相同公司名称(去重)
                    if flag == True:
                        break

                # 使用已存在的符号, 并修改符号对应的词项为最长表示字符
                if flag:
                    if len(key) >= len(curvalue):
                        sign = tmpdict[key]
                        sentence = sentence[:cmp[0]]+''+sign+''+sentence[cmp[1]:]
                    else:
                        sign = tmpdict[key]
                        del tmpdict[key]
                        tmpdict[curvalue] = sign
                        sentence = sentence[:cmp[0]] + '' + sign + '' + sentence[cmp[1]:]

                # 新建符号表示
                else:
                    # ----
                    sign = 'ORG'+str(i)
                    sentence = sentence[:cmp[0]]+''+sign+''+sentence[cmp[1]:]
                    tmpdict[cmp[2]] = sign
                    i += 1

        # 整理输出字典
        for key in tmpdict:
            value = tmpdict[key]
            replace_orgname_dict[value] = key

        return sentence, replace_orgname_dict


    '''替换句子中[姓名/职位]等专有名词为特定符号'''
    def replacePorperNoun(self, sentence):
        '''
        功能: 替换句子中[姓名/职位]等专有名词为特定符号[如PROP1,PROP2....]
        参数: sentence: 待处理的句子.
        返回值: 专有名词替换后的句子sentence, 专有名词替换字典
        '''

        replace_proper_noun_dict = {}          # 专有名词替换字典, key:符号, value:词项
        flag, proper_noun_triples = ER.findAllProperNoun(sentence)     # 查找[专有名词]实体
        proper_noun_triples = sorted(proper_noun_triples, key=lambda x: x[0], reverse=True)   # 按照索引位置从大到小排序
        i = 0
        # 构建符号替换字典
        for triple in proper_noun_triples:
            i += 1
            sign = 'PROP' + str(i)
            sentence = sentence[:triple[0]] + '' + sign + '' + sentence[triple[1]:]
            replace_proper_noun_dict[sign] = triple[2]

        return sentence, replace_proper_noun_dict


    '''替换句子书名号为特定符号'''
    def replaceBookTitle(self, sentence):
        '''
        功能: 替换句子书名号为特定符号[如BT1,BT2....]
        参数: sentence: 待处理的句子.
        返回值: 书名号替换后的句子sentence, 书名号替换字典
        '''

        pattern = '(《.*?》)'            # 正则模板
        i = 0                           # 计数符号编号
        replace_booktitle_dict = {}     # 书名号替换字典, key:符号, value:词项
        lst = re.findall(pattern, sentence)
        for item in lst:
            i += 1
            sentence = sentence.replace(item, 'BT'+str(i)+'')
            replace_booktitle_dict['BT'+str(i)] = item

        return sentence, replace_booktitle_dict





    '''句子实体替换处理'''
    def process_est(self,sentence):
        '''
        功能: 句子实体替换处理
        参数: sentence: 待处理的句子.
        返回值: 实体替换后的句子sentence,符号替换字典replace_dicts
        '''
        # 括号去除
        sentence = self.remove_all_kuohao(sentence)
        # 书名号替换
        sentence, replaced_booktitle_dict = self.replaceBookTitle(sentence)
        # 机构名替换
        sentence, replaced_orgnize_dict = self.replaceOrgnizationName(sentence)
        # 姓名/职位替换
        sentence, replaced_proper_noun_dict = self.replacePorperNoun(sentence)
        #TODO 数词替换
        # print sentence



        # 整合输出字典
        replace_dicts = replaced_booktitle_dict.copy()
        replace_dicts.update(replaced_orgnize_dict)
        replace_dicts.update(replaced_proper_noun_dict)

        return sentence, replace_dicts

