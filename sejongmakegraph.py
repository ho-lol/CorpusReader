import re
import os
from difflib import SequenceMatcher
from nltk.data import find
def remove_num(data):
    return re.compile(r'__[0-9]+').sub('',data)
def remove_alpha(data):
    return re.compile(r'/[A-Z+]').sub('',data)
def remove_alphaplus(data):
    return re.compile(r'/[A-Z+]+').sub('',data)
def remove_tag(data):
    return remove_num(data[0:data.rfind('/')])
__space_mark="@SP@"
def exist(values,data):
    for i in values:
        if compare(i[1:],data):
            i[0]+=1
            return True
    return False
def compare(list1,list2):
    if not len(list1)==len(list2):
        return False
    for i in range(len(list1)):
        if not list1[i]==list2[i]:
            return False
    return True
##def remove_num(data):
##    return re.compile(r'__[0-9]+').sub('',data)
##def remove_alpha(data):
##    return re.compile(r'/[A-Z+]').sub('',data)
##def remove_alphaplus(data):
##    return re.compile(r'/[A-Z+]+').sub('',data)
def search_alpha(data):
    return re.compile(r'/[A-Z+]').search(data)
def count_dict(dic,key,value):
    if dic.get(key):
        if not exist(dic[key],value):
            dic[key].append([1]+[ele for ele in value])    
    else:
        dic[key]=[[1]+[ele for ele in value]]
def make_resdata(mat_blocks,reduce_num):
    
    result_txt=reduce_num[mat_blocks[0][0]:mat_blocks[-2][0]+mat_blocks[-2][2]]
    result_list=result_txt.split('+')
    tail=reduce_num[mat_blocks[-2][0]:]
    tail_alpha=search_alpha(tail)
    if tail_alpha:
        result_list[-1]=result_list[-1]+str(tail_alpha.group(0))
    return [data.split('/') for data in result_list]
##rule1=re.compile(r'__[0-9]+')
##rule2=re.compile(r'/[A-Z+]+')
##rule3=re.compile(r'/[A-Z+]')

def make_arrays(fnr="sj00.raw",fnt="sj00.tagm"):
    raw_array=[]
    tagged_array=[]
    for line in open(fnr,'r',encoding="utf8").readlines():
        if line and not line.strip():
            continue
        raw_array.append(line.split(__space_mark))
    for line in open(fnt,'r',encoding="utf8").readlines():
        if line and not line.strip():
            continue
        tagged_array.append(line.split(__space_mark)) 
    return raw_array,tagged_array

def make_dict(result_dic,raw_array,tagged_array):
    
    for raw_sent,tagged_sent in zip(raw_array,tagged_array):
        if not len(raw_sent)==len(tagged_sent):
            continue
        for raw_word,tag_word in zip(raw_sent,tagged_sent):
            
            tag_morph=tag_word.split('+')
            merge_morph="".join([remove_tag(morph) for morph in tag_morph])
            SM=SequenceMatcher(None,raw_word.strip(),merge_morph.strip())
            for tag,i1,i2,j1,j2 in SM.get_opcodes():
                if tag=="replace":
                    print(raw_word)
                    print(merge_morph)
                    print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)"%(tag, i1, i2, raw_word[i1:i2], j1, j2, merge_morph[j1:j2]))
                    print("\n\n")

##     
##                    key=raw_word[i1:i2]
##                    SM2=SequenceMatcher(None, reduce_num,tagged[j1:j2])
##                    mat_blocks=SM2.get_matching_blocks()
##                    result_data=make_resdata(mat_blocks,reduce_num)
                if tag=="insert":
                    print(raw_word)
                    print(merge_morph)
                    print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)"%(tag, i1, i2, raw_word[i1:i2], j1, j2, merge_morph[j1:j2]))
                    print("\n\n")
##                    
##            reduce_num=remove_num(tag_word)
##            tagged=remove_alphaplus(remove_num(tag_word))
##            SM=SequenceMatcher(None,raw_word,tagged)
##            for tag,i1,i2,j1,j2 in SM.get_opcodes():
##                if tag=="equal":
##                    continue
##                if tag=="replace":
##     
##                    key=raw_word[i1:i2]
##                    SM2=SequenceMatcher(None, reduce_num,tagged[j1:j2])
##                    mat_blocks=SM2.get_matching_blocks()
##                    result_data=make_resdata(mat_blocks,reduce_num)
##    ##                result_txt=reduce_num[mat_blocks[0][0]:mat_blocks[-2][0]+mat_blocks[-2][2]]
##    ##                result_list=result_txt.split('+')
##    ##                tail=reduce_num[mat_blocks[-2][0]:]
##    ##                tail_alpha=search_alpha(tail)
##    ##                if tail_alpha:
##    ##                    result_list[-1]=result_list[-1]+str(tail_alpha.group(0))
##    ##                result_data=[data.split('/') for data in result_list]
##
##                    count_dict(result_dic,key,result_data)
##                    
##    ##                if result.get(key):
##    ##                    if not exist(result[key],result_data):
##    ##                        result[key].append([1]+[data for data in result_data])    
##    ##                else:
##    ##                    result[key]=[[1]+[data for data in result_data]]
##
##
##                        
##                if tag=="insert":
##
##                    key=raw_word[i1-1:i2]
##                    SM2=SequenceMatcher(None, reduce_num,tagged[j1-1:j2])
##                    mat_blocks=SM2.get_matching_blocks()
##                    if len(mat_blocks)==1:
##                        continue
##                    result_data=make_resdata(mat_blocks,reduce_num)
##    ##                result_txt=reduce_num[mat_blocks[0][0]:mat_blocks[-2][0]+mat_blocks[-2][2]]
##    ##                result_list=result_txt.split('+')
##    ##                tail=reduce_num[mat_blocks[-2][0]:]
##    ##                tail_alpha=search_alpha(tail)
##    ##                if tail_alpha:
##    ##                    result_list[-1]=result_list[-1]+str(tail_alpha.group(0))
##    ##                result_data=[data.split('/') for data in result_list]
##
##
##                    count_dict(result_dic,key,result_data)
##    ##                
##    ##                if result.get(key):
##    ##                    if not exist(result[key],result_data):
##    ##                        result[key].append([1]+[data for data in result_data])    
##    ##                else:
##    ##                    result[key]=[[1]+[data for data in result_data]]
##    ##
##    ##            if tag=="delete":
##    ##                print(raw_word)
##    ##                print(tagged)
##    ##                print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)"%(tag, i1, i2, raw_word[i1:i2], j1, j2, tagged[j1:j2]))
##    ##                print("\n\n")
                
                    

def make_df(result,fn="dictionary1.dic"):
    with open(fn,'w', encoding="utf8") as f:
        for k,v in result.items():
            print(k,v ,file=f)
            
if __name__=="__main__":
    result_dic={}
    path=find("corpora\\sejong").path
    os.chdir(path)
    files_raw=[]
    files_tagged=[]
    for fn in os.listdir(path):
        if "sjr" in fn:
            files_raw.append(fn)
        elif "sjtm" in fn:
            files_tagged.append(fn)
    raw_array=[]
    tagged_array=[]

    for i in range(len(files_raw)):
        temp_raw_array,temp_tagged_array=make_arrays(fnr=files_raw[i],fnt=files_tagged[i])
        raw_array.extend(temp_raw_array)
        tagged_array.extend(temp_tagged_array)
    
    print("리스트만들기 완료")
    make_dict(result_dic,raw_array,tagged_array)
##    print("사전만들기완료")
##    make_df(result_dic)
