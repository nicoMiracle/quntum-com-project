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

   #first bit is r, second is carry_out when measured
   #examplecounts 01 means r came out 0 and c_out is 1
    # circuit.measure(r,1)
    # circuit.measure(c_out,0)
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
# aux: list of qubits with minimum size 4
def addition(circuit, a, b, r, aux):
    def carry_over(circuit, a, b, c_in, c_out):
        circuit.ccx(a,b, c_out)
        circuit.cx(a,b)
        circuit.ccx(b,c_in,c_out)
        circuit.cx(a,b)
        circuit.barrier()
    
    for i in reversed(range(len(a))):
        # adds the qubits at position i in a and b with switching c_in and c_out
        if i % 2 == 0:
            full_adder(circuit, a[i], b[i], r[i], aux[0], aux[1], aux[2])
        else:
            full_adder(circuit, a[i], b[i], r[i], aux[1], aux[0], aux[2])
        # makes the previous c_out (which is the current c_in)
        for n in range(len(a)-i):
            if n == 0:
                circuit.barrier()
            else:
                if n % 2 == 0:
                    c_in = aux[2]
                    c_out = aux[3]
                else:
                    c_in = aux[3]
                    c_out = aux[2]
                carry_over(circuit, a[n], b[n], c_in, c_out)
        # sets c_in to the previous c_out negating it an clearing the aux register qubit
        if i % 2 == 0:
            circuit.cx(aux[3], aux[0])
        else:
            circuit.cx(aux[2], aux[1])
        circuit.barrier()
        #reverse the makeing of the previous c_out clearing the used aux register qubits
        for n in reversed(range(len(a)-i)):
            if n == 0:
                circuit.barrier()
            else:
                if n % 2 == 0:
                    c_in = aux[2]
                    c_out = aux[3]
                else:
                    c_in = aux[3]
                    c_out = aux[2]
                carry_over(circuit, a[n], b[n], c_in, c_out)
    # clearing the last c_out by making the inverse carry over operations
    for i in range(len(a)):
        if i % 2 != 0:
            carry_over(circuit, a[i], b[i], aux[0], aux[1])
        else:
            carry_over(circuit, a[i], b[i], aux[1], aux[0])
    circuit.barrier()

# havent test so dont know if this works
def subtraction(circuit, a, b, r, aux):
    circuit.x(b)
    circuit.x(aux[0]) ## flips this to 1 cus aux[0] will always be the first c_out
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



size_num = 3

a = QuantumRegister(size_num,"a")
b = QuantumRegister(size_num,"b")
# c_in = QuantumRegister(1,"c_in") # needed to remove these for testing of addition
# c_out = QuantumRegister(1,"c_out")
r = QuantumRegister(size_num,"r")
aux = QuantumRegister(4,"AUX")
c_bits = ClassicalRegister(4)
circuit = QuantumCircuit(a,b,r,aux,c_bits)
set_bits(circuit, a, "111")
set_bits(circuit, b, "111")
# circuit.x(aux[0])
# full_adder(circuit,a,b,r,aux[0],aux[1],aux[2])
addition(circuit, a, b, r, aux)

##mesure if aux is empty

circuit.measure(aux, [3,2,1,0])
# for n, i in zip(reversed(range(r._size)), range(r._size)):
#     circuit.measure(r[i], n)
print(circuit)
basic_simulation(circuit)
