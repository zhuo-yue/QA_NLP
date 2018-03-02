#coding=utf-8
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
from global_config import *
from sentence_parsing import *
import pymongo
conn==pymongo.region_corpus
db=conn.parser_pair


def sentence_process_main():
    for root,dir,files in os.path.join()
    sentence="国务院总理李克强调研上海外高桥时提出，支持上海积极探索新机制" 
    words_list=sententce_segment(sentence)
    postags=sentence_postagger(words_list)
    netags=sentence_entityrecongizer(words_list,postags)
    arcs=sentence_parser(words_list,postags)
    labels=sentence_labeler(words_list, postags, netags, arcs)
    arc_tuples=parser_tuples(words_list,postags,arcs)
 
    for item in arc_tuples:
        pair= item[1]+'_'+item[2]+'_'+item[3]+'_'+item[5]+'_'+item[6]
        print pair
    


if __name__=="__main__":
    sentence_process_main()