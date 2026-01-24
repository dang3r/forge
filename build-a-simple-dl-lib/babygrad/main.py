import numpy as np
import torch

import babygrad.ops as ops
import babygrad.tensor as tensor


def test_autograd():
    vals = []
    for T in [tensor.Tensor, torch.tensor]:
        a = T(np.arange(4).astype("float32")).reshape((2, 2))
        b = T(np.arange(4).astype("float32")).reshape((2, 2)) + 1
        if T == torch.tensor:
            a.requires_grad = True
            b.requires_grad = True
        c = a @ b
        d = c.tanh()
        vars = [a, b]
        if T == torch.tensor:
            d.backward(torch.ones_like(d))
        else:
            d.backward()

        grads = [
            v.grad.detach().numpy()
            #            v.grad.numpy() if hasattr(v.grad, "numpy") else v.grad.detach().numpy()
            for v in vars
        ]
        vals.append(np.array(grads))

    assert np.allclose(vals[0], vals[1], rtol=1e-5, atol=1e-6)
    print("Autograd test passed!")


def main():
    test_autograd()


if __name__ == "__main__":
    main()
