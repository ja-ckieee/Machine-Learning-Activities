###################################################################################

# MACATANGAY, Alquea Pauline A.
# 2019-06538
# CoE197-M THY

###################################################################################

import numpy as np
import matplotlib.pylab as plt
from tkinter import *
from tkinter import filedialog
import os

srcPoints = []

# reads input image
def imageReader():
    global imgInput, imgH, imgW, dim, cid
    media = filedialog.askopenfile(mode='r', filetypes=[('PNG', '*.png'), ('JPG', '*.jpg'), ('JPEG', '*.jpeg')])
    if media:
        btnUpload.config(state='disabled')
        path = os.path.abspath(media.name)
        imgInput = plt.imread(path)
        imgH, imgW, dim = imgInput.shape
        cid = (plt.imshow(imgInput)).figure.canvas.mpl_connect('button_press_event', selectPoints)
        plt.show()
        np.array(srcPoints)

#mark points from mouse click and store them in an array
def selectPoints(event):
    if len(srcPoints) != 4:
        srcPoints.append([event.xdata, event.ydata])
        plt.plot(event.xdata, event.ydata, 'o')
    else:
        (plt.imshow(imgInput)).figure.canvas.mpl_disconnect(cid)
    (plt.imshow(imgInput)).figure.canvas.draw()

#arrange the points from top left -> top right -> bottom left -> bottom right
def sortPoints(coordinates):
    coordinates.sort(key = lambda x: x[1])
    top = [coordinates[0],coordinates[1]]
    top.sort()
    bot = [coordinates[2],coordinates[3]]
    bot.sort()
    return np.array([top[0],top[1], bot[0],bot[1]]) 

# coordinates for mapping after correction, from width and height of the original image
def destination():
    destPoints = np.array([(0,0),(imgW,0),(0,imgH),(imgW,imgH)])
    return destPoints

# get homography matrix that will be used in the correction
def homography():
    # https://www.cs.umd.edu/class/fall2019/cmsc426-0201/files/16_Homography-estimation-and-decomposition.pdf
    # https://cseweb.ucsd.edu/classes/wi07/cse252a/homography_estimation/homography_estimation.pdf

    # P and P' are 4x2 matrices, representing the coordinates of the points
    # P: corPoints from original image
    # P': destPoints 
    corPoints = sortPoints(srcPoints)
    destPoints = destination()
    
    # A: 2Nx9 matrix, N is the number of points
    N = 4
    A = np.empty((8,9))

    for i in range(N):
        corX, corY = corPoints[i][0], corPoints[i][1]
        desX, desY = destPoints[i][0], destPoints[i][1]
        A[i*2, :] = [corX, corY, 1, 0, 0, 0, -desX*corX, -desX*corY, -desX]
        A[i*2+1, :] = [0, 0, 0, corX, corY, 1, -desY*corX, -desY*corY, -desY]

        #A[i*2, :] = [desX, desY, 1, 0, 0, 0, -corX*desX, -corX*desY, -corX]
        #A[i*2+1, :] = [0, 0, 0, desX, desY, 1, -corY*desX, -corY*desY, -corY]

    # Homogeneous Linear Least Squares using SVD
    [u, s, vh] = np.linalg.svd(A)
    # get smallest singular value from vh, this is the coefficient of the homography
    H = vh[-1, :] /vh[-1, -1]
    # reshaping the coefficient to H
    H = np.reshape(H,(3,3))
    
    return H

# linear mapping to correct distortion
def toAffine():
    plt.close()
    H = homography()
    affineOut = np.zeros((imgH, imgW, dim))
    for y in range(affineOut.shape[0]):
        for x in range(affineOut.shape[1]):
            projection = np.dot(H, np.array([[x, y, 1]]).T)
            projX, projY = (projection[0][0] / projection[2][0]).astype(int), (projection[1][0] / projection[2][0]).astype(int)
            if (projX >= 0 and projX < imgW) and (projY >= 0 and projY < imgH):
                affineOut[projY][projX] = imgInput[y][x]

    f, axarr = plt.subplots(1,2)
    axarr[0].imshow(imgInput)
    axarr[1].imshow(affineOut.astype('uint8'))

    plt.show()

def Close():
    plt.close('all')
    window.destroy()

if __name__ == "__main__":
    window = Tk()
    window.title('Projective to Affine Correction')

    btnUpload = Button(window, text='   Upload image   ', command=imageReader)
    btnUpload.pack(pady=10)

    btnHomog = Button(window, text='   Correct image  ', command=toAffine)
    btnHomog.pack(pady=10)

    btnExit = Button(window, text='    Exit    ', command=Close)
    btnExit.pack(pady=10)
    
    window.mainloop()