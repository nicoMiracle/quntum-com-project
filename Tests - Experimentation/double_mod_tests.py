#Nicole Nechita, rone8293
#Simon Nilsson sini3794
from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister
from qiskit . providers . basic_provider import BasicSimulator
from qiskit import transpile
from qiskit_aer import AerSimulator 


#the set_bits function 1.1
def set_bits(circuit, a, x):
    x = x[::-1]
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
    for i in range(len(a)):
        #initialise _p
        _p = 1+i
        full_adder(circuit, a[i], b[i], r[i], aux[_p], aux[_p+1], aux[0])
    
    #reset aux to 0
    for i in reversed(range(len(a))):
        _p = 1+i
        circuit.ccx(a[i],b[i], aux[_p+1])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p],aux[_p+1])
        circuit.cx(a[i],b[i])

## made my own since i didnt want to mess with stuff i didnt know how it worked
# it calculates the comparison by calculating the carry out in a subtraction
def greater_than_or_equal(circuit,a,b,r,aux):
    circuit.x(b)
    circuit.x(aux[0])
    for i in range(len(a)):
        _p = 1+i
        circuit.ccx(a[i],b[i], aux[_p])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p-1],aux[_p])
        circuit.cx(a[i],b[i])
        circuit.barrier()
    #last bit in the aux register
    circuit.cx(aux[len(a)], r)
    for i in reversed(range(len(a))):
        _p = 1+i
        circuit.ccx(a[i],b[i], aux[_p])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p-1],aux[_p])
        circuit.cx(a[i],b[i])
        circuit.barrier()
    circuit.x(b)
    circuit.x(aux[0])

def get_qbits(control_qbits, listoflist):
    for i in range(len(listoflist)):
        control_qbits.extend(listoflist[i])
    return control_qbits    

def subtraction(circuit, a, b, r, aux):
    circuit.x(b)
    circuit.x(aux[1])  
    addition(circuit, a, b, r, aux)

    circuit.x(b)
    circuit.x(aux[1])

## need aux len(a)*3+3
def times_two_mod(circuit, n, a, r, aux):
    qcs_a = QuantumRegister(len(a), "a")
    qcs_b = QuantumRegister(len(a), "b")
    qcs_r = QuantumRegister(len(a), "r")
    qcs_aux = QuantumRegister(len(a)+2,"aux")
    qcs = QuantumCircuit(qcs_a,qcs_b,qcs_r,qcs_aux)
    subtraction(qcs, qcs_a,qcs_b,qcs_r,qcs_aux)
    sub_gate = qcs.to_gate(None, "mysub").control(1)
    qcc_a = QuantumRegister(len(a), "a")
    qcc_b = QuantumRegister(len(a), "b")
    qcc = QuantumCircuit(qcc_a,qcc_b)
    copy(qcc, qcc_a, qcc_b)
    copy_gate = qcc.to_gate(None, "mycopy").control(1)
    
    add_r = aux[1:len(a)+1]
    extra_value = aux[1+len(a): len(a)*2+1]
    rest_aux= aux[1+len(a)*2:len(a)*3+3]
    
    copy(circuit, a, extra_value)
    addition(circuit, a, extra_value, add_r, rest_aux)
    copy(circuit, a, extra_value)
    
    set_bits(circuit, extra_value, n)
    greater_than_or_equal(circuit, add_r, extra_value, aux[0], rest_aux)
    circuit.append(sub_gate, get_qbits([aux[0]], [add_r, extra_value, r, rest_aux]))
    circuit.x(aux[0])
    circuit.append(copy_gate, get_qbits([aux[0]], [add_r, r]))
    circuit.x(aux[0])
    greater_than_or_equal(circuit, add_r, extra_value, aux[0], rest_aux)
    set_bits(circuit, extra_value, n)
    
    copy(circuit, a, extra_value)
    addition(circuit, a, extra_value, add_r, rest_aux)
    copy(circuit, a, extra_value)



def test_double_add(num_size,value_a,value_n,expected):

    a = QuantumRegister(num_size,"a")
    r = QuantumRegister(num_size,"r")
    aux = QuantumRegister(num_size*3+3,"AUX")
    c_bits = ClassicalRegister(num_size)
    circuit = QuantumCircuit(a,r,aux,c_bits)
    set_bits(circuit, a, value_a)
    times_two_mod(circuit, value_n, a, r, aux)
    print("in: "+value_a+"* 2 mod ( "+value_n+" ) Expected: "+expected)
    circuit.measure(r,c_bits)
    aer_simulation(circuit)

def aer_simulation(circuit):
    backend = AerSimulator()
    # Transpile the circuit to a set of gates
    # compatible with the backend
    compiled_circuit = transpile(circuit, backend )
    # Execute the circuit on the qasm simulator .
    n_shots = 3 # default number of shots .
    job_sim = backend.run(compiled_circuit, shots = n_shots)
    # Extract Results
    result_sim = job_sim . result ()
    counts = result_sim . get_counts ( compiled_circuit )
    probs = {key: value / n_shots for key, value in counts.items()}
    print(" Counts ", counts )
    print(" Probabilities :", probs )

test_double_add(2,"01","10","00")
test_double_add(3,"001","010","000")
test_double_add(3,"011","111","110")
test_double_add(4,"0000","0001","0000")
test_double_add(4,"0001","0010","0000")
test_double_add(4,"0001","0011","0010")
test_double_add(4,"0010","0011","0001")
test_double_add(4,"0001","0101","0010")
test_double_add(4,"0100","0101","0011")
test_double_add(4,"0100","0111","0001")
test_double_add(4,"0101","0111","0011")
test_double_add(4,"0110","0111","0101")
test_double_add(4,"0101","1011","1010")
test_double_add(4,"0101","1010","0000")