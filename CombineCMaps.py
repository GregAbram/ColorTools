import numpy as np
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from cmap import *

def syntax(a):
    print('syntax: python %s pin1 pin2 left.xml center.xml right.xml' % a)
    print('where the pins are the transitions (0->1, pin1 < pin2)')
    print('and the xml files are the colormaps for the left, center and right sections')
    print('the output will be in an xml file with a name formed by')
    print('concatenating the input xml names')

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

cmap0 = load_cmap(cmap0)
cmap1 = load_cmap(cmap1)
cmap2 = load_cmap(cmap2)

def place(cmap, a, b):
    x = a + cmap[:,0]*(b - a)
    i = np.arange(0.0, 1.0, 1.0 / 256.0)
    r = np.interp(i, x, cmap[:,1], 0, 0)
    g = np.interp(i, x, cmap[:,2], 0, 0)
    b = np.interp(i, x, cmap[:,3], 0, 0)
    return (r,g,b)

r0 = place(cmap0, 0.0, pin1)
print(np.column_stack(r0))
r1 = place(cmap1, pin1, pin2)
r2 = place(cmap2, pin2, 1.0)
r = r0[0] + r1[0] + r2[0]
g = r0[1] + r1[1] + r2[1]
b = r0[2] + r1[2] + r2[2]

cmap = np.column_stack((np.arange(0.0, 1.0, 1.0 / 256.0), r, g, b))

save_cmap(cmap, oname + '.xml')



