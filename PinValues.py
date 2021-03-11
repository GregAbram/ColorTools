#!/usr/bin/env python
# coding: utf-8

# In[1]:


from vtk import *
import png
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
import cv2
from matplotlib import pyplot as plt
import sys


# In[ ]:


if 1 == 1:
    if (len(sys.argv) != 2):
        print("syntax: python %s file.vtk" % sys.argv[0])
        sys.exit(1)
    ifile = sys.argv[1]
else:
    ifile = '/Users/gda/stef/vtk/simple_icf_001688.vtk'   


# In[26]:


if 1 == 1:
    reader = vtkGenericDataObjectReader()
    reader.SetFileName(ifile)
    reader.Update()
    vtkobject = reader.GetOutput()
    npobject = dsa.WrapDataObject(vtkobject)
    data = npobject.CellData.GetArray('mesh_topo/density')
    data = data[~np.isnan(data)]


# In[28]:


histo = np.histogram(data, bins=10000)
chisto = np.cumsum(histo[0])
pin1 = histo[1][np.argmax(chisto > (len(data)/3))]
pin2 = histo[1][np.argmax(chisto > (2*len(data))/3)]
print(pin1 / np.max(data), pin2/np.max(data))


# In[ ]:




