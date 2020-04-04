from scipy.stats import powerlaw
import numpy as np

a = 2.25
mean, var, skew, kurt = powerlaw.stats(a, moments='mvsk')

x = 1
loc = np.random.uniform(0,1)
answer = powerlaw.pdf(x, a, loc)

print(answer)