#Nicole Nechita, rone8293

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
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

def full_adder(circuit,a,b,r,c_in,c_out,aux):
    #a XOR b XOR c_in -> r
    #AUX is used to store a XOR b
    circuit.cx(a,aux)
    circuit.cx(b,aux)
    circuit.cx(aux,r)
    circuit.cx(c_in,r)

    #do gates for carry_out
    circuit.ccx(a,b,c_out)
    circuit.cx(a,b)
    circuit.ccx(b,c_in,c_out)
    circuit.cx(a,b)

    #reset AUX by doing the operation again
    circuit.cx(b,aux)
    circuit.cx(a,aux)

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
    #do the calculation  
    for i in range(len(a)):
        _p = 1+i
        full_adder(circuit, a[i], b[i], r[i], aux[i+1], aux[i+2], aux[0])
    # reset aux
    for i in reversed(range(len(a))):
        circuit.ccx(a[i],b[i], aux[i+2])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[i+1],aux[i+2])
        circuit.cx(a[i],b[i])

# subtraction
# subtract a with b
# prams:
# circuit: QuantumCircuit
# a: list of qubit in size n
# b: list of qubit in size n
# r: list of qubit in size n
# aux: list of qubits with minimum size of n+2
def subtraction(circuit, a, b, r, aux):
    # flip b and set first carry_in to 1
    circuit.x(b)
    circuit.x(aux[1])
    # do addition
    addition(circuit, a, b, r, aux)
    # rest aux
    circuit.x(b)
    circuit.x(aux[1])

# it calculates the comparison by calculating the carry out in a subtraction
def greater_than_or_equal(circuit,a,b,r,aux):
    # flip b and set first carry_in to 1
    circuit.x(b)
    circuit.x(aux[0])
    # claculate the carry_out
    for i in range(len(a)):
        circuit.ccx(a[i],b[i], aux[i+1])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[i],aux[i+1])
        circuit.cx(a[i],b[i])
        circuit.barrier()
    # places the last carry_out into r
    circuit.cx(aux[len(a)], r)
    # reset aux
    for i in reversed(range(len(a))):
        circuit.ccx(a[i],b[i], aux[i+1])
        circuit.cx(a[i],b[i])
        circuit.ccx(b[i],aux[i],aux[i+1])
        circuit.cx(a[i],b[i])
        circuit.barrier()
    circuit.x(b)
    circuit.x(aux[0])


##for use in circuit.append
def get_qbits(control_qbits, listoflist):
    for i in range(len(listoflist)):
        control_qbits.extend(listoflist[i])
    return control_qbits

## need aux len(a)*3+3
def add_mod(circuit, n, a, b, r, aux):
    #make controled gates
    qcs_a = QuantumRegister(len(a), "a")
    qcs_b = QuantumRegister(len(a), "b")
    qcs_r = QuantumRegister(len(a), "r")
    qcs_aux = QuantumRegister(len(a)+2,"aux")
    qcs = QuantumCircuit(qcs_a,qcs_b,qcs_r,qcs_aux)
    subtraction(qcs, qcs_a,qcs_b,qcs_r,qcs_aux)
    sub_gate = qcs.to_gate(None, "mysub").control(1)
    qcc_a = QuantumRegister(len(a), "a")
    qcc_b = QuantumRegister(len(a), "b")
    qc = QuantumCircuit(qcc_a,qcc_b)
    copy(qc, qcc_a, qcc_b)
    copy_gate = qc.to_gate(None, "mycopy").control(1)
    
    #split aux
    add_r = aux[1:len(a)+1]
    n_qbits = aux[1+len(a): len(a)*2+1]
    rest_aux= aux[1+len(a)*2:len(a)*3+3]
    
    #claculate the addition
    addition(circuit, a, b, add_r, rest_aux)
    
    #modulo
    set_bits(circuit, n_qbits, n)
    greater_than_or_equal(circuit, add_r, n_qbits, aux[0], rest_aux)
    # do subtraction if add_r is grater then n
    circuit.append(sub_gate, get_qbits([aux[0]], [add_r, n_qbits, r, rest_aux]))
    # copy add_r into r if add_r is lees than n 
    circuit.x(aux[0])
    circuit.append(copy_gate, get_qbits([aux[0]], [add_r, r]))
    circuit.x(aux[0])
    # reset aux
    greater_than_or_equal(circuit, add_r, n_qbits, aux[0], rest_aux)
    set_bits(circuit, n_qbits, n)
    addition(circuit, a, b, add_r, rest_aux)
    
## need aux len(a)*3+3
def times_two_mod(circuit, n, a, r, aux):
    # make controled gates
    qcs_a = QuantumRegister(len(a), "a")
    qcs_b = QuantumRegister(len(a), "b")
    qcs_r = QuantumRegister(len(a), "r")
    qcs_aux = QuantumRegister(len(a)+2,"aux")
    qcs = QuantumCircuit(qcs_a,qcs_b,qcs_r,qcs_aux)
    subtraction(qcs, qcs_a,qcs_b,qcs_r,qcs_aux)
    sub_gate = qcs.to_gate(None, "mysub").control(1)
    qcc_a = QuantumRegister(len(a), "a")
    qcc_b = QuantumRegister(len(a), "b")
    qc = QuantumCircuit(qcc_a,qcc_b)
    copy(qc, qcc_a, qcc_b)
    copy_gate = qc.to_gate(None, "mycopy").control(1)
    
    # split aux
    add_r = aux[1:len(a)+1]
    extra_value = aux[1+len(a): len(a)*2+1]
    rest_aux= aux[1+len(a)*2:len(a)*3+3]
    
    # claculate the result of a * 2
    copy(circuit, a, extra_value)
    addition(circuit, a, extra_value, add_r, rest_aux)
    copy(circuit, a, extra_value)
    
    # modulo clauculation
    set_bits(circuit, extra_value, n)
    greater_than_or_equal(circuit, add_r, extra_value, aux[0], rest_aux)
    # do subtraction if add_r is grater then n
    circuit.append(sub_gate, get_qbits([aux[0]], [add_r, extra_value, r, rest_aux]))
    # copy add_r into r if add_r is lees than n 
    circuit.x(aux[0])
    circuit.append(copy_gate, get_qbits([aux[0]], [add_r, r]))
    circuit.x(aux[0])
    # reset aux
    greater_than_or_equal(circuit, add_r, extra_value, aux[0], rest_aux)
    set_bits(circuit, extra_value, n)    
    copy(circuit, a, extra_value)
    addition(circuit, a, extra_value, add_r, rest_aux)
    copy(circuit, a, extra_value)
    
##################################################################
#                           Simulation
##################################################################

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


num_size = 3
aux_size = num_size*3+3 # amount needed for times_two_mod
classic_size = num_size

a = QuantumRegister(num_size,"a")
# b = QuantumRegister(num_size,"b")
r = QuantumRegister(num_size,"r")
aux = QuantumRegister(aux_size,"AUX")
c_bits = ClassicalRegister(classic_size)
circuit = QuantumCircuit(a,r,aux,c_bits)

set_bits(circuit, a, "011")
# set_bits(circuit, b, "011")
times_two_mod(circuit, "100", a, r, aux)
circuit.barrier()
circuit.measure(r,c_bits)

print(circuit)
aer_simulation(circuit)


