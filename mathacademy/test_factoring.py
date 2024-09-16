from factoring import Polynomial, R, synthetic_division, solve

def test_synthetic_division():
    poly = Polynomial(-6,11,-6,1)
    div = 1

    ret_poly = synthetic_division(poly, div)
    assert ret_poly == Polynomial(6,-5,1)


def test_solve():
    poly = Polynomial(168,-926,1661,-1360, 562, -114, 9)
    polys = solve(poly)
    expected_polys = [
        Polynomial.from_roots(1),
        Polynomial.from_roots(2),
        Polynomial.from_roots(3),
        Polynomial.from_roots(4),
        Polynomial.from_roots(R(7,3)),
        Polynomial.from_roots(R(1,3)),
    ]
    assert set(polys) == set(expected_polys)

