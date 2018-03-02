#coding=utf-8
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
from global_config import *

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
    if orgs:
        hasOrganize = True
        return hasOrganize,orgs
    else:
        return hasOrganize,orgs

def collect_entity(sentence):
    persons=hasPersonName(sentence)[1]
    organs=hasOrgnization(sentence)[1]
    
    return persons,organs

def sententce_segment(sentence):
    words = segmentor.segment(sentence)  # 分词
    words_list = list(words)
    return words_list

def sentence_splitter(sentence):
    sents = SentenceSplitter.split(sentence)  # 分句
    return sents

def sentence_postagger(words_list):
    postags = postagger.postag(words_list)  # 词性标注
    return postags

def sentence_entityrecongizer(words_list,postags):
    netags = recognizer.recognize(words_list, postags)  # 命名实体识别
    return netags

def sentence_parser(words_list,postags):

    arcs = parser.parse(words_list, postags)  # 句法分析
    return arcs

def sentence_labeler(words_list, postags, netags, arcs):
    roles = labeller.label(words_list, postags, netags, arcs)  # 语义角色标注
    return roles

def parser_tuples(words_list,postags,arcs):
    tag_list=[]
    for word,tag in zip(words_list, postags):
        tag_list.append(tag)

    tuple_list=[]
    for arc in arcs:
        tuple_list.append([arc.head,words_list[arc.head],arc.relation,tag_list[arc.head]])

    arc_tuples=[]
    for index in range(len(tuple_list)):
        arc_tuples.append([index,words_list[index],tag_list[index],tuple_list[index][2],tuple_list[index][0],tuple_list[index][1],tuple_list[index][3]])

    #for item in arc_tuples:
    #    print item[1],item[2],item[3],item[4],item[5]

    return arc_tuples




if __name__=="__main__":
    sentence_process_main()