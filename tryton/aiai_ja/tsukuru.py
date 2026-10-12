# SPDX-License-Identifier: GPL-3.0-or-later
"""Make the PO files from yaku.csv, and check them.

    python tsukuru.py SAO_FOLDER    (with the Python of a Tryton 8.0 install)

yaku.csv holds each English text once with its Japanese (module empty), and
the few that read differently in one module (module set, e.g. stock, sao). The texts of each
module, and where they are used (msgctxt), come from the German PO file that
the module ships, since every official PO file lists all of a module's texts.
Writes aiai_ja/locale/<module>.po and aiai_ja/locale/sao/ja.json, and lists
the texts with no Japanese and those whose placeholders do not match.
"""
import csv
import glob
import json
import os
import re
import sys

import polib
import trytond

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALE = os.path.join(HERE, 'aiai_ja', 'locale')
MARKS = re.compile(r'%\([^)]+\)[a-z]|%\d|%[sdif]|\$\{[^}]*\}|\{[A-Za-z0-9_.]*\}|<[^>]+>')
HEADER = {
    'Content-Type': 'text/plain; charset=utf-8',
    'Language': 'ja',
    'Plural-Forms': 'nplurals=1; plural=0;',
    }


def marks(text):
    return sorted(MARKS.findall(text or ''))


def read_yaku():
    """{(module, en): ja}; module is '' for all modules, else only that one"""
    with open(os.path.join(HERE, 'yaku.csv'), encoding='utf-8') as f:
        return {(row['module'], row['en']): row['ja'] for row in csv.DictReader(f)}


def find(yaku, module, en):
    return yaku.get((module, en)) or yaku.get(('', en), '')


def sources():
    base = os.path.dirname(trytond.__file__)
    for po in sorted(
            glob.glob(os.path.join(base, 'ir', 'locale', 'de.po'))
            + glob.glob(os.path.join(base, 'res', 'locale', 'de.po'))
            + glob.glob(os.path.join(base, 'modules', '*', 'locale', 'de.po'))):
        yield os.path.basename(os.path.dirname(os.path.dirname(po))), po


def main(sao):
    yaku = read_yaku()
    missing, wrong = set(), []
    os.makedirs(os.path.join(LOCALE, 'sao'), exist_ok=True)
    for module, path in sources():
        out = polib.POFile(wrapwidth=78)
        out.metadata = HEADER
        for e in polib.pofile(path):
            if e.obsolete:
                continue
            ja = find(yaku, module, e.msgid)
            if not ja:
                missing.add(e.msgid)
            elif marks(ja) != marks(e.msgid):
                wrong.append((module, e.msgid, ja))
            entry = polib.POEntry(msgctxt=e.msgctxt, msgid=e.msgid)
            if e.msgid_plural:
                entry.msgid_plural = e.msgid_plural
                entry.msgstr_plural = {0: ja}
            else:
                entry.msgstr = ja
            out.append(entry)
        out.save(os.path.join(LOCALE, module + '.po'))
    client = {'': {'language': 'ja', 'plural-forms': HEADER['Plural-Forms']}}
    for e in polib.pofile(os.path.join(sao, 'locale', 'de.po')):
        if e.obsolete:
            continue
        ja = find(yaku, 'sao', e.msgid)
        if not ja:
            missing.add(e.msgid)
            continue
        if marks(ja) != marks(e.msgid):
            wrong.append(('sao', e.msgid, ja))
        client[e.msgid] = [e.msgid_plural or None, ja]
    with open(os.path.join(LOCALE, 'sao', 'ja.json'), 'w', encoding='utf-8') as f:
        json.dump(client, f, ensure_ascii=False, separators=(',', ':'))
    for en in sorted(missing):
        print(f'no Japanese: {en!r}')
    for module, en, ja in wrong:
        print(f'placeholders differ [{module}]: {en!r} -> {ja!r}')
    print(f'no Japanese: {len(missing)}, placeholders differ: {len(wrong)}')
    return 1 if wrong else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
