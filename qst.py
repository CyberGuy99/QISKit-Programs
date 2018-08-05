from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit import register, compile, get_backend, available_backends
from scipy import linalg
import numpy as np

class Gate(enum.Enum):
    S = 0
    T = 1
    H = 2
    X = 3
    Y = 4
    Z = 5
    I = 6

def measure(qc,qr,cr,basis):
    if basis == 'X' or basis == 'Y':
        qc.h(qr)
    if basis == 'Y':
        qc.sdg(qr)
    qc.measure(qr, cr)
    global BACKEND
    global SHOTS

    #undos previous gates to reuse circuit
    if basis == 'X':
        qc.h(qr)
    if basis == 'Y':
        qc.s(qr)
        qc.h(qr)
    qobj = compile(qc,backend=BACKEND,shots=SHOTS)

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
            backend = input("chosen backend not available, choose one from the list above: ")
            bad_backend = True
    return runner

def random_gates(n):
    GATES = [Gate.S,Gate.T,Gate.H,Gate.X,Gate.Y,Gate.Z,Gate.I]
    gates = []
    for i in range(n):
        gates.append(random.choice(GATES))
    return gates

I = complex(0,-1)
def phase_gate(phi):
    row1 = [1,0]
    row2 = [0, cmath.exp(I*phi)]
    return np.array([row1,row2])

GATE_VALS = {Gate.S:phase_gate(math.pi/2), Gate.T:phase_gate(math.pi/4), Gate.H: math.pow(2,-.5) * np.array([[1,0],[0,1]]), \
        Gate.X: np.array([[0,1],[1,0]]), Gate.Y: numpy.array([[0,I],[I,0]]), \
        Gate.Z: phase_gate(math.pi), Gate.I: numpy.array([[1,0],[0,1]])}

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
        print(str(job_num) + " job results:")
        while not job.done:
            print(".", end='')
        print("\njob's done")
        counts = job.results().get_counts()
        num_zeroes = counts.get('0')
        positive = 0
        if num_zeroes != None:
            positive = num_zeroes/SHOTS
        probs.append(positive)
    return probs

#format is in [(x-prob,y-prob,z-prob),...]
def handle_results(probs,ideals):
    fidelities = []
    for x,y,z,ideal in zip(probs,ideals):
        #mean_X = x - (1-x)
        mean_X = 2*x - 1
        mean_Y = 2*y - 1
        mean_Z = 2*z - 1
        state = calculate_state_matrix(mean_X,mean_Y,mean_Z)
        fidelity = calculate_fidelity(ideal,state)
        fidelities.append(fidelity)
    return fidelities

def calculate_state_matrix(X,Y,Z):
    state = GATE_VALS[Gate.I] + X*GATE_VALS[Gate.X]
    state = state + Y*GATE_VALS[GATE.Y] + Z*GATE_VALS[GATE.Z]
    return .5 * state

def calculate_fidelity(expected,actual):
    prob_success = expected.dot(actual.dot(expected))
    return math.sqrt(prob_success)

def prepare_circuit(qc,qr,gates):
    product = np.array([1,0],[0,1])
    for g in gates:
        product = product.dot(GATE_VALS[g])
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
    final_state = product.dot(numpy.array([[1].[0]))
    return qc, qr, final_state

def test_n_gates(n):
    gates = random_gates(n)
    qr,cr,qc = construct_circuit(1)
    qc, qr, ideal = prepare_circuit(qc,qr,gates)
    runner = get_runner()
    qobjX = measure(qc,qr,cr,'X')
    qobjY = measure(qc,qr,cr,'Y')
    qobjZ = measure(qc,qr,cr,'Z')
    probs = handle_jobs(start_jobs([qobjX,qobjY,qobjZ],runner))
    fidelities = handle_results(tuple(probs),ideal)
    return fidelities

test_n_gates(1)


