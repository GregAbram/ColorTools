import numpy as np
import json, sys, png
from vtk import *
from vtk.numpy_interface import dataset_adapter as dsa
import cmap

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print('syntax: cmap ffile [variable]')
    sys.exit(1)
else:
    colormap = sys.argv[1]
    input_file = sys.argv[2]

cmap = cmap.load_cmap(colormap)

if input_file[-3:] == 'png':

  rdr = png.Reader(input_file)
  a = rdr.read()
  pix = np.array(list(a[2]))

  r = pix[:,0::3].astype('f4')
  g = pix[:,1::3].astype('f4')
  data = (r * 65536) + (g * 256)

  b = pix[:,2::3]
  data = np.where(b > 0, np.nan, data)

  n_rows,n_cols = data.shape[:2]

else:

  if len(sys.argv) != 4:
    print('syntax: cmap ffile variable')
    sys.exit(1)

  var = sys.argv[3]

  reader = vtkGenericDataObjectReader()
  reader.SetFileName(input_file)
  reader.Update()
  vtkobject = reader.GetOutput()
  npobject = dsa.WrapDataObject(vtkobject)

  n_rows, n_cols = vtkobject.GetDimensions()[:2]

  if var in npobject.CellData.keys():
    data = np.array(npobject.CellData[var]).astype('f4')
    n_rows = n_rows - 1
    n_cols = n_cols - 1
  elif var in npobject.PointData.keys():
    data = np.array(npobject.PointData[var]).astype('f4')
  else:
    print('can\'t find variable')
    sys.exit(1)

  data = data.reshape(n_rows, n_cols)

xmin = np.nanmin(data)
xmax = np.nanmax(data)

x = cmap[:,0]
x = xmin + ((x - x[0]) / (x[-1] - x[0]))*(xmax - xmin)

R = np.where(np.isnan(data), 0.0, np.interp(data, x, cmap[:,1])).flatten()
G = np.where(np.isnan(data), 0.0, np.interp(data, x, cmap[:,2])).flatten()
B = np.where(np.isnan(data), 0.0, np.interp(data, x, cmap[:,3])).flatten()

pixels = np.column_stack((R,G,B)).reshape((n_rows, 3*(n_cols)))

f = open('colored-' + input_file.rsplit('.', 1)[0] + '.png', 'wb')
w = png.Writer(n_cols, n_rows, greyscale=False)
w.write(f, (pixels*255).astype('u1'))
f.close()

