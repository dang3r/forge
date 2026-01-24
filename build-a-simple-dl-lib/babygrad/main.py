import numpy as np
import torch

import babygrad.ops as ops
import babygrad.tensor as tensor


def test_autograd():
    T = tensor.Tensor
    a = T(np.arange(4)).reshape((2, 2))
    b = T(np.arange(4)).reshape((2, 2)) + 1
    c = a @ b
    d = c.tanh()
    print(a)
    print(b)
    print(c)
    a.requires_grad = True
    b.requires_grad = True
    c.requires_grad = True
    d.requires_grad = True
    d.backward()
    print(b.grad)
    print(a.grad)

    T = torch.Tensor
    a = T(np.arange(4)).reshape((2, 2))
    b = T(np.arange(4)).reshape((2, 2)) + 1
    a.requires_grad = True
    b.requires_grad = True
    c = a @ b
    d = c.tanh()
    print(a)
    print(b)
    print(c)
    d.backward(torch.ones_like(d))
    print(b.grad)
    print(a.grad)


def main():
    test_autograd()


if __name__ == "__main__":
    main()
