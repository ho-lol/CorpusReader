import itertools
import os
import re
from difflib import SequenceMatcher
from typing import Union
import pickle

import nltk

from splitsejong import remove_num


__pre_mark = "<"  ##사전만들때 꺾쇠<를 넣거나 일단은 cyk를 위해 공백넣음
__post_mark = ">"  ##>


def pairwise(iterable: object) -> object:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    assert isinstance(b, object)
    return zip(a, b)


def remove_plus(string):
    return re.compile('\+$').sub('', string)


def exist(values, data):
    for value in values:
        if compare(value[1:], data):
            value[0] += 1
            return True
    return False


def compare(list1, list2):
    if not len(list1) == len(list2):
        return False
    for i in range(len(list1)):
        if not list1[i] == list2[i]:
            return False
    return True


def count_dict(dic, key, value):
    if dic.get(key):
        if not exist(dic[key], value):
            dic[key].append([1] + [ele for ele in value])
    else:
        dic[key] = [[1] + [ele for ele in value]]


def make_del_block(fraction,raw_word,tagged):
    index_raw, leng_raw, index_tag, leng_tag = 0, 0, 0, 0
    blocks = []

    while index_raw + leng_raw < len(raw_word):
        if raw_word[index_raw+leng_raw] == tagged[index_tag+leng_tag]: #and same_pos(fraction, index_tag+leng_tag):
            leng_tag += 1
            leng_raw += 1

        else:
            if index_raw+leng_raw != 0:
                blocks.append([index_raw,index_raw+leng_raw,index_tag,index_tag+leng_tag])
                split_data = split_cur(fraction, blocks[-1][0], blocks[-1][2], blocks[-1][1]-blocks[-1][0])
                if split_data is not None:
                    blocks.pop()
                    blocks.extend(split_data)
                index_raw = index_raw + leng_raw
                index_tag = index_tag + leng_tag
                leng_raw = 0
                leng_tag = 0
            nxt = index_raw + 1
            nxt_t = index_tag + 1
            nxt_raw = nxt
            while nxt_raw < len(raw_word):
                for nxt_merge in range(nxt_t, len(tagged)):
                    if raw_word[nxt_raw] == tagged[nxt_merge]:
                        blocks.append([index_raw, nxt_raw, index_tag, nxt_merge])
                        leng_raw = 0
                        leng_tag = 0
                        index_raw = nxt_raw
                        index_tag = nxt_merge
                        nxt_raw = len(raw_word)+3
                        break
                nxt_raw += 1
            if nxt_raw == len(raw_word):
                blocks.append([index_raw, len(raw_word), index_tag, len(tagged)])
                split_data = split_cur(fraction, blocks[-1][0], blocks[-1][2], blocks[-1][1] - blocks[-1][0])
                if split_data is not None:
                    blocks.pop()
                    blocks.extend(split_data)
                blocks.append([len(raw_word), 0, len(tagged), 0])
                return blocks

    if leng_raw != 0:
        blocks.append([index_raw, index_raw + leng_raw, index_tag, index_tag + leng_tag])
        split_data = split_cur(fraction, blocks[-1][0], blocks[-1][2], blocks[-1][1] - blocks[-1][0])
        if split_data is not None:
            blocks.pop()
            blocks.extend(split_data)
    blocks.append([len(raw_word),0,len(tagged),0])
    # split_blocks = []
    # for block in blocks:
    #     if block[0] == block[2] and block[1] == block[3]:

    #         split_blocks.append(block)
    #     split_blocks.append(block)
    return  blocks


def make_arrays(fnr, fnt):
    _raw_array = []
    _tagged_array = []
    for line in open(fnr, 'r', encoding="utf8").readlines():
        if line and not line.strip():
            continue
        _raw_array.append(line.split())
    for line in open(fnt, 'r', encoding="utf8").readlines():
        if line and not line.strip():
            continue
        _tagged_array.append(line.split())
    return _raw_array, _tagged_array


def split_cur(fraction, raw_index, morph_index, match_length):
    temp_fraction = fraction

    blocks = []
    rindex = raw_index
    mindex = morph_index
    mlength = match_length
    postag = fraction[mindex][1]
    morph_length = 0
    if match_length == 1:
        return None
    temp_fraction[-1][1] += '+'
    for index in range(morph_index,morph_index+match_length):
        if temp_fraction[index][1][-1] == '+':
            mlength = index-mindex+1
            blocks.append([rindex, rindex+mlength, mindex, mindex+mlength])
            postag = temp_fraction[index][1]
            mindex = index + 1
            rindex = rindex + mlength
            morph_length = 0
        else:
            morph_length += 1
    if mindex+morph_length == morph_index+match_length and morph_length != 0:
        blocks.append([rindex, rindex+morph_length, mindex, mindex+morph_length])
    temp_fraction[-1][1] =  temp_fraction[-1][1][:-1]
    if len(blocks) > 1:
        return blocks
    return None


def generate_block(fraction, mat_blocks):
    blocks = []
    if mat_blocks[0][0] != 0:#앞이 분리되었을때
        blocks.append([0, mat_blocks[0][0], 0, mat_blocks[0][1]])
    for cur, nxt in pairwise(mat_blocks):
        raw_word_index = cur[0]
        morph_index = cur[1]
        match_length = cur[2]
        nxt_raw_index = nxt[0]
        nxt_morph_index = nxt[1]

        blocks.append([raw_word_index, raw_word_index + match_length, morph_index, morph_index + match_length])
        split_data = split_cur(fraction, raw_word_index, morph_index, match_length)

        if raw_word_index+match_length == nxt_raw_index and morph_index+match_length == nxt_morph_index:
            if split_data is None:
                continue
            else:
                blocks.pop()
                blocks.extend(split_data)
        elif raw_word_index+match_length == nxt_raw_index and morph_index+match_length != nxt_morph_index:
            ##insert의 경우
            if split_data is not None:
                blocks.pop()
                blocks.extend(split_data)
            # if fraction[nxt_morph_index-1] == ['이','VCP+'] and nxt_morph_index-(morph_index+match_length) == 1:#이빼는 작업
            #     continue
            blocks[-1][3] = nxt_morph_index
        else:
            if split_data is not None:
                blocks.pop()
                blocks.extend(split_data)
            blocks.append([raw_word_index + match_length, nxt_raw_index, morph_index + match_length, nxt_morph_index])

    blocks.append([mat_blocks[-1][0], 0, mat_blocks[-1][1], 0])
    return blocks


def include_delete(SM):
    for opcode in SM.get_opcodes():
        if opcode[0] == "delete": return True
    return False


def del_dup(postag):
    postag_list = []
    for tag in postag.split('/'):
        if len(postag_list) == 0:
            postag_list.append(tag)
            continue
        if '+' in tag:
            if postag_list[-1] != tag[:tag.rfind('+')]:
                postag_list.append(tag)
            else:
                postag_list.pop()
                postag_list.append(tag)
                continue
        if postag_list[-1] != tag:
            postag_list.append(tag)
    return postag_list


def mark_attach(prev, cur):
    if '+' in prev:
        return False
    if '+' in cur:
        if prev == cur[:cur.rfind('+')]:
            return True
    if prev == cur:
        return True


def make_bigram(bigram_dic, collect_bigram):
    for cur_t, nxt_t in pairwise(collect_bigram.split('+')):
        if cur_t is not None and nxt_t is not None:
            # if cur_t != "SH" and nxt_t != "SH":
            #     if cur_t != "SL" and nxt_t != "SL":
            #         if cur_t != "SN" and nxt_t != "SN":
            count_bigram(bigram_dic, cur_t+" "+nxt_t )


def count_bigram(dic, key):
    """

    :rtype: object
    """
    if dic.get(key):
        dic[key] += 1
    else:
        dic[key] = 1


def print_errer(errstr, errmorph, rstr, morph, raw_word, tag_word):
    if errstr == rstr:
        if errmorph == morph:
            print(errstr, raw_word, tag_word)

def make_dict(raw_array, tagged_array, result_dic, bigram_dic):
    for raw_sent, tagged_sent in zip(raw_array, tagged_array):

        flag = 0
        collect_bigram = "START"
        if not len(raw_sent) == len(tagged_sent):
            continue

        for raw_word, tag_word in zip(raw_sent, tagged_sent):
            if "NA" in tag_word:
                flag = 1
                continue
            if collect_bigram != "START":
                collect_bigram += "+@@SP@@"
            tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", tag_word)

            fraction = []
            tagged = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])

            if raw_word == tagged:
                for morph in tag_morph:
                    pyocheung, postag = nltk.str2tuple(morph)
                    collect_bigram = collect_bigram + "+" + postag
                    if "SH" in postag:
                        continue
                    if "SL" in postag:
                        continue
                    if "SN" in postag:
                        continue
                    count_dict(result_dic, str(pyocheung), [pyocheung, postag])



                continue
            for morph_tag in tag_morph:
                morph, tag = nltk.str2tuple(morph_tag)
                for syl in morph:
                    fraction.append([syl, tag])
                fraction[-1][1] = fraction[-1][1]+"+"  ##태그 뒤에 +붙이기
            fraction[-1][1] = fraction[-1][1][:-1]


            SM = SequenceMatcher(None, raw_word, tagged)
            if include_delete(SM):
                blocks = make_del_block(fraction,raw_word, tagged)
            else:
                mat_blocks = SM.get_matching_blocks()
                if len(mat_blocks) == 1:#온 오/vx+ㄴ/etm 혹시 모를 다틀린 형태.
                    postag = '+'.join([morph_pos[morph_pos.rfind('/') + 1:] for morph_pos in tag_morph])
                    collect_bigram = collect_bigram + "+" + postag

                    print_errer('.', '어', raw_word, tagged, raw_word, tag_word)
                    if "SH" in postag:
                        continue
                    if "SL" in postag:
                        continue
                    if "SN" in postag:
                        continue
                    count_dict(result_dic, str(raw_word), [tagged, postag])
                    continue
                blocks = generate_block(fraction, mat_blocks)
            raw_temp = ''
            tagged_temp = ''
            for i in blocks:
                raw_temp += raw_word[i[0]:i[1]]
                tagged_temp += tagged[i[2]:i[3]]
            if raw_word != raw_temp:
                print("로우이상")
                flag = 1

            if tagged != tagged_temp:#이건 이이건등등 VCP

                flag = 1

            result = []

            for cur, nxt in pairwise(blocks):
                raw = raw_word[cur[0]:cur[1]]
                mor = tagged[cur[2]:cur[3]]
                postag = "/".join(fraction[tag_num][1] for tag_num in range(cur[2], cur[3]))
                post_loc = cur[2]
                if cur[1] != nxt[0] and cur[3] != nxt[2]:
                    raw = raw_word[cur[1]:nxt[0]]
                    mor = tagged[cur[3]:nxt[2]]
                    postag = "/".join(fraction[tag_num][1] for tag_num in range(cur[3], nxt[2]))
                    post_loc = cur[3]
                post_tag_list = del_dup(postag)
                if len(result) != 0 and mark_attach(result[-1][2][-1], fraction[post_loc][1]) :
                    result[-1][2][-1] = result[-1][2][-1] + __pre_mark
                    post_tag_list[0] = __post_mark + post_tag_list[0]
                result.append([raw, mor, post_tag_list])
            for data in result:
                tags = data[2]
                tag_list = [remove_plus(tag) for tag in tags]
                if "SH" in tag_list:
                    continue
                if "SL" in tag_list:
                    continue
                if "SN" in tag_list:
                    continue
                postag_result = "+".join(tag_list)
                collect_bigram = collect_bigram + "+" + postag_result
                count_dict(result_dic, str(data[0]), [data[1], postag_result])
            # for cur, nxt in pairwise(collect_bigram.split('+')):
                # if cur + nxt == "SPSL<":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == ">SLNNG":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == "SOSN<":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == "SN<>SN":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == ">SNSN":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == "SF<>SF":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == ">NNBJKB":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == "XSNJC<":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == ">SLNNP<":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
                # if cur + nxt == "JXXR<":
                #     print(cur + nxt)
                #     print(raw_word, tag_word)
        if flag == 0:
            make_bigram(bigram_dic, collect_bigram)
    # print(result_dic.get('.'))

    return result_dic, bigram_dic


def make_df(result, fn="dictionary1.bin"):
    with open(fn, 'wb') as f:
        pickle.dump(result, f)


def make_df_txt(result, fn="dictionary1.txt"):
    with open(fn, 'w', encoding="utf8") as f:
        for k in sorted(result, key=result.get):
            print(k, result[k], file=f)


def removekey(d, key):
    r = dict(d)
    del r[key]
    return  r


def del_bigram(dic):
    for k in dic.keys():
        if dic[k] == 1:
            dic = removekey(dic, k)
    return dic


# def removevalue(dic,key,value,i):
#     temp = list(dic[key])
#     if len(dic[key]) == 1:
#         if dic[key][0][0] == 1:
#             dic = removekey(dic,key)
#     else:
#         for i, data in enumerate(temp):
#             if data[0] == 1:
#                 del temp[i]
#         dic[key] = temp
#     return dic


# def del_dict(dic):
#     for k in dic.keys():
#         for i, value in enumerate(dic[k]):
#             dic = removevalue(dic,k,value,i)
#     return dic

if __name__ == "__main__":
    curr_path = os.path.dirname(os.path.abspath(__file__))
    path = nltk.data.find('corpora\\sejong').path
    assert isinstance(path, object)
    os.chdir(path)
    files_raw = []
    files_tagged = []

    for fn in os.listdir(path):
        assert isinstance(fn, object)
        if "sjr" in fn:
            files_raw.append(fn)
        elif "sjt" in fn:
            files_tagged.append(fn)

    #테스트용 나중에 삭제바람
    # files_raw = [files_raw[5]]
    # files_tagged = [files_tagged[5]]


    dic = {}
    big = {}
    raw_array = []
    tagged_array = []
    for i in range(len(files_raw)):
        temp_raw_array, temp_tagged_array = make_arrays(fnr=files_raw[i], fnt=files_tagged[i])
        raw_array = temp_raw_array
        tagged_array = temp_tagged_array
        print(str(i)+"리스트만들기 완료")
        make_dict(raw_array, tagged_array, dic, big)
        print(str(i)+"사전만들기완료")
    os.chdir(curr_path)
    make_df(dic, "dictionary.bin")
    make_df(big, "count_bigram.bin")

    make_df_txt(big,"bigram1.txt")
    make_df_txt(dic,"dictionary1.txt")
    # # print("사전만들기완료")
    #
    # os.chdir(curr_path)
    # make_df_txt(dic)
