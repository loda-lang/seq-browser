
def get_keyword_descriptions():
    return {
        'base': 'Sequences terms are defined based on a number representation in a particular base format, e.g. decimal or binary',
        'bref': 'Sequence has very few terms',
        'cofr': 'Continued fractions for (usually irrational) constants',
        'cons': 'Sequences gives terms for a decimal expansion',
        'core': 'Core sequences of the OEIS database',
        'dead': 'Errornous or duplicate sequences',
        'dumb': 'Unimportant sequences from non-mathematical contexts',
        'easy': 'Sequences that are easy to comute and understand',
        'eigen': 'Eigensequences',
        'fini': 'Finite sequences',
        'frac': 'Numerators or denominators of sequence of rationals',
        'full': 'Finite sequence with all terms available',
        'hard': 'Sequences that are hard to compute',
        'java': 'A Java program (jOEIS) exists for this sequence',
        'less': 'A less interesting sequence',
        'loda': 'A LODA program exists for this sequence',
        'look': 'Pin or scatter plots reveal interesting information',
        'maple': 'A Maple program exists for this sequence',
        'mathematica': 'A Mathematica program exists for this sequence',
        'more': 'Sequences that need more terms',
        'mult': 'Multiplicative functions',
        'nice': 'Exceptionally "nice" sequences',
        'nonn': 'Sequences with only non-negative terms',
        'obsc': 'Obscure sequence: description is known, but difficult to understand or not very enlightening',
        'pari': 'A PARI/GP program exists for this sequence',
        'sign': 'Sequence with negative terms',
        'tabf': 'Tables with irregular row lengths',
        'tabl': 'Regular tables: fixed row length',
        'unkn': 'Sequences whose definition is unknown',
        'walk': 'Sequence that contains walks through a lattice of specified shape, size and/or dimensions',
        'word': 'Numbers related to a given natural language'
    }

def get_keywords():
    descriptions = get_keyword_descriptions()
    keywords = list(descriptions.keys())
    keywords.sort()
    return keywords
