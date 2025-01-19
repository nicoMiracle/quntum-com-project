#Nicole Nechita, rone8293

from qiskit import QuantumCircuit,QuantumRegister,ClassicalRegister
from qiskit . providers . basic_provider import BasicSimulator

def copy(circuit, A, B):
    amount_registers = len(A)
    for i in range(amount_registers):
        circuit.cx(A[i],B[i])
        circuit.barrier()

def set_bits(circuit, a, x):
    x = x[::-1]
    for i in reversed(range(len(a))):
        if x[i] == "1":
            circuit.x(a[i])


#creates a circuit which should copy 1111 to B qubits
def copy_test(size,A_text):
    AQ = QuantumRegister(size,"A")
    B = QuantumRegister(size,"B")
    c_bit= ClassicalRegister(size,"c")
    circuit = QuantumCircuit(AQ,B,c_bit)
    set_bits(circuit,AQ,A_text)
    circuit.barrier()
    copy(circuit,AQ,B)
    print("Expected: " + A_text)
    circuit.measure(B,c_bit)

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

copy_test(1,"0")
copy_test(1,"1")
copy_test(2,"01")
copy_test(3,"011")
copy_test(4,"0101")
copy_test(4,"0001")

copy_test(7,"0101101")
copy_test(12,"010110110100")

