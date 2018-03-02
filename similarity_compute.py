#coding=utf-8
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
import gensim, logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import numpy as np
import jieba.posseg as pesg
model = gensim.models.KeyedVectors.load_word2vec_format("word_vector.bin", binary=False)


def calculate_semantic(word1,word2):
    try:
        word_score=model.similarity(word1,word2)
    except:
        word_score=0.0

    return word_score


if __name__=="__main__":
    word1='a'
    word2='b'
    calculate_semantic(word1,word2)