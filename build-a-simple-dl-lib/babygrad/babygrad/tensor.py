from typing import List

import numpy as np

NDArray = np.ndarray


def tensorify(a):
    if not isinstance(a, Tensor):
        return Tensor(a)
    return a


def tensor_decorator(func):
    def internal(self, *args):
        return func(self, *[tensorify(arg) for arg in args])

    return internal


class Tensor:
    def __init__(
        self, data, *, device=None, dtype="float32", requires_grad: bool = True
    ):
        self._op = None
        self._inputs = []
        self._device = device
        self.requires_grad = requires_grad
        self.grad = None
        # Make a copy instead of passing by reference
        if isinstance(data, Tensor):
            self.data = np.array(data.data, dtype=dtype)
        elif isinstance(data, NDArray):
            self.data = np.array(data, dtype=dtype)
        elif isinstance(data, List):
            self.data = np.array(data, dtype=dtype)
        elif np.isscalar(data):
            self.data = np.array([data], dtype=dtype)

    def __repr__(self):
        return f"Tensor({self.data}, requires_grad={self.requires_grad})"

    def __str__(self):
        return str(self.data)

    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        self.data.dtype

    @property
    def ndim(self):
        self.data.ndim

    @property
    def size(self):
        return self.data.size

    @property
    def device(self):
        return self._device

    def numpy(self):
        return self.data.copy()

    def detach(self):
        return Tensor(self.data, requires_grad=False)

    @tensor_decorator
    def __add__(self, b):
        from .ops import Add

        return Add()(self, b)

    def __radd__(self, b):
        return self.__add__(b)

    @tensor_decorator
    def __mul__(self, b):
        from .ops import Mul

        return Mul()(self, b)

    def __rmul__(self, b):
        return self.__mul__(b)

    @tensor_decorator
    def __pow__(self, b):
        from .ops import Pow

        return Pow()(self, b)

    @tensor_decorator
    def __sub__(self, b):
        from .ops import Sub

        return Sub()(self, b)

    @tensor_decorator
    def __rsub__(self, b):
        from .ops import Sub

        return Sub()(b, self)

    @tensor_decorator
    def __truediv__(self, b):
        from .ops import Div

        return Div()(self, b)

    @tensor_decorator
    def __rtruediv__(self, b):
        from .ops import Div

        return Div()(b, self)

    @tensor_decorator
    def __matmul__(self, b):
        from .ops import MatMul

        return MatMul()(self, b)

    @tensor_decorator
    def matmul(self, b):
        return self.__matmul__(b)

    @tensor_decorator
    def sum(self, axes):
        from .ops import Summation

        return Summation(axes)(self)

    @tensor_decorator
    def broadcast_to(self, shape):
        from .ops import BroadcastTo

        return BroadcastTo()(self, shape)

    def reshape(self, shape):
        from .ops import Reshape

        return Reshape(shape)(self)

    def __neg__(self):
        from .ops import Negate

        return Negate()(self)

    def transpose(self, axes):
        from .ops import Transpose

        return Transpose(axes)(self)

    def tanh(self):
        from .ops import Tanh

        return Tanh()(self)

    def backward(self, grad=None):
        print("Initializing bw pass...")
        topo_order = []
        visited = set()

        def build_topo(node):
            if node in visited:
                return
            visited.add(id(node))
            for n in node._inputs:
                build_topo(n)
            print("ADDING", node)
            topo_order.append(node)

        build_topo(self)

        # the terminal node will always have dL/dL = 1
        if grad is None:
            self.grad = Tensor(np.ones(shape=self.data.shape))
        for node in reversed(topo_order):
            if node._op:
                parent_grads = node._op.backward(node.grad, node)
                if not isinstance(parent_grads, tuple):
                    parent_grads = (parent_grads,)
                assert len(parent_grads) == len(node._inputs)
                for parent, parent_grad in zip(node._inputs, parent_grads):
                    if parent.requires_grad:
                        if parent.grad is None:
                            parent.grad = Tensor(np.zeros_like(parent.data))
                        parent.grad += parent_grad
