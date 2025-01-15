from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicSimulator

def set_bits(circuit, a, x):
    for i in reversed(range(len(a))):
        if x[i] == "1":
            circuit.x(a[i])


def set_test(qubits, x):
    circuit = QuantumCircuit(len(qubits),4)
    circuit.barrier()
    set_bits(circuit,qubits,x)
    circuit.measure(qubits,[3,2,1,0])

    print("Expected: " + x)
    print(circuit)
    basic_simulation(circuit)
    
    
def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Probabilities : ", prob )
    
set_test([0,1,2,3], "0001")
set_test([0,1,2,3], "0010")
set_test([0,1,2,3], "0101")
set_test([0,1,2,3], "1010")