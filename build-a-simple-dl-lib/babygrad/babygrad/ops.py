from typing import Optional, Tuple

import numpy as np

from .tensor import NDArray, Tensor


class Function:
    # Everything passed to a function must be a tensor
    def __call__(self, *inputs):
        requires_grad = any(input.requires_grad for input in inputs)
        input_d = [input.data for input in inputs]
        output_d = self.forward(*input_d)
        output_t = Tensor(output_d, requires_grad=requires_grad)
        if requires_grad:
            output_t._inputs = inputs
            output_t._op = self
        return output_t

    def forward(self, *args):
        pass

    def backward(self, out_grad, node):
        pass


class Add(Function):
    def forward(self, a: NDArray, b: NDArray):
        return a + b

    def backward(self, out_grad, node):
        # a+b
        # d/da = 1
        # d/db = 1
        return out_grad, out_grad


class Mul(Function):
    def forward(self, a: NDArray, b: NDArray):
        return a * b

    def backward(self, out_grad, node):
        a, b = node._inputs
        # ab
        # d/da = b
        # d/db = a
        return mul(out_grad, a), mul(out_grad, b)


class Sub(Function):
    def forward(self, a: NDArray, b: NDArray):
        return a - b

    def backward(self, out_grad, node):
        a, b = node._inputs
        # a-b
        # d/da = 1
        # d/db = -1
        return out_grad, neg(out_grad)


class Div(Function):
    def forward(self, a: NDArray, b: NDArray):
        return a / b

    def backward(self, out_grad, node):
        a, b = node._inputs
        # a/b
        # d/da = 1/b
        # d/db = -a/(b**2)
        return div(out_grad, b), mul(out_grad, div(neg(a), pow(b, 2)))


class Pow(Function):
    def forward(self, a: NDArray, b: int):
        return np.power(a, [b])

    def backward(self, out_grad, node):
        a, b = node._inputs
        # a**b
        # d/da = b*a**(b-1)
        # d/db = (a**b)*ln(a)
        grad_a = mul(b, pow(a, add_scalar(b, -1)))
        grad_b = mul(pow(a, b), log(a))
        return mul(out_grad, grad_a), mul(out_grad, grad_b)


class Transpose(Function):
    def __init__(self, axes: Optional[Tuple[int]] = None):
        self.axes = axes

    def forward(self, a: NDArray):
        # if no axes, we swap last two axis
        if self.axes is None:
            return np.swapaxes(a, -1, -2)

        # handle negative axis
        axes = tuple(ax if ax >= 0 else a.ndim + ax for ax in self.axes)
        if len(axes) == 2:
            # only swap the two axes in question
            all_axes = list(range(a.ndim))
            all_axes[axes[0]], all_axes[axes[1]] = all_axes[axes[1]], all_axes[axes[0]]
            axes = all_axes
        return np.transpose(a, all_axes)

    def backward(self, out_grad, node):
        a = node._inputs[0]
        if self.axes is None:
            ax1, ax2 = len(a.shape) - 2, len(a.shape) - 1
            return mul(
                out_grad,
                Transpose((ax1, ax2))(a),
            )
        axes = tuple(np.argsort(self.axes))
        return mul(out_grad, Transpose(axes)(a))


class Reshape(Function):
    def __init__(self, shape):
        self.shape = shape

    def forward(self, a: NDArray):
        return np.reshape(a, self.shape)

    def backward(self, out_grad, node):
        a = node._inputs[0]
        return Reshape(a.shape)(out_grad)


class BroadcastTo(Function):
    def __init__(self, shape: tuple):
        self.shape = shape

    def forward(self, a: NDArray):
        return np.broadcast_to(a, self.shape)

    def backward(self, out_grad, node):
        a = node._inputs[0]
        # prepended
        if len(out_grad.shape) > len(a.shape):
            while len(out_grad.shape) > len(a.shape):
                out_grad = Summation(axes=0)(out_grad)
        return reshape(out_grad, a.shape)


class Summation(Function):
    def __init__(self, axes: Optional[int] = None):
        self.axes = axes

    def forward(self, a: NDArray):
        if self.axes:
            return np.sum(a, axis=self.axes)
        return np.sum(a)

    def backward(self, out_grad, node):
        # d/da for every a in node._inputs[0] is 1
        # why?
        # d/da a+b+c+d+e+f = 1 foe any var
        a = node._inputs[0]
        if self.axes is None:
            return reshape(out_grad, a.shape)

        # expand the grad to the missing dimension
        og_shape = list(a.shape)
        og_shape[self.axes] = 1
        og_shape = tuple(og_shape)

        return broadcast_to(reshape(out_grad, og_shape), a.shape)


class MatMul(Function):
    def forward(self, a: NDArray, b: NDArray):
        return np.matmul(a, b)

    def backward(self, out_grad, node):
        a, b = node._inputs

        # to derive this, see how every cell in matrix a contributes to each grad cell
        grad_a = matmul(out_grad, transpose(b, (-1, -2)))
        grad_b = matmul(transpose(a, (-1, -2)), out_grad)

        # this is needed in case broadcasting happened. Each matrix cell gets its grad summed up
        while len(grad_a.shape) > len(a.shape):
            grad_a = Summation(0)(grad_a)
        while len(grad_b.shape) > len(b.shape):
            grad_b = Summation(0)(grad_b)

        # TODO: don't get this part
        grad_a = grad_a.reshape(a.shape)
        grad_b = grad_b.reshape(b.shape)
        return grad_a, grad_b


class Negate(Function):
    def forward(self, a: NDArray):
        return -a

    def backward(self, out_grad, node):
        # -a
        # d/da = -1
        return negate(out_grad)


class Log(Function):
    def forward(self, a: NDArray):
        return np.log(a)

    def backward(self, out_grad, node):
        a = node._inputs[0]
        # ln(a)
        # d/da = 1/a
        return div(out_grad, a)


class Exp(Function):
    def forward(self, a: NDArray):
        return np.exp(a)

    def backward(self, out_grad, node):
        a = node._inputs[0]
        # e**a
        # d/da =e**a
        return mul(out_grad, exp(a))


class Relu(Function):
    def forward(self, a: NDArray):
        return np.max(a, 0)

    def backward(self, out_grad, node):
        a = node._inputs[0]
        t = Tensor((a > 0))
        # relu(a)
        # 0 if less than 0 , 1 if greater than 0
        return mul(out_grad, t)


class Sigmoid(Function):
    def forward(self, a: NDArray):
        return np.exp(a) / (1 + np.exp(a))

    def backward(self, out_grad, node):
        a = node._inputs[0]
        g = add_scalar(negate(a), 1)
        # 1 + e**(-a)
        # d/da = 1 - sig(x)
        g = add_scalar(negate(a), 1)
        return mul(out_grad, g)


class Tanh(Function):
    def forward(self, a: NDArray):
        return np.tanh(a)

    def backward(self, out_grad, node):
        g = add_scalar(negate(pow_scalar(node, 2)), 1)
        return mul(out_grad, g)


class Sqrt(Function):
    def forward(self, a: NDArray):
        return np.sqrt(a)

    def backward(self, out_grad, node):
        # a**0.5
        # d/da = 1/2*a**-0.5
        return div(out_grad, mul_scalar(pow_scalar(node, -0.5), 2))


class Abs(Function):
    def forward(self, a: NDArray):
        return np.abs(a)

    def backward(self, out_grad, node):
        # d/da -1 if less than 0 and 1 if > 0
        a = node._inputs[0]
        t = Tensor(np.sign(a))
        return mul(out_grad, t)


class AddScalar(Function):
    def __init__(self, scalar):
        self.scalar = scalar

    def forward(self, a: NDArray):
        return a + self.scalar

    def backward(self, out_grad, node):
        # a + c
        # d/da = 1
        return out_grad


class MulScalar(Function):
    def __init__(self, scalar):
        self.scalar = scalar

    def forward(self, a: NDArray):
        return a * self.scalar

    def backward(self, out_grad, node):
        # ac
        # d/da = c
        return mul(out_grad, self.scalar)


class DivScalar(Function):
    def __init__(self, scalar):
        self.scalar = scalar

    def forward(self, a: NDArray):
        return a / self.scalar

    def backward(self, out_grad, node):
        # a/c
        # d/da =1/c
        return div_scalar(out_grad, self.scalar)


class PowScalar(Function):
    def __init__(self, scalar):
        self.scalar = scalar

    def forward(self, a: NDArray):
        return a**self.scalar

    def backward(self, out_grad, node):
        a = node._inputs[0]
        # a**c
        # d/da =c*a**(c-1)
        a_grad = mul_scalar(pow(a, self.scalar - 1), self.scalar)
        return mul(out_grad, a_grad)


def mul_scalar(a, b):
    return MulScalar(b)(a)


def add_scalar(a, b):
    return AddScalar(b)(a)


def pow_scalar(a, b):
    return PowScalar(b)(a)


def add(a, b):
    return Add()(a, b)


def mul(a, b):
    return Mul()(a, b)


def neg(a):
    return Negate()(a)


def sub(a, b):
    return Sub()(a, b)


def div(a, b):
    return Div()(a, b)


def pow(a, b):
    return Pow()(a, b)


def exp(a):
    return Exp()(a)


def log(a):
    return Log()(a)


def reshape(a, shape):
    return Reshape(shape)(a)


def abs(a):
    return Abs()(a)


def sqrt(a):
    return Sqrt()(a)


def transpose(a, axes=None):
    return Transpose(axes)(a)


def negate(a):
    return Negate()(a)


def div_scalar(a, scalar):
    return DivScalar(scalar)(a)


def broadcast_to(a, shape):
    return BroadcastTo(shape)(a)


def matmul(a, b):
    return MatMul()(a, b)
