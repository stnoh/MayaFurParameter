import maya.cmds as cmds
import maya.mel as mel

def SetFrameRange(startFrame, endFrame):
    """
    Sets rendering frame range from "startFrame" to "endframe".
    It also adjusts the playback range.
    startFrame : the initial frame number. 1 is preferable.
    endFrame   : the last frame number.
    """

    cmds.setAttr("defaultRenderGlobals.startFrame",startFrame)
    cmds.setAttr("defaultRenderGlobals.endFrame", endFrame)
    cmds.playbackOptions(ast=startFrame, min=startFrame, max=endFrame, aet=endFrame)
    return None

def SetRenderer(renderer):
    """
    Sets renderer by string.
    It is correspond to "Menubar > Render > Render Settings > Render Using" tab
    """

    if renderer in {"mayaSoftware", "mayaHardware2", "mayaVector", "arnold"}:
        cmds.setAttr("defaultRenderGlobals.currentRenderer", renderer, type="string")
    else:
        cmds.warning("There is no renderer named {0}".format(renderer))
        return False

    return True

def SetImageSize(imageW_px, imageH_px):
    """
    Sets rendered image size.
    imageW_px: image width  [pixel]
    imageH_px: image height [pixel]
    """

    aspect_px = float(imageW_px) / float(imageH_px)
    cmds.setAttr("defaultResolution.width" , imageW_px)
    cmds.setAttr("defaultResolution.height", imageH_px)
    cmds.setAttr("defaultResolution.deviceAspectRatio", aspect_px)
    cmds.setAttr("defaultResolution.pixelAspect", 1.000)

    return None

def Snapshot(renderCam, startFrame=1):
    """
    Runs "Snapshot" to change Maya's default camera to rendercamera.
    renderCam : renderCam that wants to utilize
    startFrame: the first frame of rendering sequence (optinal)
    """
    cmds.currentTime(startFrame, update=True) # get back to the first frame

    ## set this camera as render view's default camera
    mel.eval("RenderViewWindow;")
    mel.eval('renderWindowRenderCamera "snapshot" renderView '+"{0}".format(renderCam[0])+";")

    return None

def SetExportPath(filePrefix, fileExt):
    """
    Sets export path and extension.
    filePrefix: export file prefix without postfix. For example, C:/path/to/file
    fileExt   : file extension (string), this only works for "mayaSoftware" and "mayaHardware2"
    """
    
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", filePrefix, type="string")

    ## set filepath as: "file.####.ext"
    cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)
    cmds.setAttr("defaultRenderGlobals.animation", 1)
    cmds.setAttr("defaultRenderGlobals.periodInExt", 1)
    cmds.setAttr("defaultRenderGlobals.useFrameExt", 1)
    cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
    cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)

    ## get image format ID in Maya
    def _getImageFormatID(ext):
        imageFormat = {
            "jpg": 8, "jpeg": 8,
            "iff": 14,
            "bmp": 20,
            "png": 32,
            "exr": 40,
        }.get(ext.lower(), -1)

        if imageFormat == -1:
            cmds.warning("{0} - Unsupported image format: set png format, instead.".format(ext))
            imageFormat = 32

        return imageFormat

    ## set file extension
    imageFormat = _getImageFormatID(fileExt)
    cmds.setAttr("defaultRenderGlobals.imageFormat", imageFormat)

    return True
