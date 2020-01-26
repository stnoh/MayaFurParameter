###############################################################################
## generate fur images
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds
import maya.mel as mel

import numpy as np
import os

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
    
    ## where csv files exist
    folderPath = "C:/FurImages/Experiment1-CGSamples/_References_960x540"
    imgFileExt = "jpg" ## file extension for rendered images

    ########################################
    ## default setting for rendering
    ########################################

    ## default values for 3D scene
    fur_desc   = "MyFurDescription"
    material   = "lambert1"
    cam_name   = "RenderCam1"
    patch_name = "pPlane_Fur"

    ## only a single oblique-view
    RenderSetting.SetFrameRange(1, 1)
    cmds.setAttr("defaultRenderGlobals.animation", 0) # activate "(Single frame)"

    ########################################
    ## 1) get not-rendered csv file list
    ########################################

    ## get the file list
    files = next(os.walk(folderPath))[2]

    ## filter-out already rendered images
    img_files = [img_file for img_file in files if ".{0}".format(imgFileExt)==os.path.splitext(img_file)[1]]
    csv_files = [csv_file for csv_file in files
                 if ".csv"==os.path.splitext(csv_file)[1] and 
                 os.path.splitext(csv_file)[0]+".0001_tmp.{0}".format(imgFileExt) not in img_files]

    ## generate full path
    csv_list = [folderPath +'/'+csv_file for csv_file in csv_files]

    ########################################
    ## 2) prepare the fur image rendering
    ########################################

    ## initialize fur descriptor before generating fur images
    Fur.InitFurDescription(fur_desc)

    ## set default color for fur ...
    colors_dict = FurParam.ParamsColor
    Fur.SetFurDescription(fur_desc, colors_dict)
    Fur.CopyFurBaseColor2Material(fur_desc, material)

    ## stand-by rendering window
    mel.eval("RenderViewWindow;")
    cam = cmds.ls(cam_name)
    RenderSetting.Snapshot(cam) # activate RenderView
    
    ############################################################
    ## 3) rendering routine
    ############################################################

    ## set progress bar for abort
    abort = False
    cmds.progressWindow(isInterruptable=1, minValue=0, maxValue=len(csv_list))

    for n in range(0,len(csv_list)):
        csv_file = csv_list[n]

        ## load csv file & set fur parameters
        params_dict = FurParam.csv2dict(csv_file)
        Fur.SetFurDescription(fur_desc, params_dict)
        Fur.CopyFurBaseColor2Material(fur_desc, material)

        ## extract file 
        filePrefix = os.path.splitext(csv_file)[0]
        RenderSetting.SetExportPath(filePrefix, imgFileExt)

        ## render fur image
        mel.eval("RenderSequence;")

        ## abort the process by user interruption (ESC)
        cmds.progressWindow(edit=True, progress=(n+1)) 
        if cmds.progressWindow(query=1, isCancelled=1):
            abort = True
            break
        
        if abort: break

    cmds.progressWindow(endProgress=1)

    ############################################################
    ## 4) rollback fur sample status to the default
    ############################################################
    Fur.InitFurDescription(fur_desc)
    Fur.CopyFurBaseColor2Material(fur_desc, material)
