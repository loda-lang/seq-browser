
def get_oeis_keywords():
    return ['base', 'bref', 'cofr', 'cons', 'core', 'dead', 'dumb',
            'easy', 'eigen', 'fini', 'frac', 'full', 'hard', 'hear', 'less', 'look', 'more', 'mult',
            'nice', 'nonn', 'obsc', 'sign', 'tabf', 'tabl', 'uned', 'unkn', 'walk', 'word']

def get_more_keywords():
    return ['loda']

def keywords_to_index():
    index = 0
    result = {}
    for k in get_oeis_keywords():
        result[k] = index
        index += 1
    for k in get_more_keywords():
        result[k] = index
        index += 1
    return result
