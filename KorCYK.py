import pprint
import re
from typing import List

__empty_space = []


def load_dict_file(f1="dictionary.bin", f2="count_bigram.bin"):
    import pickle
    with open(f1, 'rb') as fp:
        morph_dic = pickle.load(fp, encoding='utf-8')

    with open(f2, 'rb') as fp:
        rule = pickle.load(fp, encoding='utf-8')
    return morph_dic, rule


def rule_exist(f, b, rule):
    rule_b = re.compile("^[>]?[a-zA-Z]+")
    rule_f = re.compile("[a-zA-Z]+[<]?$")
    res_b = rule_b.search(str(b[2]))
    res_f = rule_f.search(str(f[2]))
    if res_f is not None and res_b is not None:
        front = res_f.group()
        back = res_b.group()
        if f[-1] == '<' or b[0] == '>':
            if rule.get(front+" "+back) is not None:
                return True
            return False
        if rule.get(front+" "+back) is not None:
            return True
    return False


def merge_possible(table, lstart, mid, rend, dic, rule, phrase):
    front = table[lstart][mid]
    back = table[mid][rend]
    result = []

    if front != __empty_space and back != __empty_space:
        for ele_f in front:
            for ele_b in back:
                if rule_exist(ele_f, ele_b, rule):
                    temp = [[100, str(ele_f[1]) + "+" + str(ele_b[1]), str(ele_f[2]) + "+" + str(ele_b[2])]]
                    result.append(temp)

    if dic.get(phrase[lstart:rend]) != None:
        result.append(dic.get(phrase[lstart:rend]))
    return result


def del_dup(result):
    temp = []
    tag_temp = []
    for i in result:
        if i[2] not in tag_temp:
            temp.append(i)
            tag_temp.append(i[2])
    return temp


def morph_generator(phrase, dic, rule):
    __empty_space = []
    n = len(phrase)
    if dic.get(phrase) != None:
        first_result = dic[phrase]
    table = [[[] for x in range(n + 1)] for y in range(n)]

    for i in range(len(phrase)):
        if dic.get(phrase[i]) != None:
            table[i][i + 1].extend(dic.get(phrase[i]))
        else:
            table[i][i + 1] = __empty_space


    for i in range(2, len(phrase) + 1):
        for j in range(0, len(phrase) - i + 1):
            for k in range(1, i):
                lstart = j
                mid = j + k
                rend = j + i
                print(phrase[lstart:mid] + "  " + phrase[mid:rend])
                for ele in merge_possible(table, lstart, mid, rend, dic, rule, phrase):

                    table[lstart][rend].extend(ele)
                table[lstart][rend] = del_dup(table[lstart][rend])
    return del_dup(table[0][n])


if __name__ == "__main__":
    morph_dic, rule = load_dict_file()
    result = morph_generator("안녕하세요.", morph_dic, rule)
    print(len(result))
    pprint.pprint(result[:100])

