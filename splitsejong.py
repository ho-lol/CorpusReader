import re
import os
from pathlib import Path
from nltk.data import find
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
    f.close()
def make_file2(name,number,data,encoding='utf8'):
    wfn=name+number+".txt"
    with open(wfn,'w',encoding=encoding) as f:
        print("".join(data),file=f)
    f.close()
    
def split_fraction(path,fpatten='sj\d+',encoding='utf8'):#fpatten을 좀더 name이랑 분리해서 사용하기쉽게



    files=[dir_now for dir_now in path.iterdir() if dir_now.is_file() and __search(dir_now,fpatten)]
    for file in files:
        
        f=file.open(encoding=encoding).read()
        
 
        raw=['\n\n']
        tag_morphed=['\n\n']
        morphed=['\n\n']

        
        sent_rule=re.compile('(.+?)\n\n',re.DOTALL)##이거 멀티라인으로 더줄일수잇을
        del_sent_num_rule=re.compile('# \d+ / \d+\n')
        word_morph_rule=re.compile(r'(?P<raw>.+)[ \t]+(?P<tag>.+)[\n]*')
        
        for sent in sent_rule.findall(f):
            del_sent_num=del_sent_num_rule.sub('',sent)
            for word_morph in word_morph_rule.finditer(del_sent_num):
                raw_w=word_morph.group(1).strip()
                tag_m=word_morph.group(2).strip()
                morph=remove_alphaplus(remove_num(tag_m))
                raw.extend([raw_w,__space_mark])
                tag_morphed.extend([tag_m,__space_mark])
                morphed.extend([morph,__space_mark])
##                if next(r,None) is None: 이터레이션문제
            raw.pop()
            tag_morphed.pop()
            morphed.pop()
            raw.append('\n\n\n')
            tag_morphed.append('\n\n\n')
            morphed.append('\n\n\n')


        try:
            search_num=re.compile('\d+$').search(str(file))##이것도 맞는지
        except IOError:
            print(e)
        number=search_num.group()
        make_file2("sjr",number,raw)
        make_file2("sjtm",number,tag_morphed)
        make_file2("sjm",number,morphed)
        
##        make_file(file,number,'.raw',raw)
##        make_file(file,number,'.tagm',tag_morphed)
##        make_file(file,number,'.morph',morphed)
##
        


if __name__=="__main__":
    path=find("corpora\\sejong").path
    
    p=Path(path)
    os.chdir(p)
    split_fraction(p)
