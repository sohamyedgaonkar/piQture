import matplotlib.pyplot as plt
from qiskit.circuit import QuantumCircuit, ParameterVector
from quantum_image_processing.data_loader.mnist_data_loader import load_mnist_data


class TTN:
    """
    Implements a Tree Tensor Network (TTN) as given by
    Grant et al. (2018).

    The model architecture only consists of a hierarchical
    TTN model. It cannot be classified as a QCNN since
    there is no distinction between conv and pooling layers.
    """

    def __init__(self, img_dim):
        self.img_dim = img_dim
        self.param_vector = ParameterVector('theta', 2 * self.img_dim - 1)
        self.param_vector_copy = self.param_vector

    def _apply_simple_block(self, qubits):
        block = QuantumCircuit(self.img_dim)
        block.ry(self.param_vector_copy[0], qubits[0])
        block.ry(self.param_vector_copy[1], qubits[1])
        block.cx(qubits[0], qubits[1])
        self.param_vector_copy = self.param_vector_copy[2:]

        return block

    def ttn_simple(self, complex_struct=True):
        """
        Rotations here can be either real or complex.

        For real rotations only RY gates are used since
        the gate has no complex rotations involved.
        For complex rotations, a combination of RZ and RY
        gates are used.

        I HAVE NO IDEA WHY I CHOSE THESE. THE SELECTION
        OF UNITARY GATES IS COMPLETELY VOLUNTARY.

        PennyLane implements a TTN template with only RX gates.

        :return:
        """
        ttn_circ = QuantumCircuit(self.img_dim, 1)

        if complex_struct:
            pass
        else:
            qubit_list = []
            for qubits in range(0, self.img_dim, 2):
                if qubits == self.img_dim - 1:
                    qubit_list.append(qubits)
                else:
                    qubit_list.append(qubits + 1)
                    block = self._apply_simple_block(qubits=[qubits, qubits + 1])
                    ttn_circ.append(block, range(self.img_dim))

            for index, _ in enumerate(qubit_list[:-1]):
                block = self._apply_simple_block(qubits=[qubit_list[index], qubit_list[index + 1]])
                ttn_circ.append(block, range(self.img_dim))

            ttn_circ.ry(self.param_vector_copy[0], qubit_list[-1])
            ttn_circ.measure(qubit_list[-1], [0])

        return ttn_circ

    def ttn_general(self):
        pass

    def ttn_with_aux(self):
        pass


def data_embedding():
    """
    Embeds data using Qubit/Angle encoding for a
    single feature.
    Does not use QIR techniques.
    Complexity: O(1); requires 1 qubit for 1 feature.
    :return:
    """
    train, test = load_mnist_data()
    train_data = iter(train)
    train_img, train_labels = next(train_data)

    print(train_img.shape, train_labels.shape)

    flatten_img_dim = train_img[0].reshape(-1, 4)
    params_list = flatten_img_dim.tolist()[0]
    print(params_list)

    embedding = QuantumCircuit(4, 1)

    for i in range(4):
        embedding.ry(params_list[i], i)

    return embedding


if __name__ == "__main__":
    circ = data_embedding()
    circ.barrier()
    ttn = TTN(img_dim=4).ttn_simple(complex_struct=False)
    circ.append(ttn, range(4), range(1))    # For some reason .compose() doesn't work in this file.
    circ.decompose().decompose().draw("mpl")
    plt.show()
