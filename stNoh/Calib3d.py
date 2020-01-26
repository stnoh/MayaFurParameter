import numpy as np

def GetFocalLength_Maya(imageWidth_px, focalLength_px, show_angle=False):
    """
    Returns focal length of camera in Maya [metric is pixel].
    imageWidth_px  : width of image
    focalLength_px : its correspond focal length
    show_angle     : show angle of view [deg]
    """

    ## Maya's default camera is based on 135 film (36mm x 24mm)
    focalLength_film = float(focalLength_px) / imageWidth_px * 36.0

    ## show Angle-of-View in Maya
    if (show_angle):
        AoVx_radian = np.atan( (imageWidth_px/2.0) / focalLength_px ) * 2.0
        AoVx_degree = round(np.rad2deg(AoVx_radian), 2)
        print("angle of view = "+str(AoVx_degree))

    return focalLength_film

def GetCameraTransform(rotX, rotY, dist):
    """
    Returns 6-tuple of pose information in Maya.
    The returned camera pose always looks the origin.
    This function only supports tilt (as rotX) and pan (as rotY).
    rotX: tilt value [deg]
    rotY: pan  value [deg]
    dist: distance from origin
    """

    rx = -rotX
    ry = -rotY
    rz = 0 # no Z-rotation

    deg2rad = np.pi / 180.0

    cX = np.cos(-rotX * deg2rad)
    sX = np.sin(-rotX * deg2rad)
    cY = np.cos(-rotY * deg2rad)
    sY = np.sin(-rotY * deg2rad)

    tx = +dist * cX * sY
    ty = -dist * sX
    tz = +dist * cX * cY

    return (rx,ry,rz, tx,ty,tz)

def GetCameraTransforms(rotX, rotYs, dist):
    """
    Returns the list of 6-tuple of pose information.
    It can set multiple pan (rotY) values.
    """

    trs = []
    for rotY in rotYs:
        tr = GetCameraTransform(rotX, rotY, dist)
        trs.append(tr)

    return trs

def ConvertArUcoRotation(rx_ArUco, ry_ArUco, rz_ArUco):
    """
    Converts ArUco marker rotation (Z+ up) to Maya rotation (Y+ up).
    """

    # cos/sin
    c = np.cos( np.deg2rad([rx_ArUco, ry_ArUco, rz_ArUco]) )
    s = np.sin( np.deg2rad([rx_ArUco, ry_ArUco, rz_ArUco]) )

    # construct 3x3 rotation matrices (in GLM)
    rotZ = [[ c[2], -s[2],  0.0], [ s[2], c[2],   0.0], [  0.0,  0.0,  1.0]]
    rotY = [[ c[1],   0.0, s[1]], [  0.0, +1.0,   0.0], [-s[1],  0.0, c[1]]]
    rotX = [[ +1.0,   0.0,  0.0], [  0.0, c[0], -s[0]], [  0.0, s[0], c[0]]]
    rotZYX = np.dot(np.dot(rotX, rotY), rotZ)

    # convert matrix from (X+,Y+,Z+) to inv(X+,Z+,Y-)
    rot_Maya = [[0.0, 0.0, 0.0],[0.0, 0.0, 0.0],[0.0, 0.0, 0.0]]

    rot_Maya[0][0] = +rotZYX[0][0]
    rot_Maya[0][1] = +rotZYX[1][0]
    rot_Maya[0][2] = -rotZYX[2][0]

    rot_Maya[1][0] = +rotZYX[0][2]
    rot_Maya[1][1] = +rotZYX[1][2]
    rot_Maya[1][2] = -rotZYX[2][2]

    rot_Maya[2][0] = +rotZYX[0][1]
    rot_Maya[2][1] = +rotZYX[1][1]
    rot_Maya[2][2] = -rotZYX[2][1]

    # convert to euler representation
    rx_GLM = np.atan2(rot_Maya[2][1], rot_Maya[2][2])
    rx = -np.rad2deg(rx_GLM)

    C2 = np.sqrt(rot_Maya[0][0]*rot_Maya[0][0]+rot_Maya[1][0]*rot_Maya[1][0])
    ry_GLM = np.atan2(-rot_Maya[2][0], C2)
    ry = -np.rad2deg(ry_GLM)

    S1 = np.sin(rx_GLM)
    C1 = np.cos(rx_GLM)
    rz_GLM = np.atan2(S1*rot_Maya[0][2] - C1*rot_Maya[0][1], C1*rot_Maya[1][1] - S1*rot_Maya[1][2] )
    rz = +np.rad2deg(rz_GLM) # [CAUTION] use "-rz"

    return (rx, ry, rz)

def ParseArUcoCameraPose(imgFile):
    """
    Parses ArUco marker pose (Z+ up) from filename to Maya pose (Y+ up).
    """

    import re

    m = re.search('(?<=rx)[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', imgFile)
    rx_ArUco = float(m.group(0))
    m = re.search('(?<=ry)[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', imgFile)
    ry_ArUco = float(m.group(0))
    m = re.search('(?<=rz)[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', imgFile)
    rz_ArUco = float(m.group(0))

    m = re.search('(?<=tx)[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', imgFile)
    tx_ArUco = float(m.group(0))
    m = re.search('(?<=ty)[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', imgFile)
    ty_ArUco = float(m.group(0))
    m = re.search('(?<=tz)[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', imgFile)
    tz_ArUco = float(m.group(0))

    ## convert rotation ArUco/Z+up to Maya/Y+up
    (rx, ry, rz) = ConvertArUcoRotation(rx_ArUco, ry_ArUco, rz_ArUco)

    ## Z+up (ArUco, 1.0=[m]) -> Y+up (Maya, 1.0=[cm])
    tx = +100.0 * tx_ArUco
    ty = +100.0 * tz_ArUco
    tz = -100.0 * ty_ArUco

    return (rx, ry, rz, tx, ty, tz)
