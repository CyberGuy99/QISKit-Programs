from qiskit import register
from qiskit import QuantumCircuit, execute
#import notification
import time

def get_result(qc,backend='local_qasm_simulator',shots_sim=0,debug=False,notify=False):
    if shots_sim == 0:
        shots_sim = input("How many shots? (1->8192): ")
        try:
            shots_sim = int(shots_sim)
            if shots_sim<1 or shots_sim>8192:
                print('invalid shot number, using 8192')
                shots_sim = 8192
        except Exception as e:
            print("shot choice is not a number...using 8192")
            shots_sim = 8192

    back_simulator = True
    #if not back_simulator and notify:


    start = time.time()
    job_sim = execute(qc,backend,shots=shots_sim)
    stats_sim = job_sim.result().get_counts()

    end = time.time()
    if debug:
        print("time elapsed for ",backend,": ",str(end-start))
    return stats_sim, end - start

def register_program():
    try:
        import sys
        sys.path.append('../')
        import Qconfig
        qx_config = {
                'APItoken': Qconfig.APItoken,
                'url': Qconfig.config['url']}
    except Exception as e:
        qx_config = {
                'APItoken': '04ff39f24fe6d848b2c02ceccd1e1913e5243c3d5e723acc793071097de8be357baa25c319a761c202d3a024b55c04265e5f4c18914757b9fceff112997a2bdb',
                'url': 'https://quantumexperience.ng.bluemix.net/api'}
    #Setup API
    register(qx_config['APItoken'], qx_config['url'])
