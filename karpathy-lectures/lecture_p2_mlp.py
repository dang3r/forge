import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import lecture02


def dataset():
    return open("names.txt").read().split()


def initialize(words, stoi, block_size: int = 4):
    def build_dataset(words):
        X, Y = [], []
        for word in words:
            context = [0] * block_size
            for ch in word + ".":
                ix = stoi[ch]
                X.append(context)
                Y.append(ix)
                context = context[1:] + [ix]
        X = torch.tensor(X)
        Y = torch.tensor(Y)
        return X, Y

    import random

    random.seed(42)
    random.shuffle(words)
    n1 = int(0.8 * len(words))
    n2 = int(0.9 * len(words))

    Xtr, Ytr = build_dataset(words[:n1])
    Xdev, Ydev = build_dataset(words[n1:n2])
    Xte, Yte = build_dataset(words[n2:])

    return ((Xtr, Ytr), (Xdev, Ydev), (Xte, Yte))


def lr_updater(iter, previous_lr) -> float:
    if iter < 100000:
        return 0.1
    elif iter < 150000:
        return 0.05
    return 0.01


def train(
    X,
    Y,
    vocab_size: int,
    batch_size: int = 32,
    iters: int = 200000,
    embedding_size: int = 20,
    w1_size: int = 200,
    random_seed: int = 2**31 - 1,
    lr_func: callable = lr_updater,
):
    view_size = embedding_size * X[0].shape[0]
    torch.Generator().manual_seed(random_seed)
    C = torch.randn((vocab_size, embedding_size))
    W1 = torch.randn((view_size, w1_size))
    b1 = torch.randn((w1_size,))
    W2 = torch.randn((w1_size, vocab_size))
    b2 = torch.randn((vocab_size))
    params = [C, W1, b1, W2, b2]
    for p in params:
        p.requires_grad = True

    lr = None

    print(view_size)
    losses = []
    for i in range(iters):
        ix = torch.randint(0, len(X), (batch_size,))
        emb = C[X[ix]]

        l1 = torch.tanh(emb.view(-1, view_size) @ W1 + b1)
        l2 = l1 @ W2 + b2

        for p in params:
            p.grad = None
        loss = F.cross_entropy(l2, Y[ix])
        print(f"iteration {i} loss={loss.item()}")
        loss.backward()
        lr = lr_func(i, lr)
        for p in params:
            p.data += -lr * p.grad
        losses.append(loss.item())
    return losses


def train_q2(
    X,
    Y,
    vocab_size: int,
    batch_size: int = 32,
    iters: int = 200000,
    embedding_size: int = 20,
    w1_size: int = 200,
    random_seed: int = 2**31 - 1,
    lr_func: callable = lr_updater,
):
    view_size = embedding_size * X[0].shape[0]
    torch.Generator().manual_seed(random_seed)
    C = torch.randn((vocab_size, embedding_size))
    W1 = torch.randn((view_size, w1_size))
    b1 = torch.randn((w1_size,))
    W2 = torch.randn((w1_size, vocab_size))
    b2 = torch.randn((vocab_size))
    params = [C, W1, b1, W2, b2]
    for p in params:
        p.fill_(0.1)
        p.requires_grad = True

    lr = None

    print(view_size)
    losses = []
    for i in range(iters):
        ix = torch.randint(0, len(X), (batch_size,))
        emb = C[X[ix]]

        l1 = torch.tanh(emb.view(-1, view_size) @ W1 + b1)
        l2 = l1 @ W2 + b2

        for p in params:
            p.grad = None
        loss = F.cross_entropy(l2, Y[ix])
        print(f"iteration {i} loss={loss.item()}")
        loss.backward()
        lr = lr_func(i, lr)
        for p in params:
            p.data += -lr * p.grad
        losses.append(loss.item())
    return losses


def main():
    words = dataset()
    chars = sorted(set("".join(words)))
    stoi = {s: i + 1 for i, s in enumerate(chars)}
    stoi["."] = 0
    itos = {i: s for s, i in stoi.items()}
    vocab_size = len(stoi)

    tr, dev, te = initialize(words, stoi, block_size=4)
    x, y = tr
    losses = train(x, y, vocab_size=vocab_size)
    print("Final loss", losses[-1])
    best_idx, min_loss = sorted(enumerate(losses), key=lambda x: x[1])[0]
    print(f"best loss  at {best_idx} was {min_loss}")


if __name__ == "__main__":
    main()
