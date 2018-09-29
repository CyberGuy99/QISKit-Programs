import math

'''
N is the expected max_value, the real max_value is usually shifted up
to match the max value associated with the number of bits necessary
'''
def get_negations(N, solutions):
    numbits = math.ceil(math.log(N+1,2))
    max_value = int(math.pow(2,numbits)) - 1

    #handle case where solutions may be tuple of len 1
    if isinstance(solutions, int):
        solutions = [solutions]
    else:
        solutions = list(solutions)

    bitstrings = [make_bitstring(soln,numbits) for soln in solutions]
    all_bitstrings = [make_bitstring(i,numbits) for i in range(max_value + 1)]
    negations = []
    for bitstring in all_bitstrings:
        if bitstring not in bitstrings:
            negations.append(bitstring)
    return negations, bitstrings

def make_bitstring(n,numbits):
    return format(n,'0{}b'.format(numbits))

def negate(bitstring):
    negation = [ '0' if bit == '1' else '1' for bit in bitstring]
    return negation

def make_cnf(negations, solutions):
    dimacs_solutions = [bitstring_to_clause(soln) for soln in solutions]
    cnf_buffer = ["c DIMACS 3-sat with {} solution(s): {}".format(\
            str(len(solutions)), ','.join(dimacs_solutions))]
    num_literals = len(negations[0])
    cnf_buffer.append('p cnf {} {}'.format(num_literals, len(negations)))
    bs_clauses = [negate(neg) for neg in negations]
    for bs in bs_clauses:
        cnf_buffer.append(bitstring_to_clause(bs))
    return '\n'.join(cnf_buffer)

def bitstring_to_clause(bitstring):
    clause_buffer = []
    for index, num in enumerate(bitstring):
        literal = index+1 if num == '1' else -(index+1)
        clause_buffer.append(str(literal))
    clause_buffer.append('0')
    clause = ' '.join(clause_buffer)
    return clause


def clause_to_num(arr,binary=False):
    buff = []
    for num in arr:
        if num == 0:
            break
        bit = '0' if num < 0 else '1'
        buff.append(bit)
    bitstring = ''.join(buff)
    if binary:
        return bitstring
    return int(bitstring, 2)

'''
main useful method
creates a cnf string given N and array of solutions in base 10
N is the expected max value of the base 10 search range
see above comments for more on N
'''
def get_cnf(N, solutions):
    negs, solns = get_negations(N, solutions)
    return make_cnf(negs, solns)
