from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicSimulator

#the set_bits function 1.1
def set_bits(circuit, a, x):
    x = x[::-1]
    for i in reversed(range(len(a))):
        if x[i] == "1":
            circuit.x(a[i])


def set_test(qubits, x):
    circuit = QuantumCircuit(len(qubits),4)
    circuit.barrier()
    set_bits(circuit,qubits,x)
    circuit.measure(qubits,[0,1,2,3])

    print("Expected: " + x)
    basic_simulation(circuit)
    print()
    
    
def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Probabilities : ", prob )
print("set_bits test: ")
set_test([0,1,2,3], "0001")
set_test([0,1,2,3], "0010")
set_test([0,1,2,3], "0101")
set_test([0,1,2,3], "1010")