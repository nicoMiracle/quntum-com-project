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
        # circuit.barrier()

def full_adder(circuit,a,b,r,c_in,c_out,aux):
    #a XOR b XOR c_in -> r
    #AUX is used to store a XOR b
    circuit.cx(a,aux)
    circuit.cx(b,aux)
    circuit.cx(aux,r)
    circuit.cx(c_in,r)
    # circuit.barrier()

    #do gates for carry_out
    circuit.ccx(a,b,c_out)
    circuit.cx(a,b)
    circuit.ccx(b,c_in,c_out)
    circuit.cx(a,b)
    # circuit.barrier()

    #reset AUX by doing the operation again
    
    circuit.cx(b,aux)
    circuit.cx(a,aux)
    # circuit.barrier()

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
        # circuit.barrier()
    # circuit.barrier()

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
    # circuit.barrier()
    addition(circuit, a, b, r, aux)

    circuit.x(b)
    circuit.x(aux[1])
    # circuit.barrier()




## made my own since i didnt want to mess with stuff i didnt know how it worked
# it calculates the comparison by calculating the carry out in a subtraction
def greater_than_or_equal(circuit,a,b,r,aux):
    circuit.x(b)
    circuit.x(aux[0])
    for i in reversed(range(len(a))):
        _p = len(a)-i
        circuit.ccx(a[i],b[i], aux[_p])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p-1],aux[_p])
        circuit.cx(a[i],b[i])
    circuit.cx(aux[len(a)], r)
    for i in range(len(a)):
        _p = len(a)-i
        circuit.ccx(a[i],b[i], aux[_p])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p-1],aux[_p])
        circuit.cx(a[i],b[i])
    circuit.x(b)
    circuit.x(aux[0])


##for use in circuit.append
def get_qbits(control_qbits, listoflist):
    for i in range(len(listoflist)):
        control_qbits.extend(listoflist[i])
    return control_qbits    
        
#modulo
# aux needs to be len(x)*2+3
def modulo(circuit, n, x, r, aux):
    qa = QuantumRegister(len(x), "sa")
    qb = QuantumRegister(len(x), "sb")
    qr = QuantumRegister(len(x), "sr")
    qaux = QuantumRegister(len(x)+2,"sAUX")
    qu = QuantumCircuit(qa,qb,qr,qaux)
    subtraction(qu, qa, qb, qr, qaux)
    sub_gate = qu.to_gate(None, "mysub").control(1)
    qca = QuantumRegister(len(x), "ca")
    qcb = QuantumRegister(len(x), "cb")
    qc = QuantumCircuit(qca,qcb)
    copy(qc, qca, qcb)
    copy_gate = qc.to_gate(None, "mycopy").control(1)
    qna = QuantumRegister(len(x), "ga")
    qnb = QuantumRegister(len(x), "gb")
    qnr = QuantumRegister(1, "gr")
    qnaux = QuantumRegister(len(x)+1,"gAUX")
    qnu = QuantumCircuit(qna,qnb,qnr,qnaux)
    greater_than_or_equal(qnu, qna, qnb, qnr, qnaux)
    comp_gate = qnu.to_gate(None, "mycomp")
    
    n_q = aux[1: len(x)+1]
    c_a = aux[len(x)+1: len(x)*2+2]
    m_a = aux[len(x)+1: len(x)*2+3]
    set_bits(circuit, n_q, n)
    circuit.append(comp_gate, get_qbits([], [x, n_q, [aux[0]], c_a]))
    circuit.append(sub_gate, get_qbits([aux[0]], [x, n_q, r, m_a]))
    circuit.x(aux[0])
    circuit.append(copy_gate, get_qbits([aux[0]], [x, r]))
    circuit.x(aux[0])
    circuit.append(comp_gate, get_qbits([], [x, n_q, [aux[0]], c_a]))
    set_bits(circuit, n_q, n)
    
## need len(a)*3+3
def add_mod(circuit, n, a, b, r, aux):
    qa = QuantumRegister(len(a), "A")
    qb = QuantumRegister(len(a), "B")
    qr = QuantumRegister(len(a), "R")
    qaux = QuantumRegister(len(a)+2,"AUX")
    qu = QuantumCircuit(qa,qb,qr,qaux)
    addition(qu, qa, qb, qr, qaux)
    add_gate = qu.to_gate(None, "myadd")
    
    a_r = aux[:len(a)]
    a_aux= aux[len(a):len(a)*2+2]
    m_aux = aux[len(a):len(a)*3+3]
    
    circuit.append(add_gate, get_qbits([], [a, b, a_r, a_aux]))
    modulo(circuit, n, a_r, r, m_aux)
    
    
## need len(a)*4+3
def double_mod(circuit, n, a, r, aux):
    b = aux[:len(a)]
    copy(circuit, a, b)
    a_aux = aux[len(a):]
    add_mod(circuit, n, a, b, r, a_aux)
    copy(circuit, a, b)
    
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
    n_shots = 10 # default number of shots .
    job_sim = backend.run(compiled_circuit, shots = n_shots)
    # Extract Results
    result_sim = job_sim . result ()
    counts = result_sim . get_counts ( compiled_circuit )
    probs = {key: value / n_shots for key, value in counts.items()}
    print(" Counts ", counts )
    print(" Probabilities :", probs )


num_size = 3
aux_size = num_size*4+3 # +2 is needed for addition
classic_size = num_size#aux_size # | num_size

a = QuantumRegister(num_size,"a")
b = QuantumRegister(num_size,"b")
r = QuantumRegister(num_size,"r")
aux = QuantumRegister(aux_size,"AUX")
c_bits = ClassicalRegister(classic_size)
circuit = QuantumCircuit(a,b,r,aux,c_bits)
set_bits(circuit, a, "011")
set_bits(circuit, b, "011")
double_mod(circuit, "100", a, r, aux)
##mesure if aux is empty
circuit.barrier()
# circuit.measure(aux, [*reversed(range(len(aux)))])
##mesure result
circuit.measure(r, [*reversed(range(len(r)))])
print(circuit)
# basic_simulation(circuit)
aer_simulation(circuit)
