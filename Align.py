import re
import nltk
from difflib import SequenceMatcher
import itertools


def pairwise(iterable: object) -> object:
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    assert isinstance(b, object)
    return zip(a, b)


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
            blocks[-1][3] = nxt_morph_index
        else:
            if split_data is not None:
                blocks.pop()
                blocks.extend(split_data)
            blocks.append([raw_word_index + match_length, nxt_raw_index, morph_index + match_length, nxt_morph_index])

    blocks.append([mat_blocks[-1][0], 0, mat_blocks[-1][1], 0])
    return blocks



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


def include_delete(SM):
    for opcode in SM.get_opcodes():
        if opcode[0] == "delete": return True
    return False


def align(sent):
    tagged = re.split(r'\s+', sent)
    raw_word = tagged[0]
    tagged[1] = re.compile(r'__[0-9]+').sub('', tagged[1])
    tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", tagged[1])
    tagged = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])
    fraction = list()
    for morph_tag in tag_morph:
        morph, tag = nltk.str2tuple(morph_tag)

        for i, syl in enumerate(morph):
            if i == 0:
                fraction.append([syl, "B-"+tag])
            else:
                fraction.append([syl, "I-" + tag])
        fraction[-1][1] = fraction[-1][1] + "+"  ##태그 뒤에 +붙이기
    fraction[-1][1] = fraction[-1][1][:-1]
    print(raw_word,tagged)
    if raw_word == tagged:
        return fraction
    SM = SequenceMatcher(None, raw_word, tagged)
    blocks = list()
    if include_delete(SM):
        blocks = make_del_block(fraction, raw_word, tagged)
    else:
        mat_blocks = SM.get_matching_blocks()
        blocks = generate_block(fraction, mat_blocks)
        if len(mat_blocks) == 1:# 온 오/vx+ㄴ/etm 혹시 모를 다틀린 형태.
            blocks = make_del_block(fraction, raw_word, tagged)

    print(blocks)
    for cur, nxt in pairwise(blocks):
        raw = raw_word[cur[0]:cur[1]]
        mor = tagged[cur[2]:cur[3]]
        print(raw,mor)
if __name__ == "__main__":
    print(align("엠마누엘 	 엠마누엘/NNP"))
    align("아름다웠다. 	 아름답/VA+었/EP+다/EF+./SF")