
def get_oeis_keywords():
    return ['base', 'bref', 'cofr', 'cons', 'core', 'dead', 'dumb',
            'easy', 'eigen', 'fini', 'frac', 'full', 'hard', 'hear', 'less', 'look', 'more', 'mult',
            'nice', 'nonn', 'obsc', 'sign', 'tabf', 'tabl', 'uned', 'unkn', 'walk', 'word']

def get_loda_keywords():
    return ['java', 'loda']

def get_all_keywords():
    keywords = get_oeis_keywords()
    keywords.extend(get_loda_keywords())
    keywords.sort()
    return keywords
