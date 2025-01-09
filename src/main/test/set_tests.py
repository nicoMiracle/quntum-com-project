from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicSimulator

from src.main.Implementation.Modular_Exponentiation import basic_simulation, set_bits

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