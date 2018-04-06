import re
import os
from difflib import SequenceMatcher
from nltk.data import find
from nltk.tag.util import str2tuple
from itertools import chain, tee, islice

##__space_mark="@SP@"
__pre_mark = "<"  ##사전만들때 꺾쇠<를 넣거나 일단은 cyk를 위해 공백넣음
__post_mark = ">"  ##>


##rule1=re.compile(r'__[0-9]+')
##rule2=re.compile(r'/[A-Z+]+')
##rule3=re.compile(r'/[A-Z+]')
def remove_num(data):
    return re.compile(r'__[0-9]+').sub('', data)


def remove_alpha(data):
    return re.compile(r'/[A-Z+]').sub('', data)


def remove_alphaplus(data):
    return re.compile(r'/[A-Z+]+').sub('', data)


def remove_tag(data):
    return remove_num(data[0:data.rfind('/')])


def exist(values, data):
    for i in values:
        if compare(i[1:], data):
            i[0] += 1
            return True
    return False


def compare(list1, list2):
    if not len(list1) == len(list2):
        return False
    for i in range(len(list1)):
        if not list1[i] == list2[i]:
            return False
    return True


def search_alpha(data):
    return re.compile(r'/[A-Z+]').search(data)


def count_dict(dic, key, value):
    if dic.get(key):
        if not exist(dic[key], value):
            dic[key].append([1] + [ele for ele in value])
    else:
        dic[key] = [[1] + [ele for ele in value]]


def make_resdata(mat_blocks, tag_word):
    result_txt = tag_word[mat_blocks[0][0]:mat_blocks[-2][0] + mat_blocks[-2][2]]
    result_list = result_txt.split('+')
    tail = tag_word[mat_blocks[-2][0]:]
    tail_alpha = search_alpha(tail)
    if tail_alpha:
        result_list[-1] = result_list[-1] + str(tail_alpha.group(0))
    return [data.split('/') for data in result_list]


def make_arrays(fnr, fnt):
    raw_array = []
    tagged_array = []
    for line in open(fnr, 'r', encoding="utf8").readlines():
        if line and not line.strip():
            continue
        raw_array.append(line.split())
    for line in open(fnt, 'r', encoding="utf8").readlines():
        if line and not line.strip():
            continue
        tagged_array.append(line.split())
    return raw_array, tagged_array


def include_delete(opcodes):
    for code in opcodes:
        if code[0] == "delete": return True
    return False


def contain_equal(opcodes):
    for code in opcodes:
        if code[0] != "equal": return False
    return True


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


def mor_replace(pyo_temp, dic_temp, postag_temp, tag_morph,fraction):
    prev_raw = pyo_temp[-2]
    prev_dic = dic_temp[-2]
    prev_postag = postag_temp[-2]
    if len(prev_raw) == 0:  # insert,replace 이런경우는 없는듯.
        print("인설트 리플레이스")
    if prev_dic.count('++'):  # +가 있을때 요건 좀 애매한데 이런경우 잇을까?
        print("+가 있을때")

    if not prev_dic.count('+'):  ## 자유|롭게 자유|로+/vv웁+게
        prev_dic = prev_dic + __pre_mark  ##꺾쇠
        dic_temp[-2] = prev_dic
        dic_temp[-1] = __post_mark + dic_temp[-1]
    else:  ## 앞에 +잇을경우
        if prev_dic.rfind('+') == len(prev_dic) - 1:  ##제일 끝+ 붙은거를 <로 바꿈
            prev_dic = prev_dic[:-1] + __pre_mark
            dic_temp[-2] = prev_dic
            dic_temp[-1] = __post_mark + dic_temp[-1]


        else:  ##아니더라도 꺽쇠 붙이기
            prev_dic = prev_dic + __pre_mark
            dic_temp[-2] = prev_dic
            dic_temp[-1] = __post_mark + dic_temp[-1]

        split_list_byp = prev_dic.split('+')

        if len(split_list_byp) != 1:
            if split_list_byp[-1].find(__pre_mark) != -1:
                # 여기서 좀헷갈리네
                # 의무+교육+화+된  or 의무+교육+화된 화<된  화|된 어떻게 생각할것인가
                temp = (pyo_temp[-1], dic_temp[-1], postag_temp[-1])

                pyo_temp = pyo_temp[:-2]
                dic_temp = dic_temp[:-2]
                postag_temp = postag_temp[:-2]
                lastwd_index = 0

                for word in split_list_byp:
                    if word.rfind(__pre_mark) == len(word) - 1:
                        pyo_temp.append(word[:-1])
                    else:
                        pyo_temp.append(word)
                    dic_temp.append(word)
                    for morph_tag in tag_morph:
                        morph, postag = str2tuple(morph_tag)
                        if morph.find(word) != -1:
                            postag_temp.append(postag)
                            break
                        if word.rfind(__pre_mark) == len(word) - 1:
                            if fraction[lastwd_index][1].find('+') == -1:
                                postag_temp.append(fraction[lastwd_index][1])
                                break
                            else:
                                postag_temp.append(fraction[lastwd_index][1][:-1])
                                break
                    lastwd_index += len(word)

                pyo_temp.append(temp[0])
                dic_temp.append(temp[1])
                postag_temp.append(temp[2])

    return pyo_temp, dic_temp, postag_temp


def mor_freplace(pyo_temp, dic_temp, postag_temp, tag_morph):
    for i in postag_temp:
        i = i.replace('/', '')


def mor_insert(pyo_temp, dic_temp, postag_temp, tag_morph,fraction):
    prev_raw = pyo_temp[-2]

    prev_dic = dic_temp[-2]

    prev_postag = postag_temp[-2]

    if prev_dic.rfind('+') == len(prev_dic) - 1:  ##제일 끝+ 붙은거를 <로 바꿈

        prev_dic = prev_dic[:-1] + __pre_mark
    else:
        prev_dic = prev_dic + __pre_mark
    split_list_byp = prev_dic.split('+')  # plus 가 있으면
    if len(split_list_byp) != 1:
        if split_list_byp[-1].find(__pre_mark) != -1:

            temp = (pyo_temp[-1], dic_temp[-1], postag_temp[-1])
            pyo_temp = pyo_temp[:-2]
            dic_temp = dic_temp[:-2]
            postag_temp = postag_temp[:-2]
            lastwd_index = 0
            for word in split_list_byp:
                if word.rfind(__pre_mark) == len(word) - 1:
                    pyo_temp.append(word[:-1])  ## 표청어 사전
                    dic_temp.append(word + temp[1])
                else:
                    pyo_temp.append(word)
                    dic_temp.append(word)

                for morph_tag in tag_morph:  ## 태깅한거 넣는곳
                    morph, postag = str2tuple(morph_tag)

                    if morph.find(word) != -1:
                        postag_temp.append(postag)
                        break
                    if word.rfind(__pre_mark) == len(word) - 1:
                        if fraction[lastwd_index][1].find('+') == -1:
                            postag_temp.append(fraction[lastwd_index][1] + '+' + temp[2])
                            break
                        else:
                            postag_temp.append(fraction[lastwd_index][1][:-1] + '+' + temp[2])
                            break
                lastwd_index += len(word)


    else:  ##플러스가 없을때는 간단
        dic_temp[-2] = prev_dic + __post_mark + dic_temp[-1]

        dic_temp = dic_temp[:-1]

        if postag_temp[-2].find('/') != -1:
            postag_temp[-2] = postag_temp[-2][0:postag_temp[-2].find('/')] + '+' + postag_temp[-1]
            postag_temp = postag_temp[:-1]
            pyo_temp = pyo_temp[:-1]
    return pyo_temp, dic_temp, postag_temp


def make_del_block(fraction, raw_word, merge_morph):
    mat_blocks = []
    index_merge = 0
    for index_raw in range(len(raw_word)):  ##한글자씩 한글자씩 비교해가면서 달라지는곳만 합쳐서 넣었음.

        if raw_word[index_raw] == merge_morph[index_merge]:

            mat_blocks.append([raw_word[index_raw], fraction[index_merge]])
            index_merge += 1
        else:
            for nxt_raw in range(index_raw + 1, len(raw_word)):
                for nxt_merge in range(index_merge + 1, len(merge_morph)):
                    if raw_word[nxt_raw] == merge_morph[nxt_merge]:
                        fraction_morph = []
                        fraction_merge = []

                        for index in range(index_merge, nxt_merge):
                            fraction_merge.extend(fraction[index])

                        if index_raw != 0:
                            if mat_blocks[index_raw - 1][1][0].find('+') != -1:
                                mat_blocks[index_raw - 1][1][0] = mat_blocks[index_raw - 1][1][0][:-1] + __pre_mark
                                mer_mor = __post_mark + "".join(
                                    fraction_merge[i] for i in range(0, len(fraction_merge), 2))
                            else:
                                mat_blocks[index_raw - 1][1][0] = mat_blocks[index_raw - 1][1][0] + __pre_mark
                                mer_mor = __post_mark + "".join(
                                    fraction_merge[i] for i in range(0, len(fraction_merge), 2))
                        else:
                            mer_mor = "".join(fraction_merge[i] for i in range(0, len(fraction_merge), 2))

                        mer_tag = "".join(fraction_merge[i] for i in range(1, len(fraction_merge), 2))
                        mat_blocks.append([raw_word[index_raw:nxt_raw], [mer_mor, mer_tag]])
                        mat_blocks.append([raw_word[nxt_raw], fraction[nxt_merge]])
                        index_raw = nxt_raw
                        index_merge = nxt_merge
                        break
        if index_raw == len(raw_word) - 1:
            break  # 요기까지 프랙션 했다가 다시 붙이기
    return mat_blocks


def find_mergeblock(mat_blocks):
    merge_block = []

    start = 0
    while (start != len(mat_blocks) - 1):
        j = start + 1
        while (j != len(mat_blocks)):

            if mat_blocks[start][1][1].replace('+', "") != mat_blocks[j][1][1].replace('+', ""):
                merge_block.append([start, j])
                start = j - 1
                break
            else:
                if mat_blocks[j][1][1].find('+') != -1:
                    merge_block.append([start, j + 1])
                    start = j
                    break

            j += 1
        start = start + 1
    return merge_block


def find_mergeblocklist(merge_block, mat_blocks):
    block_list = []
    for ele in merge_block:
        if ele[1] - ele[0] > 1:
            start = ele[0]
            end = ele[1]
            block_temp = mat_blocks[start]

            for f_i in range(ele[0] + 1, ele[1]):
                block_temp[0] += mat_blocks[f_i][0]
                block_temp[1][0] += mat_blocks[f_i][1][0]
            block_list.append([start, end, block_temp])
    return block_list


def make_del_list(merge_block_list, mat_blocks):
    blocks = []

    if len(merge_block_list) != 0:
        len_word = 0
        if merge_block_list[0][0] == 0:
            blocks.append(merge_block_list[0][2])
            len_word = merge_block_list[0][1]

        while (len_word != len(mat_blocks)):

            blocks.append(mat_blocks[len_word])
            for start, end, block_temp in merge_block_list:
                if (len_word == start):
                    blocks.pop()
                    blocks.append(block_temp)
                    len_word = end - 1
                    break

            len_word += 1
    else:
        blocks.append([block for block in mat_blocks])
    return blocks


def del_dup(postag_temp):
    for i in range(len(postag_temp)):
        temp = postag_temp[i]
        rep_temp = temp.replace("+/", '+')
        postag_temp[i] = del_slash(rep_temp)
    return postag_temp


def del_slash(postag):
    if len(postag) < 5:
        return postag

    not_alpha = [0]
    temp_pos = []
    for i in range(len(postag)):
        if not postag[i].isalpha():
            not_alpha.append(i)
    not_alpha.append(len(postag))
    temp_pos.append(postag[not_alpha[0]:not_alpha[1]])

    for i in zip(not_alpha[1:], not_alpha[2:]):
        if i[0] == i[1]:
            continue
        if temp_pos[-1] == postag[i[0] + 1:i[1]]:
            continue
        else:
            temp_pos.append(postag[i[0] + 1:i[1]])

    return "+".join(temp_pos)


def make_dict(result_dic, raw_array, tagged_array):
    for raw_sent, tagged_sent in zip(raw_array, tagged_array):
        if not len(raw_sent) == len(tagged_sent):
            continue
        for raw_word, tag_word in zip(raw_sent, tagged_sent):

            tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", tag_word)  # lookbehind 사용했으나 fixed되야되서 or로 처리
            merge_morph = "".join([remove_tag(morph) for morph in tag_morph])

            SM = SequenceMatcher(None, raw_word, merge_morph)
            opcodes = SM.get_opcodes()
            fraction, pyochung_list, dic_list, postag_list = [], [], [], []
            for morph_tag in tag_morph:
                morph, tag = str2tuple(morph_tag)
                for syl in morph:
                    fraction.append([syl, tag])
                fraction[-1][0] = fraction[-1][0] + '+'
                fraction[-1][1] = fraction[-1][1] + '+'  ##음절 뒤에 +붙이기
            fraction[-1][0] = fraction[-1][0][0]
            fraction[-1][1] = fraction[-1][1][:-1]

            if contain_equal(opcodes):  ##전부 같을 때

                for morph in tag_morph:
                    pyochung, postag = str2tuple(morph)

                    pyochung_list.append(pyochung)
                    dic_list.append(pyochung)
                    postag_list.append(postag)

            elif not include_delete(opcodes):  ##Delete가 경우가 달라서 Delete만 따로
                pyo_temp, dic_temp, postag_temp = [], [], []
                for prev, curr, nxt in previous_and_next(opcodes):  # insert, replace 처리

                    i1, i2, j1, j2 = curr[1], curr[2], curr[3], curr[4]
                    pyo_temp.append(raw_word[i1:i2])
                    dic_temp.append("".join([w[0] for w in fraction[j1:j2]]))
                    postag_temp.append("/".join([w[1] for w in fraction[j1:j2]]))

                    if curr[0] == "replace":
                        if prev != None:
                            pyo_temp, dic_temp, postag_temp = mor_replace(pyo_temp, dic_temp, postag_temp, tag_morph,fraction)
                            if nxt != None:  # replace,insert 이런경우도 잇을까?
                                if nxt[0] == "insert":
                                    print("리플레이스 인설트")
                                    print(raw_word)
                                    print(merge_morph)
                                    print(opcodes)
                        else:
                            mor_freplace(pyo_temp, dic_temp, postag_temp, tag_morph)

                    elif curr[0] == "insert":
                        if prev == None:  ##걸렸음  이어 이--05/NP이/VCP/어/EC 이게뭐옄ㅋㅋㅋ
                            ##                            print(raw_word)
                            ##                            print(merge_morph)
                            ##                            print(tag_word)
                            ##                            print(opcodes)
                            continue
                        pyo_temp, dic_temp, postag_temp = mor_insert(pyo_temp, dic_temp, postag_temp, tag_morph,fraction)
                postag_temp = del_dup(postag_temp)
                pyochung_list.extend(pyo_temp)
                dic_list.extend(dic_temp)
                postag_list.extend(postag_temp)


            else:  ##대망의 딜리트...

                mat_blocks = make_del_block(fraction, raw_word, merge_morph)

                ## 붙였는데 태깅중복되는것들 다시 합치기  딜리트를 쓰면 되게 쉬울것같았는데 지우면 바로 리스트에 인덱스가 전부 바뀌어버려서 생각보다 하드코딩함...
                merge_block = find_mergeblock(mat_blocks)

                merge_block_list = find_mergeblocklist(merge_block, mat_blocks)

                del_result_list = make_del_list(merge_block_list, mat_blocks)

                for block in del_result_list:
                    pyochung_list.append(block[0])
                    dic_list.append(block[1][0])
                    postag_list.extend(block[1][1])
                ##요정도까지 하면 전부 나오긴나오는데 + > 에대한 정의를 확실히 내리고 다시한번 봐야될듯 그리고 너무 하드코딩이라 고민해봐야됨

            ##사전에 넣는거는 그리어렵지 않으니 일단 월요일날 다시 가서 살펴봐야될

            for pyo, di, pos in zip(pyochung_list, dic_list, postag_list):
                count_dict(result_dic, str(pyo), [di, pos])


def make_df(result, fn="dictionary1.bin"):
    import pickle
    with open(fn, 'wb') as f:
        pickle.dump(result, f)
def make_df_txt(result, fn="dictionary1.txt"):
    with open(fn,'w') as f:
        for k,v in result.items():
            print(k,v, file=f)


if __name__ == "__main__":
    result_dic = {}
    path = find("corpora\\sejong").path
    os.chdir(path)
    files_raw = []
    files_tagged = []

    for fn in os.listdir(path):
        if "sjr" in fn:
            files_raw.append(fn)
        elif "sjt" in fn:
            files_tagged.append(fn)

    # 테스트용 나중에 삭제바람
    files_raw = [files_raw[1]]
    files_tagged = [files_tagged[1]]

    raw_array = []
    tagged_array = []
    for i in range(len(files_raw)):
        temp_raw_array, temp_tagged_array = make_arrays(fnr=files_raw[i], fnt=files_tagged[i])
        raw_array.extend(temp_raw_array)
        tagged_array.extend(temp_tagged_array)

    print("리스트만들기 완료")
    make_dict(result_dic, raw_array, tagged_array)

    print("사전만들기완료")
    make_df_txt(result_dic)
# 딕셔너리가 본디렉토리가 아니라 세종코퍼스아래디렉토리로 가는 문제 및 exception processing필
