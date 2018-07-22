from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit, execute
from qiskit.tools.visualization import plot_histogram
from qiskit import register

qr = QuantumRegister(3)
cr = ClassicalRegister(3)
qc = QuantumCircuit(qr,cr)

qc.h(qr[1])
qc.cx(qr[1],qr[0])

qc.cx(qr[2],qr[1])
qc.h(qr[2])

qc.cx(qr[1],qr[0])

qc.h(qr[0])
qc.cx(qr[2],qr[0])
qc.h(qr[0])

qc.measure(qr[0],cr[0])

#backend = 'local_statevector_simulator'
#backend = "local_unitary_simulator"
#backend = 'local_qasm_simulator'
backend = 'ibmq_qasm_simulator'
#backend = 'ibmqx4'
#backend = 'ibmqx5'

from results import get_result
stats_sim, time_elapsed = get_result(qc,backend)

print(stats_sim)
plot_histogram(stats_sim)
