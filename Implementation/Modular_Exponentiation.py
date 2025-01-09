#Nicole Nechita, rone8293

from qiskit import QuantumCircuit,QuantumRegister, ClassicalRegister
from qiskit . providers . basic_provider import BasicSimulator

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
    circuit.cx(a,aux)
    circuit.cx(b,aux)
    circuit.barrier()

   #first bit is r, second is carry_out when measured
   #examplecounts 01 means r came out 0 and c_out is 1
    circuit.measure(r,1)
    circuit.measure(c_out,0)
    circuit.barrier()

def basic_simulation(circuit):
    
    backend = BasicSimulator ()
    n_shots = 1024 # Default number of shots is 1024
    result = backend . run ( circuit , shots = n_shots ) . result ()
    # Extract counts and probability distribution
    counts = result.get_counts()
    prob = { key : value / n_shots for key , value in counts . items () }
    print (" Counts : ", counts )
    print (" Probabilities : ", prob )

a = QuantumRegister(1,"a")
b = QuantumRegister(1,"b")
c_in = QuantumRegister(1,"c_in")
c_out = QuantumRegister(1,"c_out")
r = QuantumRegister(1,"r")
aux = QuantumRegister(1,"AUX")
c_bits = ClassicalRegister(2)
circuit = QuantumCircuit(a,b,c_in,r,c_out,aux,c_bits)
#circuit.x(a)
circuit.x(b)
circuit.x(c_in)
full_adder(circuit,a,b,r,c_in,c_out,aux)
print(circuit)
basic_simulation(circuit)
