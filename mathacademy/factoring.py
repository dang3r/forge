# Through mathacademy.com (I highly recommend), I learned about the rational roots theorem and synthetic division.
# For polynomials with rational roots, you can use both to factor a polynomial with rational roots and integer coefficients.
# tl-dr: rrtheorem gives you hints, use synthetic dvision when a hint is true
# my simplification algo is:
# - find the potential candidates for a polynomial using the constant and highest degree term (with non-zero coefficient)
# - determine a candidate is true by calling the function and seeing if f(x) == 0
# - when you have a root, simplify the polynomial using `synthetic_division`
# - if polynomial has degree >= 2, continue, else return all roots
# notes:
# - I don't handle non-integer rational roots at all. All potential roots are coerced to floats (during the p/q factor step)
#   This will cause issues with floating point math. Using an actual Rational or Integer class could help, or using tuples to
#   represent (num,denom) could be a hack to keep this non-OOP _functional_
# - I could keep iterating through the candidates to find multiple roots per polynomial but don't
# - its 2AM and I'm not going to simplify this today.


def format_polynomial(poly):
    terms = []
    for degree, coeff in enumerate(poly):
        if coeff:
            if degree == 0:
                terms.append(str(coeff))
            else:
                terms.append(f"{coeff}x^{degree}")
    return " + ".join(terms[::-1])


def multiply_polynomials(poly1, poly2):
    ret_degree = len(poly1) - 1 + len(poly2) - 1 + 1
    ret_poly = [0]* ret_degree

    for i, p1 in enumerate(poly1):
        for j, p2 in enumerate(poly2):
            val = p1*p2
            if i == 0 or j == 0:
                degree = max(i,j)
            else:
                degree = i+j
            ret_poly[degree] += val
    return ret_poly

def make_polynomial(*roots):
    if len(roots) == 0:
        return 0
    elif len(roots) == 1:
        return [-roots[0], 1]
    elif len(roots) >= 2:
        polys = []
        for root in roots:
            polys.append([-root, 1])

        agg = polys[0]
        for poly in polys[1:]:
            agg = multiply_polynomials(agg, poly)
        return agg
    

def factor(number):
    # kludge: when factoring a number, it may have a negative coefficient so coerce to +
    # kludge: We are only factoring integer coefficients of a polynomial, so coerce to int
    number = abs(int(number))
    factors = set()
    for i in range(1, number+1):
        if abs(number) % i == 0:
            factors.add(i)
            factors.add(-i)
    return factors
    

def rational_root_candidates(poly):
    p_factors = factor(poly[0])
    q_factors = factor(poly[-1])

    candidates = set()

    # kludge: I know this is bad because we want to represent rationals and not decimals
    # This whole file has to be tweaked to use rationals instead of just integers
    for p_factor in p_factors:
        for q_factor in q_factors:
            _factor = p_factor / q_factor
            candidates.add(_factor)
    return candidates


def synthetic_division(dividend_poly, root):
    ret = [0] * len(dividend_poly)
    ret_idx = len(ret) - 1
    ret[ret_idx] = dividend_poly[-1]
    ret_idx -=1
    for term in dividend_poly[-2::-1]:
        ret[ret_idx] = term + root*ret[ret_idx+1]
        ret_idx -= 1
    
    assert ret[0] == 0
    
    return [val for val in ret[1:]]
        
def simplify(poly):
    polys = []

    while len(poly) >= 2:
        candidates = rational_root_candidates(poly)
        fcn_str =f"lambda x: {format_polynomial(poly).replace('x', '*x').replace('^', '**')}" 
        fcn = eval(fcn_str)
        found = False
        for candidate in candidates:
            if fcn(candidate) == 0:
                polys.append([-candidate, 1])
                poly = synthetic_division(poly, candidate)
                found = True
                break
        assert found

    return polys



print("Formatting two polynomials")
p1 = [1,1,-3]
p2 = [1,1,-4,7,8]
print(f"({format_polynomial(p1)})*({format_polynomial(p2)})")
print()


print("Multiply two polynomials")
p1 =  [1,1, -3]
p2 = [1,1, -4, 7, 8]
print("- p1: ", format_polynomial(p1))
print("- p2: ", format_polynomial(p2))
poly = multiply_polynomials(p1,p2)
print("- p1*p2: ", format_polynomial(poly))
print()

print("Making a polynomial from roots")
roots = list(range(4))
print("- roots: ", roots)
p = make_polynomial(*roots)
print("- expanded_polynomial: ", format_polynomial(p))
print()


print("Performing synthetic division")
poly = [-6, 11, -6, 1]
divisor = 1
print("- dividend: ", format_polynomial(poly))
print("- divisor: ", divisor)
print(f"- simplified polynomial:  ({format_polynomial([-divisor, 1])})({format_polynomial(synthetic_division(poly, divisor))})")
print()


print("Simplifying a polynomial to its rational (only integers for now)")
roots = list(range(1,8))
poly = make_polynomial(1,2,3,4,5,6,7)
print("- roots: ", roots)
print("- expanded_polynomial: ", format_polynomial(poly))
polys = simplify(poly)
s = ""
for poly in polys:
    s += f"({format_polynomial(poly)})"
print("- factored_polynomial: ", s)