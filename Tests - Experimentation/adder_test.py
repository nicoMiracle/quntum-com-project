#Nicole Nechita, rone8293
#Simon Nilsson sini3794
from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister
from qiskit . providers . basic_provider import BasicSimulator

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
    
def add_test(value_a, value_b, value_c_in, expected):
    a = QuantumRegister(1,"a")
    b = QuantumRegister(1,"b")
    c_in = QuantumRegister(1,"c_in") # needed to remove these for testing of addition
    c_out = QuantumRegister(1,"c_out")
    r = QuantumRegister(1,"r")
    aux = QuantumRegister(1,"AUX")
    c_bits = ClassicalRegister(2)
    circuit = QuantumCircuit(a,b,r,c_in,c_out,aux,c_bits)
    set_bits(circuit, a, value_a)
    set_bits(circuit, b, value_b)
    set_bits(circuit,c_in,value_c_in)
    full_adder(circuit, a, b, r, c_in, c_out, aux)
    circuit.measure(r,1)
    circuit.measure(c_out,0)

    print("Expected: " + expected)
    basic_simulation(circuit)
    print()
    
    
def basic_simulation(circuit):
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts.items() }
    print (" Probabilities : ", prob )
print("full_adder test: " )
print("OBS: First digit is sum, second is carry_out.") 
add_test("0", "0","0", "00")
add_test("1", "1","0", "01")
add_test("1", "0","0", "10")
add_test("0", "1","0", "10")
add_test("1","1","1","11")