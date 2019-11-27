from devStabilize.ui import UI
from devStabilize.api import stabilize
from PySide2 import (QtWidgets)
from maya import (cmds, OpenMayaUI, OpenMaya)


def get_maya_window():
    '''Get Maya MainWindow as a QWidget.'''

    for widget in QtWidgets.QApplication.instance().topLevelWidgets():
        if widget.objectName() == 'MayaWindow':
            return widget
    raise RuntimeError('Could not locate MayaWindow...')


def create():
    '''
    Creates the UI.
    '''
    return maya_UI()


class maya_UI(UI):
    '''
    Maya UI.
    '''
    def __init__(self, parent=get_maya_window()):
        '''
        Initializer.
        '''
        super(maya_UI, self).__init__(parent)

        # Create connections.
        self.create_connections()

        self.loadCamera()

    def create_connections(self):
        '''
        Connects controls.
        '''
        self.cam_Btn.clicked.connect(self.loadCamera)
        self.doIt_Btn.clicked.connect(self.doIt)

    def loadCamera(self):
        '''
        Load camera based on selection or view.
        '''
        # We only want to turn off views on panels if they are proper panels.
        # This is the list of panels that you can't do anything with.
        badPanels = ['scriptEditorPanel', 'outlinerPanel', 'hyperShadePanel',
                     'renderView', 'graphEditor', 'nodeEditorPanel',
                     'hyperGraphPanel', 'polyTexturePlacementPanel',
                     'dopeSheetPanel', 'relationshipPanel',
                     'clipEditorPanel', 'visorPanel', 'sequenceEditorPanel',
                     'createNodePanel', 'blendShapePanel',
                     'dynRelEdPanel', 'componentEditorPanel',
                     'referenceEditorPanel', 'dynPaintScripted']

        # Get current panel.
        currentPanel = cmds.getPanel(withFocus=True)

        # Clear the view to make simmin' faster.
        if currentPanel not in badPanels:
            try:
                modelEditerPresets = self.modelEditorSet(currentPanel)
                cmds.modelEditor(
                    currentPanel, edit=True, **modelEditerPresets["clearView"])
            except BaseException:
                pass

        # Time.
        self.timeStart = int(cmds.playbackOptions(query=True, minTime=True))
        self.timeEnd = int(cmds.playbackOptions(query=True, maxTime=True))

        # Get the camera via selection or active view.
        selection = cmds.ls(selection=True)

        if len(selection) == 0:
            self.camera = self.getActiveCamera()
        else:
            cameraShape = cmds.listRelatives(
                selection[0], children=True, type="camera", fullPath=True)

            if not cameraShape:
                self.camera = self.getActiveCamera()
            else:
                self.camera = [selection[0], cameraShape[0]]

        self.cam_LEdit.setText(self.camera[0])

    def getActiveCamera(self):
        '''
        Gets the name of the active camera.
        Returns cameraTransform and cameraShape.
        '''
        # Get active view.
        activeView = OpenMayaUI.M3dView.active3dView()

        # Get camera.
        mDag_cameraShape = OpenMaya.MDagPath()
        mDag_cameraTrans = OpenMaya.MDagPath()
        activeView.getCamera(mDag_cameraShape)

        # Got cameraShape
        cameraShape = mDag_cameraShape.fullPathName()

        # Got camera trans.
        mDag_cameraTrans = mDag_cameraShape
        mDag_cameraTrans.pop(1)

        cameraTrans = mDag_cameraTrans.fullPathName()

        return [cameraTrans, cameraShape]

    def doIt(self):
        '''
        Does the work for the camera.
        '''
        select = cmds.ls(selection=True)

        if len(select) == 0:
            raise RuntimeError("Nothing selected!")

        if len(select) > 1:
            raise RuntimeError("More than one object selected!")

        # Set obj.
        self.obj = select[0]

        # Get trans.
        self.cameraTrans = self.cam_LEdit.text()

        if not cmds.objExists(self.cameraTrans):
            raise RuntimeError("Camera does not exist.")

        # Start end.
        self.start = int(cmds.playbackOptions(query=True, min=True))
        self.end = int(cmds.playbackOptions(query=True, max=True))

        # Run the stabilize function.
        stabilize(obj=self.obj,
                  camera=self.cameraTrans,
                  timeRange=[self.start, self.end],
                  rotation=self.rotate_chkBox.isChecked(),
                  scale=self.scale_chkBox.isChecked())
