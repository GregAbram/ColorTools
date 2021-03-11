import numpy as np
import json, sys, png
from vtk import *
from vtk.numpy_interface import dataset_adapter as dsa

if len(sys.argv) != 5:
    print('syntax: min% max% cmap ffile')
    sys.exit(1)
else:
    LOWER = float(sys.argv[1])
    UPPER = float(sys.argv[2])
    colormap = sys.argv[3]
    input_file = sys.argv[4]

f = open(colormap)
jcmap = json.load(f)
f.close()

p = jcmap['colormaps'][0]['points']
xrgbo = [[i['x'],i['r'],i['g'],i['b'],i['o']] for i in p]
xrgbo = np.array(sorted(xrgbo, key = lambda a: a[0])).reshape(-1,5)
x = xrgbo[:,0]
rgb = xrgbo[:,1:4]

reader = vtkGenericDataObjectReader()
reader.SetFileName(input_file)
reader.Update()
vtkobject = reader.GetOutput()
npobject = dsa.WrapDataObject(vtkobject)
data = npobject.CellData.GetArray('mesh_topo/density')
data = np.nan_to_num(data, nan=np.nanmin(data))
n_rows, n_cols = vtkobject.GetDimensions()[:2]

xmin = np.min(data) + LOWER*(np.max(data) - np.min(data))
xmax = np.max(data) + UPPER*(np.max(data) - np.min(data))
x = xmin + ((x - x[0]) / (x[-1] - x[0]))*(xmax - xmin)

R = np.interp(data, x, rgb[:,0])
G = np.interp(data, x, rgb[:,1])
B = np.interp(data, x, rgb[:,2])

pixels = np.column_stack((R,G,B)).reshape((n_rows-1, 3*(n_cols-1)))

f = open(input_file.rsplit('.', 1)[0] + '.png', 'wb')
w = png.Writer(n_cols-1, n_rows-1, greyscale=False)
w.write(f, (pixels*255).astype('u1'))
f.close()

