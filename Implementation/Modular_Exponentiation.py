#Nicole Nechita, rone8293

from qiskit import QuantumCircuit

#the copy function 1.2
def copy(circuit, A, B):
    amount_registers = len(A)
    for i in range(amount_registers):
        circuit.cx(A[i],B[i])
        circuit.barrier()

#a simple try of the copy function 1.2 
def copy_experiment():
    A = [0,1,2,3]
    B = [4,5,6,7]
    circuit = QuantumCircuit(len(A)+len(B),0)
    circuit.x(0)
    circuit.x(2)
    circuit.x(3)
    circuit.barrier()
    copy(circuit,A,B)

    print(circuit)

copy_experiment()