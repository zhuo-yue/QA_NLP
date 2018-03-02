#!/usr/bin/env python
# coding=utf-8
import os,sys
import esm
from global_config import *
# import global_config

reload(sys)
sys.setdefaultencoding('utf-8')


'''根据关键词的AC树对句子进行查找'''
def findKeyWords(sentence, KeyWordTree):
    p1 = None
    items = []
    for item in KeyWordTree.query(sentence):
        p2 = item[0]
        if p1 is None:
            items.append(item)
        else:
            if p2[0] >= p1[1]:
                items.append(item)
            elif len(item[1]) > len(items[-1][1]):
                tmp = items.pop()
                items.append(item)
            else:
                pass
        p1 = p2
    kwds = []
    for each in items:
        first = each[0][0]
        last = each[0][1]
        kwds.append((first, last, each[1]))


    if kwds:
        return True, kwds
    else:
        return False, kwds



'''通过LTP识别姓名实体'''
def hasPersonName(sentence):
    if len(sentence.strip()) == 0:
        return False, []
    words = [word.encode('utf-8') for word in jieba.cut(sentence)]  # 分词
    postags = postagger.postag(words)  # 词性标注
    netags = recognizer.recognize(words, postags)  # 实体标注
    # find  name
    tmp = []
    count = 0
    oragnizeIndex = []
    orgs = []
    for tag in netags:
        if tag == "S-Nh":
            oragnizeIndex.append([count])
        elif tag == "B-Nh":
            tmp.append(count)
        elif tag == "I-Nh":
            tmp.append(count)
        elif tag == "E-Nh":
            tmp.append(count)
            oragnizeIndex.append(tmp)
            tmp = []
        else:
            pass
        count += 1

    for eachIndex in oragnizeIndex:
        og = ''
        for eachOragnize in eachIndex:
            og += words[int(eachOragnize)]
        if len(og) == 3:
            continue

        orgs.append(og)
    if not orgs:
        return False, []
    else:
        return True, orgs


'''通过LTP 识别机构实体'''
def hasOrgnization(sentence):
    orgs = []
    hasOrganize = False
    if len(sentence.strip())==0:
        return hasOrganize,orgs
    words = [word.encode('utf-8') for word in jieba.cut(sentence)]  #分词
    postags = postagger.postag(words)  #词性标注
    netags = recognizer.recognize(words, postags)  #实体标注
    # print sentence
    # print '  '.join(words)
    # print '  '.join(postags)
    # print '  '.join(netags)
    count = 0
    oragnizeIndex = []
    tmp = []
    for tag in netags:
        if tag == 'S-Ni':
            oragnizeIndex.append([count])
        elif tag == 'B-Ni':
            tmp.append(count)
        elif tag == 'I-Ni':
            tmp.append(count)
        elif tag == 'E-Ni':
            tmp.append(count)
            oragnizeIndex.append(tmp)
            tmp = []
        else:
            pass
        count += 1


    for eachIndex in oragnizeIndex:
        og = ''.join([words[idx] for idx in eachIndex])
        orgs.append(og)
    # print oragnizeIndex
    if orgs:
        hasOrganize = True
        return hasOrganize,orgs
    else:
        return hasOrganize,orgs



'''获取公司/政府/机构实体'''
def findAllOrgnization(sentence):

    # 根据LTP找机构名
    flag_ner, companyList = hasOrgnization(sentence)
    companyList = list(set(companyList))

    # 根据上述两种公司名+公司名词典构造AC树
    if flag_ner == False:
        flag, orgnizeTripleList = findKeyWords(sentence, ORGNIZE_ACTREE)
    else:
        flag_ac, orgnizeTripleList_ac = findKeyWords(sentence, ORGNIZE_ACTREE)

        orgnize_ltp_ACTree = makeACTree(wordList=companyList)
        flag_ltp, orgnizeTripleList_ltp = findKeyWords(sentence, orgnize_ltp_ACTree)

        if flag_ac or flag_ltp:
            flag = True
            orgnizeTripleList = list(set(orgnizeTripleList_ac+orgnizeTripleList_ltp))
            orgnizeTripleList = merge_intersect_item(orgnizeTripleList)
        else:
            flag = False


    if flag==False:
        return False, []
    else:
        return True, orgnizeTripleList



'''对查找的元素有并集的索引及元素合并'''
def merge_intersect_item(triple_list):
    out = []
    triple_list = sorted(triple_list, key=lambda x:x[0])

    for item in triple_list:
        if out and item[0] <= out[-1][1]:
            new_tripple = (out[-1][0], max(out[-1][1], item[1]), out[-1][2])
            del out[-1]
            out.append(new_tripple)

        else:
            out.append(item)

    return out




'''获取专有名词实体[姓名/职位]'''
def findAllProperNoun(sentence):
    '''
    功能: 获取专有名词实体[姓名/职位]
    参数: sentence: 待处理的句子.
    返回值: flag表示是否存在相应实体; properNounTripleList 为list类型, 表示实体元组构成的列表
    '''


    # 1. 先根据LTP识别[姓名]实体(鉴于LTP只能识别特定类型的实体)
    flag_ner, person_name_list = hasPersonName(sentence)
    person_name_list = list(set(person_name_list))

    # 2. 利用AC树进行实体查找,提高效率
    # 2.1 没有识别到姓名实体,则直接在外部词典中查找
    if flag_ner == False:
        flag, properNounTripleList = findKeyWords(sentence, PROPER_NOUN_ACTREE)
    # 2.2 识别到新的实体, 则需要再构建一个AC树,并在两个AC树上查找.
    else:
        flag_ac, properNounTripleList_ac = findKeyWords(sentence, PROPER_NOUN_ACTREE)

        name_ltp_ACTree = makeACTree(wordList=person_name_list)
        flag_ltp, nameTripleList_ltp = findKeyWords(sentence, name_ltp_ACTree)

        if flag_ac or flag_ltp:
            flag = True
            properNounTripleList = list(set(properNounTripleList_ac + nameTripleList_ltp))
            properNounTripleList = merge_intersect_item(properNounTripleList)
        else:
            flag = False


    if flag == False:
        return False, []
    else:
        return True, properNounTripleList

if __name__=='__main__':
    words=['2007年25日','我','去','江西省信丰县','看','爸妈','半天']
    postags=['nt','r','v','ns','v','n','nt']
  #  words = [word.encode('utf-8') for word in jieba.cut(sentence)]  #分词
  #  postags = postagger.postag(words)  #词性标注
    arcs = parser.parse(words, postags)  # 句法分析
    print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
    
