# -*- coding=utf-8 -*-

'''
author: lirui
date: 2017-07-26
function: 公共参数或设置
'''

import re, os
import esm
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SentenceSplitter, SementicRoleLabeller
import jieba


def my_print(num):
    print(num)
    return num

LTP_DIR = "./ltp_data"
DICT_DIR = './dicts'
orgnization_file = os.path.join(DICT_DIR, "cmp_govs.txt")
proper_noun_file = os.path.join(DICT_DIR, "name_jobs.txt")
city_file = os.path.join(DICT_DIR, "city_names.txt")
xuzhi_word_dict_file = os.path.join(DICT_DIR,"xuzhi_word_dict.txt")    # 虚指词字典
auxiliary_verb_dict_file = os.path.join(DICT_DIR,"auxiliary_verb_dict.txt")    # 助动词字典
jieba_userdict_file = os.path.join(DICT_DIR, "user_dict.txt")

print "正在加载LTP模型... ..."
segmentor = Segmentor()
# segmentor.load(os.path.join(LTP_DIR, "cws.model"))
segmentor.load_with_lexicon(os.path.join(LTP_DIR, "cws.model"),os.path.join(LTP_DIR, "steel_tar_sti_words.txt"))

postagger = Postagger()
postagger.load(os.path.join(LTP_DIR, "pos.model"))
# postagger.load_with_lexicon(os.path.join(LTP_DIR, "pos.model"),os.path.join(LTP_DIR, "Pos_companyName.txt"))

parser = Parser()
parser.load(os.path.join(LTP_DIR, "parser.model"))

recognizer = NamedEntityRecognizer()
recognizer.load(os.path.join(LTP_DIR, "ner.model"))

labeller = SementicRoleLabeller()
# labeller.load(os.path.join(LTP_DIR, 'pisrl.model') )  # 语义角色标注模型目录路径，模型目录为`srl`。
labeller.load(os.path.join(LTP_DIR, 'srl') )  # 语义角色标注模型目录路径，模型目录为`srl`。
print "加载模型完毕。"





'''加载字典'''
def load_dict(path):
    lists = []
    with open(path, 'r') as fp:
        for eachLine in fp:
            if len(eachLine.strip()) == 0:
                continue
            else:
                lists.append(eachLine.strip())
    return lists



'''加载字典及字典标注'''
def load_dict_labeled(path):
    '''
    功能: 加载词典中的字典
    参数: path: 词典存储路径
    返回值: 字典类型. 返回词项的字典
    '''
    dics ={}
    with open(path, 'r') as fp:
        for eachLine in fp:
            eachLine = eachLine.strip()
            if len(eachLine) == 0:
                continue
            else:
                info =eachLine.split('\t')
            dics[info[0]] = info[1]
    return dics


'''根据字典构造AC树'''
def makeACTree(dictPath="", wordList = []):
    if dictPath=="":
        allWordList = wordList
    else:
        allWordList = list(set(load_dict(dictPath)+wordList))

    esmreIndex = esm.Index()
    for word in allWordList:
        esmreIndex.enter(word)
    esmreIndex.fix()

    return esmreIndex

# 加载jieba用户字典
jieba.load_userdict(jieba_userdict_file)


# 公司名树 ACTREE
ORGNIZE_ACTREE = makeACTree(dictPath=orgnization_file)
# 专有名词树 ACTREE
PROPER_NOUN_ACTREE = makeACTree(dictPath=proper_noun_file)
# 城市名树  ACTREE
CITY_ACTREE = makeACTree(dictPath=city_file)
# EST中实体符号表示的集合
ENTITY_SIGN = ['BT','PROP','ORG']
# 虚指词ACTree
XUZHI_WORD_ACTREE = makeACTree(dictPath=xuzhi_word_dict_file)
# 助动词ACTree
AUXILIARY_VERB_SET = set(load_dict(auxiliary_verb_dict_file))