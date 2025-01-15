from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister
from qiskit.providers.basic_provider import BasicSimulator

def set_bits(circuit, a, x):
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
# aux[0] will always be the first carry in of the addition
#
# TODO: need to make this circuit into one of those fancy compact ones
# otherwise we are gonna be scrolling for days when we do multiplication
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

def subtraction(circuit, a, b, r, aux):
    circuit.x(b)
    circuit.x(aux[0]) 
    circuit.barrier()
    addition(circuit, a, b, r, aux)
    circuit.x(b)
    circuit.x(aux[0])
    circuit.barrier()

def add_test(value_a, value_b, expected):
    size_num = len(expected)
    a = QuantumRegister(size_num,"a")
    b = QuantumRegister(size_num,"b")
    # c_in = QuantumRegister(1,"c_in") # needed to remove these for testing of addition
    # c_out = QuantumRegister(1,"c_out")
    r = QuantumRegister(size_num,"r")
    aux = QuantumRegister(size_num+3,"AUX")
    c_bits = ClassicalRegister(size_num)
    circuit = QuantumCircuit(a,b,r,aux,c_bits)
    set_bits(circuit, a, value_a)
    set_bits(circuit, b, value_b)
    addition(circuit, a, b, r, aux)

    for n, i in zip(reversed(range(r._size)), range(r._size)):
        circuit.measure(r[i], n)

    print("Expected: " + expected)
    basic_simulation(circuit)
    
def sub_test(value_a, value_b, expected):
    size_num = len(expected)
    a = QuantumRegister(size_num,"a")
    b = QuantumRegister(size_num,"b")
    # c_in = QuantumRegister(1,"c_in") # needed to remove these for testing of addition
    # c_out = QuantumRegister(1,"c_out")
    r = QuantumRegister(size_num,"r")
    aux = QuantumRegister(size_num+3,"AUX")
    c_bits = ClassicalRegister(size_num)
    circuit = QuantumCircuit(a,b,r,aux,c_bits)
    set_bits(circuit, a, value_a)
    set_bits(circuit, b, value_b)
    subtraction(circuit, a, b, r, aux)

    for n, i in zip(reversed(range(r._size)), range(r._size)):
        circuit.measure(r[i], n)

    print("Expected: " + expected)
    basic_simulation(circuit)
    
    
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
sub_test("0000", "0000", "0000")
sub_test("1111", "0001", "1110")
sub_test("0101", "0001", "0100")
sub_test("10001", "00001", "10000")
sub_test("11111", "11111", "00000")
sub_test("01111", "00001", "01110")
sub_test("10101", "10001", "00100")