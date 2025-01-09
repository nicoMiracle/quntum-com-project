from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicSimulator

def set_bits(circuit, a, x):
    for i in reversed(range(len(a))):
        if x[i] == "1":
            circuit.x(a[i])


def set_test():
    A = [0,1,2,3]
    X = "1101"
    circuit = QuantumCircuit(len(A),4)
    circuit.barrier()
    set_bits(circuit,A,X)
    circuit.measure(A,[3,2,1,0])

    print(circuit)
    basic_simulation(circuit)
    
    
def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Counts : ", counts )
    print (" Probabilities : ", prob )
    
set_test()