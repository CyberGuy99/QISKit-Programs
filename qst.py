from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit import register, compile, get_backend, available_backends
from scipy import linalg
import numpy as np
import math, cmath, random, enum
import time

class Gate(enum.Enum):
    S = 0
    T = 1
    H = 2
    X = 3
    Y = 4
    Z = 5
    I = 6

#qc becomes useless after measure so qr is reset
def measure(qc,qr,cr,basis):
    if basis == 'X' or basis == 'Y':
        qc.h(qr)
    if basis == 'Y':
        qc.sdg(qr)
    qc.measure(qr, cr)
    global BACKEND
    global SHOTS

    log(qc.qasm())
    qobj = compile(qc,backend=BACKEND,shots=SHOTS)
    qc.reset(qr)

    return qobj

def init_circuit(n):
    qr = QuantumRegister(n)
    cr = ClassicalRegister(n)
    return qr, cr, QuantumCircuit(qr,cr)

def get_runner():
    bad_backend = True
    runner = None
    global BACKEND
    while bad_backend:
        try:
            runner = get_backend(BACKEND)
            bad_backend = False
        except Exception as e:
            print(available_backends())
            BACKEND = input("chosen backend not available, choose one from the list above: ")
            bad_backend = True
    return runner

def random_gates(n):
    GATES = [Gate.S,Gate.T,Gate.H,Gate.X,Gate.Y,Gate.Z,Gate.I]
    gates = []
    for i in range(n):
        gates.append(random.choice(GATES))
    return gates

I = complex(0,1)
def phase_gate(phi):
    flat = np.array([1,0,0,cmath.exp(I*phi)])
    return np.matrix(flat.reshape(2,2))

GATE_VALS = {Gate.S:phase_gate(math.pi/2), Gate.T:phase_gate(math.pi/4), Gate.H: math.pow(2,-.5) * np.matrix([[1,1],[1,-1]]), \
        Gate.X: np.matrix([[0,1],[1,0]]), Gate.Y: np.matrix([[0,-1*I],[I,0]]), \
        Gate.Z: phase_gate(math.pi), Gate.I: np.matrix([[1,0],[0,1]])}

def start_jobs(qobjs, runner):
    started_jobs = []
    for job_num, qobj in enumerate(qobjs):
        try:
            job = runner.run(qobj)
            started_jobs.append(job)
        except Exception as e:
            print("job number " + str(job_num) + " failed...\nrunning next job...")
    return started_jobs

def handle_jobs(started_jobs):
    probs = []
    for job_num, job in enumerate(started_jobs):
        print(str(job_num) + "th job is running:")
        while not job.done:
            time.sleep(.01)
        print("job's done")
        counts = job.result().get_counts()
        log(counts)
        num_zeroes = counts.get('0')
        positive = 0
        if num_zeroes != None:
            positive = num_zeroes/SHOTS
        probs.append(positive)
    return probs

#format is in [(x-prob,y-prob,z-prob),...]
def handle_results(prob,ideal):
    x,y,z = prob
    #mean_X = x - (1-x)
    mean_X = 2*x - 1
    mean_Y = 2*y - 1
    mean_Z = 2*z - 1
    #log("<X>: ": str(mean_X) + "\n<Y>: " + str(mean_Y) + "\n<Z>: " + str(mean_Z))
    log("<X>: {}\n<Y>: {} \n<Z>: {}".format(mean_X,mean_Y,mean_Z))
    log(ideal)
    state = calculate_state_matrix(mean_X,mean_Y,mean_Z)
    log(state)
    fidelity = calculate_fidelity(ideal,state)
    return fidelity

def calculate_state_matrix(X,Y,Z):
    state = GATE_VALS[Gate.I] + X*GATE_VALS[Gate.X]
    state = state + Y*GATE_VALS[Gate.Y] + Z*GATE_VALS[Gate.Z]
    return .5 * state

def calculate_fidelity(expected,actual):
    dagger = expected.transpose().conjugate()
    prob_success = dagger.dot(actual.dot(expected))
    p = round(float(prob_success.real),5)
    return math.sqrt(p)

def get_ideal_state(gates):
    product = np.matrix([[1,0],[0,1]])
    #gates goes in order from first gate applied to last
    #so multiplication is reversed

    #calculate ideal-expected state
    index = len(gates) - 1
    while index >= 0:
        g = gates[index]
        product = product.dot(GATE_VALS[g])
        index -= 1
    final_state = product.dot(np.array([[1],[0]]))
    return final_state


def apply_gates(qc,qr,gates):
    for g in gates:
        if g == Gate.S:
            qc.s(qr)
        elif g == Gate.T:
            qc.t(qr)
        elif g == Gate.H:
            qc.h(qr)
        elif g == Gate.X:
            qc.x(qr)
        elif g == Gate.Y:
            qc.y(qr)
        elif g == Gate.Z:
            qc.z(qr)
        elif g == Gate.I:
            qc.iden(qr)
        else:
            print("ERROR NOT A GATE")


def prepare_circuit(qc,qr,gates):
    ideal  = get_ideal_state(gates)
    apply_gates(qc,qr,gates)
    return qc, qr, ideal

def test_n_gates(n,gates=None):
    if gates is None:
        gates = random_gates(n)
    log(gates)
    qr,cr,qc = init_circuit(1)
    qc, qr, ideal = prepare_circuit(qc,qr,gates)
    runner = get_runner()
    qobjX = measure(qc,qr,cr,'X')
    apply_gates(qc,qr,gates)
    qobjY = measure(qc,qr,cr,'Y')
    apply_gates(qc,qr,gates)
    qobjZ = measure(qc,qr,cr,'Z')
    probs = handle_jobs(start_jobs([qobjX,qobjY,qobjZ],runner))
    fidelities = handle_results(tuple(probs),ideal)
    if fidelities != 1:
        print(gates)
    print("fidelities for {} gates: {}".format(n,fidelities))
    return fidelities

def log(*arg):
    if DEBUG:
        print(*arg)

DEBUG = False
SHOTS = 1024
BACKEND = 'local_qasm_simulator'

#testing gates
num_gates = [1,2,4,8,16]
#for n in num_gates:
#    test_n_gates(n)

gates = [Gate.X,Gate.H,Gate.I,Gate.T]
test_n_gates(4,gates)

gates = [Gate.Y, Gate.X, Gate.S, Gate.I, Gate.T, Gate.I, Gate.H, Gate.I, Gate.S, Gate.S, Gate.I, Gate.T, Gate.I, Gate.Z, Gate.I, Gate.I]
test_n_gates(16,gates)
