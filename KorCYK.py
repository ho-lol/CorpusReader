from pprint import pprint
import re
def load_dict_file(f1="dictionary1.dic",f2="count_bigramtag.txt"):
    morph_dic = {}
    rule = []
    with open(f1,'r',encoding='utf8') as fp:
        for line in fp:

            key=line.split()[0]
            value=line.split()[1:]
            morph_dic[key]=value
            
    with open(f2,'r',encoding='utf8') as fp:
        for line in fp:         
            cur =line.split()[0]
            nxt =line.split()[1]
            rule.append([cur,nxt])
    return morph_dic,rule
def rule_exist(f,b,rule):
    
    rule_b=re.compile("^[a-zA-Z]+")
    rule_f=re.compile("[a-zA-Z]+$")
    res_b=rule_b.search(b[2])
    res_f=rule_f.search(f[2])
    if [res_f.group(),res_b.group()] in rule:
        return True
    return False
def merge_possible(table,lstart,mid,rend,dic,rule,phrase):
    front=table[lstart:mid]
    back=table[mid][rend]
    result=[]
    if front!=__empty_space and back!=__empty_space:
        for ele_f in front:
            for ele_b in back:
                if dic.get(str(ele_f[1])+str(ele_b[1]))!=None:
                    result.append(dic.get(str(ele_f[1])+str(ele_b[1])))
                elif rule_exist(ele_f,ele_b,rule):
                    result.append([1,str(ele_f[1])+"+"+str(ele_b[1]),str(ele_f[2])+"+"+str(ele_b[2])])
    else:
         if dic.get(phrase[lstart:mid])!=None:
             result.append(dic.get(phrase[lstart:mid]))
    return result
                                   
                                   
                
def del_dup(result):
    temp=[]
    for i in result:
        if not i in temp:
            temp.append(i)
    return temp
def morph_generator(phrase,dic,rule):
    __empty_space=[]
    n=len(phrase)
    if dic.get(phrase) != None:
        first_result = dic[phrase]
    table = [[[] for x in range(n+1)] for y in range(n+1)]
    pprint(table)
    for i in range(len(phrase)):
        if dic.get(phrase[i]) != None:
            table[i][i+1].append(dic.get(phrase[i]))
        else:
            table[i][i+1]=__empty_space
                             
    pprint(table)
        
    for i in range(2,len(phrase)+1):
        for j in range(0,len(phrase)-i+1):
            for k in range(1,i):
                lstart = j
                mid = j + k
                rend = j + i
                for ele in merge_possible(table,lstart,mid,rend,dic,rule,phrase):
                    table[lstart][rend].append(ele)
    return del_dup(table[0][n])
        
        
        
    
if __name__ == "__main__":

    morph_dic,rule = load_dict_file()
    morph_dic['a']=[[30 ,'a',"SL"]]
    result=morph_generator("abcd",morph_dic,rule)
    print(result)
    
