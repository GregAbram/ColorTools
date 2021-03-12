import numpy as np
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

from cmap import *

def syntax(a):
    print('syntax: python %s pin1 pin2 frac left.xml center.xml right.xml' % a)
    print('where the pins are the transitions (0->1, pin1 < pin2)')
    print('frac is the ramp width between cmaps')
    print('and the xml files are the colormaps for the left, center and right sections')
    print('the output will be in an xml file with a name formed by')
    print('concatenating the input xml names')

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

oname = '_'.join([i.rsplit('.', 1)[0] for i in [cmap0, cmap1, cmap2]]) + '-ramp'

p0 = pin1 - (frac / 2.0)
p1 = pin1 + (frac / 2.0)
p2 = pin2 - (frac / 2.0)
p3 = pin2 + (frac / 2.0)
i = np.arange(0.0, 1.0, 1.0 / 256.0)
w0 = np.where(i < p0, 1.0, np.where(i < p1, 1 - (i - p0)/(p1 - p0), 0.0))
w1 = np.where(i < p0, 0, np.where(i < p1, (i - p0)/(p1 - p0), np.where(i < p2, 1, np.where(i < p3, 1 - (i - p2)/(p3 - p2), 0))))
w2 = np.where(i < p2, 0, np.where(i < p3, (i - p2)/(p3 - p2), 1))

cmap0 = load_cmap(cmap0)
cmap1 = load_cmap(cmap1)
cmap2 = load_cmap(cmap2)

def place(cmap, a, b):
    x = a + cmap[:,0]*(b - a)
    i = np.arange(0.0, 1.0, 1.0 / 256.0)
    r = np.interp(i, x, cmap[:,1])
    g = np.interp(i, x, cmap[:,2])
    b = np.interp(i, x, cmap[:,3])
    return (r,g,b)

r0 = place(cmap0, 0.0, p0)
r1 = place(cmap1, p1, p2)
r2 = place(cmap2, p3, 1.0)
r = r0[0]*w0 + r1[0]*w1 + r2[0]*w2
g = r0[1]*w0 + r1[1]*w1 + r2[1]*w2
b = r0[2]*w0 + r1[2]*w1 + r2[2]*w2

cmap = np.column_stack((np.arange(0.0, 1.0, 1.0 / 256.0), r, g, b))

save_cmap(cmap, oname + '.xml')
