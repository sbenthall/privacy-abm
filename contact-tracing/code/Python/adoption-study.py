{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sys\n",
    "\n",
    "sys.path.append('.')\n",
    "\n",
    "import model"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "import matplotlib.pyplot as plt\n",
    "import networkx as nx\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import random\n",
    "import seaborn as sns\n",
    "import statistics"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Some invariant parameters for this notebook:"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "## Population parameters:\n",
    "base_params = {\n",
    "    # Node parameter\n",
    "    'A' : 0.0, # Now this will vary case by case.\n",
    "    \n",
    "    # Edge parameter\n",
    "    'W' : .5, # probability of edge activation; 2/K\n",
    "    'C' : 1.0, ## all edges can be traced.\n",
    "    \n",
    "    ## Disease parameters\n",
    "\n",
    "    'beta_hat' : .4, # probability of transmission upon contact\n",
    "    'alpha' : .25, # probability of exposed becoming infectious\n",
    "    'gamma' : .1, # probability of infectious becoming recovered\n",
    "    'zeta' : .1, # probability of infectious becoming symptomatic\n",
    "\n",
    "    ## Contact tracing parameters\n",
    "\n",
    "    'limit' : 10, # number of time steps the contact tracing system remembers\n",
    "}"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "$p^*$ has been chosen because it exposes the effects of the Watts-Strogatz structure.\n",
    "With $K = 4$, roughly one edge for every node is rewired, with the rest comprising the circle lattice."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "p_star = 0.256\n",
    "K = 4\n",
    "\n",
    "# N = 2000  --- allowing this to vary now"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "This time, run the model with no contact tracing at all."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "def ws_case_generator(N, K, p_star):\n",
    "    def wscg(**kwargs):\n",
    "        return model.watts_strogatz_case_p_star(N, K, p_star, **kwargs)\n",
    "    \n",
    "    return wscg"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "conditions = {\n",
    "    'A-0.000' : {'A' : 0.000},\n",
    "    'A-0.100' : {'A' : 0.100},\n",
    "    'A-0.200' : {'A' : 0.200},\n",
    "    'A-0.300' : {'A' : 0.300},\n",
    "    'A-0.400' : {'A' : 0.400},\n",
    "    'A-0.500' : {'A' : 0.500},\n",
    "    'A-0.600' : {'A' : 0.600},\n",
    "    'A-0.700' : {'A' : 0.700},\n",
    "    'A-0.800' : {'A' : 0.800},\n",
    "    'A-0.900' : {'A' : 0.900},\n",
    "    'A-1.000' : {'A' : 1.000},\n",
    "}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "def dfr(rs):\n",
    "    return pd.DataFrame(\n",
    "        [r for case in rs \n",
    "         for r in model.data_from_results(rs, case)])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "runs = 200"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Starting A-0.000\n",
      "Finished A-0.000 in 184.850950516\n",
      "Starting A-0.100\n",
      "Finished A-0.100 in 197.3668366820002\n",
      "Starting A-0.200\n",
      "Finished A-0.200 in 170.30853718099934\n",
      "Starting A-0.300\n",
      "Finished A-0.300 in 173.3529398160008\n",
      "Starting A-0.400\n",
      "Finished A-0.400 in 167.56829729799938\n",
      "Starting A-0.500\n",
      "Finished A-0.500 in 193.15755965000062\n",
      "Starting A-0.600\n",
      "Finished A-0.600 in 136.26803106099942\n",
      "Starting A-0.700\n",
      "Finished A-0.700 in 93.92581745999996\n",
      "Starting A-0.800\n",
      "Finished A-0.800 in 80.03087079100078\n",
      "Starting A-0.900\n",
      "Finished A-0.900 in 56.318548174998796\n",
      "Starting A-1.000\n",
      "Finished A-1.000 in 46.70530561899977\n"
     ]
    }
   ],
   "source": [
    "rs = model.experiment(\n",
    "    ws_case_generator(1000, K, p_star),\n",
    "    base_params,\n",
    "    conditions,\n",
    "    runs)\n",
    "\n",
    "dfr(rs).to_csv('data_1.csv')\n",
    "del rs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Starting A-0.000\n",
      "Finished A-0.000 in 461.10462321699924\n",
      "Starting A-0.100\n",
      "Finished A-0.100 in 442.4919866179989\n",
      "Starting A-0.200\n",
      "Finished A-0.200 in 457.1868344409995\n",
      "Starting A-0.300\n",
      "Finished A-0.300 in 387.06899439899826\n",
      "Starting A-0.400\n",
      "Finished A-0.400 in 401.2832571859999\n",
      "Starting A-0.500\n",
      "Finished A-0.500 in 400.696298562998\n",
      "Starting A-0.600\n",
      "Finished A-0.600 in 274.26739157700285\n",
      "Starting A-0.700\n",
      "Finished A-0.700 in 167.48479207700075\n",
      "Starting A-0.800\n",
      "Finished A-0.800 in 142.02787156799968\n",
      "Starting A-0.900\n",
      "Finished A-0.900 in 108.8522099710026\n",
      "Starting A-1.000\n",
      "Finished A-1.000 in 110.45430653700168\n"
     ]
    }
   ],
   "source": [
    "rs = model.experiment(\n",
    "    ws_case_generator(2000, K, p_star),\n",
    "    base_params,\n",
    "    conditions,\n",
    "    runs)\n",
    "\n",
    "dfr(rs).to_csv('data_2.csv')\n",
    "del rs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Starting A-0.000\n",
      "Finished A-0.000 in 1179.8195238040025\n",
      "Starting A-0.100\n",
      "Finished A-0.100 in 1123.9075262139995\n",
      "Starting A-0.200\n",
      "Finished A-0.200 in 925.7199715089992\n",
      "Starting A-0.300\n",
      "Finished A-0.300 in 892.5989056920007\n",
      "Starting A-0.400\n",
      "Finished A-0.400 in 1112.3019679330027\n",
      "Starting A-0.500\n",
      "Finished A-0.500 in 774.752421424997\n",
      "Starting A-0.600\n",
      "Finished A-0.600 in 719.7500741219992\n",
      "Starting A-0.700\n",
      "Finished A-0.700 in 376.8246060220008\n",
      "Starting A-0.800\n",
      "Finished A-0.800 in 375.60182946099667\n",
      "Starting A-0.900\n",
      "Finished A-0.900 in 255.48551803300143\n",
      "Starting A-1.000\n",
      "Finished A-1.000 in 241.38928705999933\n"
     ]
    }
   ],
   "source": [
    "rs = model.experiment(\n",
    "    ws_case_generator(4000, K, p_star),\n",
    "    base_params,\n",
    "    conditions,\n",
    "    runs)\n",
    "\n",
    "dfr(rs).to_csv('data_3.csv')\n",
    "del rs"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "data = pd.concat([\n",
    "    pd.read_csv('data_1.csv'),\n",
    "    pd.read_csv('data_2.csv'),\n",
    "    pd.read_csv('data_3.csv')\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "   Unnamed: 0  time    A    W    C  beta_hat  alpha  gamma  zeta  limit     N  \\\n",
      "0           0   221  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  1000   \n",
      "1           1   173  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  1000   \n",
      "2           2     1  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  1000   \n",
      "3           3    26  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  1000   \n",
      "4           4   258  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  1000   \n",
      "\n",
      "   K      p  s_final     case  infected_ratio  \n",
      "0  4  0.256      448  A-0.000           0.552  \n",
      "1  4  0.256      468  A-0.000           0.532  \n",
      "2  4  0.256      999  A-0.000           0.001  \n",
      "3  4  0.256      999  A-0.000           0.001  \n",
      "4  4  0.256      369  A-0.000           0.631  \n",
      "   Unnamed: 0  time    A    W    C  beta_hat  alpha  gamma  zeta  limit     N  \\\n",
      "0           0   204  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  2000   \n",
      "1           1    62  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  2000   \n",
      "2           2     4  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  2000   \n",
      "3           3    42  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  2000   \n",
      "4           4     5  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  2000   \n",
      "\n",
      "   K      p  s_final     case  infected_ratio  \n",
      "0  4  0.256      527  A-0.000          0.7365  \n",
      "1  4  0.256     1962  A-0.000          0.0190  \n",
      "2  4  0.256     1998  A-0.000          0.0010  \n",
      "3  4  0.256     1986  A-0.000          0.0070  \n",
      "4  4  0.256     1998  A-0.000          0.0010  \n",
      "   Unnamed: 0  time    A    W    C  beta_hat  alpha  gamma  zeta  limit     N  \\\n",
      "0           0   221  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  4000   \n",
      "1           1    18  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  4000   \n",
      "2           2   305  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  4000   \n",
      "3           3   280  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  4000   \n",
      "4           4   314  0.0  0.5  1.0       0.4   0.25    0.1   0.1     10  4000   \n",
      "\n",
      "   K      p  s_final     case  infected_ratio  \n",
      "0  4  0.256     1598  A-0.000         0.60050  \n",
      "1  4  0.256     3997  A-0.000         0.00075  \n",
      "2  4  0.256     1903  A-0.000         0.52425  \n",
      "3  4  0.256     1722  A-0.000         0.56950  \n",
      "4  4  0.256     1433  A-0.000         0.64175  \n"
     ]
    }
   ],
   "source": [
    "for x in data.groupby('N'):\n",
    "    print(x[1].head())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.legend.Legend at 0x7f7ba7a1a7f0>"
      ]
     },
     "execution_count": 5,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "iVBORw0KGgoAAAANSUhEUgAAAXcAAAD4CAYAAAAXUaZHAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEgAACxIB0t1+/AAAADh0RVh0U29mdHdhcmUAbWF0cGxvdGxpYiB2ZXJzaW9uMy4xLjEsIGh0dHA6Ly9tYXRwbG90bGliLm9yZy8QZhcZAAAemUlEQVR4nO3dfXQV9b3v8fdXHi+tIo9dSETgiN5SVwVPsFCvXvGhKqsGvQst2AIWFa3YS7HVSruOUo9d2gdl+UDtwULBY01QqSVtwStQwFMraCgcxFAJIGiQJYEKopan8L1/ZIduYDZ7kplJ2JPPa62s7P2b38zvOyZ+mfzmt79j7o6IiKTLSc0dgIiIxE/JXUQkhZTcRURSSMldRCSFlNxFRFKodXMHANC1a1fv3bt3c4chIlJQVq5cucPduwVtOyGSe+/evamoqGjuMERECoqZbcm1TdMyIiIppOQuIpJCSu4iIil0Qsy5i4jE7cCBA1RXV7N3797mDiWy9u3bU1RURJs2bULvo+QuIqlUXV3NySefTO/evTGz5g6n0dydnTt3Ul1dTZ8+fULvl3daxsxON7MlZrbOzN4ys4mZ9s5mttDMqjLfO2XazcweM7MNZrbGzM5r9FmJiDTS3r176dKlS0EndgAzo0uXLg3+CyTMnPtB4Lvu/nlgMDDBzPoD9wCL3b0fsDjzHuAqoF/mazzwZIMiEhGJSaEn9nqNOY+8yd3dt7n7XzOv9wDrgJ7AcGB2ptts4JrM6+HA015nOXCqmfVocGQiItJoDZpzN7PewEBgBfA5d98Gdf8AmFn3TLeewHtZu1Vn2rYddazx1F3Z06tXr0aELiIS3tSF62M93qTLzwrV76WXXmLixInU1tZy8803c8899xyxfd++fYwZM4aVK1fSpUsX5syZQxyf2A+d3M3ss8Bc4Dvu/tFx/kwI2nDME0HcfTowHaC4uDjSE0Ny/dDC/scXEUlCbW0tEyZMYOHChRQVFTFo0CBKSkro37//4T4zZsygU6dObNiwgbKyMr7//e8zZ86cyGOHWuduZm2oS+y/cfffZpo/qJ9uyXzfnmmvBk7P2r0IeD9ypCIiBeb111/nzDPPpG/fvrRt25aRI0cyb968I/rMmzePsWPHAjBixAgWL15MHE/IC7NaxoAZwDp3fyRrUzkwNvN6LDAvq31MZtXMYGB3/fSNiEhLsnXrVk4//Z/XukVFRWzdujVnn9atW9OxY0d27twZeeww0zIXAKOBN81sdabtB8BDwHNmdhPwLnBdZtt8YBiwAfgU+GbkKEVEClDQFfjRU9ph+jRG3uTu7n8meB4d4NKA/g5MiBiXiEjBKyoq4r33/rm+pLq6mtNOOy2wT1FREQcPHmT37t107tw58tip+ITqX3btCWyf1MRxiIhkGzRoEFVVVbzzzjv07NmTsrIynn322SP6lJSUMHv2bIYMGcILL7zAJZdc0jRX7iIiadAcq+dat27NE088wRVXXEFtbS3jxo3jC1/4Avfeey/FxcWUlJRw0003MXr0aM4880w6d+5MWVlZPGPHchQREQk0bNgwhg0bdkTb/ffff/h1+/btef7552MfVyV/RURSSMldRCSFlNxFRFIoFXPu//jH1hxb/rVJ4xAROVHoyl1EJIWU3EVEUigV0zIiInkteTDe4w2dHKpbvpK/r7zyCt/5zndYs2YNZWVljBgxIpbwdOUuIpKQ+pK/CxYsoLKyktLSUiorK4/o06tXL2bNmsUNN9wQ69i6chcRSUh2yV/gcMnf7Hru9Q/mOOmkeK+1deUuIpKQMCV/k6LkLiKSkKTK+Yah5C4ikpAwJX+TouQuIpKQ7JK/+/fvp6ysjJKSkiYZWzdURaRlCLl0MU5hSv6+8cYbXHvttXz44Yf8/ve/57777uOtt96KPna+DmY2E/gqsN3dz8m0zQHOznQ5Fdjl7gPMrDewDng7s225u98WOUoRkQKVr+TvoEGDqK6ujn3cMFfus4AngKfrG9z9a/WvzexhYHdW/43uPiCuAEVEpOHCPEP1lcwV+TGs7rbv9cAl8YYlIiJRRL2heiHwgbtXZbX1MbNVZrbMzC7MtaOZjTezCjOrqKmpiRiGiIhki5rcRwGlWe+3Ab3cfSBwJ/CsmZ0StKO7T3f3Yncv7tatW8QwREQkW6OTu5m1Bv4PMKe+zd33ufvOzOuVwEag6Z9KKyLSwkW5cr8M+Ju7H77Na2bdzKxV5nVfoB+wKVqIIiLSUGGWQpYCFwNdzawauM/dZwAjOXJKBuAi4H4zOwjUAre5+9/jDflYe/fuTXoIESlwv1j9i1iPd/uA20P1y1fy95FHHuFXv/oVrVu3plu3bsycOZMzzjgjcnxhVsuMytF+Y0DbXGBu5KhERFKgvuTvwoULKSoqYtCgQZSUlBxRFXLgwIFUVFTQoUMHnnzySe6++27mzJlznKOGo/IDIiIJyS7527Zt28Mlf7MNHTqUDh06ADB48ODYPtCk5C4ikpCGlvydMWMGV111VSxjq7aMiEhCGlLy95lnnqGiooJly5bFMraSu4hIQsKW/F20aBE//vGPWbZsGe3atYtlbE3LiIgkJEzJ31WrVnHrrbdSXl5O9+7dYxtbV+4i0iKEXboYpzAlf++66y4+/vhjrrvuOqDugdnl5eXRx458BBERySlfyd9FixYlMq6mZUREUkjJXUQkhZTcRURSSMldRCSFlNxFRFJIyV1EJIW0FFJEWoSax5+I9Xjdvn1HqH75Sv7+8pe/ZNq0abRq1YrPfvazTJ8+/YiqkY2lK3cRkYTUl/xdsGABlZWVlJaWUllZeUSfG264gTfffJPVq1dz9913c+edd8YytpK7iEhCwpT8PeWUfz5m+pNPPslZWKyhNC0jIpKQoJK/K1asOKbftGnTeOSRR9i/fz9/+tOfYhk775W7mc00s+1mtjarbYqZbTWz1ZmvYVnbJpvZBjN728yuiCXKPPzgocAvEZHmFLbk74QJE9i4cSM/+clPeOCBB2IZO8y0zCzgyoD2qe4+IPM1H8DM+lP3bNUvZPb5Rf0Ds0VEWpqwJX/rjRw5kt/97nexjJ03ubv7K0DYh1wPB8rcfZ+7vwNsAM6PEJ+ISMEKU/K3qqrq8Os//vGP9OvXL5axo8y532FmY4AK4Lvu/iHQE1ie1ac603YMMxsPjIe6EpciIkkKu3QxTmFK/j7xxBMsWrSINm3a0KlTJ2bPnh3P2I3c70ng3wHPfH8YGAcE3eY9dtIJcPfpwHSA4uLiwD4iIoUuX8nfRx99NJFxG7UU0t0/cPdadz8EPMU/p16qgdOzuhYB70cLUUREGqpRyd3MemS9vRaoX0lTDow0s3Zm1gfoB7weLUQREWmovNMyZlYKXAx0NbNq4D7gYjMbQN2Uy2bgVgB3f8vMngMqgYPABHevTSZ0ERHJJW9yd/dRAc0zjtP/x8CPowQlIiLRqPyAiEgKKbmLiKSQasuISIvw+u83xXq886/uG6pfvpK/9V544QWuu+463njjDYqLiyPHpyt3EZGEhCn5C7Bnzx4ee+wxvvSlL8U2tpK7iEhCwpT8Bfi3f/s37r77btq3bx/b2EruIiIJCSr5u3Xr1iP6rFq1ivfee4+vfvWrsY6tOXcRkYTkK/l76NAhJk2axKxZs2IfW1fuIiIJyVfyd8+ePaxdu5aLL76Y3r17s3z5ckpKSqioqIg8tpK7iEhC8pX87dixIzt27GDz5s1s3ryZwYMHU15eHstqGU3LiEiLEHbpYpzClPxNbOzEjiwiInlL/mZbunRpbOOmIrn7IZWDFxHJpuQuIpJCuqEqIpJCSu4iIimk5C4ikkKpmHOHQ80dgIjICSXMY/ZmAl8Ftrv7OZm2nwFXA/uBjcA33X2XmfUG1gFvZ3Zf7u63JRC3iEiD/OX538R6vC9f9/VQ/fKV/J01axZ33XUXPXv2BOCOO+7g5ptvjhxfmGmZWcCVR7UtBM5x9y8C64HJWds2uvuAzJcSu4i0WGFL/n7ta19j9erVrF69OpbEDiGSu7u/Avz9qLaX3f1g5u1yoCiWaEREUiRsyd8kxHFDdRywIOt9HzNbZWbLzOzCXDuZ2XgzqzCzipqamhjCEBE5sYQp+Qswd+5cvvjFLzJixIgjCo1FESm5m9kPgYNA/WTWNqCXuw8E7gSeNbNTgvZ19+nuXuzuxd26dYsShojICSlfyV+Aq6++ms2bN7NmzRouu+wyxo4dG8vYjU7uZjaWuhutX/fMGbj7PnffmXm9krqbrWfFEaiISKHJV/IXoEuXLrRr1w6AW265hZUrV8YydqOSu5ldCXwfKHH3T7Pau5lZq8zrvkA/IN6n0oqIFIh8JX8Btm3bdvh1eXk5n//852MZO8xSyFLgYqCrmVUD91G3OqYdsDDzJ0b9kseLgPvN7CBQC9zm7n8PPLCISBMKu3QxTmFK/j722GOUl5fTunVrOnfuHNtTmSxoTqipFRcXe5Qnjwx99JnA9iUTv9HoY4pIYVu3bl1sV8EngqDzMbOV7h74ZA+VHxARSSEldxGRFEpFbRmn+aeWREROJLpyFxFJISV3EZEUUnIXEUmhVMy5i4jks3vhlliP1/HyM0L1y1fyF+C5555jypQpmBnnnnsuzz77bOT4lNxFRBJSX/J34cKFFBUVMWjQIEpKSujfv//hPlVVVTz44IO8+uqrdOrUie3bt8cytqZlREQSEqbk71NPPcWECRPo1KkTAN27d49lbCV3EZGEhCn5u379etavX88FF1zA4MGDeemll2IZW9MyIiIJCVPy9+DBg1RVVbF06VKqq6u58MILWbt2LaeeemqksXXlLiKSkDAlf4uKihg+fDht2rShT58+nH322VRVVUUeW8ldRCQhYUr+XnPNNSxZsgSAHTt2sH79evr27Rt5bE3LiEiLEHbpYpzClPy94oorePnll+nfvz+tWrXiZz/7GV26dIk8dipK/l786H8Gti+dOLrRxxSRwqaSvyIikjpK7iIiKRQquZvZTDPbbmZrs9o6m9lCM6vKfO+UaTcze8zMNpjZGjM7L6ngRUQkWNgr91nAlUe13QMsdvd+wOLMe4CrqHswdj9gPPBk9DBFRKQhQiV3d38FOPpB18OB2ZnXs4Frstqf9jrLgVPNrEccwYqISDhR5tw/5+7bADLf6wsi9ATey+pXnWk7gpmNN7MKM6uoqamJEIaIiBwtiXXuFtB2zHpLd58OTIe6pZAJxCEiclj9B4XiMnTo0FD98pX8nTRp0uHYPv30U7Zv386uXbsixxcluX9gZj3cfVtm2qW+TmU1cHpWvyLg/QjjiIgUpDAlf6dOnXr49eOPP86qVatiGTvKtEw5MDbzeiwwL6t9TGbVzGBgd/30jYhISxKm5G+20tJSRo0aFcvYYZdClgKvAWebWbWZ3QQ8BFxuZlXA5Zn3APOBTcAG4Cng9lgiFREpMGFK/tbbsmUL77zzDpdcckksY4ealnH3XP+UXBrQ14EJUYISEUmDMCV/65WVlTFixAhatWoVy9j6hKqISELClPytV1ZWFtuUDCi5i4gkJkzJX4C3336bDz/8kCFDhsQ2tkr+ikiLEHbpYpzClPyFuhupI0eOzDll06ixYzuSiIgcY9iwYQwbNuyItvvvv/+I91OmTIl9XE3LiIikkJK7iEgKKbmLiKSQkruISAopuYuIpJCSu4hICmkppIi0CJs2PRrr8fr2nRiqX76Sv++++y5jx45l165d1NbW8tBDDx2zdLIxdOUuIpKQ+pK/CxYsoLKyktLSUiorK4/o88ADD3D99dezatUqysrKuP32eGotKrmLiCQkTMlfM+Ojjz4CYPfu3TlrzzSUpmVERBISVPJ3xYoVR/SZMmUKX/nKV3j88cf55JNPWLRoUSxj68pdRCQhYUr+lpaWcuONN1JdXc38+fMZPXo0hw4dijy2kruISELClPydMWMG119/PQBDhgxh79697NixI/LYSu4iIgkJU/K3V69eLF68GIB169axd+9eunXrFnnsRs+5m9nZwJyspr7AvcCpwC1ATab9B+4+v9ERiojEIOzSxTiFKfn78MMPc8sttzB16lTMjFmzZsVS+rfRyd3d3wYGAJhZK2Ar8CLwTWCqu/88cnQiIgUuX8nf/v378+qrr8Y+blzTMpcCG919S0zHExGRCOJK7iOB0qz3d5jZGjObaWadgnYws/FmVmFmFTU1NUFdRESkkSIndzNrC5QAz2eangT+hbopm23Aw0H7uft0dy929+I4bh6IiMg/xXHlfhXwV3f/AMDdP3D3Wnc/BDwFnB/DGCIi0gBxJPdRZE3JmFmPrG3XAmtjGENERBogUvkBM+sAXA7cmtX8UzMbADiw+ahtIiLSBCIld3f/FOhyVNvoSBGJiCTgZ+9si/V4d/Xpkb8T+Uv+btmyhXHjxlFTU0Pnzp155plnKCoqihyfPqEqIpKQMCV/v/e97zFmzBjWrFnDvffey+TJk2MZW8ldRCQhYUr+VlZWcumllwIwdOjQY7Y3lpK7iEhCgkr+bt269Yg+5557LnPnzgXgxRdfZM+ePezcuTPy2EruIiIJCVPy9+c//znLli1j4MCBLFu2jJ49e9K6dfRHbehhHSIiCQlT8ve0007jt7/9LQAff/wxc+fOpWPHjpHH1pW7iEhCwpT83bFjx+GHczz44IOMGzculrF15S4iLULYpYtxClPyd+nSpUyePBkz46KLLmLatGnxjB3LUUREJFC+kr8jRoxgxIgRsY+raRkRkRRSchcRSSEldxGRFFJyFxFJISV3EZEUUnIXEUkhLYUUkRZh6sL1sR5v0uVn5e0zbtw4/vCHP9C9e3fWrj32uUXuzsSJE5k/fz4dOnRg1qxZnHfeebHEpyt3EZGE3Hjjjbz00ks5ty9YsICqqiqqqqqYPn063/rWt2IbW8ldRCQhF110EZ07d865fd68eYwZMwYzY/DgwezatYtt2+J5qEjk5G5mm83sTTNbbWYVmbbOZrbQzKoy3ztFD1VEJF3ClARurLiu3Ie6+wB3L868vwdY7O79gMWZ9yIikiVMSeDGSmpaZjgwO/N6NnBNQuOIiBSsMCWBGyuO5O7Ay2a20szGZ9o+5+7bADLfux+9k5mNN7MKM6uoqamJIQwRkcJSUlLC008/jbuzfPlyOnbsSI8e8VSvjGMp5AXu/r6ZdQcWmtnfwuzk7tOB6QDFxcXH/m0iIhKjMEsX4zZq1CiWLl3Kjh07KCoq4kc/+hEHDhwA4LbbbmPYsGHMnz+fM888kw4dOvDrX/86trEjJ3d3fz/zfbuZvQicD3xgZj3cfZuZ9QC2Rx1HRKTQlJaWHne7mcVWv/1okaZlzOwzZnZy/WvgK8BaoBwYm+k2Fojncd4iIhJK1Cv3zwEvZu7utgaedfeXzOwN4Dkzuwl4F7gu4jgiItIAkZK7u28Czg1o3wlcGuXYIiJRuXtsSwubU9CSyXz0CVURSaX27duzc+fORiXGE4m7s3PnTtq3b9+g/VQ4TERSqaioiOrqatKw1Lp9+/YUFRU1aB8ldxFJpTZt2tCnT5/mDqPZaFpGRCSFlNxFRFJIyV1EJIWU3EVEUkjJXUQkhZTcRURSSMldRCSFlNxFRFJIyV1EJIWU3EVEUkjJXUQkhZTcRURSSMldRCSFlNxFRFKo0cndzE43syVmts7M3jKziZn2KWa21cxWZ76GxReuiIiEEaWe+0Hgu+7+18xDslea2cLMtqnu/vPo4YmISGM0Orm7+zZgW+b1HjNbB/SMKzAREWm8WObczaw3MBBYkWm6w8zWmNlMM+uUY5/xZlZhZhVpeAyWiMiJJHJyN7PPAnOB77j7R8CTwL8AA6i7sn84aD93n+7uxe5e3K1bt6hhiIhIlkjJ3czaUJfYf+PuvwVw9w/cvdbdDwFPAedHD1NERBoiymoZA2YA69z9kaz2HlndrgXWNj48ERFpjCirZS4ARgNvmtnqTNsPgFFmNgBwYDNwa6QIRUSkwaKslvkzYAGb5jc+HBERiYM+oSoikkJRpmVE5ATwi9W/CGy/fcDtTRyJnEiU3EUKxNSF6wPb22klsQTQtIyISAopuYuIpJCmZUQSVPP4E4Ht3b59RxNHIi2NkrtIgXtt487A9tsHNHEgckJRchc5weRa/QKXNWkcUtiU3EWaQe4EnvtK/LxTkopG0ijVyX3JkiWB7UOHDm3iSKTF2vxfgc2vnXZOzl2KPloZvOGUr8URkbQQqU7uIo31+u83Bbaff3XfwPZcN05zuXDxmpzb3hkU3L69+u7gDaf8a4PGBmDJg8HtQyc3/FhyQlJylxYrVwJvzD59ogaTgFwfegKYpP/zU0/r3EVEUkj/fovEoHrVy4Ht2/7HR4Htp+w7eJyjdY0houN7bVPwTdshuh2VGqlO7nP+sTGwfd+M3YHtV950TZLhSAP95fnfBLZ/+bqvx3KcrW9/mHOfM84dFtj+yetvBLafmuM4H+09XhIPdu6fdwS2//f/Ck76uW7ADt4V/HsuLUOqk3vtgUPNHYJEcLzkG6QxSTwuq1qdG9je4VDwii2RpKU6uR+qPZD4GLsXbgls73j5GQUzdq7jALy168+B7Q29es55/Ef/0OB9miKJ57pCb065ruhz+vKZOTeVn7QhsH2IVtGkRmLJ3cyuBB4FWgG/cveHkhorJ4/nyj3XenmA8wheGtdQT097LLB9zIT/G8vxIXcSr658M/dOpwU3N3TKJFd/29E299jtgps7vt8xsH0rwcl9/9b3A9trgg8DwI5dnwS224H3AtvbntQp98Ea6NOTgie+G/pXQK4ELi1DIsndzFoB04DLgWrgDTMrd/fKJMbLxT24/UDbuYHt0370dmB7/4vOb/DYTZGscyXlXFfux03iMXn+geD13v1P7h3Y/hH/aPAYH+0I3md/dY5fr/bBM+Jttm7PPchngjP/voPBFwy1h7YFtnc4zr9dJ6LJm1cEtue4npcTWFJX7ucDG9x9E4CZlQHDgSZN7pu25rjN1Tm4+bQewTem9m3J/YGTFScHfyb85K7BN7P+8nyXwPb2e4IvU5//aWnOsf1Q8EqMk6atDmzPJVeyhDxX1gE6HugQvOHkBh0GgKJ9nwts33NgT2D7GZ8J/tRn7aHgf+V3kTu5H/qkKrC9of/D7Nz/PwPbu7T9WwOP1HDHm8bJdXM2l9dmfC+wfXmv8YHtky4/q0HHl/iZ57q8jXJQsxHAle5+c+b9aOBL7n5HVp/xQP1vxtlA8GVzOF2BBk5IFrSWdr6gc24pdM4Nc4a7Bz6LK6krdwtoO+JfEXefDkyPZTCzCncvjuNYhaClnS/onFsKnXN8kvqEajVwetb7IiD4rpaIiMQuqeT+BtDPzPqYWVtgJFCe0FgiInKURKZl3P2gmd0B/D/qlkLOdPe3khgrI5bpnQLS0s4XdM4thc45JoncUBURkealqpAiIimk5C4ikkIFk9zN7Eoze9vMNpjZPQHb25nZnMz2FWbWu+mjjFeIc77TzCrNbI2ZLTaz5AvaJCzfOWf1G2FmbmYFv2wuzDmb2fWZn/VbZvZsU8cYtxC/273MbImZrcr8fgeX6SwQZjbTzLab2doc283MHsv891hjZudFHtTdT/gv6m7KbgT6Am2B/wb6H9XnduCXmdcjgTnNHXcTnPNQoEPm9bdawjln+p0MvAIsB4qbO+4m+Dn3A1YBnTLvuzd33E1wztOBb2Ve9wc2N3fcEc/5IuA8YG2O7cOABdR9RmgwsCLqmIVy5X64nIG77wfqyxlkGw7Mzrx+AbjUzII+TFUo8p6zuy9x908zb5dT93mCQhbm5wzw78BPgb1NGVxCwpzzLcA0d/8QwN2PUxSnIIQ5Zwfqa3t0pMA/J+PurwB/P06X4cDTXmc5cKqZ9YgyZqEk955Adjm+6kxbYB93PwjsBoILuRSGMOec7Sbq/uUvZHnP2cwGAqe7e8NrBZ+YwvyczwLOMrNXzWx5puJqIQtzzlOAb5hZNTAf+HbThNZsGvr/e16FUs89bzmDkH0KSejzMbNvAMXA/040ouQd95zN7CRgKnBjUwXUBML8nFtTNzVzMXV/nf2XmZ3j7rsSji0pYc55FDDL3R82syHAf2bOOa1P4Ik9fxXKlXuYcgaH+5hZa+r+lDven0EnulAlHMzsMuCHQIm772ui2JKS75xPBs4BlprZZurmJssL/KZq2N/tee5+wN3foa7IXr8mii8JYc75JuA5AHd/DWhPUzxctvnEXrKlUJJ7mHIG5cDYzOsRwJ88c6eiQOU958wUxX9Ql9gLfR4W8pyzu+92967u3tvde1N3n6HE3SuaJ9xYhPnd/h11N88xs67UTdNsatIo4xXmnN8FLgUws89Tl9xrmjTKplUOjMmsmhkM7Hb34IcEhNXcd5EbcLd5GLCeurvsP8y03U/d/9xQ98N/HtgAvA70be6Ym+CcFwEfAKszX+XNHXPS53xU36UU+GqZkD9nAx6h7nkIbwIjmzvmJjjn/sCr1K2kWQ18pbljjni+pcA24AB1V+k3AbcBt2X9jKdl/nu8GcfvtcoPiIikUKFMy4iISAMouYuIpJCSu4hICim5i4ikkJK7iEgKKbmLiKSQkruISAr9fwPre0Ove20fAAAAAElFTkSuQmCC\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "bins = np.linspace(0, 1, 50)\n",
    "\n",
    "\n",
    "## get this with a log-y axis!\n",
    "for A_case, d in data[data['N'] == 2000].groupby('A'):\n",
    "    plt.hist(\n",
    "        d['infected_ratio'],\n",
    "        bins,\n",
    "        alpha=.5,\n",
    "        label=A_case)\n",
    "\n",
    "\n",
    "plt.legend()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "## This doesn't work any more because of new data efficiencies\n",
    "\n",
    "##g = results_2000['A-0.000'][0][2]\n",
    "##bins = np.linspace(0, len(g.nodes()), 50)\n",
    "\n",
    "##for case in results_2000:\n",
    "##    plt.plot(\n",
    "##        model.average_over_time(results_2000[case], infected=True) / N,\n",
    "##        alpha=.8,\n",
    "##        label=case)\n",
    "    \n",
    "##plt.legend()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[Text(0, 0.5, 'average final infected ratio'), Text(0.5, 0, 'adoption rate')]"
      ]
     },
     "execution_count": 7,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "data[\"N-cat\"] = data[\"N\"].apply(lambda x: f\"N = {x}\")\n",
    "\n",
    "splot = sns.lineplot(x='A', y='infected_ratio', hue=\"N-cat\", data=data)\n",
    "\n",
    "splot.set(#xscale=\"log\",\n",
    "          xlabel='adoption rate',\n",
    "          ylabel='average final infected ratio')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [],
   "source": [
    "d4000 = data[data['N'] == 4000]\n",
    "d = d4000[d4000['A'] == 0.0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(array([100.,   0.,   0.,   0.,   0.,   0.,   0.,   6.,  51.,  43.]),\n",
       " array([2.50000e-04, 6.95250e-02, 1.38800e-01, 2.08075e-01, 2.77350e-01,\n",
       "        3.46625e-01, 4.15900e-01, 4.85175e-01, 5.54450e-01, 6.23725e-01,\n",
       "        6.93000e-01]),\n",
       " <a list of 10 Patch objects>)"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "plt.hist(d['infected_ratio'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "ename": "TypeError",
     "evalue": "cannot compare a dtyped [float64] array with a scalar of type [bool]",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mTypeError\u001b[0m                                 Traceback (most recent call last)",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/pandas/core/ops/__init__.py\u001b[0m in \u001b[0;36mna_op\u001b[0;34m(x, y)\u001b[0m\n\u001b[1;32m   1253\u001b[0m         \u001b[0;32mtry\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m-> 1254\u001b[0;31m             \u001b[0mresult\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mop\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mx\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0my\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m   1255\u001b[0m         \u001b[0;32mexcept\u001b[0m \u001b[0mTypeError\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/pandas/core/ops/roperator.py\u001b[0m in \u001b[0;36mrand_\u001b[0;34m(left, right)\u001b[0m\n\u001b[1;32m     52\u001b[0m \u001b[0;32mdef\u001b[0m \u001b[0mrand_\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mleft\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mright\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 53\u001b[0;31m     \u001b[0;32mreturn\u001b[0m \u001b[0moperator\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mand_\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mright\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mleft\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     54\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;31mTypeError\u001b[0m: ufunc 'bitwise_and' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''",
      "\nDuring handling of the above exception, another exception occurred:\n",
      "\u001b[0;31mValueError\u001b[0m                                Traceback (most recent call last)",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/pandas/core/ops/__init__.py\u001b[0m in \u001b[0;36mna_op\u001b[0;34m(x, y)\u001b[0m\n\u001b[1;32m   1268\u001b[0m                 \u001b[0;32mtry\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m-> 1269\u001b[0;31m                     \u001b[0mresult\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mlibops\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mscalar_binop\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mx\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0my\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mop\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m   1270\u001b[0m                 except (\n",
      "\u001b[0;32mpandas/_libs/ops.pyx\u001b[0m in \u001b[0;36mpandas._libs.ops.scalar_binop\u001b[0;34m()\u001b[0m\n",
      "\u001b[0;31mValueError\u001b[0m: Buffer dtype mismatch, expected 'Python object' but got 'double'",
      "\nDuring handling of the above exception, another exception occurred:\n",
      "\u001b[0;31mTypeError\u001b[0m                                 Traceback (most recent call last)",
      "\u001b[0;32m<ipython-input-14-c110bd5b87da>\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[0;32m----> 1\u001b[0;31m \u001b[0mplt\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mhist\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mdata\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0mdata\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'N'\u001b[0m\u001b[0;34m]\u001b[0m \u001b[0;34m==\u001b[0m \u001b[0;36m4000\u001b[0m \u001b[0;34m&\u001b[0m \u001b[0mdata\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'A'\u001b[0m\u001b[0;34m]\u001b[0m \u001b[0;34m==\u001b[0m \u001b[0;36m0.2\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'infected_ratio'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/pandas/core/ops/__init__.py\u001b[0m in \u001b[0;36mwrapper\u001b[0;34m(self, other)\u001b[0m\n\u001b[1;32m   1319\u001b[0m         \u001b[0;31m#   integer dtypes.  Otherwise these are boolean ops\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m   1320\u001b[0m         \u001b[0mfiller\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mfill_int\u001b[0m \u001b[0;32mif\u001b[0m \u001b[0mis_self_int_dtype\u001b[0m \u001b[0;32mand\u001b[0m \u001b[0mis_other_int_dtype\u001b[0m \u001b[0;32melse\u001b[0m \u001b[0mfill_bool\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m-> 1321\u001b[0;31m         \u001b[0mres_values\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mna_op\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mvalues\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0movalues\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m   1322\u001b[0m         \u001b[0munfilled\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_constructor\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mres_values\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mindex\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mindex\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mname\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mres_name\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m   1323\u001b[0m         \u001b[0mfilled\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mfiller\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0munfilled\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/pandas/core/ops/__init__.py\u001b[0m in \u001b[0;36mna_op\u001b[0;34m(x, y)\u001b[0m\n\u001b[1;32m   1278\u001b[0m                         \u001b[0;34m\"cannot compare a dtyped [{dtype}] array \"\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m   1279\u001b[0m                         \"with a scalar of type [{typ}]\".format(\n\u001b[0;32m-> 1280\u001b[0;31m                             \u001b[0mdtype\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mx\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mdtype\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mtyp\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mtype\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0my\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m__name__\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m   1281\u001b[0m                         )\n\u001b[1;32m   1282\u001b[0m                     )\n",
      "\u001b[0;31mTypeError\u001b[0m: cannot compare a dtyped [float64] array with a scalar of type [bool]"
     ]
    }
   ],
   "source": [
    "plt.hist(data[data['N'] == 4000 & data['A'] == 0.2]['infected_ratio'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "data[\"A^2\"] = data[\"A\"].apply(lambda x: x ** 2)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "[Text(0, 0.5, 'average final infected ratio'), Text(0.5, 0, 'adoption rate^2')]"
      ]
     },
     "execution_count": 25,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "splot = sns.lineplot(x='A^2', y='infected_ratio', hue=\"N-cat\", data=data)\n",
    "\n",
    "splot.set(#xscale=\"log\",\n",
    "          xlabel='adoption rate^2',\n",
    "          ylabel='average final infected ratio')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([1000, 2000, 4000])"
      ]
     },
     "execution_count": 17,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "data[\"N\"].unique()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Finding the inflection point\n",
    "\n",
    "Trying to find the inflection point. (What if there isn't one?)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "epidemic_size = data[data[\"N\"] == 2000].groupby(\"A\")['infected_ratio'].mean()\n",
    "\n",
    "x = epidemic_size.index\n",
    "y = epidemic_size.values"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [],
   "source": [
    "df1 = np.gradient(epidemic_size.values,\n",
    "            epidemic_size.index,\n",
    "            edge_order = 1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "array([ 3.138625 ,  1.1521875, -1.7994375, -0.2449375,  0.423125 ,\n",
       "       -1.1945625,  1.0626875,  2.4206875,  1.047375 ,  0.2375   ,\n",
       "        0.135625 ])"
      ]
     },
     "execution_count": 20,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "np.gradient(df1, epidemic_size.index, edge_order = 1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "Float64Index([0.6, 0.3, 0.0, 0.5, 0.4, 0.2, 0.7, 0.1, 0.8, 0.9, 1.0], dtype='float64', name='A')"
      ]
     },
     "execution_count": 21,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "x[np.argsort(df1)]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(0.0, 0.27944750000000007)"
      ]
     },
     "execution_count": 22,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "model.inflection_point(x,y)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "ename": "IndexError",
     "evalue": "tuple index out of range",
     "output_type": "error",
     "traceback": [
      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[0;31mIndexError\u001b[0m                                Traceback (most recent call last)",
      "\u001b[0;32m<ipython-input-23-d0d1dfa5badf>\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[0;32m----> 1\u001b[0;31m \u001b[0mplt\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mplot\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mx\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0my\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/matplotlib/pyplot.py\u001b[0m in \u001b[0;36mplot\u001b[0;34m(scalex, scaley, data, *args, **kwargs)\u001b[0m\n\u001b[1;32m   2793\u001b[0m     return gca().plot(\n\u001b[1;32m   2794\u001b[0m         *args, scalex=scalex, scaley=scaley, **({\"data\": data} if data\n\u001b[0;32m-> 2795\u001b[0;31m         is not None else {}), **kwargs)\n\u001b[0m\u001b[1;32m   2796\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m   2797\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/matplotlib/axes/_axes.py\u001b[0m in \u001b[0;36mplot\u001b[0;34m(self, scalex, scaley, data, *args, **kwargs)\u001b[0m\n\u001b[1;32m   1664\u001b[0m         \"\"\"\n\u001b[1;32m   1665\u001b[0m         \u001b[0mkwargs\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mcbook\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mnormalize_kwargs\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mkwargs\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mmlines\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mLine2D\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_alias_map\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m-> 1666\u001b[0;31m         \u001b[0mlines\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0;34m[\u001b[0m\u001b[0;34m*\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_get_lines\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m*\u001b[0m\u001b[0margs\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mdata\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mdata\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0;34m**\u001b[0m\u001b[0mkwargs\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m   1667\u001b[0m         \u001b[0;32mfor\u001b[0m \u001b[0mline\u001b[0m \u001b[0;32min\u001b[0m \u001b[0mlines\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m   1668\u001b[0m             \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0madd_line\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mline\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/matplotlib/axes/_base.py\u001b[0m in \u001b[0;36m__call__\u001b[0;34m(self, *args, **kwargs)\u001b[0m\n\u001b[1;32m    223\u001b[0m                 \u001b[0mthis\u001b[0m \u001b[0;34m+=\u001b[0m \u001b[0margs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;36m0\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m,\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    224\u001b[0m                 \u001b[0margs\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0margs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;36m1\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 225\u001b[0;31m             \u001b[0;32myield\u001b[0m \u001b[0;32mfrom\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_plot_args\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mthis\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mkwargs\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    226\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    227\u001b[0m     \u001b[0;32mdef\u001b[0m \u001b[0mget_next_color\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
      "\u001b[0;32m~/anaconda3/lib/python3.6/site-packages/matplotlib/axes/_base.py\u001b[0m in \u001b[0;36m_plot_args\u001b[0;34m(self, tup, kwargs)\u001b[0m\n\u001b[1;32m    397\u001b[0m             \u001b[0mfunc\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_makefill\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    398\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 399\u001b[0;31m         \u001b[0mncx\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mncy\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mx\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mshape\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;36m1\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0my\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mshape\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;36m1\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    400\u001b[0m         \u001b[0;32mif\u001b[0m \u001b[0mncx\u001b[0m \u001b[0;34m>\u001b[0m \u001b[0;36m1\u001b[0m \u001b[0;32mand\u001b[0m \u001b[0mncy\u001b[0m \u001b[0;34m>\u001b[0m \u001b[0;36m1\u001b[0m \u001b[0;32mand\u001b[0m \u001b[0mncx\u001b[0m \u001b[0;34m!=\u001b[0m \u001b[0mncy\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    401\u001b[0m             cbook.warn_deprecated(\n",
      "\u001b[0;31mIndexError\u001b[0m: tuple index out of range"
     ]
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "plt.plot(x, y)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.plot(x, df1)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.9"
  },
  "latex_envs": {
   "LaTeX_envs_menu_present": true,
   "autoclose": false,
   "autocomplete": true,
   "bibliofile": "biblio.bib",
   "cite_by": "apalike",
   "current_citInitial": 1,
   "eqLabelWithNumbers": true,
   "eqNumInitial": 1,
   "hotkeys": {
    "equation": "Ctrl-E",
    "itemize": "Ctrl-I"
   },
   "labels_anchors": false,
   "latex_user_defs": false,
   "report_style_numbering": false,
   "user_envs_cfg": false
  },
  "toc": {
   "base_numbering": 1,
   "nav_menu": {},
   "number_sections": true,
   "sideBar": true,
   "skip_h1_title": false,
   "title_cell": "Table of Contents",
   "title_sidebar": "Contents",
   "toc_cell": false,
   "toc_position": {},
   "toc_section_display": true,
   "toc_window_display": false
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
