import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import seaborn as sns
from scipy.ndimage import interpolation
import random

from pprint import pprint




class featuresAnalyzer:
    def __init__(self, features, smoothing=1, remove_edges=True):
        self.features = features
        self.side = None
        self.angles = None
        self.angle_names = ['genou','coude','hanche','epaule','cheville']
        
        self.cut_none()
        self.get_side()
        self.extract_angles()
        self.smooth_angles(n=smoothing)
        if remove_edges:
            self.cut_edges(p=0.1)
        
    
    def cut_none(self):
        self.features = [f for f in self.features if f is not None]
    
    
    def get_side(self):
        viz_droit = sum([f['droit']['avg_viz'] for f in self.features])/len(self.features)
        viz_gauche = sum([f['gauche']['avg_viz'] for f in self.features])/len(self.features)
        print('viz droit : ',viz_droit)
        print('viz gauche : ',viz_gauche)
        self.side = 'droit' if viz_droit > viz_gauche else 'gauche'
        
        
    def extract_angles(self):
        self.angles = dict()
        for n in self.angle_names:
            self.angles[n] = np.array([f[self.side][n]['value'] for f in self.features])
        
        
    def smooth_angles(self, n=1):
        if n > 0:
            f = [2**i for i in range(n+1)]+[2**(n-i) for i in range(1,n+1)]
            f = [i/sum(f) for i in f]
            for n in self.angle_names:
                self.angles[n] = np.convolve(self.angles[n], f)
                self.angles[n] = self.angles[n][1:]
    
    
    def cut_edges(self, p=0.1):
        for n in self.angle_names:
            k = int(len(self.angles[n])*(p/2))
            self.angles[n] = self.angles[n][k:-k]


    def get_sats(self):
        STATS = dict()
        for n in self.angle_names:
            id_maxs = argrelextrema(self.angles[n], np.greater, order=5)[0] # indexes of maxs   
            signal_maxs = np.array([True if i in id_maxs else False for i in range(len(self.angles[n]))])
            avg_max = np.mean(self.angles[n][signal_maxs])
            
            id_mins = argrelextrema(self.angles[n], np.less, order=5)[0] # indexes of mins   
            signal_mins = np.array([True if i in id_mins else False for i in range(len(self.angles[n]))])
            avg_min = np.mean(self.angles[n][signal_mins])
            
            viz = np.mean(np.array([f[self.side][n]['viz'] for f in self.features]))
            
            STATS[n] = {'avg':np.mean(self.angles[n]),
                        'avg flexion' : avg_min,
                        'avg extension' : avg_max,
                        'avg amplitude' : avg_max-avg_min,
                        'viz' : viz}

        return STATS


    def extract_cycle(self, name='genou', cycle_length=None):
        """interpolate all series to same size, mean all of them"""
        # Reference signal
        ids = argrelextrema(self.angles['genou'], np.less, order=5)[0]
        signal = [True if i in ids else False for i in range(len(self.angles['genou']))]
        
        # Cut angles in cycles
        i = 0
        series = []
        cycle = []
        for i,s in enumerate(signal):
            if s:
                series.append(cycle)
                cycle = []
            cycle.append(self.angles[name][i])
        
        # Remove 1st and last
        series = series[1:-1]
        
        # Interpolate all series
        if cycle_length is None:
            cycle_length = sum([len(s) for s in series])//len(series)
        normalized_series = []
        for c in series:
            z = cycle_length/len(c)
            normalized_series.append(interpolation.zoom(c,z))
            if 0 in normalized_series[-1]:
                normalized_series = normalized_series[:-1]
        normalized_series = np.array(normalized_series)
        
        # Return mean and std
        mean_cycle = np.mean(normalized_series, axis=0)
        std_cycle = np.std(normalized_series, axis=0)
        
        return mean_cycle, std_cycle




def compare_cycles_hist(fa_ref : featuresAnalyzer, fa : featuresAnalyzer):
    for n in fa_ref.angle_names:
        a = fa_ref.angles[n]
        b = fa.angles[n]
        mean_a, std_a = fa_ref.extract_cycle(name=n)
        mean_b, std_b = fa.extract_cycle(name=n, cycle_length=len(mean_a))

        # Histogram
        plt.subplot(2,1,1)
        sns.histplot(a, kde=True, label='ref', color='blue')
        sns.histplot(b, kde=True, label='sample', color='orange')
        plt.xlabel('angle_'+n)
        plt.legend()
        
        # Cycle
        plt.subplot(2,1,2)
        plt.plot(mean_a, alpha=1, color='blue', label='ref')
        plt.plot(mean_a+2*std_a, alpha=0.2, color='blue')
        plt.plot(mean_a-2*std_a, alpha=0.2, color='blue')
        plt.plot(mean_b, alpha=1, color='orange', label='sample')
        plt.plot(mean_b+2*std_b, alpha=0.2, color='orange')
        plt.plot(mean_b-2*std_b, alpha=0.2, color='orange')
        plt.xlabel('time (frames)')
        plt.ylabel('angle_'+n)
        plt.legend()
        plt.show()
        
        
def compare_cycles(fa_ref : featuresAnalyzer, fa : featuresAnalyzer, thresh=1):
    groups = [['lower body',['genou','cheville']], ['upper body',['hanche','epaule','coude']]]
    
    for g_name, g in groups:
        fig, ax = plt.subplots(len(g),1)
        
        for i,n in enumerate(g):
            a = fa_ref.angles[n]
            b = fa.angles[n]
            mean_a, std_a = fa_ref.extract_cycle(name=n)
            mean_b, std_b = fa.extract_cycle(name=n, cycle_length=len(mean_a))

            # Plot curves
            ax[i].plot(mean_a, alpha=1, color='black', linestyle='--', label='ref')
            ax[i].plot(mean_b, alpha=1, color='blue', label='sample')

            # Color zones
            red = np.array([montecarlo_sup(mean_a[x], std_a[x], mean_b[x], std_b[x], n=1000) for x in range(len(mean_a))])
            red = red>thresh
            for x in range(len(red)-1):
                if red[x]:
                    ax[i].axvspan(x, x+1, alpha=0.2, color='red', linewidth=0)
            green = np.array([montecarlo_inf(mean_a[x], std_a[x], mean_b[x], std_b[x], n=1000) for x in range(len(mean_a))])
            green = green>thresh            
            for x in range(len(red)-1):
                if green[x]:
                    ax[i].axvspan(x, x+1, alpha=0.2, color='green', linewidth=0)

            # Labelling
            ax[i].set_ylabel('angle_'+n)
            
        ax[0].set_title(f'pedaling cycle angles ({g_name} group)')
        ax[-1].set_xlabel('time (frames)')
        ax[0].legend()
        plt.show()



def montecarlo_sup(meana, stda, meanb, stdb, n=1000):
    dista = np.random.normal(meana, stda, n)
    distb = np.random.normal(meanb, stdb, n)
    return sum(dista>distb)/n

def montecarlo_inf(meana, stda, meanb, stdb, n=1000):
    dista = np.random.normal(meana, stda, n)
    distb = np.random.normal(meanb, stdb, n)
    return sum(dista<distb)/n



if __name__ == '__main__':    
    print('\n# Reference stats')
    with open('features/features_ref_cut_11.p','rb') as f:
        features = pickle.load(f)
    fa1 = featuresAnalyzer(features, smoothing=2)
    pprint(fa1.get_sats())

    print('\n# My stats')
    with open('features/features_test_TT.p','rb') as f:
        features = pickle.load(f)
    fa2 = featuresAnalyzer(features, smoothing=2)
    pprint(fa2.get_sats())
    
    compare_cycles(fa1, fa2, thresh=0.75)



    
    
