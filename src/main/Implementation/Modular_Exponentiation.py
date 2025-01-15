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
# TODO: need to make this circuit into one of those fancy compact one 
# otherwise we are gonna be scrolling for days whe we do multiplication
#
# prams:
# circuit: QuantumCircuit
# a: list of qubit in size n
# b: list of qubit in size n
# r: list of qubit in size n
# aux: list of qubits with minimum size n + 3



def addition(circuit, a, b, r, aux):
    def carry_over(circuit, a, b, c_in, c_out):
        circuit.ccx(a,b, c_out)
        circuit.cx(a,b)
        circuit.ccx(b,c_in,c_out)
        circuit.cx(a,b)
        circuit.barrier()
    
    # copies the first c_in in aux[3] and switched first c_in to aux[1] if nececary
    circuit.cx(aux[0], aux[3])
    if len(a) % 2 == 0:
        circuit.cx(aux[0], aux[1])
        circuit.cx(aux[1], aux[0])
    circuit.barrier()
    
    for i in reversed(range(len(a))):
        # adds the qubits at position i in a and b with switching c_in and c_out
        
        if i % 2 == 0:
            carry_in = aux[0] 
            carry_out = aux[1]
        else:
            carry_in = aux[1] 
            carry_out = aux[0]
            
        # circuit.append(qc, [a[i], b[i], r[i], carry_in, carry_out, aux[2]])
        full_adder(circuit, a[i], b[i], r[i], carry_in, carry_out, aux[2])
        # makes the previous c_out (which is the current c_in)
        switch_out = None
        for n, ax in zip(reversed(range(len(a)-i)), range(len(a)-i)):
            # circuit.barrier()
            if n == 0:
                circuit.barrier()
            else:
                c_in = aux[ax+3]
                c_out = aux[ax+4]
                carry_over(circuit, a[i+n], b[i+n], c_in, c_out)
                switch_out = c_out
        # sets c_in to the previous c_out negating it an clearing the aux register qubit
        if switch_out != None:
            circuit.cx(switch_out, carry_in)
        circuit.barrier()
        #reverse the makeing of the previous c_out clearing the used aux register qubits
        for ax, n in zip(reversed(range(len(a)-i)), range(len(a)-i)):
            if n == 0:
                circuit.barrier()
            else:
                c_in = aux[ax+3]
                c_out = aux[ax+4]
                carry_over(circuit, a[i+n], b[i+n], c_in, c_out)
    # clearing the last c_out by making the inverse carry over operations
    switch = None
    for i, ax in zip(reversed(range(len(a)-1)), range(len(a)-1)):
        carry_over(circuit, a[i+1], b[i+1], aux[ax+3], aux[ax+4])
        switch = aux[ax+4]
    if switch != None:
        circuit.cx(switch,carry_out)
    circuit.barrier()
    for ax, i in zip(reversed(range(len(a)-1)), range(len(a)-1)):
        carry_over(circuit, a[i+1], b[i+1], aux[ax+3], aux[ax+4])
        switch = aux[ax+4]
    circuit.barrier()
    # resets the aux for c_in
    if len(a) % 2 == 0:
        circuit.cx(aux[0], aux[1])
        circuit.cx(aux[1], aux[0])
    circuit.cx(aux[0], aux[3])
    circuit.barrier()

# havent test so dont know if this works
def subtraction(circuit, a, b, r, aux):
    circuit.x(b)
    circuit.x(aux[0]) ## need to check %2 for 
    circuit.barrier()
    addition(circuit, a, b, r, aux)
    circuit.x(b)
    circuit.x(aux[0])
    circuit.barrier()

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
    
def aer_simulation(circuit):
    # Import the transpile module
    from qiskit import transpile
    # Define the backend AerSimulator
    from qiskit_aer import AerSimulator
    backend = AerSimulator ()
    # Transpile the circuit to a set of gates
    # compatible with the backend
    compiled_circuit = transpile ( circuit , backend )
    # Execute the circuit on the qasm simulator .
    n_shots = 1024 # default number of shots .
    job_sim = backend . run ( compiled_circuit , shots = n_shots )
    # Extract Results
    result_sim = job_sim . result ()
    counts = result_sim . get_counts ( compiled_circuit )
    probs = { key : value / n_shots for key , value in counts . items () }
    print (" Counts ", counts )
    print (" Probabilities :", probs )



size_num = 5

a = QuantumRegister(size_num,"a")
b = QuantumRegister(size_num,"b")
# c_in = QuantumRegister(1,"c_in") # needed to remove these for testing of addition
# c_out = QuantumRegister(1,"c_out")
r = QuantumRegister(size_num,"r")
aux = QuantumRegister(8,"AUX")
c_bits = ClassicalRegister(8)
circuit = QuantumCircuit(a,b,r,aux,c_bits)
set_bits(circuit, a, "111111")
set_bits(circuit, b, "001001")
# circuit.x(aux[0])
# full_adder(circuit,a,b,r,aux[0],aux[1],aux[2])
addition(circuit, a, b, r, aux)

##mesure if aux is empty

circuit.measure(aux, [7,6,5,4,3,2,1,0])
# for n, i in zip(reversed(range(r._size)), range(r._size)):
#     circuit.measure(r[i], n)
print(circuit)
basic_simulation(circuit)
# aer_simulation(circuit)
