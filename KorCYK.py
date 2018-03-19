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
def morph_generator(phrase,dic,rule):
    
    if dic.get(phrase) != None:
        first_result = dic[phrase]
    result = []
    for i in range(len(phrase)):
        if dic.get(phrase[i]) != None:
            result.append([i,i+1,dic.get(phrase[i])])
        else:
            result.append([i,i+1,0])
    print(result)
        
    for i in range(2,len(phrase)+1):
        for j in range(0,len(phrase)-i+1):
            for k in range(1,i):
                lstart = j
                mid = j + k
                rend = j + i
                print(lstart,mid,rend)
        
        
        
    
if __name__ == "__main__":

    morph_dic,rule = load_dict_file()
    morph_generator("abcd",morph_dic,rule)
    
    
