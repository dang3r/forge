# Through mathacademy.com (I highly recommend), I learned about the rational roots theorem and synthetic division.
# For polynomials with rational roots, you can use both to factor a polynomial with rational roots and integer coefficients.
# tl-dr: rrtheorem gives you hints, use synthetic dvision when a hint is true
# my simplification algo is:
# - find the potential candidates for a polynomial using the constant and highest degree term (with non-zero coefficient)
# - determine a candidate is true by calling the function and seeing if f(x) == 0
# - when you have a root, simplify the polynomial using `synthetic_division`
# - if polynomial has degree >= 2, continue, else return all roots
# notes:
# - added a custom R/Rational class that has specific operations for rationals and integers. Not sure if this is the most
#   elegant way, but it helps bundle all of the rational ops into a convenient class. Felt like an interview question
# - before I would find a root, simplify the polynomial and iterate the algo again. RRT says all rational roots are p/q
#   for the values set in the original function. Do that and save time.


from typing import Union, List


class R:
    def __init__(self, num: int, denom: int = 1):
        assert denom != 0
        # ensure the num has the sign
        if (num < 0 and denom < 0) or (num > 0 and denom < 0):
            num = -1 * num
            denom = -1 * denom
        self.num = num
        self.denom = denom
        assert type(self.num) == int
        assert type(self.denom) == int

    def is_zero(self) -> bool:
        return self.num == 0

    def __mul__(self, other):
        if type(other) == int:
            return R(self.num * other, self.denom)
        elif type(other == R):
            return R(self.num * other.num, self.denom * other.denom)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __str__(self):
        if self.denom != 1:
            return f"({self.num}/{self.denom})"
        return str(self.num)

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return R(-1 * self.num, self.denom)

    def __add__(self, other):
        if type(other) == int:
            return R(self.num + self.denom * other, self.denom)
        elif type(other) == R:
            return R(
                self.num * other.denom + other.num * self.denom,
                self.denom * other.denom,
            )

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def __int__(self) -> int:
        assert self.num % self.denom == 0
        return self.num // self.denom

    def __pow__(self, exp):
        assert type(exp) == int
        return R(self.num**exp, self.denom**exp)

    def __eq__(self, other) -> bool:
        if type(other) == int:
            return self.num % self.denom and (self.num // self.denom) == other
        elif type(other) == R:
            if self.denom == other.denom:
                return self.num == other.num
            else:
                return self.num * other.denom == other.num * self.denom

    def __hash__(self):
        self.simplify()
        return hash((self.num, self.denom))

    def simplify(self):
        _gcd = gcd(self.num, self.denom)
        self.num //= _gcd
        self.denom //= _gcd

Rational = R


class Polynomial:
    def __init__(self, *coefficients: List[Union[R | int]]):
        self.poly = list(coefficients)

    @classmethod
    def from_roots(self, *roots):
        assert len(roots)
        if len(roots) == 1:
            return Polynomial(*[-roots[0], 1])
        elif len(roots) >= 2:
            polys = []
            for root in roots:
                polys.append(Polynomial(*[-root, 1]))

            agg = polys[0]
            for poly in polys[1:]:
                agg *= poly
            return agg

    def simplify(self):
        try:
            for degree, coefficient in enumerate(self.poly):
                int(coefficient)
        except:
            agg_denom = 1
            for term in self.poly:
                if type(term) == R:
                    new_denom = term.denom * agg_denom
            for degree, coeff in enumerate(self.poly):
                self.poly[degree] = int(coeff * new_denom)

    def __call__(self, val):
        ret = 0
        for degree, coeff in enumerate(self.poly):
            ret += coeff * (val**degree)

        if type(ret) == R and ret.num == 0:
            return 0
        return ret

    def __str__(self) -> str:
        terms = []
        for degree, coeff in enumerate(self.poly):
            if coeff:
                if degree == 0:
                    terms.append(str(coeff))
                else:
                    terms.append(f"{coeff}x^{degree}")
        return " + ".join(terms[::-1])

    def __mul__(self, other) -> "Polynomial":
        if type(other) == R:
            for idx, coeff in enumerate(self.poly):
                self.poly[idx] *= other
        elif type(other) == Polynomial:
            poly1 = self
            poly2 = other

            # this is the length
            # eg. x^2 * x^3 == (3-1) + (4-1) + 1 ==  6
            ret_degree = (len(poly1) - 1) + (len(poly2) - 1)
            ret_num_terms = ret_degree + 1
            ret_poly = [0] * ret_num_terms

            for i, p1 in enumerate(poly1.poly):
                for j, p2 in enumerate(poly2.poly):
                    val = p1 * p2
                    if i == 0 or j == 0:
                        degree = max(i, j)
                    else:
                        degree = i + j
                    ret_poly[degree] += val
            return Polynomial(*ret_poly)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __len__(self):
        return len(self.poly)

    def __eq__(self, other):
        assert type(other) == Polynomial
        assert len(other) == len(self)

        for i in range(len(self)):
            if self.poly[i] != other.poly[i]:
                return False
        return True
    
    def __hash__(self):
        self.simplify()
        return hash(tuple(self.poly))


def gcd(a: int, b: int):
    if a == 0:
        return b

    return gcd(b % a, a)


def rational_root_candidates(poly: Polynomial) -> List[R | int]:
    assert len(poly) > 1
    p = int(poly.poly[0])
    q = int(poly.poly[-1])
    p_factors = factor(p)
    q_factors = factor(q)

    candidates = set()

    for p_factor in p_factors:
        for q_factor in q_factors:
            if p_factor % q_factor == 0:
                candidates.add(p_factor // q_factor)
            else:
                candidates.add(R(p_factor, q_factor))
    return candidates


def synthetic_division(dividend_poly: Polynomial, root: Union[int | R]) -> Polynomial:
    ret = [0] * len(dividend_poly)
    ret_idx = len(ret) - 1
    ret[ret_idx] = dividend_poly.poly[-1]
    ret_idx -= 1
    for term in dividend_poly.poly[-2::-1]:
        ret[ret_idx] = term + root * ret[ret_idx + 1]
        ret_idx -= 1

    if type(ret[0]) == int:
        assert ret[0] == 0
    elif type(ret[0]) == R:
        assert ret[0].is_zero()
    return Polynomial(*ret[1:])


def solve(poly: Polynomial) -> List[Polynomial]:
    polys = []

    while len(poly) >= 2:
        candidates = rational_root_candidates(poly)
        found = False
        for candidate in candidates:
            if poly(candidate) == 0:
                polys.append(Polynomial(*[-candidate, 1]))
                poly = synthetic_division(poly, candidate)
                found = True
                if len(poly) >= 2:
                    break
        assert found

    return polys


def factor(number: int):
    # kludge: when factoring a number, it may have a negative coefficient so coerce to +
    # kludge: We are only factoring integer coefficients of a polynomial, so coerce to int
    number = abs(int(number))
    factors = set()
    for i in range(1, number + 1):
        if abs(number) % i == 0:
            factors.add(i)
            factors.add(-i)
    return factors


def test_new():
    p = Polynomial(1, 2, 3, 4, 5)
    print("Printing a polynomial")
    print(p)
    print()

    print("Multiply two polynomials")
    p1 = Polynomial(5, 1, 2, 3)
    p2 = Polynomial(3, 3, 4)
    p3 = p1 * p2
    print(f"({p1})*({p2}) = ({p3})")
    print()

    roots = [1, 2, 3, 4, R(7, 3), R(1, 3)]
    print(f"Making a polynomial from roots: {roots}")
    proots = Polynomial.from_roots(*roots)
    print(proots)
    print()

    print("Simplifying a polynomial")
    print(proots)
    proots.simplify()
    print(proots)
    print()

    poly = Polynomial(-6, 11, -6, 1)
    div = 1
    print(f"Performing synthetic division: {poly} / {div}")
    dpoly = synthetic_division(poly, div)
    print(dpoly)
    print()

    proots = Polynomial.from_roots(*roots)
    proots.simplify()
    print("Finding all rational roots for a polynomial with integer coefficients")
    print(f"Solving for {proots}")
    polys = solve(proots)
    s = ""
    for poly in polys:
        s += f"({poly})"
    print(s)


# test_old()
test_new()
