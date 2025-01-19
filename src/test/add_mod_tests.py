#Nicole Nechita, rone8293
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
    circuit.cx(aux[-1], r)
    for i in reversed(range(len(a))):
        _p = 1+i
        circuit.ccx(a[i],b[i], aux[_p])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[_p-1],aux[_p])
        circuit.cx(a[i],b[i])
        circuit.barrier()
    circuit.x(b)
    circuit.x(aux[0])

def add_mod_second(circuit,n,a,b,r,aux):
    #shorten via variable
    aux_n_list=aux[1:len(a)+1]
    aux_r_list = aux[1+len(a):1+len(a)*2]
    aux_calculation_list = aux[1+len(a)*2:3+len(a)*3]
    aux_greater_list = aux[2+len(a)*2:3+len(a)*3]
    #addition
    addition(circuit,a,b,aux_r_list,aux_calculation_list)
    
    set_bits(circuit,aux_n_list,n)
    
    greater_than_or_equal(circuit,aux_r_list,aux_n_list,aux[0],aux_greater_list)
    controlled_subtraction(circuit,aux_r_list,aux_n_list,r,aux_calculation_list,aux[0])
    
    circuit.x(aux[0])
    for i in range(len(a)):
        circuit.ccx(aux[0],aux_r_list[i],r[i])
        
    circuit.x(aux[0])
    circuit.barrier()
    
    greater_than_or_equal(circuit,aux_r_list,aux_n_list,aux[0],aux_greater_list)
    set_bits(circuit,aux_n_list,n)
    addition(circuit,a,b,aux_r_list,aux_calculation_list)
    #print(circuit)


#controlled subtraction, which subtracts only if A+B is >= N
def controlled_subtraction(circuit, a, b, r, aux,control):
    circuit.cx(control,b)
    circuit.cx(control,aux[1])  
    
    for i in range(len(a)):
    
        _p = 1+i
        controlled_full_adder(circuit, a[i], b[i], r[i], aux[_p], aux[_p+1], aux[0],control)
    
    for i in reversed(range(len(a))):
        _p = 1+i
        circuit.mcx([control,a[i],b[i]], aux[_p+1])
        circuit.ccx(control,a[i],b[i])
        circuit.mcx([control,b[i],aux[_p]],aux[_p+1])
        circuit.ccx(control,a[i],b[i])
    circuit.cx(control,b)
    circuit.cx(control,aux[1])
    # circuit.barrier()

#a function made for only doing full adder if A+B is bigger or equal to N
def controlled_full_adder(circuit,a,b,r,c_in,c_out,aux,control):
    circuit.ccx(control,a,aux)
    circuit.ccx(control,b,aux)
    circuit.ccx(control,aux,r)
    circuit.ccx(control,c_in,r)

    circuit.mcx([control,a,b],c_out)
    circuit.ccx(control,a,b)
    circuit.mcx([control,b,c_in],c_out)
    circuit.ccx(control,a,b)
    
    circuit.ccx(control,b,aux)
    circuit.ccx(control,a,aux)

def test_mod_add(num_size,value_a,value_b,value_n,expected):

    a = QuantumRegister(num_size,"a")
    b = QuantumRegister(num_size,"b")
    r = QuantumRegister(num_size,"r")
    aux = QuantumRegister(num_size*3+3,"AUX")
    c_bits = ClassicalRegister(num_size)
    circuit = QuantumCircuit(a,b,r,aux,c_bits)
    set_bits(circuit, a, value_a)
    set_bits(circuit, b, value_b)
    add_mod_second(circuit, value_n, a,b, r, aux)
    print("Expected: "+expected)
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

test_mod_add(2,"00","00","00","00")
test_mod_add(2,"10","01","11","00")
test_mod_add(2,"01","01","11","10")
test_mod_add(2,"00","01","11","01")

test_mod_add(3,"000","000","001","000")
test_mod_add(3,"101","010","111","000")
test_mod_add(3,"010","010","110","100")
test_mod_add(3,"010","011","111","101")

test_mod_add(4,"0000","0000","0001","0000")
test_mod_add(4,"0001","0001","0010","0000")
test_mod_add(4,"0000","0001","0010","0001")
test_mod_add(4,"0001","0001","0011","0010")

test_mod_add(4,"0011","0011","0101","0001")
test_mod_add(4,"0110","0011","0111","0010")
test_mod_add(4,"0000","0001","0010","0001")
test_mod_add(4,"0000","0001","0010","0001")

test_mod_add(4,"0001","0101","1010","0110")
test_mod_add(4,"0110","0111","1011","0010")
test_mod_add(4,"0000","0001","0001","0000")

test_mod_add(4,"0000","0001","0011","0001")
test_mod_add(4,"1000","0111","1111","0000")
test_mod_add(4,"0100","0101","0111","0010")
test_mod_add(4,"0110","0111","1111","1101")