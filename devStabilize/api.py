import math
from maya import (OpenMaya, cmds)


def fillKeyframe(obj, attrs, timeRange=[1, 20]):
    '''
    Fills keys on inputed object.

    Input:
        @param obj[string]- Name of the Maya object.
        @param attrs[list of strings]- List of maya attributes to key.
        @param timeRange[list of 2 ints]- Start and End frame.

    Raises:
        None

    Returns:
        None
    '''
    cmds.setKeyframe(obj, attribute=attrs, time=min(timeRange))

    for key in xrange(timeRange[0], timeRange[1] + 1):
        cmds.setKeyframe(obj, time=key, insert=True, attribute=attrs)

    curveNames = cmds.keyframe(obj, query=True, name=True)

    for curve in curveNames:
        cmds.keyTangent(
            curve, inTangentType='linear')
        cmds.keyTangent(
            curve, outTangentType='linear')


def stabilize(obj=None,
              camera=None,
              timeRange=[0, 20],
              rotation=False,
              scale=False):
    '''
    Transfers an object's values to camera.

    Input:
        @param obj[string]- Name of the Maya object.
        @param camera[string]- Name of the Maya Camera.
        @param timeRange[list of ints]- Start and stop of timerange ex. [0, 20]
        @param rotation[bool]- Whether or not rotation affects the camera.
        @param scale[bool]- Whether or not scale affects the camera.

    Raises:
        RuntimeError for non-existant or improper camera or object.

    Returns:
        None
    '''
    # Undo chunk to make undo easy.
    cmds.undoInfo(openChunk=True)

    # Store current time.
    cTime = cmds.currentTime(query=True)

    if not obj or not camera:
        raise RuntimeError("You didn't set object or camera input.")

    if not cmds.objExists(obj):
        raise RuntimeError("Object doesn't exist.")

    if not cmds.objExists(camera):
        raise RuntimeError("Camera doesn't exist.")

    kAttrs = ["translateX", "translateY", "translateZ"]

    if rotation:
        kAttrs.extend(["rotateX", "rotateY", "rotateZ"])

    if scale:
        kAttrs.extend(["scaleX", "scaleY", "scaleZ"])

    # Fill keyframes.
    fillKeyframe(obj, kAttrs, timeRange=timeRange)
    fillKeyframe(camera, kAttrs, timeRange=timeRange)

    for t in xrange(timeRange[0], timeRange[1] + 1):

        cmds.currentTime(t)

        # Get worldMatrix
        objMat = cmds.getAttr("%s.worldMatrix" % obj)
        objMMat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(objMat, objMMat)

        # Get translation matrix.
        objTrans = cmds.xform(
            obj, query=True, worldSpace=True, translation=True)
        objTMat = [1.0, 0.0, 0.0, 0.0,
                   0.0, 1.0, 0.0, 0.0,
                   0.0, 0.0, 1.0, 0.0,
                   objTrans[0], objTrans[1], objTrans[2], 1.0]
        objTMMat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(objTMat, objTMMat)

        # Get Scale Matrix.
        objScale = cmds.xform(obj, query=True, worldSpace=True, scale=True)
        objSMat = [objScale[0], 0.0, 0.0, 0.0,
                   0.0, objScale[1], 0.0, 0.0,
                   0.0, 0.0, objScale[2], 0.0,
                   0.0, 0.0, 0.0, 1.0]
        objSMMat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(objSMat, objSMMat)

        # Get matrix without translation.
        objRSMMat = objMMat * objTMMat.inverse()

        # Normalize matrix to remove scale.
        X = OpenMaya.MVector(
            objRSMMat(0, 0), objRSMMat(0, 1), objRSMMat(0, 2)).normal()
        Y = OpenMaya.MVector(
            objRSMMat(1, 0), objRSMMat(1, 1), objRSMMat(1, 2)).normal()
        Z = OpenMaya.MVector(
            objRSMMat(2, 0), objRSMMat(2, 1), objRSMMat(2, 2)).normal()

        # THE rotation matrix.
        objRMat = [X.x, X.y, X.z, objRSMMat(0, 3),
                   Y.x, Y.y, Y.z, objRSMMat(1, 3),
                   Z.x, Z.y, Z.z, objRSMMat(2, 3),
                   objRSMMat(3, 0), objRSMMat(3, 1),
                   objRSMMat(3, 2), objRSMMat(3, 3)]

        objRMMat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(objRMat, objRMMat)

        # Get correct matrix based on circumstance.
        cObjMMat = OpenMaya.MMatrix()

        if scale:
            cObjMMat = objSMMat

        if rotation:
            cObjMMat *= objRMMat

        cObjMMat *= objTMMat

        invObjMMat = cObjMMat.inverse()

        camMat = cmds.getAttr("%s.worldMatrix" % camera)
        camMMat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(camMat, camMMat)

        finalMat = camMMat * invObjMMat
        trans, rots, scales = decomposeMatrix(finalMat)

        # We always set translation. If we didn't it wouldn't work.
        cmds.setAttr("%s.translate" % camera, *trans)
        cmds.setAttr("%s.translate" % obj, 0, 0, 0)

        # Set other values if they are set.
        if rotation:
            cmds.setAttr("%s.rotate" % camera, *rots)
            cmds.setAttr("%s.rotate" % obj, 0, 0, 0)

        if scale:
            cmds.setAttr("%s.scale" % camera, *scales)
            cmds.setAttr("%s.scale" % obj, 1.0, 1.0, 1.0)

        cmds.setKeyframe(obj, time=t, attribute=kAttrs)
        cmds.setKeyframe(camera, time=t, attribute=kAttrs)

    # Set time back.
    cmds.currentTime(cTime)

    # Close undo chunk to make it easy.
    cmds.undoInfo(closeChunk=True)


def decomposeMatrix(mat):
    '''
    Decomposes an MMatrix into translation, rotation(XYZ), and Scale.

    Input:
        @param mat(OpenMaya.MMatrix): MMatrix to be decomposed.

    Raises:
        None

    Returns:
        Translation [list of floats](XYZ)
        Rotation [list of floats](XYZ)
        Scale [list of floats](XYZ)
    '''
    mt = OpenMaya.MTransformationMatrix(mat)

    trans = mt.translation(OpenMaya.MSpace.kWorld)
    eulerRot = mt.rotation().asEulerRotation()

    angles = [math.degrees(angle)
              for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

    scaleUtil = OpenMaya.MScriptUtil()
    scaleUtil.createFromList([0, 0, 0], 3)
    scaleVec = scaleUtil.asDoublePtr()

    mt.getScale(scaleVec, OpenMaya.MSpace.kWorld)

    scale = [OpenMaya.MScriptUtil.getDoubleArrayItem(scaleVec, i)
             for i in xrange(0, 3)]

    return [trans.x, trans.y, trans.z], angles, scale


if __name__ == '__main__':
    stabilize("stable_GEO", "stable_CAM")
