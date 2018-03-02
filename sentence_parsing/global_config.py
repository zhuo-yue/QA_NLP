#coding=utf-8
import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SentenceSplitter, SementicRoleLabeller
import jieba

LTP_DIR='./ltp_data'
DICT_DIR='./dicts'
print "正在加载LTP模型... ..."
segmentor = Segmentor()
segmentor.load_with_lexicon(os.path.join(LTP_DIR, "cws.model"),os.path.join(DICT_DIR, "user_dict.txt"))

postagger = Postagger()
postagger.load(os.path.join(LTP_DIR, "pos.model"))
# postagger.load_with_lexicon(os.path.join(LTP_DIR, "pos.model"),os.path.join(LTP_DIR, 
parser = Parser()
parser.load(os.path.join(LTP_DIR, "parser.model"))

recognizer = NamedEntityRecognizer()
recognizer.load(os.path.join(LTP_DIR, "ner.model"))

labeller = SementicRoleLabeller()

labeller.load(os.path.join(LTP_DIR, 'srl') )  # 语义角色标注模型目录路径，模型目录为`srl`。
print "加载模型完毕。"
userdict_path=os.path.join(DICT_DIR,'user_dict.txt')
