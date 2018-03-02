#!/usr/bin/env python
# coding=utf-8
import math
from syntax_parser import *

"""递归查找ATT等关系,查找修饰路径"""
def check_predicate_type(sent_parse_list,predicate_pair):
    SBV_flag=0
    ATT_flag=0
    VOB_flag=0

    for item in sent_parse_list:
        if item[0] == 'SBV' and item[5] == predicate_pair[0]:
            SBV_flag+=1
        if item[0] in ['ATT','ADV'] and item[5] == predicate_pair[0]:
            ATT_flag+=1
        if item[0] in ['VOB','POB'] and item[5] == predicate_pair[0]:
            VOB_flag+=1        
    
    if SBV_flag>0:
        return 'SBV'
         
    elif ATT_flag>0:
        return 'ATT'

    elif VOB_flag>0:
        return 'VOB'

    else :
        return ''

"""属性值修正,取最大化"""
def maxlen_attributes(item_list):
    remove_list=[]
    for item1 in item_list:
        for item2 in item_list:
            if item1 in item2 and item1 !=item2:
                remove_list.append(item1)
    max_list=[tmp for tmp in item_list if tmp not in remove_list]
    return max_list


"""查找修饰路径"""
def find_attributes(sent_parse_list,subject_pair,relation):
    def check_child(word_index,word_name,sent_parse_list,relation,word_fullname):
        if not word_index:
            return 
        else:
            for subitem in sent_parse_list:
                if subitem[0] in relation and subitem[5] == word_index:
                    word_subindex=subitem[2]
                    word_subname=subitem[1]
                    word_fullname=word_subname+'_'+word_fullname
                    result_list.append([word_name,word_subname,word_subindex,word_index,word_fullname])
                    check_child(word_subindex,word_subname,sent_parse_list,relation,word_fullname)
    
    attributed_subject=[]
    for item in sent_parse_list:

        result_list=[]
        if item[0] in relation and item[5] == subject_pair[0]:
            word_index=item[2]
            word_name=item[1]
            word_fullname=word_name
            check_child(word_index,word_name,sent_parse_list,relation,word_fullname)       
            
            if len(result_list)>0:
                for pair in result_list:
                    attributed_subject.append(pair[-1])
            else:
                attributed_subject.append(word_name)

    return attributed_subject

"""获取问句核心"""
def find_question_predicate(sent_parse_list):
    predicate_arc=[]
    for arc in sent_parse_list:
        if arc[0] == 'HED':
            predicate_arc=arc
    predicate_pair=[predicate_arc[2],predicate_arc[1],predicate_arc[3]]

    return predicate_pair
    
"""扩展问句核心词"""
def find_all_predicates(predicate_pair,sent_parse_list):
    predicate_pairs=[]
    predicate_pairs.append(predicate_pair)
        
    for item in sent_parse_list:
        if item[0]=='COO' and item[5]==predicate_pair[0]:
            predicate_pairs.append([item[2],item[1]])
            for subitem in sent_parse_list:
                if subitem[0]=='COO' and subitem[5]==item[2]:
                    predicate_pairs.append([subitem[2],subitem[1]])

    return predicate_pairs

"""查找问句核心主语subject"""

def find_question_subject(predicate_pair,sent_parse_list,relation):
    #根据核心词,查找核心词动作的主体, 根据COO扩展subject           
    subject_pairs=[]
    for item in sent_parse_list:
        if item[0] in relation and item[5] == predicate_pair[0]:
            subject_arc=[item[2],item[1]]
            subject_pairs.append(subject_arc)
            for sub_item in sent_parse_list:
                if sub_item[0]=='COO' and sub_item[5] == subject_arc[0]:
                    subject_pairs.append([sub_item[2],sub_item[1]])
    
    return subject_pairs

"""查找问句宾语,object"""
def find_question_object(predicate_pair,sent_parse_list):
    #根据核心词,查找事实路线,根据VOB->COO查找VOB的扩展体 
    object_pairs=[]
    for item in sent_parse_list:
        if item[0] in ['VOB','POB'] and item[5] == predicate_pair[0]:
            object_pair=[item[2],item[1]] 
            object_pairs.append(object_pair)
            for sub_item in sent_parse_list:
                if sub_item[0] in ['COO'] and sub_item[5] == object_pair[0]:
                    object_pairs.append([sub_item[2],sub_item[1]])

    return object_pairs

"""<s,p,o>三元组提取"""
def spo_parser(predicate_type,predicate_pairs,sent_parse_list,subject_relation,attributed_relation,predicate_relation,relation_dict):
    subject_list=[]
    spo_list=[]
    for predicate_pair in predicate_pairs:
        attributed_predicate=maxlen_attributes(find_attributes(sent_parse_list,predicate_pair,predicate_relation))
        #print 'attributed_predicate','*'.join(attributed_predicate)

        subject_pairs=find_question_subject(predicate_pair,sent_parse_list,subject_relation)

        #print 'subject_pairs',subject_pairs
        subject_attribute_dict={}
        for subject_pair in subject_pairs:
            attributed_subject=maxlen_attributes(find_attributes(sent_parse_list,subject_pair,attributed_relation))
            subject_attribute_dict[str(subject_pair[0])+'_'+str(subject_pair[1])]=attributed_subject
        #print 'subject_attribute_dict',subject_attribute_dict

        if len(subject_pairs)<1:
            subject_pairs=[['NA','NA']]
            subject_attribute_dict['NA_NA']=''
        
        if predicate_type == 'VOB':
            #VOB结构中不存在object,将其转换成subject进行处理
            object_pairs=[['NA','NA']]
            object_attribute_dict={}
            object_attribute_dict['NA_NA']=''
        else:
            object_pairs=find_question_object(predicate_pair,sent_parse_list)
            #print 'object_pairs',object_pairs
            object_attribute_dict={}
            for object_pair in object_pairs:
                attributed_object=maxlen_attributes(find_attributes(sent_parse_list,object_pair,attributed_relation))
                object_attribute_dict[str(object_pair[0])+'_'+str(object_pair[1])]=attributed_object
            #print 'object_attribute_dict',object_attribute_dict
            
            if len(object_pairs)<1:
                object_pairs=[['NA','NA']]

            object_attribute_dict['NA_NA']=''
        
        for subject_pair in subject_pairs:
            for object_pair in object_pairs:
                spo_dict={}
                spo_dict['S']=[subject_pair[1],' '.join(subject_attribute_dict[str(subject_pair[0])+'_'+str(subject_pair[1])])]
                spo_dict['P']=[predicate_pair[1],' '.join(attributed_predicate)]
                spo_dict['O']=[object_pair[1],' '.join(object_attribute_dict[str(object_pair[0])+'_'+str(object_pair[1])])]                
                if spo_dict['S'][0] !='NA':
                    subject_list.append(spo_dict['S'][0])
                spo_list.append(spo_dict)
        
    return spo_list,list(set(subject_list))

def question_parser(sent_parse_list,relation_dict):
    #获取问句核心词
    predicate_pair=find_question_predicate(sent_parse_list)
    #根据问句predicate_pair,选择扩展方式
    predicate_type=check_predicate_type(sent_parse_list,predicate_pair)
    print predicate_type
    #扩展问句核心词
    predicate_pairs=find_all_predicates(predicate_pair,sent_parse_list)
    
    attributed_relation=['ATT','ADV','COO']
    predicate_relation= ['ATT','ADV']

    if predicate_type == 'SBV':
        subject_relation=['SBV']

    elif predicate_type == 'ATT':
        subject_relation=['ATT','POB']
        attributed_relation=['ATT','ADV','COO','POB']

    elif predicate_type == 'VOB':
        subject_relation=['VOB','POB','SBV']
        attributed_relation=['ATT','ADV','COO','SBV','VOB']

    spo_list,subject_list=spo_parser(predicate_type,predicate_pairs,sent_parse_list,subject_relation,attributed_relation,predicate_relation,relation_dict)
    spo_list=fulfil_spo(spo_list,sent_parse_list,subject_list,relation_dict)
    
    return spo_list
 
"""根据依存关系,修正spo"""
def fulfil_spo(spo_list,sent_parse_list,subject_list,relation_dict):
    for spo in spo_list:
        if spo['S'][0] == 'NA' :
            spo['S'][0] = subject_list[0]
    
    return spo_list


def main_parser(sentence):

    parse_object=SyntaxParsing()
    sent_parse_list = parse_object.process_parse_structure(sentence)        
    relation_list=[]
    relation_dict = {}
    for item in sent_parse_list:
        relation_list.append(item[0])
        relation_dict[item[1]+'_'+item[4]]=item[0]

    spo_list=question_parser(sent_parse_list,relation_dict)

    return spo_list

   
if __name__=="__main__":
    sentence=raw_input('please enter an sentence to parser:')
    while(1):
        for spo in main_parser(sentence):
            for key,value in spo.items():
                print key,value[0],value[1]
        sentence=raw_input('please enter an sentence to parser:')
 
