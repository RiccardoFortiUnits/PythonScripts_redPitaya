import numpy as np
import matplotlib.pyplot as plt

class volterraRegressor:
    def __init__(self, maxPowers):
        self.maxPowers = np.array(maxPowers)
    @property
    def nOfInputs(self):
        return len(self.maxPowers)
    def coefficientOrder(self, inputNames = None):
        if inputNames is None:
            inputNames = [f"x{i}" for i in range(self.nOfInputs)]
        l = ["1"]
        for j in range(self.nOfInputs):
            for jj in range(self.maxPowers[j]):
                l.append(f"{inputNames[j]} ^ {jj+1}")
        return l
    def makeVolterraMatrix(self, x):
        A = np.ones((1 + np.sum(self.maxPowers), x.shape[1]))
        i = 1
        for j in range(self.nOfInputs):
            for jj in range(self.maxPowers[j]):
                A[i + jj] = x[j] ** (jj + 1)
            i += self.maxPowers[j]
        return A
    def regrade(self, x : np.ndarray, y : np.ndarray, returnMeanSquareError : bool = False):
        '''
        x: nInput x signalLength
        y: signalLength
        '''
        A = self.makeVolterraMatrix(x)
        bestCoefficients = np.linalg.pinv(A.T)@y
        if returnMeanSquareError:
            y_ = self.estimate(x, bestCoefficients)
            mse = np.mean((y-y_)**2)
            return bestCoefficients, mse
        return bestCoefficients
    def estimate(self, x : np.ndarray, coefficients : np.ndarray):
        A = self.makeVolterraMatrix(x)
        y = A.T@coefficients
        return y

if __name__ == "__main__":
    vr = volterraRegressor([2,1])
    x = np.array([[0,1,2,3],[2,4,1,3]])
    q = vr.regrade(x, np.array([2,1,-3,6]))
    names = vr.coefficientOrder(["x", "y"])
    for i in range(len(q)):
        print(f"{names[i]}: {q[i]}")
    y = vr.estimate(x, q)
    print(y)

