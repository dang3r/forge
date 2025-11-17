from typing import List, Generator

import pandas as pd
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import matplotlib as mpl
import string
from itertools import product


def chunk(word: str, size: int) -> Generator:
    for i in range(0, len(word) - size + 1):
        x = word[i : i + size - 1]
        y = word[i + size - 1]
        yield x, y


class NGramModel:
    def __init__(self, size: int, special_char: str = "."):
        self.size = size
        self.special_char = special_char
        self.lbl = "".join([self.special_char] * (self.size - 1))
        self.stoi = None
        self.itos = None
        self.N = None

    def encode(self, text: str) -> int:
        return self.stoi[text]

    def decode(self, i: int) -> str:
        return self.itos[i]

    def corpus(self, words):
        chars = set("".join(words))
        chars.add(self.special_char)
        x_terms = sorted(set(list(product(chars, repeat=self.size - 1))))
        x_terms = ["".join(x_term) for x_term in x_terms]
        y_terms = sorted(chars)
        terms = x_terms + y_terms
        all_dim = len(x_terms) + len(y_terms)
        itos = {idx: s for idx, s in enumerate(terms)}
        stoi = {s: idx for idx, s in itos.items()}
        return x_terms, y_terms, all_dim, itos, stoi

    def train(self, words: List[str], print_graph: bool = False):
        x_terms, y_terms, all_dim, itos, stoi = self.corpus(words)
        x_dim = len(x_terms)
        y_dim = len(y_terms)

        # build frequency mapping
        ngram_to_count = dict()
        for word in words:
            word = self.lbl + word + self.lbl
            for x, y in chunk(word, self.size):
                ngram_to_count[(x, y)] = ngram_to_count.get((x, y), 0) + 1

        N = torch.zeros((all_dim, all_dim))
        for (x, y), count in ngram_to_count.items():
            N[stoi[x], stoi[y]] = count
        self.N = N
        self.itos = itos
        self.stoi = stoi

        if print_graph:
            itox = {idx: s for idx, s in enumerate(x_terms)}
            itoy = {idx: s for idx, s in enumerate(y_terms)}

            mpl.rcParams["font.size"] = 4
            scale = 1
            fig, ax = plt.subplots(figsize=(y_dim * scale, x_dim * scale))
            A = N[:y_dim, x_dim:]
            ax.imshow(A, cmap="Blues")
            for i in range(x_dim):
                for j in range(y_dim):
                    chstr = itox[i] + itoy[j]
                    _x = stoi[itox[i]]
                    _y = stoi[itoy[j]]
                    plt.text(j, i, chstr, ha="center", va="bottom", color="gray")
                    plt.text(
                        j, i, N[_x, _y].item(), ha="center", va="top", color="gray"
                    )
            ax.axis("off")
            fig.tight_layout(pad=0)
            fig.savefig("figure.png", dpi=300)

    def sample(self, number_samples: int = 10) -> str:
        g = torch.Generator()
        P = self.N.float()
        P /= P.sum(1, keepdim=True)
        rets = []
        for _ in range(number_samples):
            s = self.lbl
            while True:
                idx = self.stoi[s[-self.size + 1 :]]
                cidx = torch.multinomial(
                    P[idx], num_samples=1, replacement=True, generator=g
                ).item()
                s += self.itos[cidx]
                if s[-self.size + 1 :] == self.lbl:
                    rets.append(s)
                    break
        return rets

    def loss(self, words: List[str]) -> float:
        P = self.N.float()
        P /= P.sum(1, keepdim=True)
        ll = 0
        for word in words:
            word = self.lbl + word + self.lbl
            for x, y in chunk(word, self.size):
                prob = P[self.encode(x), self.encode(y)]
                logprob = torch.log(prob)
                ll += logprob
        return -ll


class NGramModelNN(NGramModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.W = None
        self.all_dim = None
        self.stoi = None
        self.itos = None
        self.x_dim = None
        self.stoi_y = None
        self.itos_y = None

    def encode(self, words: List[str], stoi, stoi_y):
        xs = []
        ys = []
        for word in words:
            word = self.lbl + word + self.lbl
            for x, y in chunk(word, self.size):
                xs.append(stoi[x])
                ys.append(stoi_y[y])
        xs = torch.tensor(xs)
        ys = torch.tensor(ys)
        return xs, ys

    def train(self, words, epochs: int = 10, batch_size: int = 100):
        x_terms, y_terms, all_dim, itos, stoi = self.corpus(words)
        x_dim = len(x_terms)
        y_dim = len(y_terms)

        stoi_y = {s: idx for idx, s in enumerate(y_terms)}
        itos_y = {idx: s for s, idx in stoi_y.items()}

        xs, ys = self.encode(words, stoi, stoi_y)
        W = torch.randn((x_dim, y_dim), requires_grad=True)
        device = torch.device("cuda")
        W.to(device)

        for epoch in range(epochs):
            print(f"Epoch {epoch}/{epochs}")
            for xb, yb in zip(torch.split(xs, batch_size), torch.split(ys, batch_size)):
                if xb.shape[0] != batch_size:
                    break
                xenc = F.one_hot(xb, num_classes=x_dim).float()
                logits = xenc @ W
                counts = logits.exp()
                probs = counts / counts.sum(1, keepdim=True)
                loss = -probs[torch.arange(batch_size), yb].log().mean()
                W.grad = None
                loss.backward()
                W.data += -100 * W.grad
        self.W = W
        self.all_dim = all_dim
        self.stoi = stoi
        self.itos = itos
        self.x_dim = x_dim
        self.stoi_y = stoi_y
        self.itos_y = itos_y

    def loss(self, words: List[str]) -> float:
        xs, ys = self.encode(words, self.stoi, self.stoi_y)
        xenc = F.one_hot(xs, num_classes=self.x_dim).float()
        logits = xenc @ self.W
        counts = logits.exp()
        probs = counts / counts.sum(1, keepdim=True)
        loss = -probs[torch.arange(len(xs)), ys].log().mean()
        return loss

    def sample(self, number_samples: int = 10) -> List[str]:
        rets = []
        for _ in range(number_samples):
            s = self.lbl
            while True:
                x = torch.tensor([self.stoi[s[-self.size + 1 :]]])
                xenc = F.one_hot(x, num_classes=self.x_dim).float()
                logits = xenc @ self.W
                counts = logits.exp()
                probs = counts / counts.sum(1, keepdim=True)
                output_char_idx = torch.multinomial(
                    probs, num_samples=1, replacement=False
                ).item()
                s += self.itos_y[output_char_idx]
                if s[-self.size + 1 :] == self.lbl:
                    rets.append(s)
                    break
        return rets


def main():
    names = pd.read_csv("98-505-X2021007_eng_csv_data.csv").sort_values(
        "GENDER_TOTAL_COUNT"
    )
    names["names"] = names["FIRST_NAME"].astype(str)
    names["names"] = names["names"].str.lower()
    names.to_csv("names.csv", columns=["names"])
    names = names["names"].tolist()

    models = [
        ("ngram2", NGramModel(2, special_char="#")),
        ("ngram3", NGramModel(3, special_char="#")),
        ("ngram3_nn", NGramModelNN(3, special_char="#")),
    ]
    for model_name, model in models:
        print("model name", model_name)
        model.train(names)
        print(model.loss(["daniel", "oliver", "isabella"]))
        for sample in model.sample(3):
            print(sample)


if __name__ == "__main__":
    main()
