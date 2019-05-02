from tristanSim  import TristanSim
import yaml, os
import matplotlib.pyplot as plt
import numpy as np

yamlFile='config.yaml'
with open(yamlFile, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        #print(config)
    except yaml.YAMLError as exc:
        print(exc)
        
#outdir = config['ROOT_DIRECTORY']

outdir = '../batchTristan'

runs = []
# runs will be a list a tristan simulations instances 
# that reside in outdir


# So any run can be accessed as run5 = runs[4]
# to access the output time e.g. 3rd output, run5Time3 = runs[4].output[2]

runNames = [] #the directory name that automater created.
for elm in os.listdir(outdir):
    elm = os.path.join(outdir, elm)
    if os.path.isdir(elm):
        elm = os.path.join(elm,'output')
        if os.path.exists(elm):
            runs.append(TristanSim(elm))
            runNames.append(os.path.split(os.path.split(elm)[0])[-1])

# TristanSim is an object that exposes an API to access tristan.
# The cool thing is nothing is loaded until it is accessed for 
# first time, then it is cached.

# fields are accessed via sim.output[n].ex [ex, ey, ez, bx, by, bz, dens...]
# particle values are accessed like sim.output[n].ions.x or sim.output[n].lecs.y etc..

# Here's an example of plotting the 5th time step of ex of each run
# in a 3 x 3 grid. Because of how I set up the searcher, all are at the
# same physical time.

fig = plt.figure()
axes = fig.subplots(3,3).flatten()
#print(axes)
j = 0
for run, name in zip(runs, runNames):
    ax = axes[j]
    istep = run.output[4].istep
    comp = run.output[4].comp
    ex = run.output[4].ex[0,:,:]
    ax.imshow(ex,extent=(0, ex.shape[1]*istep/comp, 0, ex.shape[0]*istep/comp), origin = 'lower')
    ax.set_title(name)
    #plt.colorbar()
    j += 1
    if j == 18:
        break
#plt.savefig('test.png')
plt.show()


### As another example, let's plot all the total electron energy
## as function of time for each run

# I know I changed c_omp, ntimes and ppc. get from YAML

c_omp_val = config['paramOpts']['c_omp']
ppc_val = config['paramOpts']['ppc0']
ntimes_val = config['paramOpts']['ntimes']

# Some arrays that change what the lines will look like
ms = ['.', 'x', '4', '8']
ls = ['-', '--', ':', '-.']
color = ['b', 'r', 'g', 'y']

fig = plt.figure()
for run in runs:
    # we don't want to count the fast moving particles towards our KE average
    plt.plot([o.time for o in run.output], [np.average(o.lecs.KE[o.lecs.index>0]) for o in run.output],
             c = color[ppc_val.index(run.output[0].ppc0)],
             linestyle = ls[ntimes_val.index(run.output[0].ntimes)],
             marker = ms[c_omp_val.index(run.output[0].comp)], markersize = 10)
plt.show()


###
#
# EXAMPLE OF TRACKING PARTICLES
#
###

# you'll find all of the tracked particles in a trackedLecs and 
# trackedIon object. The first call builds the database which may take
# awhile. It is saved afterwards. Let's plot a single tracked electron
# for these runs we didn't track the ions. 

# Let's focus just on one run for simplicity

myRun = runs[0]


# plot t vs gamma for a random prtl
choice = np.random.randint(len(myRun.trackedLecs))
randPrtl = myRun.trackedLecs[choice]
# Each prtl has the following attributes: 'x', 'y', 'u', 'v', 'w', 
# 'gamma', 'bx', 'by', 'bz', 'ex', 'ey', 'ez'
plt.plot(randPrtl.t, randPrtl.gamma)
plt.show()

# This is nice, but let's say you want to find the 10 highest energy
# prtls you saved.

# First sort by energy. You can pass any function here
myRun.trackedLecs.sort(lambda x: np.max(x.gamma))
# now plot the botton N
for prtl in myRun.trackedLecs[:-10]:
    plt.plot(prtl.t, prtl.gamma, 'lightgray')

for prtl in myRun.trackedLecs[-10:]:
    plt.plot(prtl.t, prtl.gamma, 'k')

plt.show()