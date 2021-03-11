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
    print('syntax: python %s pin1 pin2 frac left.xml center.xml right.xml' % a)
    print('where the pins are the transitions (0->1, pin1 < pin2)')
    print('frac is the ramp width between cmaps')
    print('and the xml files are the colormaps for the left, center and right sections')
    print('the output will be in an xml file with a name formed by')
    print('concatenating the input xml names')


# In[216]:


if 1 == 1:
    if len(sys.argv) != 7:
        syntax(sys.argv[0])
        sys.exit(0)
    else:
        pin1 = float(sys.argv[1])
        pin2 = float(sys.argv[2])
        frac = float(sys.argv[3])
        cmap0 = sys.argv[4]
        cmap1 = sys.argv[5]
        cmap2 = sys.argv[6]
else:
    pin1 = 0.3333
    pin2 = 0.6666
    frac = 0.03
    cmap0 = '/Users/gda/stef/blue.xml'
    cmap1 = '/Users/gda/stef/orange.xml'
    cmap2 = '/Users/gda/stef/green.xml'

oname = '_'.join([i.rsplit('.', 1)[0] for i in [cmap0, cmap1, cmap2]])

# In[217]:


p0 = pin1 - (frac / 2.0)
p1 = pin1 + (frac / 2.0)
p2 = pin2 - (frac / 2.0)
p3 = pin2 + (frac / 2.0)
i = np.arange(0.0, 1.0, 1.0 / 256.0)
w0 = np.where(i < p0, 1.0, np.where(i < p1, 1 - (i - p0)/(p1 - p0), 0.0))
w1 = np.where(i < p0, 0, np.where(i < p1, (i - p0)/(p1 - p0), np.where(i < p2, 1, np.where(i < p3, 1 - (i - p2)/(p3 - p2), 0))))
w2 = np.where(i < p2, 0, np.where(i < p3, (i - p2)/(p3 - p2), 1))


# In[218]:


cmap0 = load_cmap(cmap0)
cmap1 = load_cmap(cmap1)
cmap2 = load_cmap(cmap2)


# In[219]:


def place(cmap, a, b):
    x = a + cmap[0]*(b - a)
    i = np.arange(0.0, 1.0, 1.0 / 256.0)
    r = np.interp(i, x, cmap[1])
    g = np.interp(i, x, cmap[2])
    b = np.interp(i, x, cmap[3])
    return (r,g,b)


# In[220]:


r0 = place(cmap0, 0.0, p0)
r1 = place(cmap1, p1, p2)
r2 = place(cmap2, p3, 1.0)
r = r0[0]*w0 + r1[0]*w1 + r2[0]*w2
g = r0[1]*w0 + r1[1]*w1 + r2[1]*w2
b = r0[2]*w0 + r1[2]*w1 + r2[2]*w2


# In[221]:


out = ET.Element('ColorMaps')

cmap = ET.SubElement(out, 'ColorMap', {'space': 'CIELAB', 'indexedLookup': 'false', 'name': oname + "-ramp"})
for i,rgb in enumerate(zip(r, g, b)):
    ET.SubElement(cmap, "Point", {'x': str(i/256.0), 'r': str(rgb[0]), 'g': str(rgb[1]), 'b': str(rgb[2]), 'o': '1.0'})
ET.SubElement(cmap, 'NaN', {'r': '0', 'g': '0', 'b': '0'})

s = ET.tostring(out, 'utf-8') 
s = minidom.parseString(s)
s = s.toprettyxml(indent="  ")

f = open(oname + '-ramp.xml', 'w')
f.write(s)
f.close()

