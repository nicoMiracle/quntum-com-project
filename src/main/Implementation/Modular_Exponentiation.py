#Nicole Nechita, rone8293

from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister
from qiskit . providers . basic_provider import BasicSimulator

#the set_bits function 1.1
def set_bits(circuit, a, x):
    for i in reversed(range(len(a))):
        if x[i] == "1":
            circuit.x(a[i])

#the copy function 1.2
def copy(circuit, A, B):
    amount_registers = len(A)
    for i in range(amount_registers):
        circuit.cx(A[i],B[i])
        circuit.barrier()

def full_adder(circuit,a,b,r,c_in,c_out,aux):
    #a XOR b XOR c_in -> r
    #AUX is used to store a XOR b
    circuit.cx(a,aux)
    circuit.cx(b,aux)
    circuit.cx(aux,r)
    circuit.cx(c_in,r)
    circuit.barrier()

    #do gates for carry_out
    circuit.ccx(a,b,c_out)
    circuit.cx(a,b)
    circuit.ccx(b,c_in,c_out)
    circuit.cx(a,b)
    circuit.barrier()

    #reset AUX by doing the operation again
    
    circuit.cx(b,aux)
    circuit.cx(a,aux)
    circuit.barrier()

# Addition function
# adds two values made with n number of qubits
#
# aux[1] will always be the first carry in of the addition
#
# prams:
# circuit: QuantumCircuit
# a: list of qubit in size n
# b: list of qubit in size n
# r: list of qubit in size n
# aux: list of qubits with minimum size of n+2
def addition(circuit, a, b, r, aux):    
    for i in reversed(range(len(a))):
        _p = len(a)-i
        full_adder(circuit, a[i], b[i], r[i], aux[_p], aux[_p+1], aux[0])
    for i in range(len(a)):
        _p = len(a)-i
        circuit.ccx(a[i],b[i], aux[_p+1])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p],aux[_p+1])
        circuit.cx(a[i],b[i])
        circuit.barrier()
    circuit.barrier()

# subtraction
# subtract a with b
#
# prams:
# circuit: QuantumCircuit
# a: list of qubit in size n
# b: list of qubit in size n
# r: list of qubit in size n
# aux: list of qubits with minimum size of n+2
def subtraction(circuit, a, b, r, aux):
    circuit.x(b)
    circuit.x(aux[1])  
    circuit.barrier()
    addition(circuit, a, b, r, aux)
    circuit.x(b)
    circuit.x(aux[1])
    circuit.barrier()
  
#modulo
#
def modulo(circuit, n, x, r, aux):
    a = QuantumRegister(len(n), "a")
    b = QuantumRegister(len(n), "b")
    r = QuantumRegister(len(n), "r")
    aux = QuantumRegister(len(n)+2,"AUX")
    qu = QuantumCircuit(a,b,r,aux)
    subtraction(qu, a, b, r, aux)
    sub_gate = qu.to_gate(None, "sub").control(1)
    
    greater_than_or_equal(circuit, x, n, aux[0], aux[*range(1, len(aux))]) 
    circuit.append(sub_gate, [aux[0], x, n, r, aux[*range(len(n)+1, len(n)*2+3)]])
    greater_than_or_equal(circuit, x, n, aux[0], aux[range(1, len(aux))]) 
    
##################################################################
#                           Simulation
##################################################################

def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Counts : ", counts )
    print (" Probabilities : ", prob )

# Import the transpile module
from qiskit import transpile
# Define the backend AerSimulator
from qiskit_aer import AerSimulator   
def aer_simulation(circuit):
    backend = AerSimulator()
    # Transpile the circuit to a set of gates
    # compatible with the backend
    compiled_circuit = transpile(circuit, backend )
    # Execute the circuit on the qasm simulator .
    n_shots = 1024 # default number of shots .
    job_sim = backend.run(compiled_circuit, shots = n_shots)
    # Extract Results
    result_sim = job_sim . result ()
    counts = result_sim . get_counts ( compiled_circuit )
    probs = {key: value / n_shots for key, value in counts.items()}
    print(" Counts ", counts )
    print(" Probabilities :", probs )

num_size = 5
aux_size = num_size + 2 # +2 is needed for addition
classic_size = aux_size # | num_size

a = QuantumRegister(num_size,"a")
b = QuantumRegister(num_size,"b")
# c_in = QuantumRegister(1,"c_in") # needed to remove these for testing of addition
# c_out = QuantumRegister(1,"c_out")
r = QuantumRegister(num_size,"r")
aux = QuantumRegister(aux_size,"AUX")
c_bits = ClassicalRegister(classic_size)
circuit = QuantumCircuit(a,b,r,aux,c_bits)
set_bits(circuit, a, "111111")
set_bits(circuit, b, "001001")
# circuit.x(aux[0])
# full_adder(circuit,a,b,r,aux[0],aux[1],aux[2])
addition(circuit, a, b, r, aux)

##mesure if aux is empty
circuit.measure(aux, [*reversed(range(len(aux)))])
##mesure result
# for n, i in zip(reversed(range(r._size)), range(r._size)):
#     circuit.measure(r[i], n)
print(circuit)
basic_simulation(circuit)
# aer_simulation(circuit)
