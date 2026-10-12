# SPDX-License-Identifier: GPL-3.0-or-later
"""Load the Japanese translation into a Tryton database.

    trytond_import_ja -c trytond.conf -d tryton [--sao /path/to/sao]

Tryton has no Japanese, so the language "ja" is made here, and the
translation of each activated module is loaded from locale/<module>.po the
same way Tryton loads its own PO files. Run it again after activating more
modules. Restart trytond afterwards.
"""
import os
import shutil
from argparse import ArgumentParser

HERE = os.path.dirname(__file__)
LOCALE = os.path.join(HERE, 'locale')

# From the ja_JP.UTF-8 locale of glibc; dates as written on Japanese forms
LANG = {
    'code': 'ja',
    'name': '日本語',
    'nplurals': 1,
    'plural': '0',
    'date': '%Y/%m/%d',
    'am': '午前',
    'pm': '午後',
    'grouping': '[3, 0]',
    'decimal_point': '.',
    'thousands_sep': ',',
    'mon_grouping': '[3, 0]',
    'mon_decimal_point': '.',
    'mon_thousands_sep': ',',
    'p_sign_posn': 4,
    'n_sign_posn': 4,
    'positive_sign': '',
    'negative_sign': '-',
    'p_cs_precedes': True,
    'n_cs_precedes': True,
    'p_sep_by_space': False,
    'n_sep_by_space': False,
    }


def main(database, config_file=None, sao=None):
    import trytond.config as config
    config.update_etc(config_file)
    from trytond.pool import Pool
    from trytond.transaction import Transaction

    Pool.start()
    pool = Pool(database)
    pool.init()
    loaded = []
    with Transaction().start(database, 0) as transaction:
        Lang = pool.get('ir.lang')
        Module = pool.get('ir.module')
        Translation = pool.get('ir.translation')
        with transaction.set_context(active_test=False):
            langs = Lang.search([('code', '=', 'ja')])
        if langs:
            Lang.write(langs, {**LANG, 'active': True, 'translatable': True})
        else:
            Lang.create([{**LANG, 'translatable': True}])
        activated = {m.name for m in Module.search(
                [('state', '=', 'activated')])}
        for name in sorted(os.listdir(LOCALE)):
            module, ext = os.path.splitext(name)
            if ext == '.po' and module in activated:
                Translation.translation_import(
                    'ja', module, [os.path.join(LOCALE, name)])
                loaded.append(module)
    if sao:
        shutil.copy(os.path.join(LOCALE, 'sao', 'ja.json'),
            os.path.join(sao, 'locale', 'ja.json'))
        loaded.append('sao')
    print('ja: ' + ', '.join(loaded))


def run():
    parser = ArgumentParser()
    parser.add_argument('-d', '--database', dest='database', required=True)
    parser.add_argument('-c', '--config', dest='config_file',
        help='the trytond config file')
    parser.add_argument('--sao', help='the folder of sao, to add its ja.json')
    args = parser.parse_args()
    main(args.database, args.config_file, args.sao)


if __name__ == '__main__':
    run()
