###############################################################################
## Miscellaneous subroutines for fur rendering
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds
import maya.mel  as mel

from datetime import datetime

import cv2

from stNoh import Fur
from stNoh import FurParam
from stNoh import RenderSetting


###############################################################################
## subroutine: show rendered image by cv2.highgui
###############################################################################
def show_text_on_image_cv2(img_cv2, text, winTitle="temp"):
    y0, dy = 30, 30
    for i, line in enumerate(text.split('\n')):
        y = y0 + i * dy
        cv2.putText(img_cv2, line, (10, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,255,0), 2)

    cv2.imshow(winTitle, img_cv2)
    cv2.waitKey(1)
    return None


###############################################################################
## wrapper class for rendering MayaFur
###############################################################################
class FurRenderer:

    ############################################################
    ## ctor / dtor
    ############################################################
    def __init__(self):

        ## default image size as QHD
        self.imageW_px  = 960
        self.imageH_px  = 540
        self.imgFileExt = "jpg" ## default file extension for rendered image

        ## default setting
        self.fur_desc = "MyFurDescription"
        self.material = "lambert1"
        self.camera   = "RenderCam1"
        pass

    def __del__(self):
        Fur.InitFurDescription(self.fur_desc)
        Fur.CopyFurBaseColor2Material(self.fur_desc, self.material)
        pass

    ############################################################
    ## member functions
    ############################################################

    ## change image size & extension
    def SetImageFormat(self, imageW_px, imageH_px, imgFileExt="jpg"):
        self.imageW_px  = imageW_px
        self.imageH_px  = imageH_px
        self.imgFileExt = imgFileExt
        return None

    ## initialize renderer setting
    def Init(self, folder_path):

        ## limit to single view as reference
        RenderSetting.SetRenderer("mayaSoftware")
        RenderSetting.SetImageSize(self.imageW_px, self.imageH_px)
        RenderSetting.SetExportPath(folder_path, self.imgFileExt)
        cmds.setAttr("defaultRenderGlobals.animation", 0) # activate "(Single frame)"
        cmds.currentTime(1)

        ## standby rendering window
        cmds.select(cl=True)
        cmds.select(self.camera)
        cam = cmds.ls(sl=True)
        cmds.select(cl=True)
        RenderSetting.Snapshot(cam)

        return None
    
    ## render image & read (BGR format)
    def RenderFur(self, params_dict, img_path, exportCSV=True):

        ## assign fur parameters
        Fur.SetFurDescription(self.fur_desc, params_dict)
        Fur.CopyFurBaseColor2Material(self.fur_desc, self.material)

        t_render_start = datetime.now()

        ## export single frame as image
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", img_path, type="string")
        mel.eval('renderWindowRenderCamera "render" renderView '+"{0}".format(self.camera)+";")

        t_render_end = datetime.now()
        t_render_elapsed = t_render_end - t_render_start

        t_imageio_start = datetime.now()

        ## export parameter as CSV file if needed
        if exportCSV:
            csv_file = img_path + ".csv"
            FurParam.dict2csv(params_dict, csv_file)
        
        ## read rendered image for further processing
        img_file = img_path + "_tmp." + self.imgFileExt
        img_cv2  = cv2.imread(img_file)

        t_imageio_end = datetime.now()
        t_imageio_elapsed = t_imageio_end - t_imageio_start

        return img_cv2, t_render_elapsed, t_imageio_elapsed
