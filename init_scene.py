###############################################################################
## initialize scene to reproduce calibrated sample images
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds
import maya.mel as mel

import numpy as np
from datetime import datetime

from stNoh import Calib3d
from stNoh import Fur
from stNoh import RenderSetting


###############################################################################
# subroutine
###############################################################################
def CreateLightSource(Light_name, dist, angle, size):
    cmds.CreateAreaLight()
    cmds.rename(Light_name)
    
    deg2rad = np.pi / 180.0
    ty = dist * np.cos(angle * deg2rad)
    tx = dist * np.sin(angle * deg2rad)
    sc = 0.5 * size

    cmds.setAttr("{0}.intensity".format(Light_name), 0.400)
    cmds.setAttr("{0}.tx".format(Light_name), tx)
    cmds.setAttr("{0}.ty".format(Light_name), ty)
    cmds.setAttr("{0}.rx".format(Light_name), -90.0)
    cmds.setAttr("{0}.rz".format(Light_name), -angle)
    cmds.setAttr("{0}.sx".format(Light_name), sc)
    cmds.setAttr("{0}.sy".format(Light_name), sc)
    cmds.setAttr("{0}.sz".format(Light_name), sc)

    return None

def CreateObliqueTransform(angle, tr_y, tr_z):
    rot = Calib3d.GetCameraTransform(angle, 0.0, 0.0)
    return (rot[0], rot[1], rot[2], 0.0, tr_y, tr_z)


###############################################################################
# main routine
###############################################################################
if "__main__" == __name__:

    ############################################################
    ## 3D scene setting 
    ############################################################

    ########################################
    ## i) camera
    ########################################

    ## camera paremeters in pixel metric 
    imageW_px = 960
    imageH_px = 540
    focalL_px = 735 # focal length from camera calibration

    ## camera views in animation [NOW: single-view only]
    trs = [CreateObliqueTransform(45.0, 17.50, 16.75)]

    ## set proper FoV for rendering camera
    focalLength_film = Calib3d.GetFocalLength_Maya(imageW_px, focalL_px)
    cam = cmds.camera(name="RenderCam")
    cmds.setAttr("{0}.fl".format(cam[0]), focalLength_film)

    ## view change per frame [NOT USED]
    frame_num = 0
    for tr in trs:

        # change current time
        frame_num += 1
        cmds.currentTime(frame_num, update=True)

        # assign transform to camera
        (rx, ry, rz, tx, ty, tz) = tr
        cmds.setAttr("{0}.rx".format(cam[0]), rx)
        cmds.setAttr("{0}.ry".format(cam[0]), ry)
        cmds.setAttr("{0}.rz".format(cam[0]), rz)
        cmds.setAttr("{0}.tx".format(cam[0]), tx)
        cmds.setAttr("{0}.ty".format(cam[0]), ty)
        cmds.setAttr("{0}.tz".format(cam[0]), tz)

        # fix this pose as keyframe
        cmds.setKeyframe()
    cmds.select(clear=True)

    ########################################
    ## ii) create a patch for fur base
    ########################################

    ## size: 15 x 15 [cm^2]
    FurPlane_root = cmds.polyPlane(name="pPlane_Fur", w=15, h=15, sx=32, sy=32)

    ## attach a fur description for this patch
    cmds.select("pPlane_Fur", r=True)
    mel.eval("AttachFurDescription;")
    cmds.rename("FurDescription1", "MyFurDescription")

    ########################################
    ## iii) create light sources
    ########################################
    CreateLightSource("areaLight_top"  , 30.0,   0.0, 25.0)
    cmds.setAttr(".intensity", 0.3) ## top is too bright ...
    cmds.select(clear=True)

    CreateLightSource("areaLight_left" , 30.0, -45.0, 25.0) # [for experiment]
    cmds.select(clear=True)

    CreateLightSource("areaLight_right", 30.0, +45.0, 25.0) # [for experiment]
    cmds.select(clear=True)

    ## turn-off left/right lights
    cmds.hide('areaLight_left')
    cmds.hide('areaLight_right')


    ############################################################
    ## renderer setting
    ############################################################
    RenderSetting.SetRenderer("mayaSoftware")
    RenderSetting.SetImageSize(imageW_px, imageH_px)
    RenderSetting.SetFrameRange(1, frame_num)
    RenderSetting.Snapshot(cam)

    ## set export path with image format
    datetime_now = datetime.now()
    filePath = "C:/FurImages/"+datetime_now.strftime("%Y%m%d")+"/rendered_"+datetime_now.strftime("%H%M")
    RenderSetting.SetExportPath(filePath, "jpg")

    mel.eval("colorManagementPrefs -edit -cmEnabled 0;") # turn off color management
