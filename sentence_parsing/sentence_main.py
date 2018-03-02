#coding=utf-8
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
from global_config import *
from sentence_parsing import *


def sentence_process_main():
    sentence="国务院总理李克强调研上海外高桥时提出，支持上海积极探索新机制" 
    persons,organs=collect_entity(sentence)
    print 'persons',' '.join(persons)
    print 'organs',' '.join(organs)

    entity_tag_dict={}
    tag_entity_dict={}

    for index in range(len(persons)):
        entity_tag_dict[persons[index]]=' nh'+str(index)+'p '
    for index in range(len(organs)):
        entity_tag_dict[organs[index]]=' ni'+str(index)+'p '

    for index in range(len(persons)):
        tag_entity_dict[' nh-'+str(index)+'p ']=persons[index]
    for index in range(len(organs)):
        tag_entity_dict[' ni-'+str(index)+'p ']=organs[index]
    
    for entity,tag in entity_tag_dict.items():
        sentence=sentence.replace(entity,tag)
        
    words_list=sententce_segment(sentence)
    postags=sentence_postagger(words_list)
    netags=sentence_entityrecongizer(words_list,postags)
    arcs=sentence_parser(words_list,postags)
    labels=sentence_labeler(words_list, postags, netags, arcs)
    arc_tuples=parser_tuples(words_list,postags,arcs)
 
    return arc_tuples


if __name__=="__main__":
    sentence_process_main()
