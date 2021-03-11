#!/usr/bin/env python
# coding: utf-8

# In[213]:


import numpy as np
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


# In[214]:


def load_cmap(file):
    cmap = []
    if file[-3:] == 'xml':
        tree = ET.parse(file)
        root = tree.getroot()
        for i in root[0]:
            if i.tag == 'Point':
                row = [i.attrib['x'],i.attrib['r'],i.attrib['g'],i.attrib['b']]
                cmap.append([float(r) for r in row])
    cmap = np.array(cmap)
    x = cmap[:,0]
    x = (x - x[0]) / (x[-1] - x[0])
    return [x,cmap[:,1],cmap[:,2],cmap[:,3]]


# In[215]:


def syntax(a):
    print('syntax: python %s pin1 pin2 left.xml center.xml right.xml' % a)
    print('where the pins are the transitions (0->1, pin1 < pin2)')
    print('and the xml files are the colormaps for the left, center and right sections')
    print('the output will be in an xml file with a name formed by')
    print('concatenating the input xml names')


# In[216]:


if 1 == 1:
    if len(sys.argv) != 6:
        syntax(sys.argv[0])
        sys.exit(0)
    else:
        pin1 = float(sys.argv[1])
        pin2 = float(sys.argv[2])
        cmap0 = sys.argv[3]
        cmap1 = sys.argv[4]
        cmap2 = sys.argv[5]
else:
    pin1 = 0.3333
    pin2 = 0.6666
    cmap0 = '/Users/gda/stef/blue.xml'
    cmap1 = '/Users/gda/stef/orange.xml'
    cmap2 = '/Users/gda/stef/green.xml'

oname = '_'.join([i.rsplit('.',1)[0] for i in [cmap0, cmap1, cmap2]])


# In[218]:


cmap0 = load_cmap(cmap0)
cmap1 = load_cmap(cmap1)
cmap2 = load_cmap(cmap2)


# In[219]:


def place(cmap, a, b):
    x = a + cmap[0]*(b - a)
    i = np.arange(0.0, 1.0, 1.0 / 256.0)
    r = np.interp(i, x, cmap[1], 0, 0)
    g = np.interp(i, x, cmap[2], 0, 0)
    b = np.interp(i, x, cmap[3], 0, 0)
    return (r,g,b)


# In[220]:


r0 = place(cmap0, 0.0, pin1)
r1 = place(cmap1, pin1, pin2)
r2 = place(cmap2, pin2, 1.0)
r = r0[0] + r1[0] + r2[0]
g = r0[1] + r1[1] + r2[1]
b = r0[2] + r1[2] + r2[2]


# In[221]:


out = ET.Element('ColorMaps')

cmap = ET.SubElement(out, 'ColorMap', {'space': 'CIELAB', 'indexedLookup': 'false', 'name': oname})
for i,rgb in enumerate(zip(r, g, b)):
    ET.SubElement(cmap, "Point", {'x': str(i/256.0), 'r': str(rgb[0]), 'g': str(rgb[1]), 'b': str(rgb[2]), 'o': '1.0'})
ET.SubElement(cmap, 'NaN', {'r': '0', 'g': '0', 'b': '0'})

s = ET.tostring(out, 'utf-8') 
s = minidom.parseString(s)
s = s.toprettyxml(indent="  ")

f = open(oname + '.xml', 'w')
f.write(s)
f.close()


# In[ ]:





# In[ ]:




