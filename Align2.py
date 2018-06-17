import re
import nltk

def make_del_block(fraction,raw_word,tagged):
    index_raw, leng_raw, index_tag, leng_tag = 0, 0, 0, 0
    blocks = []

    while index_raw + leng_raw < len(raw_word):

        if raw_word[index_raw+leng_raw] == tagged[index_tag+leng_tag]: #and same_pos(fraction, index_tag+leng_tag):
            leng_tag += 1
            leng_raw += 1

        else:
            if index_raw+leng_raw != 0:
                blocks.append([index_raw, index_raw+leng_raw, index_tag, index_tag+leng_tag])
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
    blocks.append([len(raw_word), 0, len(tagged), 0])

    return blocks


def split_cur(fraction, raw_index, morph_index, match_length):
    temp_fraction = fraction

    blocks = []
    rindex = raw_index
    mindex = morph_index
    morph_length = 0
    if match_length == 1:
        return None

    temp_fraction[-1][1] += '+'

    for index in range(morph_index, morph_index+match_length):
        if temp_fraction[index][1][-1] == '+':
            mlength = index-mindex+1
            blocks.append([rindex, rindex+mlength, mindex, mindex+mlength])
            mindex = index + 1
            rindex = rindex + mlength
            morph_length = 0
        else:
            morph_length += 1
    if mindex+morph_length == morph_index+match_length and morph_length != 0:
        blocks.append([rindex, rindex+morph_length, mindex, mindex+morph_length])
    temp_fraction[-1][1] = temp_fraction[-1][1][:-1]
    if len(blocks) > 1:
        return blocks
    return None


def split_syn(s1, s2):
    result = []
    raw = ''.join(s1)
    tag_morph = re.split("(?<=/[A-Z]{2})\+|(?<=/[A-Z]{3})\+", ''.join(s2))
    tagged = ''.join([morph_pos[:morph_pos.rfind('/')] for morph_pos in tag_morph])

    fraction = []
    for morph_tag in tag_morph:
        morph, tag = nltk.str2tuple(morph_tag)
        for mor_i in range(len(morph)):
            if mor_i == 0:
                fraction.append([morph[mor_i], "B-"+tag])
            else:
                fraction.append([morph[mor_i], "I-"+tag])
        fraction[-1][1] = fraction[-1][1] + "+"  ##태그 뒤에 +붙이기
    fraction[-1][1] = fraction[-1][1][:-1]
    if raw == tagged:
        temp = []
        for i in range(len(fraction)):
            temp.append(raw[i])
            temp.extend(fraction[i])
            result.append(temp)
            temp = []
        return result
    blocks = make_del_block(fraction, raw, tagged)

    for block in blocks[:-1]:
        raw_b, raw_e, tag_b, tag_e = block[0], block[1], block[2], block[3]
        temp = []
        if raw_e - raw_b == tag_e - tag_b:
            for i in range(raw_e-raw_b):
                temp.append(raw[raw_b+i])
                temp.extend(fraction[tag_b+i])
                result.append(temp)
                temp = []
        elif raw_e-raw_b == 1:
            for i in range(tag_e-tag_b):
                temp.extend(fraction[tag_b+i])
            tag_syn = ''.join([temp[i] for i in range(0,len(temp),2)])
            tag = ''.join([temp[i] for i in range(1, len(temp), 2)])
            result.append([raw[raw_b], tag_syn, tag])

    return result


if __name__ == "__main__":

    s1 = list("궁금해하였다.")
    s2 = list("궁금/XR+하/XSA+어/EC+하/VV+었/EP+다/EF+./SF")
    s1 = list("학교다")
    s2 = list("학교/NNG+이/VCP+다/EF")
    s1 = list("무서워서가")
    s2 = list("무섭/VA+어서/EC+가/JKC")
    s1 = list("넓혀")
    s2 = list("넓히/VV+어/EC")
    s1 = list("엠마누엘")
    s2 = list("엠마누엘/NNP")
    s1 = list("나섰다.")
    s2 = list("나서/VV+었/EP+다/EF+./SF")
    s1 = list("웅가로가")
    s2 = list("웅가로/NNP+가/JKS")
    s1 = list("성과임에")
    s2 = list("성과/NNG+이/VCP+ㅁ/ETN+에/JKB")
    print(split_syn(s1, s2))




