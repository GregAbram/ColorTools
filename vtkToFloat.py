from vtk import *
import png
import numpy as np
from vtk.numpy_interface import dataset_adapter as dsa
import cv2
from matplotlib import pyplot as plt
import sys

SZ = 1024             # output resolution

# crop region
xmin = 140
xmax = 1908
ymin = 140
ymax = 1908

for infile in sys.argv[1:]:

    # First we read in the input vtk file to create a VTK object

    reader = vtkGenericDataObjectReader()
    reader.SetFileName(infile)
    reader.Update()
    vtkobject = reader.GetOutput()

    # Create a numpy wrapper for the vtk object - this makes 
    # accessing its internals much easier from Python

    npobject = dsa.WrapDataObject(vtkobject)

    # Access the one data array thats associated with the 
    # cells of the data.   Think of a chess board - 8x8 
    # squares separated by 9 vertical and 9 horizontal lines.
    # In VTK terms, this is a grid of 9x9 vertices defining
    # 8x8 cells.  Data can be associated with either the
    # places where the lines meet - the vertices - or the 
    # chessboard squares - the cells.  In this case, the data
    # is defined as a 2049 x 2049 grid defining 2048 x 2048
    # cells - and the data is defined on the cells.
    #
    # This returns a simple list of 2048x2048 values.

    data = npobject.CellData.GetArray('mesh_topo/density')

    # Exactly one data value is 'nan' - not a number - a pattern
    # of 32 bits that does not make sense as a floating point 
    # number.   This sometimes happens when a calculation 
    # includes a divide-by-zero - here, not sure why its there,
    # but it is.  So I replace that one value with the minimum
    # valid value of the dataset as a whole.   

    # data = np.nan_to_num(data, nan=np.nanmin(data))

    # log of data
    # data = np.log(data)

    # Get the dimensions of the VTK grid - in this case it'll
    # be 2049, 2049, 1 - see above.  We 'reshape' the data into a
    # 2048 x 2048 array.  This doesn't change the datavalues at all,
    # but we need to do this so that later stuff realized 

    i,j,k = vtkobject.GetDimensions()
    data = data.reshape((i-1,j-1))

    # And now we crop out the desired window of the data
    data = data[ymin:ymax,xmin:xmax]

    # Remove the comment characters - the hash symbols - on the
    # following lines to see the data

    # plt.imshow(data, cmap='gray')
    # plt.show()

    # Now we resample the data onto the 1048 x 1048 grid we want.
    # This filters the data so that the reduced resolution result
    # is as accurate as possible.

    data = cv2.resize(data, dsize=(SZ,SZ), interpolation=cv2.INTER_LANCZOS4)

    # Rescale the data first to 0 -> 1, then scale it to 65535 - the
    # largest integer representable in 16 bits.   The 'float image'
    # format uses each pixel's 8-bit red and blue channels as a single
    # 16 bit number, so we need to put the data into 16 bit form.  Note - 
    # this loses information - there are 65536 possible 16 bit numbers,
    # and a whole lot more possible floating point numbers.

    sdata = (((data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data))) * 65535).astype('u2')

    # This magic takes each 16 bit number and shifts it rights 8 bits -
    # that is, takes the upper 8 bits of each - and reinterprets as a
    # 8 bit number for the red channel.  This is then 'flattened' into
    # a simple list.

    red = np.right_shift(sdata, 8).astype('u1').flatten()

    # This magic takes each 16 bit number and takes only the *lower*
    # 8 bits and reinterprets it as a simple list of 8 bit numbers for
    # the green channel.

    green = (sdata % 256).astype('u1').flatten()

    # blue is the NAN flag

    blue = np.where(np.isnan(data), 255, 0).astype('u1').flatten()

    # Now we form the output pixels by combining the red and green channels
    # we set up above with a zero blue channel that we create by red - red.
    # The PNG code expects a simple list of (r,g,b) values.

    rgb = np.column_stack((red,green,blue)).reshape(-1,3*SZ)

    # and we write out the png file

    f = open('%s.png' % infile.rsplit('.')[0], 'wb')
    w = png.Writer(SZ,SZ,greyscale=False)
    w.write(f,rgb)
    f.close()
