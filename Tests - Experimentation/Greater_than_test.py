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
    circuit.cx(a,aux)
    circuit.cx(b,aux)
    circuit.cx(aux,r)
    circuit.cx(c_in,r)

    circuit.ccx(a,b,c_out)
    circuit.cx(a,b)
    circuit.ccx(b,c_in,c_out)
    circuit.cx(a,b)

    circuit.cx(b,aux)
    circuit.cx(a,aux)

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

def test_comparison(a, b,expected):
    A = QuantumRegister(len(a),"a")
    B = QuantumRegister(len(a),"b")
    r = QuantumRegister(1,"r")
    AUX = QuantumRegister(len(a)+1,"AUX")
    c_bits = ClassicalRegister(1,"ctrl")
    circuit = QuantumCircuit(A,B,r,AUX,c_bits)
    circuit.barrier()

    set_bits(circuit,A,a)
    set_bits(circuit,B,b)
    greater_than_or_equal(circuit,A,B,r,AUX)
    circuit.barrier()
    circuit.measure(r,c_bits)
    print("in:" + a + " >= "+ b+" Expected: "+expected)
    aer_simulation(circuit)
    print()
        
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

test_comparison("0","1","0")
test_comparison("11","11","1")
test_comparison("101","110","0")
test_comparison("1010","1001","1")
test_comparison("1111","1111","1")
test_comparison("1111","1110","1")
test_comparison("1110","1111","0")
test_comparison("1111","0111","1")
test_comparison("0111","1111","0")
test_comparison("1010","0101","1")
test_comparison("0101","1011","0")
test_comparison("0011","0001","1")
test_comparison("0110","0110","1")
test_comparison("0000","1111","0")
test_comparison("1111","0000","1")
test_comparison("10100","10010","1")