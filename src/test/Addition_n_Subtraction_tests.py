from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister
from qiskit.providers.basic_provider import BasicSimulator

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
        circuit.barrier()
    circuit.barrier()


#original code before revision
#def addition(circuit, a, b, r, aux):    
#    for i in reversed(range(len(a))):
#        _p = len(a)-i
#        full_adder(circuit, a[i], b[i], r[i], aux[_p], aux[_p+1], aux[0])
#    for i in range(len(a)):
#        _p = len(a)-i
#        circuit.ccx(a[i],b[i], aux[_p+1])
#        circuit.cx(a[i],b[i])
#        circuit.ccx(b[i],aux[_p],aux[_p+1])
#        circuit.cx(a[i],b[i])
#        circuit.barrier()
#    circuit.barrier()


def subtraction(circuit, a, b, r, aux):
    circuit.x(b)
    circuit.x(aux[1]) 
    circuit.barrier()
    addition(circuit, a, b, r, aux)
    circuit.x(b)
    circuit.x(aux[1])
    circuit.barrier()

def add_test(value_a, value_b, expected):
    size_num = len(expected)
    a = QuantumRegister(size_num,"a")
    b = QuantumRegister(size_num,"b")
    r = QuantumRegister(size_num,"r")
    aux = QuantumRegister(size_num+2,"AUX")
    c_bits = ClassicalRegister(size_num)
    circuit = QuantumCircuit(a,b,r,aux,c_bits)
    set_bits(circuit, a, value_a)
    set_bits(circuit, b, value_b)
    addition(circuit, a, b, r, aux)

    #for n, i in zip(reversed(range(r._size)), range(r._size)):
        #circuit.measure(r[i], n)
    circuit.measure(r,c_bits)
    print("in: "+ value_a +" + "+ value_b +" Expected: " + expected)
    basic_simulation(circuit)
    print()
    
def sub_test(value_a, value_b, expected):
    size_num = len(expected)
    a = QuantumRegister(size_num,"a")
    b = QuantumRegister(size_num,"b")
    r = QuantumRegister(size_num,"r")
    aux = QuantumRegister(size_num+2,"AUX")
    c_bits = ClassicalRegister(size_num)
    circuit = QuantumCircuit(a,b,r,aux,c_bits)
    set_bits(circuit, a, value_a)
    set_bits(circuit, b, value_b)
    subtraction(circuit, a, b, r, aux)

    #for n, i in zip(reversed(range(r._size)), range(r._size)):
        #circuit.measure(r[i], n)
    circuit.measure(r,c_bits)
    print("in: "+ value_a +" - "+ value_b +" Expected: " + expected)
    basic_simulation(circuit)
    print()
    
    
def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 10 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Probabilities : ", prob )


    

print("Addition tests:")
add_test("0001", "0001", "0010")
add_test("0000", "0000", "0000")
add_test("0001", "1111", "0000")
add_test("0101", "0001", "0110")

add_test("10001", "00001", "10010")
add_test("11111", "11111", "11110")
add_test("00001", "11111", "00000")
add_test("00101", "00001", "00110")

print("Subtraction tests:")
sub_test("0001", "0001", "0000")
sub_test("0011", "0010", "0001")
sub_test("0000", "0000", "0000")
sub_test("1111", "0001", "1110")
sub_test("0101", "0001", "0100")
sub_test("10101", "00101", "10000")
sub_test("11111", "11111", "00000")
sub_test("01111", "00011", "01100")
sub_test("10101", "10001", "00100")