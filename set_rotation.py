###############################################################################
## set rotate animation for selected object
## Author: Seung-Tak Noh (seungtak.noh@gmail.com)
###############################################################################
import maya.cmds as cmds
from stNoh import RenderSetting

## set rotation (Y-axis) on SELECTED object
obj = cmds.ls(sl=True)

frame_num = 0
for ry in range(0,360,2): ## rotate 2-degree/frame
    # change current time
    frame_num += 1
    cmds.currentTime(frame_num, update=True)

    # assign transform to camera
    cmds.setAttr("{0}.ry".format(obj[0]), ry)

    # fix this pose as keyframe
    cmds.setKeyframe()

cmds.select(clear=True)

RenderSetting.SetFrameRange(1, frame_num)
cmds.currentTime(1) 
