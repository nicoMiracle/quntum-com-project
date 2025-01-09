#Nicole Nechita, rone8293

from qiskit import QuantumCircuit
from qiskit . providers . basic_provider import BasicSimulator

def copy(circuit, A, B):
    amount_registers = len(A)
    for i in range(amount_registers):
        circuit.cx(A[i],B[i])
        circuit.barrier()


#creates a circuit which should copy 1111 to B qubits
def copy_experiment_all_one():
    A = [0,1,2,3]
    B = [4,5,6,7]
    circuit = QuantumCircuit(len(A)+len(B),4)
    circuit.x(0)
    circuit.x(1)
    circuit.x(2)
    circuit.x(3)
    circuit.barrier()
    copy(circuit,A,B)
    circuit.measure(B,[3,2,1,0])

    print(circuit)
    basic_simulation(circuit)

#creates a circuit which should copy 0000 to B qubits
def copy_experiment_all_zero():
    A = [0,1,2,3]
    B = [4,5,6,7]
    circuit = QuantumCircuit(len(A)+len(B),4)
    circuit.barrier()
    copy(circuit,A,B)
    circuit.measure(B,[3,2,1,0])

    print(circuit)
    basic_simulation(circuit)

#creates a circuit which should copy 1101 to B qubits
def copy_experiment_varied():
    A = [0,1,2,3]
    B = [4,5,6,7]
    circuit = QuantumCircuit(len(A)+len(B),4)
    circuit.x(0)
    circuit.x(1)
    circuit.x(3)
    circuit.barrier()
    copy(circuit,A,B)
    circuit.measure(B,[3,2,1,0])

    print(circuit)
    basic_simulation(circuit)

#auxiliary function for basic simulation
def basic_simulation(circuit):
    
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts . items () }
    print (" Counts : ", counts )
    print (" Probabilities : ", prob )

copy_experiment_all_one()
copy_experiment_all_zero()
copy_experiment_varied()


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
