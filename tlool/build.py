import rig, tools, shapes, perseus
import maya.api.OpenMaya as om
import pymel.core as pm
import json, os, math

from maya import OpenMayaUI as omui
from PySide2 import QtCore, QtGui, QtWidgets, __version__
from shiboken2 import wrapInstance 

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class BuildStep:
    name = None
    display_name = None
    def __init__(self, name, display_name=None):
        self.name = name
        if display_name is None:
            self.display_name = name
        else:self.display_name = display_name
    def getName(self):
        return(self.name)
    def getDisplayName(self):
        return(self.display_name)
    def setName(self, name):
        self.name = name
        return(name)
    def setDisplayName(self, display_name):
        self.display_name = display_name
        return(self.display_name)
    def run(self, rigData, rigChar, additional_values = None):
        result = False
        if self.check(rigChar) == 1:
            pm.warning("This step({}) has been processed!!!".format(self.getDisplayName()))
            return(None)

        if self.name == 'Customize Perseus':
            result = perseus.Perseus.customizePerseus(perseus_name = rig.RigMain.findPerseusName())

        elif self.name == 'Apply Weighted Blended For Eyes':
            if self.check(rigChar) == 2:
                pm.warning('Re-doing step ({})!!!!'.format(self.getDisplayName()))
            else:
                print("# Processing a build step({})!!!!".format(self.getDisplayName()))

            if additional_values is not None:
                w = additional_values['eyelidsWeight']
                result = perseus.Perseus.applyWeightedBlendForEyelids(rigData, perseus_name = rig.RigMain.findPerseusName(),weight=w)
            else:
                result = perseus.Perseus.applyWeightedBlendForEyelids(rigData, perseus_name = rig.RigMain.findPerseusName())
        elif self.name == 'Customize Head Squash & Stretch':
            result = rigChar.setupSquashStretchHead()

        elif self.name == 'Duplicate Meshes':
            self.rigChar = rig.RigChar(rig.RigMain.findCharName(), rig.RigMain.findPerseusName())            
            rigChar.createJntBaseHeadGeo()
            rigChar.createBridgeGeos()
            rigChar.createSublipHeadGeo()
            result = True
        elif self.name == 'Build Lips Controllers':
            up_falloff = 3.5
            dw_falloff =3.5
            if additional_values is not None:
                up_falloff = additional_values['upLipFalloff']
                dw_falloff = additional_values['dwLipFalloff']

            if self.check(rigChar) != 2: # first run
                rigChar.createJntBaseHeadSkinJnt()
                rigChar.createJntBaseLipSkinJnts(rigData)
                rigChar.bindJntBaseSkin()
                rigChar.createLipCrvs(rigData)
                rigChar.paintJntBaseSkinWeight(rigData, init=True, falloffRadiusUp=up_falloff, falloffRadiusDown=dw_falloff)
            else: # re-doing
                rigChar.paintJntBaseSkinWeight(rigData, init=True, falloffRadiusUp=up_falloff, falloffRadiusDown=dw_falloff)
            result=True
        elif self.name == 'Build Eyes Controllers':
            result = rigChar.createEyeCrvs(rigData)
        elif self.name == 'Build Sublip Controllers':
            forehead_falloff = 3.5
            philtrum_falloff = 2.5
            jawDodown_falloff = 1.5
            eyeClown_falloff = 1.0
            if additional_values is not None:
                forehead_falloff = additional_values['foreheadFalloff']
                philtrum_falloff = additional_values['philtrumFalloff']
                jawDodown_falloff = additional_values['jawDodownFalloff']
                eyeClown_falloff = additional_values['eyeClownFalloff']
            result = rigChar.createSublip(rigData, forehead_falloff=forehead_falloff, philtrum_falloff=philtrum_falloff, 
                                            jawDodown_falloff=jawDodown_falloff, eyeClown_falloff=eyeClown_falloff )
        elif self.name == 'Build Forehead Controllers':
            result = rigChar.createForehead(rigData)            
        else:
            pm.warning('A build step ({}) is not defined!!!!'.format(self.getDisplayName()))

        if result == True:
            print("#### "+self.name+ " COMPLETE ####")

    def check(self, rigChar):
        if self.name == 'Customize Perseus':
            if pm.objExists('FacialSettings'):
                return(True)
            else:
                return(False)
        elif self.name == 'Apply Weighted Blended For Eyes':
            setup_geo_sc = tools.getSkinClusterFromMesh(perseus.Perseus.getRigHeadSetupGeo())
            if pm.getAttr(setup_geo_sc.name()+'.skinningMethod') == 2:
                return(2)
            else:
                return(0)
        elif self.name == 'Customize Head Squash & Stretch':
            if pm.objExists('sqst_ctrl_grp'):
                return(True)
            else:
                return(False)

        elif self.name == 'Duplicate Meshes':
            if rigChar.getJntBaseHeadGeo() is not None:
                if pm.objExists(rigChar.getJntBaseHeadGeo()):
                    return(True)
            return(False)
        elif self.name == 'Build Lips Controllers':
            if pm.objExists('LipSet_DW_M') and pm.objExists('LipSet_UP_M'):
                return(2)
            else:
                return(0)
        elif self.name == 'Build Eyes Controllers':
            if pm.objExists('eye_ctrl_grp'):
                return(True)
            else:
                return(False)
        elif self.name == 'Build Sublip Controllers':
            if pm.objExists('sublip_ctrl_grp'):
                return(True)
            else:
                return(False)
        elif self.name == 'Build Forehead Controllers':
            if pm.objExists('forehead_ctrl_grp'):
                return(True)
            else:
                return(False)
        else:
            pm.warning('A build step ({}) is not defined!!!!'.format(self.name))       

class BuildWorkflow:
    step_customize_perseus = BuildStep('Customize Perseus')
    step_fix_eye_skin = BuildStep('Apply Weighted Blended For Eyes')
    step_fix_eye_skin.setDisplayName('Apply Weighted Blended(Setup Geo/Skin Cluster) For Eyes - Redoable')
    step_customize_sqst = BuildStep('Customize Head Squash & Stretch')
    duplicate_meshes = BuildStep('Duplicate Meshes')
    duplicate_meshes.setDisplayName('Duplicate Meshes(Bridge Geos, JntBase Geo, Sublip Geo)')
    build_lips = BuildStep('Build Lips Controllers')
    build_lips.setDisplayName('Build Lips Controllers - Redoable(Skinning only)')
    build_eyes = BuildStep('Build Eyes Controllers') 
    build_sublip = BuildStep('Build Sublip Controllers')
    build_sublip.setDisplayName('Build JawDodown, Philtrum, EyeClowns & Forehead Contollers')
    build_forehead = BuildStep('Build Forehead Controllers')

    @classmethod
    def getBuildSteps(cls):
        build_steps = [
                cls.step_customize_perseus,
                cls.step_customize_sqst,
                cls.step_fix_eye_skin,
                cls.duplicate_meshes,
                cls.build_lips,
                cls.build_eyes,
                cls.build_sublip
                #cls.build_forehead               
                ]        
        return(build_steps)        

    @classmethod
    def getBuildStepByName(cls, name):
        for step in cls.getBuildSteps():
            if step.getName() == name:
                return(step)
        return(None)

    @classmethod
    def getBuildStepByDisplayName(cls, display_name):
        for step in cls.getBuildSteps():
            if step.getDisplayName() == display_name:
                return(step)
        return(None)

class FaceBuildUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(FaceBuildUI, self).__init__(parent)
        self.qtSignal = QtCore.Signal()
        #################################################################
    
    def create(self):
        self.rigChar = rig.RigChar(rig.RigMain.findCharName(), rig.RigMain.findPerseusName())

        try:
            self.setWindowTitle("The Life of Our Lord - Face Builder")
            self.setWindowFlags(QtCore.Qt.Tool)
            self.resize(400, 400) # re-size the window

            self.mainLayout = QtWidgets.QVBoxLayout(self)
            
            self.charInfoTitle = QtWidgets.QLabel(" Char Info")         
            self.charInfoTitle.setStyleSheet("color: white;background-color: black;")
            self.charInfoTitle.setFixedSize(400,30)


            self.charNameLayout = QtWidgets.QHBoxLayout(self)
            self.charNameLabel = QtWidgets.QLabel(" Char Name : ")
            self.charNameLayout.addWidget(self.charNameLabel)
            self.perseusNameLayout = QtWidgets.QHBoxLayout(self)
            self.perseusNameLabel = QtWidgets.QLabel(" Persues Name : ")
            self.perseusNameLayout.addWidget(self.perseusNameLabel)
            self.rigInfoPathLayout = QtWidgets.QHBoxLayout(self)
            self.rigInfoPathLabel = QtWidgets.QLabel(" Rig Info Path : ")
            self.rigInfoPathValue = QtWidgets.QLineEdit("")
            self.rigInfoPathButton = QtWidgets.QPushButton("Change")
            self.rigInfoPathButton.clicked.connect(self.rigInfoPathButtonClicked)
            self.rigInfoPathLayout.addWidget(self.rigInfoPathLabel)
            self.rigInfoPathLayout.addWidget(self.rigInfoPathValue)
            self.rigInfoPathLayout.addWidget(self.rigInfoPathButton)
            self.rigInfoFileLayout = QtWidgets.QHBoxLayout(self)
            self.rigInfoFileLabel = QtWidgets.QLabel(" Rig Info File : ")
            self.rigInfoFileValue = QtWidgets.QLineEdit("")
            self.rigInfoFileButton = QtWidgets.QPushButton("Change")
            self.rigInfoFileButton.clicked.connect(self.rigInfoFileButtonClicked)
            self.rigInfoFileLayout.addWidget(self.rigInfoFileLabel)
            self.rigInfoFileLayout.addWidget(self.rigInfoFileValue)
            self.rigInfoFileLayout.addWidget(self.rigInfoFileButton)

            self.updateCharInfo()

            self.mainLayout.addWidget(self.charInfoTitle)
            self.mainLayout.addLayout(self.charNameLayout)
            self.mainLayout.addLayout(self.perseusNameLayout)            
            self.mainLayout.addLayout(self.rigInfoPathLayout)
            self.mainLayout.addLayout(self.rigInfoFileLayout)

            self.tab1 = QtWidgets.QWidget(self)
            self.tab2 = QtWidgets.QWidget(self)
            self.tabs = QtWidgets.QTabWidget(self)
            self.tabs.addTab(self.tab1, 'Build')
            self.tabs.addTab(self.tab2, 'Rig Data')
            self.mainLayout.addWidget(self.tabs)

            self.tab1Layout = QtWidgets.QVBoxLayout(self)
            self.tab1.setLayout(self.tab1Layout)

            self.buildStepTitle = QtWidgets.QLabel(" Build Steps")
            self.buildStepTitle.setStyleSheet("color: white;background-color: black;")
            self.buildStepTitle.setFixedSize(400,30)
            self.buildStepList = QtWidgets.QListWidget(self)
            self.buildStepList.resize(400, 160)
            self.populateBuildSteps()

            self.tab1Layout.addWidget(self.buildStepTitle)
            self.tab1Layout.addWidget(self.buildStepList)            
    
            self.buildEyelidsFalloffInputLayout = QtWidgets.QHBoxLayout(self)
            self.tab1Layout.addLayout(self.buildEyelidsFalloffInputLayout)            
            self.EyelidsWeightBlendedMultiplierLabel = QtWidgets.QLabel("Eyelids Weight Blended multiplier(<=1.0)")
            self.EyelidsWeightBlendedMultiplierLineEdit = QtWidgets.QLineEdit("")
            self.EyelidsWeightBlendedMultiplierLineEdit.setValidator(QtGui.QDoubleValidator())
            self.buildEyelidsFalloffInputLayout.addWidget(self.EyelidsWeightBlendedMultiplierLabel)
            self.buildEyelidsFalloffInputLayout.addWidget(self.EyelidsWeightBlendedMultiplierLineEdit)

            self.buildLipsFalloffInputLayout = QtWidgets.QHBoxLayout(self)
            self.tab1Layout.addLayout(self.buildLipsFalloffInputLayout)            
            self.upLipFalloffLabel = QtWidgets.QLabel("upLip skin weight falloff")
            self.upLipFalloffLineEdit = QtWidgets.QLineEdit("")
            self.upLipFalloffLineEdit.setValidator(QtGui.QDoubleValidator())
            self.dwLipFalloffLabel = QtWidgets.QLabel("dwLip skin weight falloff")
            self.dwLipFalloffLineEdit = QtWidgets.QLineEdit("")
            self.dwLipFalloffLineEdit.setValidator(QtGui.QDoubleValidator())

            self.buildLipsFalloffInputLayout.addWidget(self.upLipFalloffLabel)
            self.buildLipsFalloffInputLayout.addWidget(self.upLipFalloffLineEdit)
            self.buildLipsFalloffInputLayout.addWidget(self.dwLipFalloffLabel)
            self.buildLipsFalloffInputLayout.addWidget(self.dwLipFalloffLineEdit)


            self.buildSublipFalloffInputLayout = QtWidgets.QHBoxLayout(self)
            self.tab1Layout.addLayout(self.buildSublipFalloffInputLayout)            
            self.philtrumFalloffLabel = QtWidgets.QLabel("philtrum skin weight falloff ")
            self.philtrumFalloffLineEdit = QtWidgets.QLineEdit("")
            self.philtrumFalloffLineEdit.setValidator(QtGui.QDoubleValidator())
            self.jawDodownFalloffLabel = QtWidgets.QLabel("jawDodown skin weight falloff")
            self.jawDodownFalloffLineEdit = QtWidgets.QLineEdit("")
            self.jawDodownFalloffLineEdit.setValidator(QtGui.QDoubleValidator())

            self.buildSublipFalloffInputLayout.addWidget(self.philtrumFalloffLabel)
            self.buildSublipFalloffInputLayout.addWidget(self.philtrumFalloffLineEdit)
            self.buildSublipFalloffInputLayout.addWidget(self.jawDodownFalloffLabel)
            self.buildSublipFalloffInputLayout.addWidget(self.jawDodownFalloffLineEdit)


            self.buildForeheadFalloffInputLayout = QtWidgets.QHBoxLayout(self)
            self.tab1Layout.addLayout(self.buildForeheadFalloffInputLayout)            
            self.foreheadFalloffLabel = QtWidgets.QLabel("forehead skin weight falloff")
            self.foreheadFalloffLineEdit = QtWidgets.QLineEdit("")
            self.foreheadFalloffLineEdit.setValidator(QtGui.QDoubleValidator())
            self.eyeClownFalloffLabel = QtWidgets.QLabel("eyeClown skin weight falloff")
            self.eyeClownFalloffLineEdit = QtWidgets.QLineEdit("")
            self.eyeClownFalloffLineEdit.setValidator(QtGui.QDoubleValidator())
            #self.blankFalloffLabel1 = QtWidgets.QLabel("                                  ")
            #self.blankFalloffLabel2 = QtWidgets.QLabel("                                 ")

            self.buildForeheadFalloffInputLayout.addWidget(self.foreheadFalloffLabel)
            self.buildForeheadFalloffInputLayout.addWidget(self.foreheadFalloffLineEdit)
            self.buildForeheadFalloffInputLayout.addWidget(self.eyeClownFalloffLabel)
            self.buildForeheadFalloffInputLayout.addWidget(self.eyeClownFalloffLineEdit)

            self.buildRunButtonLayout = QtWidgets.QHBoxLayout(self)
            self.tab1Layout.addLayout(self.buildRunButtonLayout)

            self.buildRunButton = QtWidgets.QPushButton("Run a Selected step")
            self.buildRefreshButton = QtWidgets.QPushButton("Refresh all data")
            self.buildRunButtonLayout.addWidget(self.buildRunButton)
            self.buildRunButtonLayout.addWidget(self.buildRefreshButton)
            self.buildRunButton.clicked.connect(self.buildRunButtonClicked)
            self.buildRefreshButton.clicked.connect(self.refreshAllData)

            self.rigDataTitle = QtWidgets.QLabel(" Rig Data (Double-click loads data)")
            self.rigDataTitle.setStyleSheet("color: white;background-color: black;")
            self.rigDataTitle.setFixedSize(400,30)
            self.rigDataList = QtWidgets.QListWidget(self)
            self.rigDataList.resize(400, 100)

            self.tab2Layout = QtWidgets.QVBoxLayout(self)
            self.tab2.setLayout(self.tab2Layout)

            self.tab2Layout.addWidget(self.rigDataTitle)
            self.tab2Layout.addWidget(self.rigDataList)

            #self.rigGeoCheck = QtWidgets.QCheckBox("Rig Geo")
            #self.rigGeoCheck.setCheckState(QtCore.Qt.CheckState.Checked)
            #self.setupGeoCheck = QtWidgets.QCheckBox("Setup Geo")

            self.saveSelectionButton = QtWidgets.QPushButton("Save Selection to Selected Key")
            self.saveSelectionButton.clicked.connect(self.saveSelectionButtonClicked)
            
            self.geoDisplayTitle = QtWidgets.QLabel(" Geo & Curve Display")
            self.geoDisplayTitle.setStyleSheet("color: white;background-color: black;")
            self.geoDisplayTitle.setFixedSize(400,30)
            
            self.toggleCurveButton = QtWidgets.QPushButton("Toggle Joint and Curve Display(Eyes & Lips)")
            self.toggleCurveButton.clicked.connect(self.toggleCurveButtonClicked)
            
            self.renderGeoCheckBox = QtWidgets.QCheckBox('Render Geo Vis', self)
            self.rigGeoCheckBox = QtWidgets.QCheckBox('Rig Geo Vis', self)
            self.setupGeoCheckBox = QtWidgets.QCheckBox('Setup Geo Vis', self)
            self.jntBaseGeoCheckBox = QtWidgets.QCheckBox('JntBase Geo Vis', self)
            self.bridgeGeoCheckBox = QtWidgets.QCheckBox('Bridge Geo Vis', self)
            self.sublipGeoCheckBox = QtWidgets.QCheckBox('Sublip Geo Vis', self)
            self.renderGeoCheckBox.released.connect(self.renderGeoCheckBoxReleased)
            self.rigGeoCheckBox.released.connect(self.rigGeoCheckBoxReleased)
            self.setupGeoCheckBox.released.connect(self.setupGeoCheckBoxReleased)
            self.jntBaseGeoCheckBox.released.connect(self.jntBaseGeoCheckBoxReleased)
            self.bridgeGeoCheckBox.released.connect(self.bridgeGeoCheckBoxReleased)
            self.sublipGeoCheckBox.released.connect(self.sublipGeoCheckBoxReleased)
            self.initGeoVis()

            #self.tab2Layout.addWidget(self.rigGeoCheck)
            #self.tab2Layout.addWidget(self.setupGeoCheck)                        
            self.tab2Layout.addWidget(self.saveSelectionButton)
            self.tab2Layout.addWidget(self.geoDisplayTitle)
            self.tab2Layout.addWidget(self.renderGeoCheckBox)
            self.tab2Layout.addWidget(self.rigGeoCheckBox)
            self.tab2Layout.addWidget(self.setupGeoCheckBox)
            self.tab2Layout.addWidget(self.jntBaseGeoCheckBox)
            self.tab2Layout.addWidget(self.bridgeGeoCheckBox)
            self.tab2Layout.addWidget(self.sublipGeoCheckBox)
            self.tab2Layout.addWidget(self.toggleCurveButton)

            self.populateRigData()

        except Exception as e:
            pm.warning("FaceBuildUI")
            pm.warning(e.message)

    def rigInfoFileButtonClicked(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Open Data files"), rig.RigMain.getRigDataPath(), 
                    self.tr("Data Files (*.json);; All Files(*.*)"))[0]
        if fileName != "":
            self.rigInfoFileValue.setText(fileName)
            self.populateRigData()

    def rigInfoPathButtonClicked(self):
        dirName = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), rig.RigMain.getRigDataPath(), QtWidgets.QFileDialog.ShowDirsOnly)
        if dirName != "":
            self.rigInfoPathValue.setText(dirName)

    def buildRunButtonClicked(self):
        current_item = self.buildStepList.currentItem()
        additional_values = dict()
        additional_values['upLipFalloff'] = float(self.upLipFalloffLineEdit.text())
        additional_values['dwLipFalloff'] = float(self.dwLipFalloffLineEdit.text())
        additional_values['eyelidsWeight'] = float(self.EyelidsWeightBlendedMultiplierLineEdit.text())
        additional_values['jawDodownFalloff'] = float(self.jawDodownFalloffLineEdit.text())
        additional_values['philtrumFalloff'] = float(self.philtrumFalloffLineEdit.text())
        additional_values['foreheadFalloff'] = float(self.foreheadFalloffLineEdit.text())
        additional_values['eyeClownFalloff'] = float(self.eyeClownFalloffLineEdit.text())

        self.rigData.setValue('upLipFalloff', additional_values['upLipFalloff'])
        self.rigData.setValue('dwLipFalloff', additional_values['dwLipFalloff'])
        self.rigData.setValue('eyelidsWeight', additional_values['eyelidsWeight'])
        self.rigData.setValue('jawDodownFalloff', additional_values['jawDodownFalloff'])
        self.rigData.setValue('philtrumFalloff', additional_values['philtrumFalloff'])
        self.rigData.setValue('foreheadFalloff', additional_values['foreheadFalloff'])
        self.rigData.setValue('eyeClownFalloff', additional_values['eyeClownFalloff'])

        if current_item is None:
            pm.warning('Select a step!!!!!')
            return(None)
        buildStep = BuildWorkflow.getBuildStepByDisplayName(current_item.text())
        with tools.UndoContext():
            buildStep.run(self.rigData, self.rigChar, additional_values=additional_values)
        self.populateBuildSteps()

    def populateBuildSteps(self):
        self.buildStepList.clear()
        build_steps = BuildWorkflow.getBuildSteps()     
        for step in build_steps:
            self.buildStepList.addItem(step.getDisplayName())
            current_item = self.buildStepList.item(self.buildStepList.count()-1)
            buildStep = BuildWorkflow.getBuildStepByDisplayName(current_item.text())
            if not buildStep.check(self.rigChar):
                current_item.setTextColor(QtGui.QColor("red"))

    def populateRigData(self):
        self.rigData = rig.RigData(rig.RigMain.findCharName(), file_full_path=self.rigInfoFileValue.text())

        #update values in build tab
        eyelidsWeight = self.rigData.getValue(None, 'eyelidsWeight', raise_exception=False)
        if eyelidsWeight is None:
            eyelidsWeight = 0.7
        self.EyelidsWeightBlendedMultiplierLineEdit.setText(str(eyelidsWeight))
        upLipFalloff = self.rigData.getValue(None, 'upLipFalloff', raise_exception=False)
        if upLipFalloff is None:
            upLipFalloff = 3.5
        self.upLipFalloffLineEdit.setText(str(upLipFalloff))
        dwLipFalloff = self.rigData.getValue(None, 'dwLipFalloff', raise_exception=False)
        if dwLipFalloff is None:
            dwLipFalloff = 3.5
        self.dwLipFalloffLineEdit.setText(str(dwLipFalloff))

        jawDodownFalloff = self.rigData.getValue(None, 'jawDodownFalloff', raise_exception=False)
        if jawDodownFalloff is None:
            jawDodownFalloff = 1.5
        self.jawDodownFalloffLineEdit.setText(str(jawDodownFalloff))
        philtrumFalloff = self.rigData.getValue(None, 'philtrumFalloff', raise_exception=False)
        if philtrumFalloff is None:
            philtrumFalloff = 2.5
        self.philtrumFalloffLineEdit.setText(str(philtrumFalloff))
        foreheadFalloff = self.rigData.getValue(None, 'foreheadFalloff', raise_exception=False)
        if foreheadFalloff is None:
            foreheadFalloff = 3.5
        self.foreheadFalloffLineEdit.setText(str(foreheadFalloff))
        eyeClownFalloff = self.rigData.getValue(None, 'eyeClownFalloff', raise_exception=False)
        if eyeClownFalloff is None:
            eyeClownFalloff = 1.0
        self.eyeClownFalloffLineEdit.setText(str(eyeClownFalloff))

        #update values in Rig Data tab
        self.rigDataList.clear()
        for key in self.rigData.getKeys(type='vtx')+self.rigData.getKeys(type='area'):
            geo = perseus.Perseus.getRigHeadSetupGeo()
            value = self.rigData.getValue(geo, key, raise_exception=False, selection_clear=True)
            self.rigDataList.addItem(str(key))
            if value is None:
                self.rigDataList.item(self.rigDataList.count()-1).setTextColor(QtGui.QColor("red"))
            #print(self.rigDataList.item(self.rigDataList.count()-1).text())
        self.rigDataList.itemDoubleClicked.connect(self.rigDataItemClicked)        

    def updateCharInfo(self):
        self.charNameLabel.setText(" Char Name : "+str(rig.RigMain.findCharName()))
        self.perseusNameLabel.setText(" Perseus Name : "+str(rig.RigMain.findPerseusName())) 
        self.rigInfoPathValue.setText(rig.RigMain.getRigDataPath())  
        self.rigInfoPathValue.setReadOnly(True)  
        self.rigData = rig.RigData(rig.RigMain.findCharName())
        self.rigChar = rig.RigChar(rig.RigMain.findCharName(), rig.RigMain.findPerseusName())
        self.rigInfoFileValue.setText(self.rigData.getFullFilePath())  

        print("# Initiated and populated Char Info!!!!!")

    def saveSelectionButtonClicked(self):
        current_item = self.rigDataList.currentItem()
        if current_item is None:
            pm.warning('Select a item and push the button!!!')
            return(None)
        key = current_item.text()
        self.rigData.setValue(key, pm.ls(sl=True,fl=True))
        self.populateRigData()

    def rigDataItemClicked(self, item):
        components = None
        if pm.getAttr(self.rigChar.getRigHeadGeoGrp()+'.v') == 1:
            components = self.rigData.getValue(rig.RigChar.getRigHeadGeo(),item.text(), raise_exception=False)
        elif pm.getAttr(self.rigChar.getRigHeadSetupGeoGrp()+'.v') == 1:
            components = self.rigData.getValue(perseus.Perseus.getRigHeadSetupGeo(),item.text(), raise_exception=False)
        if components is None:
            pm.warning("No data!!!!!!!!!")
        else:
            pm.select(components, r=True)


    def initGeoVis(self):
        rig_geo_grp = self.rigChar.getRigHeadGeoGrp()
        render_geo_grp = self.rigChar.getRenderGeoGrp()
        facial_geo_grp = self.rigChar.getFacialGeoGrp()
        setup_geo_grp = self.rigChar.getRigHeadSetupGeoGrp()

        self.renderGeoCheckBox.setChecked(False)
        self.toggleRenderGeoVis(False)
        self.rigGeoCheckBox.setChecked(True)
        self.toggleRigGeoVis(True)
        self.setupGeoCheckBox.setChecked(False)
        self.toggleSetupGeoVis(False)
        self.jntBaseGeoCheckBox.setChecked(False)
        self.toggleJntBaseGeoVis(False)
        self.bridgeGeoCheckBox.setChecked(False)
        self.toggleBridgeGeoVis(False)

    def renderGeoCheckBoxReleased(self):
        if self.renderGeoCheckBox.isChecked():
            self.toggleRenderGeoVis(True)
        else:
            self.toggleRenderGeoVis(False)

    def rigGeoCheckBoxReleased(self):
        if self.rigGeoCheckBox.isChecked():
            self.toggleRigGeoVis(True)
        else:
            self.toggleRigGeoVis(False)

    def setupGeoCheckBoxReleased(self):
        if self.setupGeoCheckBox.isChecked():
            self.toggleSetupGeoVis(True)
        else:
            self.toggleSetupGeoVis(False)

    def jntBaseGeoCheckBoxReleased(self):
        if self.jntBaseGeoCheckBox.isChecked():
            self.toggleJntBaseGeoVis(True)
        else:
            self.toggleJntBaseGeoVis(False)       

    def bridgeGeoCheckBoxReleased(self):
        if self.bridgeGeoCheckBox.isChecked():
            self.toggleBridgeGeoVis(True)
        else:
            self.toggleBridgeGeoVis(False)

    def sublipGeoCheckBoxReleased(self):
        if self.sublipGeoCheckBox.isChecked():
            self.toggleSublipGeoVis(True)
        else:
            self.toggleSublipGeoVis(False)

    def toggleRenderGeoVis(self,vis):
        render_geo_grp = self.rigChar.getRenderGeoGrp()
        if not pm.objExists(render_geo_grp):
            return()
        if vis == True:
            pm.setAttr(render_geo_grp+'.v', 1)
            return()
        if vis == False:
            pm.setAttr(render_geo_grp+'.v', 0)
            return()
    def toggleSublipGeoVis(self,vis):
        sublip_geo_grp = self.rigChar.createSublipTargetGrp()
        if not pm.objExists(sublip_geo_grp):
            return()
        if vis == True:
            pm.setAttr(sublip_geo_grp+'.v', 1)
            return()
        if vis == False:
            pm.setAttr(sublip_geo_grp+'.v', 0)
            return()
    def toggleRigGeoVis(self,vis):
        rig_geo_grp = self.rigChar.getRigHeadGeoGrp()
        if not pm.objExists(rig_geo_grp):
            return()
        if vis == True:
            pm.setAttr(rig_geo_grp+'.v', 1)
            return()
        if vis == False:
            pm.setAttr(rig_geo_grp+'.v', 0)
            return()
    def toggleSetupGeoVis(self,vis):
        setup_geo_grp = self.rigChar.getRigHeadSetupGeoGrp()
        if not pm.objExists(setup_geo_grp):
            return()
        if vis == True:
            pm.setAttr(setup_geo_grp+'.v', 1)
            return()
        if vis == False:
            pm.setAttr(setup_geo_grp+'.v', 0)
            return()

    def toggleJntBaseGeoVis(self,vis):
        facial_geo_grp = self.rigChar.getFacialGeoGrp()
        if not pm.objExists(facial_geo_grp):
            return()
        pm.setAttr(facial_geo_grp+'.v', 1)
        if vis == True:
            pm.setAttr('jntBase_target_grp'+'.v', 1)
            return()
        if vis == False:
            pm.setAttr('jntBase_target_grp'+'.v', 0)
            return()

    def toggleBridgeGeoVis(self,vis):
        facial_geo_grp = self.rigChar.getFacialGeoGrp()
        if not pm.objExists(facial_geo_grp):
            return()
        pm.setAttr(facial_geo_grp+'.v', 1)
        if vis == True:
            pm.setAttr('bridge_target_grp'+'.v', 1)
            return()
        if vis == False:
            pm.setAttr('bridge_target_grp'+'.v', 0)
            return()

    def toggleTargetGeoGrpButtonClicked(self):
        setup_geo_grp = self.rigChar.getPRSSetupGeoGrp()
        if pm.objExists('facial_target_grp'):
            if pm.getAttr('facial_target_grp.v') == 1:
                pm.setAttr('facial_target_grp.v', 0)
                pm.setAttr(setup_geo_grp+'.v', 1)
            else:
                pm.setAttr('facial_target_grp.v', 1)
                pm.setAttr(setup_geo_grp+'.v', 0)


    def toggleRigGeoButtonClicked(self, vis=None):
        rig_geo_grp = self.rigChar.getRigHeadGeoGrp()
        render_geo_grp = self.rigChar.getRenderGeoGrp()
        setup_geo_grp = self.rigChar.getRigHeadSetupGeoGrp()

        if vis == True:
            pm.setAttr(rig_geo_grp+'.v', 1)
            return()
        if vis == False:
            pm.setAttr(rig_geo_grp+'.v', 0)
            return()

        if pm.getAttr(rig_geo_grp+'.v') == 0:
            pm.setAttr(rig_geo_grp+'.v', 1)
            pm.setAttr(render_geo_grp+'.v', 0)
            pm.setAttr(setup_geo_grp+'.v', 0)
        else:
            pm.setAttr(rig_geo_grp+'.v', 0)
            pm.setAttr(render_geo_grp+'.v', 1)
            pm.setAttr(setup_geo_grp+'.v', 0)

    def toggleSetupGeoButtonClicked(self):
        rig_geo_grp = self.rigChar.getRigHeadGeoGrp()
        render_geo_grp = self.rigChar.getRenderGeoGrp()
        facial_geo_grp = self.rigChar.getFacialGeoGrp()
        setup_geo_grp = self.rigChar.getRigHeadSetupGeoGrp()
        if pm.getAttr(setup_geo_grp+'.v') == 0:
            pm.setAttr(rig_geo_grp+'.v', 0)
            pm.setAttr(render_geo_grp+'.v', 0)
            pm.setAttr(facial_geo_grp+'.v', 1)
            pm.setAttr(setup_geo_grp+'.v', 1)
        else:
            pm.setAttr(rig_geo_grp+'.v', 1)
            pm.setAttr(render_geo_grp+'.v', 0)
            pm.setAttr(facial_geo_grp+'.v', 0)
            pm.setAttr(setup_geo_grp+'.v', 0)
    
    def toggleCurveButtonClicked(self):
        face_jnt_grp = rig.RigMain.findPerseusName()+'_face_jnt_grp'
        face_curve_jnt_grps = [
                        rig.RigMain.findPerseusName()+'_RUpEye_curve_grp',
                        rig.RigMain.findPerseusName()+'_RUpEye_center_grp_jnt',
                        rig.RigMain.findPerseusName()+'_RDownEye_curve_grp',
                        rig.RigMain.findPerseusName()+'_RDownEye_center_grp_jnt',
                        rig.RigMain.findPerseusName()+'_LUpEye_curve_grp',
                        rig.RigMain.findPerseusName()+'_LUpEye_center_grp_jnt',
                        rig.RigMain.findPerseusName()+'_LDownEye_curve_grp',
                        rig.RigMain.findPerseusName()+'_LDownEye_center_grp_jnt'
                        ]

        nodes = pm.listConnections(face_jnt_grp)
        facial_setting_node = None
        for node in nodes:
            if 'facial' in node.name().lower() and 'settings' in node.name().lower():
                facial_setting_node = node
                break

        curve_vis_state = pm.getAttr(face_curve_jnt_grps[0]+'.v')     
        if curve_vis_state == 1:
            pm.setAttr(facial_setting_node.name()+'.faceJoints', 0)
            for grp in face_curve_jnt_grps:
                pm.setAttr(grp+'.v', 0)
        else:
            pm.setAttr(facial_setting_node.name()+'.faceJoints', 1)
            for grp in face_curve_jnt_grps:
                pm.setAttr(grp+'.v', 1)
    def refreshAllData(self):
        self.updateCharInfo()
        self.populateRigData() 
        self.populateBuildSteps()  

