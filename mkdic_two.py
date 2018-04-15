import itertools
import os
import re
from difflib import SequenceMatcher
from typing import Union

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


def count_dict(dic, key, value):
    if dic.get(key):
        if not exist(dic[key], value):
            dic[key].append([1] + [ele for ele in value])
    else:
        dic[key] = [[1] + [ele for ele in value]]


def same_pos(fraction, index):
    if fraction+1<len(fraction):
        print(fraction[index],fraction[index+1])
def make_del_block(fraction,raw_word,tagged):
    index_raw, leng_raw, index_tag, leng_tag = 0, 0, 0, 0
    blocks = []

    while index_raw + leng_raw < len(raw_word):
        if raw_word[index_raw+leng_raw] == tagged[index_tag+leng_tag]: #and same_pos(fraction, index_tag+leng_tag):
            leng_tag += 1
            leng_raw += 1

        else:
            if index_raw+leng_raw != 0:
                blocks.append([index_raw,leng_raw,index_tag,leng_tag])
                index_raw = index_raw + leng_raw
                index_tag = index_tag + leng_tag
                leng_raw = 0
                leng_tag = 0
            nxt = index_raw + 1
            nxt_t = index_tag + 1
            for nxt_raw in range(nxt, len(raw_word)):
                for nxt_merge in range(nxt_t, len(tagged)):
                    if raw_word[nxt_raw] == tagged[nxt_merge]:
                        blocks.append([index_raw, nxt_raw, index_tag, nxt_merge])
                        leng_raw = 0
                        leng_tag = 0
                        index_raw = nxt_raw
                        index_tag = nxt_merge
                        break

    if leng_raw != 0:
        blocks.append([index_raw, index_raw + leng_raw, index_tag, index_tag + leng_tag])
    blocks.append([len(raw_word),0,len(tagged),0])
    return blocks


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


def generate_block(mat_blocks):
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
        if raw_word_index+match_length == nxt_raw_index and morph_index+match_length == nxt_morph_index:
            continue
        elif raw_word_index+match_length == nxt_raw_index and morph_index+match_length != nxt_morph_index:##insert의 경우
            blocks[-1][3]=nxt_morph_index-morph_index
        else:
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


def make_dict(result_dic, raw_array, tagged_array):
    pyochung_list, dic_list, postag_list = [], [], []
    for raw_sent, tagged_sent in zip(raw_array, tagged_array):
        if not len(raw_sent) == len(tagged_sent):
            continue
        for raw_word, tag_word in zip(raw_sent, tagged_sent):
            tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", tag_word)
            fraction = []
            tagged = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])
            if raw_word == tagged:
                for morph in tag_morph:
                    pyochung, postag = nltk.str2tuple(morph)
                    pyochung_list.append(pyochung)
                    dic_list.append(pyochung)
                    postag_list.append(postag)
                continue
            for morph_tag in tag_morph:
                morph, tag = nltk.str2tuple(morph_tag)
                for syl in morph:
                    fraction.append([syl, tag])
            #     fraction[-1][0] = fraction[-1][0]
                fraction[-1][1] = fraction[-1][1]+"+"  ##태그 뒤에 +붙이기
            # fraction[-1][0] = fraction[-1][0][0]
            fraction[-1][1] = fraction[-1][1][:-1]

            SM = SequenceMatcher(None, raw_word, tagged)
            if include_delete(SM):
                blocks = make_del_block(fraction,raw_word, tagged)

            else:
                mat_blocks = SM.get_matching_blocks()
                if len(mat_blocks) == 1:#온 오/vx+ㄴ/etm 혹시 모를 다틀린 형태.
                    pyochung_list.append(raw_word)
                    dic_list.append(tagged)
                    postag_list.append('+'.join([morph_pos[morph_pos.rfind('/')+1:] for morph_pos in tag_morph]))
                    continue
                blocks=generate_block(mat_blocks)
            print(raw_word,tagged)
            result = []
            for cur, nxt in pairwise(blocks):
                print(cur)
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
                if len(result) != 0 and mark_attach(result[-1][2][-1], fraction[post_loc][1]):
                    result[-1][2][-1] = result[-1][2][-1] + __pre_mark
                    post_tag_list[0] = __post_mark + post_tag_list[0]
                result.append([raw, mor, post_tag_list])
            print(result)


def make_df_txt(result, fn="dictionary1.txt"):
    with open(fn, 'w', encoding="utf8") as f:
        for k, v in result.items():
            print(k, v, file=f)


if __name__ == "__main__":
    result_dic = {}
    curr_path: Union[bytes, str] = os.path.dirname(os.path.abspath(__file__))
    path: object = nltk.data.find('corpora\\sejong').path
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

    # 테스트용 나중에 삭제바람
    files_raw = [files_raw[0]]
    files_tagged = [files_tagged[0]]

    raw_array = []
    tagged_array = []
    for i in range(len(files_raw)):
        temp_raw_array, temp_tagged_array = make_arrays(fnr=files_raw[i], fnt=files_tagged[i])
        raw_array.extend(temp_raw_array)
        tagged_array.extend(temp_tagged_array)

    print("리스트만들기 완료")

    make_dict(result_dic, raw_array, tagged_array)

    print("사전만들기완료")

    os.chdir(curr_path)
    make_df_txt(result_dic)
