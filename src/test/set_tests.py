from qiskit import QuantumCircuit
from qiskit.providers.basic_provider import BasicSimulator
from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister

#the set_bits function 1.1
def set_bits(circuit, a, x):
    x = x[::-1]
    for i in reversed(range(len(a))):
        if x[i] == "1":
            circuit.x(a[i])


def set_test(size, x):
    qbits = QuantumRegister(size,"q")
    classical = ClassicalRegister(size,"c_")
    circuit = QuantumCircuit(qbits,classical)
    circuit.barrier()
    set_bits(circuit,qbits,x)
    circuit.measure(qbits ,classical)

    print("Expected: " + x)

    basic_simulation(circuit)
    
    
def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Probabilities : ", prob )

set_test(1,"0")
set_test(1,"1")
set_test(2,"10")
set_test(3,"000")
set_test(3,"101")
set_test(3,"100")
set_test(4, "0001")
set_test(4, "0010")
set_test(4, "0101")
set_test(4, "1010")
set_test(24,"101001111010101110111101")