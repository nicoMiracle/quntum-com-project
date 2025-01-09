from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicSimulator

#creates a circuit which should copy 1101 to B qubits
def set_test():
    A = [0,1,2,3]
    X = "1111"
    circuit = QuantumCircuit(len(A),4)
    circuit.barrier()
    set_bits(circuit,A,X)
    circuit.measure(A,[3,2,1,0])

    print(circuit)
    basic_simulation(circuit)
    
set_test()