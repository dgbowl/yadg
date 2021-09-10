import math
from scipy.optimize import curve_fit

def _lognormal(x, mu=1, sigma=0, c=0):
    return (c + 1/(x*sigma*math.sqrt(2*math.pi))) * math.exp(-(math.log(x) - mu)**2/(2*sigma**2))

def func(xs, mu, sigma, c):
    return [_lognormal(x, mu, sigma, c) for x in xs]
    
def fit(xs, ys):
    xs = list(xs)
    return curve_fit(func, xs, ys, p0 = [1, 0, 0])
