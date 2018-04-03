import pprint
import re

__empty_space = []


def load_dict_file(f1="dictionary1.bin", f2="count_bigramtag.txt"):
    import pickle
    morph_dic = {}
    rule = []
    with open(f1, 'rb') as fp:
        morph_dic = pickle.load(fp, encoding='utf-8')

    with open(f2, 'r', encoding='utf8') as fp:
        for line in fp:
            cur = line.split()[0]
            nxt = line.split()[1]
            rule.append([cur, nxt])
    return morph_dic, rule


def rule_exist(f, b, rule):
    ##    print(f)
    ##    print(b)
    rule_b = re.compile("^[a-zA-Z]+")
    rule_f = re.compile("[a-zA-Z]+$")
    res_b = rule_b.search(str(b[2]))
    res_f = rule_f.search(str(f[2]))
    if res_f != None and res_b != None:
        if [res_f.group(), res_b.group()] in rule:
            return True
    return False


def merge_possible(table, lstart, mid, rend, dic, rule, phrase):
    front = table[lstart][mid]
    back = table[mid][rend]
    result = []
    ##    print(front)
    ##    print(back)
    if front != __empty_space and back != __empty_space:
        for ele_f in front:
            for ele_b in back:

                ##                print(ele_f)
                ##                print(ele_b)
                if rule_exist(ele_f, ele_b, rule):
                    temp = [[100, str(ele_f[1]) + "+" + str(ele_b[1]), str(ele_f[2]) + "+" + str(ele_b[2])]]
                    ##                    print(temp)
                    result.append(temp)

    if dic.get(phrase[lstart:mid]) != None:
        result.append(dic.get(phrase[lstart:mid]))
    return result


def del_dup(result):
    temp = []
    for i in result:
        if not i in temp:
            temp.append(i)
    return temp


def morph_generator(phrase, dic, rule):
    __empty_space = []
    n = len(phrase)
    if dic.get(phrase) != None:
        first_result = dic[phrase]
    table = [[[] for x in range(n + 1)] for y in range(n)]
    ##    pprint(table)
    for i in range(len(phrase)):
        if dic.get(phrase[i]) != None:
            table[i][i + 1].extend(dic.get(phrase[i]))
        else:
            table[i][i + 1] = __empty_space

    ##    pprint(table)

    for i in range(2, len(phrase) + 1):
        for j in range(0, len(phrase) - i + 1):
            for k in range(1, i):
                lstart = j
                mid = j + k
                rend = j + i
                print(phrase[lstart:mid] + "  " + phrase[mid:rend])
                for ele in merge_possible(table, lstart, mid, rend, dic, rule, phrase):
                    ##                    print(ele)
                    table[lstart][rend].extend(ele)
    ##
    return del_dup(table[0][n])


if __name__ == "__main__":
    morph_dic, rule = load_dict_file()
    result = morph_generator("안녕하세요", morph_dic, rule)
    print(len(result))
