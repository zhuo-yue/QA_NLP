#coding=utf-8

import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')

from info_extract import *
from similarity_compute import *
from question_parser import *


def modify_sentence(sentence):
    sentence=sentence.split('是')[0]
    sentence=sentence.split('有')[0]
    sentence=sentence.split('怎样')[0]
    sentence=sentence.split('怎么')[0]
    sentence=sentence.split('多少')[0]
    sentence=sentence.split('如何')[0]
    sentence=sentence.split('? ')[0]

    return sentence

def demo():
    sentence = raw_input("please enter your question:")
     
    sentence = modify_sentence(sentence)

    while(1):
        try:
            search_dict = {}
            spo_list = main_parser(sentence)
            for spo in spo_list:
                if spo['S'] !=  'NA':
                    word = spo['S'][0]
                    attribute = spo['P'][0]
                    if word not in search_dict:
                        search_dict[word]=attribute
                    else:
                        search_dict[word]+=','+attribute

            for search_word,attributes in search_dict.items():
                search_word=search_word.decode('utf-8')
                
                info_data=info_extract_union(search_word)
                match_dict={}

                for attribute in attributes.split(','):
                    attribute=attribute.decode('utf-8')

                    score_dict={}
                    for tmp in info_data.keys():
                        score=calculate_semantic(attribute,tmp)
                        score_dict[tmp] = score
                    
                    score_dict=sorted(score_dict.items(),key=lambda asd:asd[1],reverse=True)

                    best_match=[word[0] for word in score_dict][0]
                    match_dict[attribute]=best_match

                
                for attribute in attributes.split(','):

                    attribute=match_dict[attribute.decode('utf-8')]
                    value=info_data[attribute] 

                    print search_word,attribute,info_data[attribute] 
        except:
            print "对不起,我不知道,问点其他的吧"


        sentence = raw_input("please enter an sentence to input:")



if __name__ == '__main__':
    demo()
