#coding=utf-8
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib,urllib2
from urllib import quote
from lxml import etree
import json


def info_extract_baidu(word):#百度百科
    url = "http://baike.baidu.com/item/%s" % quote(word)
   # print url
    content = urllib.urlopen(url).read().replace('&nbsp;','')
    selector = etree.HTML(content)
    info_data = {}
    attribute_list=[]
    value_list=[]
    try:
        for li_result in selector.xpath('//div[@class="basic-info cmn-clearfix"]')[0].xpath('./dl'):
            for attribute in li_result.xpath('./dt'):
                attribute_list.append(attribute.xpath('string(.)').replace('\n','').replace('\r',''))
            for attribute in li_result.xpath('./dd'):
                value_list.append(attribute.xpath('string(.)').replace('\n','').replace('\r',''))
        for index in range(0,len(attribute_list)):
            info_data[attribute_list[index]]=value_list[index]
    except:
        pass

    return info_data

def info_extract_biying(word):#必应网典
    url = "http://www.bing.com/knows/search?q=%s" % quote(word)
  #  print url
    content = urllib.urlopen(url).read().decode('utf-8').replace('&nbsp;','').replace('：','')
    selector = etree.HTML(content)
    info_data = {}
    try:
        for li_result in selector.xpath('//div[@class="bk_sidebar_content"]')[0].xpath('./div'):
            attribute = li_result.xpath('./div[1]')[0].xpath('string(.)')
            value = li_result.xpath('./div[2]')[0].xpath('string(.)')
            info_data[attribute] = value
    except:
        pass

    return info_data

def info_extract_hudong(word):#互动百科
    url = "http://www.baike.com/wiki/%s" % quote(word)
   # print url
    content = urllib.urlopen(url).read().replace('&nbsp;', '').replace('：', '')
    selector = etree.HTML(content)
    info_data = {}
   #基本信息抽取
    for li_result in selector.xpath('//div[@class="module zoom"]')[0].xpath('//tr'):
        try:
            info_data[li_result.xpath('./td[1]/strong/text()')[0]]=li_result.xpath('./td[1]/span')[0].xpath('string(.)').replace('\r','').replace('\n','').replace(' ','')
            info_data[li_result.xpath('./td[3]/strong/text()')[0]]=li_result.xpath('./td[3]/span')[0].xpath('string(.)').replace('\r','').replace('\n','').replace(' ','')
        except:
            pass

    introduction=selector.xpath('//div[@class="summary"]')[0].xpath('string(.)').replace('编辑摘要','')
    if "互动百科" in introduction:
        introduction="恩,我再想想,一时想不起来了....."
   # info_data['词条介绍']=introduction

    #关系信息抽取
    try:
        for li_result in selector.xpath('//ul[@id="fi_opposite"]')[0].xpath('./li'):
            try:
                target = ' '.join(li_result.xpath('./a/text()')).replace('\n', '').split('[')[0].split('（')[0]
                relation = ' '.join(li_result.xpath('./text()')).replace('\n', '').split('[')[0].split('（')[0]
                if relation not in info_data.keys():
                    info_data[relation] = target
            except:
                pass
    except:
        pass
    try:
        for li_result in selector.xpath('//ul[@id="holder1"]')[0].xpath('./li'):
            try:
                target = ' '.join(li_result.xpath('./a/text()')).replace('\n', '').split('[')[0].split('（')[0]
                relation = ' '.join(li_result.xpath('./text()')).replace('\n', '').split('[')[0].split('（')[0]
                if relation not in info_data.keys():
                    info_data[relation] = target
            except:
                pass
    except:
        pass

    #关系合并/修正
    for target, relation in info_data.items():
        if relation=='':
            relation="朋友"
        info_data[target]=relation

    return info_data,introduction


def info_extract_union(word):#百科知识融合,做三元组信息的整理工作
    word=word.encode('utf-8')
    info_baidu=info_extract_baidu(word)
    info_hudong,introduction=info_extract_hudong(word)
    info_biying=info_extract_biying(word)
   # info_wiki=info_extract_wiki(word)
    info_data={}
    for attribute,value in info_baidu.items():
        if attribute not in info_data.keys():
            info_data[attribute]=value
        else:
            info_data[attribute]+='、'+value

    for attribute,value in info_hudong.items():
        if attribute not in info_data.keys():
            info_data[attribute]=value
        else:
            info_data[attribute]+='、'+value

    for attribute,value in info_biying.items():
        if attribute not in info_data.keys():
            info_data[attribute]=value
        else:
            info_data[attribute]+='、'+value

    object_list=info_data.keys()
    remove_list=[]
    for sub_object in object_list:
        for object in object_list:
            if sub_object != object and sub_object in object:
                remove_list.append(sub_object)
    remove_list = list(set(remove_list))
    object_list_new = [i for i in object_list if i not in remove_list]
    info_data_modify={}
    for attribute in object_list_new:
        info_data_modify[attribute.replace(' ','').replace('，',',').replace('、',',').split(',')[0]]=','.join(list(set(info_data[attribute].replace(' ','').replace('；','、').replace('等','').replace('，','、').split('、')))).split('[')[0]
    info_data_modify['introduction']=introduction.replace('\n','')
   
    #for key,value in info_data_modify.items():
    #    print key,value

    return info_data_modify


if  __name__=="__main__":
    word=raw_input("please enter an word to search:")
    while(1):
        try:
            info_extract_union(word)
            word=raw_input("please enter an word to search:")
        except:
            word=raw_input("please enter an word to search:")
