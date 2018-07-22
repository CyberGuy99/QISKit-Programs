# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

from qiskit_acqua.input import get_input_instance
from qiskit_acqua import run_algorithm
import time
import random
import numpy as np
from cnf import get_cnf

sat_cnf = """
c Example DIMACS 3-sat, with 3 solutions: 1 -2 3 0, -1 -2 -3 0, 1 2 -3 0
p cnf 3 5
-1 -2 -3 0
1 -2 3 0
1 2 -3 0
1 -2 -3 0
-1 2 3 0
"""

safe_sat_cnf_search = """
c DIMACS 3-sat with one solution (midpoint variable): -1 2 -3 0
p cnf 3 7
-1 2 -3 0
-1 -2 3 0
1 2 -3 0
1 2 3 0
1 -2 -3 0
-1 2 3 0
-1 -2 -3 0
"""
sat_cnf_search = """
c DIMACS 3-sat with one solution (midpoint variable): -1 2 -3
p cnf 3 7
-1 2 -3
-1 -2 3
1 2 -3
1 2 3
1 -2 -3
-1 2 3
-1 -2 -3
"""



params = {
    'problem': {'name': 'search'},
    'algorithm': {'name': 'Grover'},
    'oracle': {'name': 'SAT', 'cnf': safe_sat_cnf_search},
    'backend': {'name': 'local_qasm_simulator'}
}

NUM_ITEMS = 3
location = random.randint(0,NUM_ITEMS)
risk_sat = get_cnf(NUM_ITEMS,location)

start = time.time()
result = run_algorithm(params)
end = time.time()

print('job took {} seconds'.format(end-start))
print(result['result'])


# classical version search
arr = np.zeros(NUM_ITEMS)
db = [int(num) for num in arr]
db[location] = 1
start = time.time()
for i,val in enumerate(db):
    if val == 1:
        print(i)
        break
end = time.time()
print("{} seconds for classical search".format(end-start))
