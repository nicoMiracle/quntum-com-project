#Nicole Nechita, rone8293

from qiskit import QuantumCircuit
from qiskit . providers . basic_provider import BasicSimulator

#the copy function 1.2
def copy(circuit, A, B):
    amount_registers = len(A)
    for i in range(amount_registers):
        circuit.cx(A[i],B[i])
        circuit.barrier()
