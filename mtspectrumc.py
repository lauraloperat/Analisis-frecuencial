"""
@author: Brayan Hoyos Madera, Universidad de Antioquia, leobahm72@gmail.com

Inspired by: Chronux Toolbox,  mtspectrumc.m.
"""

from math import ceil
from math import floor
from math import log
from numpy import arange
from numpy import float32
from numpy import size
from numpy import logical_and
from scipy.signal.windows import dpss
from numpy import sqrt
from numpy import ones
from numpy.fft import fft
from numpy import mean
from numpy import conj
from numpy import squeeze
from numpy import real

def row_to_columns(data):
    '''
    Function that change the samles to trials if the size of samples is 1 and
    trials is different from 1.

    :param data: numpy array, required.
        Data to evaluate

    :return data: numpy array.
        Modified data.
    '''
    (samples, trials) = data.shape
    if samples == 1 and trials != 1:
        data = data.transpose()
    return data
        
def getfgrid(fs, nfft, fpass):
    '''
    Helper function that generate the frequencies axes based on limits entered
    in the parameter fpass.
    
    :param fs: int or float, required.
        sampling frequency associated with the data
    :param nfft: int or float, required.
        number of point of window.
    :param fpass: list or tuple, required.
        band of frequencies at which the fft is being calculated.

    :return f: numpy array.
        Contains the frecuens obtained from the limits in fpass.
    :return find: numpy array.
        Contain the positions where the frequencies are in the range of fpass.
    '''
    if size(fpass) != 2:
        print("fpass dimensions must be [min, max].")
        return False
    df = fs/nfft #step
    f = arange(0,fs,df, dtype = float32)
    #get positions
    find = logical_and(f >= fpass[0], f <= fpass[1])
    #get frequencies
    f = f[find == True]
    return f, find

def get_params(params):
    '''
    Function that retriever the executions parameters and asigns default values
    of data that hs not been entered.

    :param params: dict, required.
        Dict that contain the executions parameters.

    :return tapers, pad, fs, fpass, err, trialave.
    '''
    #get the params
    tapers = params.get("tapers", [])
    pad = params.get("pad", 0)
    fs = params.get("fs", 1)
    fpass = params.get("fpass", [0, fs/2])
    err = params.get("err", 0)
    trialave = params.get("trialave", 0);
        
    if tapers == [] or size(tapers) != 3:
        print('tapers unspecified, defaulting to params.tapers=[3 5]')
        tapers = [3, 5]
    else:
        #Compute timebandwidth product
        TW = tapers[1]*tapers[0]
        #Compute number of tapers
        K  = floor(2*TW - tapers[2]);
        tapers = [TW, K]
    return tapers, pad, fs, fpass, err, trialave
        
        
    
def mtspectrumc(data, params):
    '''
    Function responsible for calculating Multi-taper spectrum.

    :param data: numpy array, required.
        2-D matrix [samples, trials]. It contains the data to process.
    :param params: dict, required.
        Contained the executions parameters and necessary constants for the 
        calculations of spectrum of the input data.
        params = dict(fs = srate, fpass = [lowpass, highpass], 
                        tapers = [2, 2, 1], trialave = 1)
        
    :return s: numpy array.
        Contain the aritmetic mean of the spectral power caculated with the fft.
    :return f: numpy array.
        Contains the frecuens obtained from the limits in fpass.    
    '''
    (samples, trials) = data.shape
    tapers, pad, fs, fpass, err, trialave = get_params(params)#get params
    nfft = 2**(ceil(log(samples,2)))#calculate dimensions of window
    f, find = getfgrid(fs, nfft, fpass)#get de frequencies
    #Calculate  a matrix of tapering windows
    tapers = dpss(samples, tapers[0], tapers[1]).transpose()
    tapers = tapers*sqrt(fs)
    #Resize the data to calculate the spectrum power with fft
    (r, c) = tapers.shape
    tapers = tapers.reshape((r, c, 1))
    matrix_one = ones((samples, c, trials), dtype = float32)
    tapers = tapers * matrix_one
    data = data.reshape((samples, trials, 1))
    matrix_one = ones((samples, trials, c), dtype = float32)
    data = (data*matrix_one).transpose(0,2,1)
    data_proj = data*tapers
    #calculate the spectrum power with fft
    j = fft(data_proj, nfft, axis = 0)/fs
    #getting the values.
    j = j[find == True, :, :]
    #Eliminate the imaginary part of the data.
    s = real(mean(conj(j)*j, axis=1))

    if trialave == 1: s = squeeze(mean(s,axis=1))
    else: s = squeeze(s)
    return s, f 
