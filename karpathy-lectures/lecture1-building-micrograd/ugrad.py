import numpy as np
from graphviz import Digraph
import sys

# Required for topolical sort when the number of neurons + inputs is large
sys.setrecursionlimit(10000)

# The MLP does not converge quickly during certain runs, because the model params
# constantly change. Fix the feed, so model convergence is determinstic
np.random.seed(13337)


class Value:
    """A class representing a node containing a single scalar value in a computational graph.

    Notes:
        - The gradients of a node accumulate over multiple calls to backward. This is useful
          if a node is used in multiple places in the graph.
        - The gradient is calculated using the chain rule. This means the downstream gradient AND
          the data of the current/sibling node may be used.
        - The _sorted_nodes list is only populated for the leaf node / final node in the graph.
          Doing a topo sort can be expensive, so we only do it once.


    Attributes:
        data (float): The value of the node.
        grad (float): The gradient of the node.
        label (str): The label of the node.
        op (str): The operation that generated the node. Can be unary or binary
        _backward (function): The function that computes the gradient of the node.
        _sorted_nodes (list): The list of nodes sorted in the graph topologically.
            Only populated when called on the leaf node.
    """

    def __init__(
        self,
        data,
        _children=(),
        op="",
        label=None,
    ):
        self.data = data
        self.grad = 0
        self.label = label
        self.op = op
        self.prev = set(_children)
        self._backward = lambda: None
        self._sorted_nodes = None

    def __add__(self, other):
        other = Value(other, op="const") if not isinstance(other, Value) else other
        new = Value(self.data + other.data, op="+", _children=(self, other))

        def _backward():
            self.grad += new.grad
            other.grad += new.grad

        new._backward = _backward

        return new

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return self.__sub__(other)

    def neg(self):
        return self * -1

    def __mul__(self, other):
        other = Value(other, op="const") if not isinstance(other, Value) else other
        new = Value(self.data * other.data, op="x", _children=(self, other))

        def _backward():
            self.grad += other.data * new.grad
            other.grad += self.data * new.grad

        new._backward = _backward

        return new

    def __pow__(self, other):
        out = Value(self.data**other, op="**", _children=(self,), label=f"**{other}")

        def _backward():
            self.grad += out.grad * (other * (self.data ** (other - 1)))

        out._backward = _backward
        return out

    def tanh(self):
        new = Value(np.tanh(self.data), op="tanh", _children=(self,))

        def _backward():
            self.grad += (1 - new.data**2) * new.grad

        new._backward = _backward

        return new

    def backward(self):
        # Compute the gradients from the leaf node back to the root
        # Assume that graph is a DAG with 1 component
        if not self._sorted_nodes:
            self._sorted_nodes = topological_sort(self)
        sorted_nodes = self._sorted_nodes
        self.grad = 1
        for node in reversed(sorted_nodes):
            node._backward()

    def __str__(self):
        return f"Value(label={self.label}, data={self.data}, grad={self.grad})"


def trace(root):
    # builds a set of all nodes and edges in a graph
    nodes, edges = set(), set()

    def build(v):
        if v not in nodes:
            nodes.add(v)
            for child in v.prev:
                edges.add((child, v))
                build(child)

    build(root)
    return nodes, edges


def draw_dot(root, fname="graph"):
    dot = Digraph(format="png", graph_attr={"rankdir": "LR"})  # LR = left to right

    nodes, edges = trace(root)
    for n in nodes:
        uid = str(id(n))
        # for any value in the graph, create a rectangular ('record') node for it
        dot.node(
            name=uid,
            label="{ %s | data %.4f | grad %.4f }" % (n.label, n.data, n.grad),
            shape="record",
        )
        if n.op:
            # if this value is a result of some operation, create an op node for it
            dot.node(name=uid + n.op, label=n.op)
            # and connect this node to it
            dot.edge(uid + n.op, uid)

    for n1, n2 in edges:
        # connect n1 to the op node of n2
        dot.edge(str(id(n1)), str(id(n2)) + n2.op)

    dot.render(fname, view=False, cleanup=True)
    return dot


def topological_sort(final_node):
    # sort nodes in topological order
    sorted_nodes = []
    visited = set()

    def visit(node):
        if node not in visited:
            visited.add(node)
            for child in node.prev:
                visit(child)
            sorted_nodes.append(node)

    visit(final_node)

    return sorted_nodes


a = Value(-0.5, label="a")
b = Value(0.6, label="b")
c = a * b
c.label = "c"
d = a * c
d.label = "d"
e = d * b
e.label = "e"
f = e.tanh()
f.label = "f"


f.backward()
draw_dot(f, "toy_graph")


def decreasing_graph():
    """Create a graph with decreasing number of nodes per layer.

    Each node in a given layer is the product of two adjacent nodes in the previous layer.

    a1 --> b1 --> c1
    a2 _/      /
       \__ b2 -
    a3 /
    """
    nodes = []
    for i in range(5):
        nodes.append([])
        for j in range(0, 5 - i):
            if i == 0:
                nodes[-1].append(
                    Value(float(np.random.uniform(-1.0, 1.0)), label=f"l{i}_n{j}")
                )
            else:
                new = nodes[-2][j] * nodes[-2][j + 1]
                new.label = f"l{i}_n{j}"
                nodes[-1].append(new)

    nodes[-1][-1].backward()
    return nodes


def layered_graph():
    """Create a graph where each neuron is the sum of all nodes in the previous layer"""
    nodes = []
    for i in range(5):
        nodes.append([])
        for j in range(5):
            if i == 0:
                nodes[-1].append(
                    Value(float(np.random.uniform(-1.0, 1.0)), label=f"l{i}_n{j}")
                )
            else:
                nodes[-1].append(sum(nodes[-2]))
                nodes[-1][-1].label = f"l{i}_n{j}"

    return nodes


class Neuron:
    """A neuron takes in a vector of inputs, multiples that by its weight vector of the same size,
    adds the bias and applies the activation function to the result.
    """

    def __init__(self, num_inputs):
        self.weights = [Value(np.random.uniform(-1.0, 1.0)) for _ in range(num_inputs)]
        self.bias = Value(np.random.uniform(-1.0, 1.0))

    def __call__(self, x):
        ret = sum([w * x for w, x in zip(self.weights, x)], self.bias)
        ret = ret.tanh()
        return ret

    def parameters(self):
        return [self.bias] + self.weights


class Layer:
    """A layer is composed of multiple neurons each receiving the same input vector"""

    def __init__(self, num_neurons, num_inputs):
        self.neurons = [Neuron(num_inputs) for _ in range(num_neurons)]

    def __call__(self, x):
        outs = [n(x) for n in self.neurons]
        return outs[0] if len(outs) == 1 else outs

    def parameters(self):
        return [p for n in self.neurons for p in n.parameters()]


class MLP:
    """A multi-layer perceptron is a sequence of layers, each layer receiving the output of the previous one."""

    def __init__(self, number_inputs, layer_sizes):
        sz = [number_inputs] + layer_sizes
        self.layers = [
            Layer(num_inputs=sz[i], num_neurons=sz[i + 1])
            for i in range(len(layer_sizes))
        ]

    def __call__(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]


nds = decreasing_graph()
draw_dot(nds[-1][-1], "decreasing_graph")

nds = layered_graph()
draw_dot(nds[-1][-1], "layered_graph")

# MODEL TRAINING
n = Neuron(10)
x = [Value(np.random.uniform(-0.5, 0.5)) for _ in range(10)]

m = MLP(1, [5, 4, 3, 1])

xs = [
    [2.0, 3.0, -1.0],
    [3.0, -1.0, 0.5],
    [0.5, 1.0, 1.0],
    [1.0, 1.0, -1.0],
]
ys = [1.0, -1.0, -1.0, 1.0]

xs = [[np.random.uniform(-0.5, 0.5)] for _ in range(100)]
ys = [x[0] * 0.1 for x in xs]

for it in range(200):
    ypreds = [m(x) for x in xs]
    loss = sum((ypred - y) ** 2 for ypred, y in zip(ypreds, ys))

    # zero grads before computing them
    for p in m.parameters():
        p.grad = 0
    loss.backward()

    # update parameters
    for p in m.parameters():
        p.data += -0.001 * p.grad

    print(it, loss.data)

for it in range(50):
    new_x = np.random.uniform(-0.5, 0.5)
    y_expected = new_x * 0.1
    y_pred = m([new_x])
    print(f"Input: {new_x}, Expected: {y_expected}, Predicted: {y_pred.data}")
