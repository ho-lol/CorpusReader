import re
import os
from difflib import SequenceMatcher
from nltk.data import find

__space_mark="@SP@"

##rule1=re.compile(r'__[0-9]+')
##rule2=re.compile(r'/[A-Z+]+')
##rule3=re.compile(r'/[A-Z+]')
def remove_num(data):
    return re.compile(r'__[0-9]+').sub('',data)
def remove_alpha(data):
    return re.compile(r'/[A-Z+]').sub('',data)
def remove_alphaplus(data):
    return re.compile(r'/[A-Z+]+').sub('',data)
def remove_tag(data):
    return remove_num(data[0:data.rfind('/')])

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
def search_alpha(data):
    return re.compile(r'/[A-Z+]').search(data)
def count_dict(dic,key,value):
    if dic.get(key):
        if not exist(dic[key],value):
            dic[key].append([1]+[ele for ele in value])    
    else:
        dic[key]=[[1]+[ele for ele in value]]
def make_resdata(mat_blocks,tag_word):
    
    result_txt=tag_word[mat_blocks[0][0]:mat_blocks[-2][0]+mat_blocks[-2][2]]
    result_list=result_txt.split('+')
    tail=tag_word[mat_blocks[-2][0]:]
    tail_alpha=search_alpha(tail)
    if tail_alpha:
        result_list[-1]=result_list[-1]+str(tail_alpha.group(0))
    return [data.split('/') for data in result_list]


def make_arrays(fnr="sj00.raw",fnt="sj00.tagm"):
    raw_array=[]
    tagged_array=[]
    for line in open(fnr,'r',encoding="utf8").readlines():
        if line and not line.strip():
            continue
        raw_array.append(line.split())
    for line in open(fnt,'r',encoding="utf8").readlines():
        if line and not line.strip():
            continue
        tagged_array.append(line.split()) 
    return raw_array,tagged_array

def make_dict(result_dic,raw_array,tagged_array):
    
    for raw_sent,tagged_sent in zip(raw_array,tagged_array):
        if not len(raw_sent)==len(tagged_sent):
            continue
        for raw_word,tag_word in zip(raw_sent,tagged_sent):
            
            tag_morph=re.split("\+(?=[^\+])",tag_word)
            # ++이 오지않을때를 걸럿는데 이렇게 되면 +가 앞으로가고 뒤에는 아무것도없다.
            merge_morph="".join([remove_tag(morph) for morph in tag_morph])            


            SM=SequenceMatcher(None,raw_word,merge_morph)
            for tag,i1,i2,j1,j2 in SM.get_opcodes():
                if tag=="replace":

                    print(raw_word)
                    print(merge_morph)
##                    print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)"%(tag, i1, i2, raw_word[i1:i2], j1, j2, merge_morph[j1:j2]))
##                    print("\n\n")
                    SM3=SequenceMatcher(None,tag_word,merge_morph)
                    mat_blocks2=SM3.get_matching_blocks()
                    valid_block=[]
                    print(j2)
                    for block in mat_blocks2:
                        if block[1]+block[2]>=j1 and block[1]+block[2]<=j2+1:
                            valid_block.append(block)

                    print(mat_blocks2)
                    print(valid_block)
                    if len(valid_block)==2:
                        
                           print("망함")
                    for i in range(len(valid_block)-1):
                        
                        if i==0:
                            content_words=tag_word[valid_block[i][0]:valid_block[i][0]+valid_block[i+1][0]]
                            print(content_words)
                        else:
                            function_words=tag_word[valid_block[i][0]:valid_block[i+1][0]]
                            print(function_words)
                    
                    key=raw_word[i1:i2]
                    SM2=SequenceMatcher(None, tag_word,merge_morph[j1:j2])
                    mat_blocks=SM2.get_matching_blocks()
                    result_data=make_resdata(mat_blocks,tag_word)
                    result_txt=tag_word[mat_blocks[0][0]:mat_blocks[-2][0]+mat_blocks[-2][2]]
                    result_list=result_txt.split('+')
                    tail=tag_word[mat_blocks[-2][0]:]
                    tail_alpha=search_alpha(tail)
                    if tail_alpha:
                        result_list[-1]=result_list[-1]+str(tail_alpha.group(0))
                    result_data=[data.split('/') for data in result_list]
                    count_dict(result_dic,key,result_data)
                    
                    if result_dic.get(key):
                        if not exist(result_dic[key],result_data):
                            result_dic[key].append([1]+[data for data in result_data])    
                    else:
                        result_dic[key]=[[1]+[data for data in result_data]]

                if tag=="insert":
##                    print(raw_word)
##                    print(merge_morph)
##                    print ("%7s a[%d:%d] (%s) b[%d:%d] (%s)"%(tag, i1, i2, raw_word[i1:i2], j1, j2, merge_morph[j1:j2]))
##                    print("\n\n")

                    key=raw_word[i1-1:i2]
                    SM2=SequenceMatcher(None, tag_word,merge_morph[j1-1:j2])
                    mat_blocks=SM2.get_matching_blocks()
                    if len(mat_blocks)==1:
                        continue
                    result_data=make_resdata(mat_blocks,tag_word)
                    result_txt=tag_word[mat_blocks[0][0]:mat_blocks[-2][0]+mat_blocks[-2][2]]
                    result_list=result_txt.split('+')
                    tail=tag_word[mat_blocks[-2][0]:]
                    tail_alpha=search_alpha(tail)
                    if tail_alpha:
                        result_list[-1]=result_list[-1]+str(tail_alpha.group(0))
                    result_data=[data.split('/') for data in result_list]


                    count_dict(result_dic,key,result_data)
                    
                    if result_dic.get(key):
                        if not exist(result_dic[key],result_data):
                            result_dic[key].append([1]+[data for data in result_data])    
                    else:
                        result_dic[key]=[[1]+[data for data in result_data]]


                
                    

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
        elif "sjt" in fn:
            files_tagged.append(fn)


    #테스트용 나중에 삭제바람        
    files_raw=[files_raw[0]]
    files_tagged=[files_tagged[0]]
    
    raw_array=[]
    tagged_array=[]

    for i in range(len(files_raw)):
        temp_raw_array,temp_tagged_array=make_arrays(fnr=files_raw[i],fnt=files_tagged[i])
        raw_array.extend(temp_raw_array)
        tagged_array.extend(temp_tagged_array)
    
    print("리스트만들기 완료")
    make_dict(result_dic,raw_array,tagged_array)
    
    print("사전만들기완료")
    make_df(result_dic)
