import numpy as np
import torch

import babygrad.ops as ops
import babygrad.tensor as tensor


def test_autograd():
    vals = []
    ag = np.random.uniform(low=0.0, high=1.0, size=(17, 100)).astype("float32")
    bg = np.random.uniform(low=0.0, high=1.0, size=(100, 137)).astype("float32")
    cg = np.random.uniform(low=0.0, high=1.0, size=(17, 137)).astype("float32")
    dg = np.random.uniform(low=0.0, high=1.0, size=(137, 1)).astype("float32")
    for T in [tensor.Tensor, torch.tensor]:
        a = T(ag)
        b = T(bg)
        c = T(cg)
        d = T(dg)
        if T == torch.tensor:
            a.requires_grad = True
            b.requires_grad = True
            c.requires_grad = True
            d.requires_grad = True
        L = ((a @ b) + c) @ d
        vars = [a, b, c, d]
        if T == torch.tensor:
            L.backward(torch.ones_like(L))
        else:
            L.backward()
        grads = [v.grad.detach().numpy() for v in vars]
        vals.append(grads)

    for s1, s2 in zip(vals[0], vals[1]):
        print("Comparing", s1, s2)
        np.testing.assert_allclose(s1, s2, rtol=1e-3, atol=1e-3)
    print("Autograd test passed!")


def main():
    test_autograd()


if __name__ == "__main__":
    main()
