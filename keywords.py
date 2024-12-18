
def get_keyword_descriptions():
    return {
        'base': 'Sequence terms are defined based on a number representation in a particular base format, e.g. decimal or binary',
        'bref': 'Sequences with very few terms',
        'cofr': 'Continued fractions for (usually irrational) constants',
        'conjecture': 'Sequences that include conjectures in their OEIS description',
        'cons': 'Sequences that give terms for decimal expansions',
        'core': 'Core sequences of the OEIS database',
        'dead': 'Errornous or duplicate sequences',
        'decimal-expansion': 'Decimal expansions of constants',
        'dumb': 'Unimportant sequences from non-mathematical contexts',
        'easy': 'Sequences that are easy to comute and understand',
        'egf-expansion': 'Expansions of exponential generating functions',
        'eigen': 'Eigensequences',
        'fini': 'Finite sequences',
        'formula': 'Formulas exist in OEIS entries for these sequences',
        'frac': 'Numerators or denominators of sequence of rationals',
        'full': 'Finite sequence with all terms available',
        'gf-expansion': 'Expansions of generating functions',
        'hard': 'Sequences that are hard to compute',
        'less': 'Less interesting sequences',
        'loda': 'LODA programs exist for these sequence',
        'loda-formula': 'Formulas generated from a LODA programs exist for these sequences',
        'loda-inceval': 'LODA programs that can be computed incrementally exist for these sequences',
        'loda-logeval': 'LODA programs with logarithmic complexity exist for these sequences',
        'loda-loop': 'LODA programs with loop exist for these sequences',
        'look': 'Pin or scatter plots reveal interesting information',
        'more': 'Sequences that need more terms',
        'mult': 'Multiplicative functions',
        'nice': 'Exceptionally "nice" sequences',
        'nonn': 'Sequences with only non-negative terms',
        'obsc': 'Obscure sequences: descriptions are known, but difficult to understand',
        'pari': 'PARI/GP programs exist for these sequence',
        'sign': 'Sequences with negative terms',
        'tabf': 'Tables with irregular row lengths',
        'tabl': 'Regular tables: fixed row length',
        'unkn': 'Sequences whose definition is unknown',
        'walk': 'Sequences that contain walks through a lattice',
        'word': 'Numbers related to a given natural language'
    }

def get_keywords():
    descriptions = get_keyword_descriptions()
    keywords = list(descriptions.keys())
    keywords.sort()
    return keywords
