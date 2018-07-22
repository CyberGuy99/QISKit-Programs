from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit, execute
from qiskit import register, compile, get_backend, available_backends
import enum
import random
import math
import results
import matplotlib.pyplot as plt
import time

class Gate(enum.Enum):
    S = 0
    T = 1
    H = 2
    X = 3
    Y = 4
    Z = 5
    I = 6

def fidelity_to_p(f,m):
    const = math.log(.5)
    try:
        lhs = math.log(f-.5)
    except Exception as e:
        print("f<=.5 (unreasonably low...try more shots")
    logp = (lhs - const)/(m+1)
    return math.exp(logp)

def create_circuit(n=5):
    debug_print("creating circuit with "+str(n)+" registers")
    qr_temp = QuantumRegister(n)
    cr_temp = ClassicalRegister(n)
    return qr_temp, cr_temp, QuantumCircuit(qr_temp,cr_temp)

#returns random number from 0 to 5 inclusive
def random_num():
    qr,cr,qc = create_circuit(1,1)
    qc.h(qr[0])

def random_gates(n):
    debug_print("generating "+str(n)+" random gates...")
    GATES = [Gate.S,Gate.T,Gate.H,Gate.X,Gate.Y,Gate.Z,Gate.I]
    gates = []
    for i in range(n):
        gates.append(random.choice(GATES))
    return gates

def benchmark_circuit(qc,qr,gates):
    debug_print("applying gates...")

    for g in gates:
        if g == Gate.S:
            qc.s(qr[0])
        elif g == Gate.T:
            qc.t(qr[0])
        elif g == Gate.H:
            qc.h(qr[0])
        elif g == Gate.X:
            qc.x(qr[0])
        elif g == Gate.Y:
            qc.y(qr[0])
        elif g == Gate.Z:
            qc.z(qr[0])
        elif g == Gate.I:
            qc.iden(qr[0])
        else:
            print("ERROR NOT A GATE")
    return qc, qr

def inverse_benchmark(qc,qr,gates):
    debug_print("applying inverses...")
    current = len(gates) - 1
    while current >= 0:
        g = gates[current]
        if g == Gate.S:
            qc.sdg(qr[0])
        elif g == Gate.T:
            qc.tdg(qr[0])
        elif g == Gate.H:
            qc.h(qr[0]).inverse()
        elif g == Gate.X:
            qc.x(qr[0]).inverse()
        elif g == Gate.Y:
            qc.y(qr[0]).inverse()
        elif g == Gate.Z:
            qc.z(qr[0]).inverse()
        elif g == Gate.I:
            qc.iden(qr[0]).inverse()
        else:
            print("ERROR NOT A GATE")

        current-=1
    return qc, qr

def prepare_circuit(qc,qr,cr,n,backend):
    debug_print("setting up circuit...")
    gates = random_gates(n)
    qc, qr = benchmark_circuit(qc,qr,gates)
    qc.barrier()
    qc, qr = inverse_benchmark(qc,qr,gates)
    qc.measure(qr,cr)
    global SHOTS
    qobj = compile(qc,backend=backend,shots=SHOTS)
    return qobj

def exec_circuits(jobs,backend):
    bad_backend = True
    runner = None
    while bad_backend:
        try:
            runner = get_backend(backend)
            bad_backend = False
            global BACKEND
            BACKEND = backend #remember new backend
        except Exception as e:
            print(available_backends())
            backend = input("chosen backend not available, choose one from the list above: ")
            bad_backend = True

    job_num = 0
    started_jobs = []
    for qobj in jobs:
        try:
            job = runner.run(qobj)
        except Exception as e:
            print("job number "+str(job_num)+" failed...\nrunning next job...")
        job_num+=1
        started_jobs.append(job)
    return started_jobs

def commence_test(n):
    global BACKEND
    global num_tests
    jobs = []
    context = "backend: "+BACKEND+", num_gates: "+str(n)+", num_tests: "+str(num_tests)
    for i in range(num_tests):
        qr,cr,qc = create_circuit(1)
        qobj = prepare_circuit(qc,qr,cr,n,BACKEND)
        jobs.append(qobj)
    started_jobs = exec_circuits(jobs,BACKEND)

    fidelities = []
    global SHOTS

    for i in range(len(started_jobs)):
        job = started_jobs[i]
        if not job.done:
            print("waiting for job number: "+str(i)+"\nwith context: "+context+".",end='')

        while not job.done:
            print(".",end='')
            time.sleep(1)
        print("\njob's done")
        counts = job.result().get_counts()
        num_zeroes = counts.get('0')
        if num_zeroes == None:
            fidelity = 0
        else:
            fidelity = num_zeroes/SHOTS #pr[0]
        fidelities.append(fidelity)
    return fidelities

def start_test(n):
    qr,cr,qc = create_circuit(1)
    f = commence_test(n)
    assert(num_tests==len(f))
    fidelity = sum(f)/num_tests
    p_success = fidelity_to_p(fidelity,n)
    return n,sum(f)/num_tests,p_success

def start_tests(gate_nums):
    global num_tests
    debug_print("starting tests...")
    fidelities = []
    for n in gate_nums:
        fidelities.append(start_test(n))

    x = [f[0] for f in fidelities]
    y = [f[1] for f in fidelities]
    p = [f[2] for f in fidelities]

    assert(len(fidelities)==len(gate_nums))
    print("Test results for",str(num_tests),"test(s) and for",str(len(gate_nums)),"sets of random gates")
    print("num_gates:\tfidelity:\tp_success:")
    num_spaces = len("num_gates:") + 5
    s1 = spaces(num_spaces)
    s2 = spaces(num_spaces-2)
    for i in range(len(fidelities)):
        if x[i] == 10:
            s1 = spaces(num_spaces-1)
            s2 = spaces(num_spaces-2)
        print(str(x[i])+s1+str(y[i])+s2+str(p[i]))

    plt.plot(x,y,'ro')
    plt.axis([min(gate_nums),max(gate_nums),0,1])
    plt.ylabel('fidelity')
    plt.xlabel('number of random clifford gates applied')
    plt.title('Fidelity Results')
    plt.show()


    plt.plot(x,p,'ro')
    plt.axis([min(gate_nums),max(gate_nums),0,1])
    plt.ylabel('probability')
    plt.xlabel('number of random clifford gates applied')
    plt.title('Probability of Not Foo-Bar Results')
    plt.show()

def spaces(n):
    spacebar = ""
    while n > 0:
       spacebar += " "
       n-=1
    return spacebar

def debug_print(statement):
    global DEBUG
    if DEBUG:
        print(statement)

DEBUG = False
#BACKEND = "local_qasm_simulator"
#BACKEND = "ibmq_qasm_simulator"
BACKEND = "ibmqx4"
num_tests = 10 #number of repetitions for each test (for each entry of m)
GATE_NUMS = [x+1 for x in range(6)] #list of number of gates to apply, each entry is a new m
SHOTS = 1024

jobs = []

results.register_program()
start_tests(GATE_NUMS)
