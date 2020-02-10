###############################################################################
## load fur parameters from csv file
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.mel as mel

import os
from collections import OrderedDict

import cv2

from stNoh import RenderSetting
from stNoh import Fur
from stNoh import FurParam


###############################################################################
# main routine
###############################################################################
if "__main__" == __name__:

    ############################################################
    ## user specified parameters
    ############################################################
    folderPath = "C:/FurImages/Experiment2-Final/Sample01"
    imgFileExt = "jpg" ## file extension for rendered images
    image_W = 640
    image_H = 640

    ########################################
    ## default setting for rendering
    ########################################

    ## default values for 3D scene
    fur_desc   = "MyFurDescription"
    material   = "lambert1"

    ########################################
    ## load parameters & render images
    ########################################
    
    ## read parameters from csv files
    params_dict_geom  = FurParam.csv2dict( os.path.join(folderPath, "_best_geom.csv") )
    params_dict_color = FurParam.csv2dict( os.path.join(folderPath, "_best_color.csv") )

    ## set fur description
    Fur.SetFurDescription(fur_desc, params_dict_geom)
    Fur.SetFurDescription(fur_desc, params_dict_color)
    Fur.CopyFurBaseColor2Material(fur_desc, material)

    ## render images
    renderPath = "{0}/render/render".format(folderPath)
    RenderSetting.SetImageSize(image_W, image_H)
    RenderSetting.SetExportPath(renderPath, imgFileExt)
    mel.eval("RenderSequence;")
    
    ########################################
    ## make video using cv2
    ########################################
    renderPath = "{0}/render".format(folderPath)
    
    output = "{0}/output.avi".format(folderPath)
    print(output)
    writer = cv2.VideoWriter(output, cv2.cv.CV_FOURCC(*"MJPG"), 30, (image_W, image_H))

    img_files = next(os.walk(renderPath))[2]
    for img_file in img_files:
        img_path = os.path.join(renderPath, img_file)
        img = cv2.imread(img_path)
        
        ret = writer.write(img)
        
    #'''
        cv2.imshow("video_progess", img)
        cv2.waitKey(1)
    cv2.destroyWindow("video_progess")
    #'''

    writer.release()
