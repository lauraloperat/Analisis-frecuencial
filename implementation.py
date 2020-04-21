"""
@author: Brayan Hoyos Madera, Universidad de Antioquia, leobahm72@gmail.com
"""

#Importing libaries
from scipy.io import loadmat
from qeeg_psd_chronux import qeeg_psd_chronux
from time import time

#load the data.
data = loadmat("../Datos_filtrados.mat")
#get information
fs = data["fs"]
data = data["data"]

star = time()
#calculate of bands of power
d, t, a1, a2, a, b, g, i = qeeg_psd_chronux(data[3,:,:], fs)
print("time of execution: {0} seconds".format(time()-star))#time of execution
print("""
Delta band power: {0}
Theta band power: {1}
Alpha 1 band power: {2}
Alpha 2 band power: {3}
Alpha band power: {4}
Beta band power: {5}
Gamma band power: {6}
""".format(d, t, a1, a2, a, b, g))


