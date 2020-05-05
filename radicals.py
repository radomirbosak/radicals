#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
import string
from collections import namedtuple


Kanji = namedtuple('Kanji', 'character radicals')
Radical = namedtuple('Radical', 'id characters strokes readings meanings comment')


alternatives = {
    '人': ['⺅', '𠆢'],
    '丨': ['｜'],
    '丿': ['ノ'],
    '乙': ['⺄'],
    '小': ['⺍'],
    '巛': ['巜'],
    '心': ['㣺'],
    '水': ['氺'],
    '爪': ['爫', '爫'],
    '牛': ['⺧'],
    '玉': ['⺩'],
    '示': ['⺬'],
    '羊': ['⺶'],
    '聿': ['⺻'],
    '艸': ['䒑', '艹', '艹'],
    '西': ['襾'],
    '食': ['𩙿'],
}

def get_kanjis():
    kanjis = []
    # from https://raw.githubusercontent.com/jmettraux/kensaku/master/data/kradfile-u
    with open('kradfile-u', 'r') as fp:
        for i, line in enumerate(fp):
            if line[0] == '#':
                continue
            split = line.split()
            k = Kanji(split[0], split[2:])
            kanjis.append(k)
    return kanjis
    

def get_radicals(patch_alternatives=True):
    radicals = []
    # from https://raw.githubusercontent.com/mifunetoshiro/kanjium/master/data/source_files/radicals.txt
    with open('radicals.txt', 'r') as fp:
        for line in fp:
            l = line.split('\t')
            id_ = int(l[2])

            characters = [l[0], l[1]] if l[1] else [l[0]]
            if patch_alternatives and l[0] in alternatives:
                characters.extend(alternatives[l[0]])

            strokes = int(l[3])
            readings = l[4].split('・')
            meanings = l[5].split(', ')
            comment = l[6].rstrip('\n')
            r = Radical(id_, characters, strokes, readings, meanings, comment)
            radicals.append(r)
    return radicals


radicals = get_radicals()
kanjis = get_kanjis()

mean2radical = dict()
for radical in radicals:
    for meaning in radical.meanings:
        mean2radical[meaning] = radical.characters


radchar2rad = dict()
for radical in radicals:
    for character in radical.characters:
        radchar2rad[character] = radical
        for alt in alternatives.get(character, []):
            radchar2rad[alt] = radical            
        # if character in alternatives:

        #     radchar2rad[alternatives[character]] = radical

# print(radchar2rad['亻'])


def _get_uncovered_radicals():
    """
    Return set of radicals that are used in kanji decomposition kradfile-u but
    do not have entry in radicals.txt
    """
    from itertools import chain
    radicals_from_kanjis = set(chain(*(kanji.radicals for kanji in kanjis)))
    return radicals_from_kanjis.difference(radchar2rad.keys())


def find_kanji_from_radical_meanings(meanings):
    results = []

    # convert english words to radical characters
    searched_rads = []
    for meaning in meanings:
        if meaning in mean2radical:
            searched_rads.append(mean2radical[meaning])
        else:
            print(f'Error: Radical with meaning {meaning} not found')
            sys.exit(1)

    # if len(searched_rads) == 0:
    #     print('Error: No radicals found')
    #     sys.exit(1)

    #searched_rads = [mean2radical[meaning] for meaning in meanings]
    for kanji in kanjis:
        if all(any(variant in kanji.radicals for variant in sr) for sr in searched_rads):
            results.append(kanji)
    return results


def list_available_radicals():
    for r in radicals:
        meaningstring = ', '.join(r.meanings)
        print(f'{r.characters[0]}  {meaningstring}')


def list_kanji_radicals(kanji_char):
    for kanji in kanjis:
        if kanji_char == kanji.character:
            for rchar in kanji.radicals:
                # print('亻', rchar, '亻' == rchar, ord('亻'), ord(rchar))
                radical = radchar2rad[rchar]
                meaningstring = ', '.join(radical.meanings)
                print(f'{rchar}  {meaningstring}')
            break
    else:
        print('Kanji not found')


def search_kanji(meanings):
    possible = find_kanji_from_radical_meanings(meanings)
    for p in possible:
        meanarr = []
        for rchar in p.radicals:
            radical = radchar2rad.get(rchar)
            if radical:
                meanarr.extend(radical.meanings)

        meaningstring = ', '.join(meanarr)
        print(f'{p.character}  {meaningstring}')

        # print(p.character)


def list_possible_meanings(fish=True):
    for radical in radicals:
        for meaning in radical.meanings:
            charstring = '/'.join(radical.characters)
            if fish:
                print(f'{meaning}\t{charstring}')
            else:
                print(f'{meaning}')


def main():
    if '--fish-completion' in sys.argv:
        list_possible_meanings(fish=True)
        return

    if len(sys.argv) <= 1:
        list_available_radicals()
        return

    terms = sys.argv[1:]

    if len(terms) == 1 and len(terms[0]) == 1 and terms[0] not in string.ascii_letters:
        list_kanji_radicals(terms[0])
        return

    search_kanji(terms)


if __name__ == '__main__':
    main()
