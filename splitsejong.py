import re
import os
import glob
from pathlib import Path
from nltk.data import find
from nltk.tag.util import str2tuple
__space_mark="@SP@"
def __search(path,patten):
    if re.compile(patten).search(str(path)) is None:
        return False
    return True
def remove_num(data):
    return re.compile(r'__[0-9]+').sub('',data)
def remove_alpha(data):
    return re.compile(r'/[A-Z+]').sub('',data)
def remove_alphaplus(data):
    return re.compile(r'/[A-Z+]+').sub('',data)


def make_file(path,number,extension,data,encoding='utf8'):
    search_name=re.compile(r'(\\([a-zA-Z]+)(\d+))$').search(str(path))##메이크파일정규식도 바꿀수잇게
    wfn=search_name.group(2)+number+extension
    with open(wfn,'w',encoding=encoding) as f:
        print("".join(data),file=f)

        
def make_file2(name,number,data,encoding='utf8'):
    wfn=name+number+".txt"
    with open(wfn,'w',encoding=encoding) as f:
        print("".join(data),file=f)
    
def split_fraction(path,fpatten='sj\d+',encoding='utf8'):#fpatten을 좀더 name이랑 분리해서 사용하기쉽게



    files=[dir_now for dir_now in path.iterdir() if dir_now.is_file()  and __search(dir_now,fpatten)]
    ##글롭을 써서 한줄코

    
##    files = path.glob(r'.*.txt')
##    for f in files:
##        print(f.name)
    for file in files:
        
        f=file.open(encoding=encoding).read()
        
 
        raw=['\n\n']
        tag_morphed=['\n\n']
        tag_raw=['\n\n']

        
        sent_rule=re.compile('(.+?)\n\n',re.DOTALL)##이거 멀티라인으로 더줄일수잇을
        del_sent_num_rule=re.compile('# \d+ / \d+\n')
        word_morph_rule=re.compile(r'(?P<raw>.+)[ \t]+(?P<tag>.+)[\n]*')
        
        for sent in sent_rule.findall(f):##2줄씩 있는거 붙이고
                                         ## 한줄코딩가능하지만 그럴경우 문장경계를 어떻게 찾을지
            
            del_sent_num=del_sent_num_rule.sub('',sent)## #3 /#3 이런 문장번호 지우고
            tagged = re.split(r'\s+', del_sent_num)
            raw.append([tagged[i] for i in range(0, len(tagged), 2)])
            tag_morphed.append([remove_num(tagged[i]) for i in range(1, len(tagged), 2)])
            tag_raw.append([tagged[i] for i in range(1, len(tagged), 2)])
##            print(words)
##            print(tag_m)
##            print(morph)
##            for word_morph in word_morph_rule.finditer(del_sent_num):##그룹핑
##                raw_w=word_morph.group(1).strip()
##                tag_m=word_morph.group(2).strip()
##                morph=remove_alphaplus(remove_num(tag_m))
##                raw.extend([raw_w,__space_mark])
##                tag_morphed.extend([tag_m,__space_mark])
##                morphed.extend([morph,__space_mark])
####                if next(r,None) is None: 이터레이션문제
##            raw.pop()
##            tag_morphed.pop()
##            morphed.pop()
            raw.append('\n\n\n')
            tag_morphed.append('\n\n\n')
            tag_raw.append('\n\n\n')
            print(raw)
##            print(tag_morphed)
##            print(tag_raw)
##        
        ##플러스 그룹핑 /[a-zA-Z]+\+


        try:##숫자찾기
            search_num=re.compile('\d+$').search(str(file))##이것도 맞는지
        except IOError:
            print(e)
            ##return raise 
        number=search_num.group()
        make_file2("sjr",number,raw)##nltk에서 load할때 확장자명변경을 안함
        make_file2("sjtm",number,tag_morphed)
        make_file2("sjm",number,morphed)
        
##        make_file(file,number,'.raw',raw)  ##확장자로 붙일때
##        make_file(file,number,'.tagm',tag_morphed)
##        make_file(file,number,'.morph',morphed)
##
        


if __name__=="__main__":
    path_f=find("corpora\\sejong").path
    
    p=Path(path_f)
    
    
    os.chdir(os.path.join(path_f))
    #os.chdir(p) 3.6일때
    split_fraction(p)
