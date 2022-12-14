import tools, shapes
import maya.api.OpenMaya as om
import pymel.core as pm
import json, os, math

class RigMain:
    '''
    has chracter independent class methods

    '''
    @classmethod
    def getRigDataPath(cls):
        return("D:/work/tlool/data")

    @classmethod
    def getEtcGrp(cls):
        etc_grp = tools.createGroup('etc_grp')
        return(etc_grp)

    @classmethod
    def getFacialHiddenGrp(cls, vis=False):
        facial_hidden_grp = tools.createGroup('facial_hidden_when_done_grp', parent = cls.getEtcGrp())
        pm.setAttr('facial_hidden_when_done_grp.v', vis)
        return(facial_hidden_grp)

    @classmethod
    def getFacialTargetGrp(cls):
        facial_target_grp = tools.createGroup('facial_target_grp', parent = cls.getEtcGrp())        
        return(facial_target_grp)

    @classmethod
    def getFacialJntGrp(cls):
        facial_jnt_grp = tools.createGroup('facial_jnt_grp', parent = cls.getFacialHiddenGrp())        
        return(facial_jnt_grp)


    @classmethod
    def findCharName(cls):
        targets = pm.ls('*_body_rig_head_geo_facial')
        if len(targets) == 0:
            raise ValueError('Open a rig scene file and run!!!!!')
        if len(targets) > 1:
            raise ValueError('rig_head_geo_facial objects are more than one!!!')
        name = str(targets[0])
        name = name.replace('_body_rig_head_geo_facial', '')
        return(name)

    @classmethod
    def findPerseusName(cls):
        targets = pm.ls('*_facial_geo_grp')
        if len(targets) == 0:
            raise ValueError('facial_geo_grp does not exists. No perseus rig found!!!')
        if len(targets) > 1:
            raise ValueError('facial_geo_grp groups are more than one!!!')
        name = str(targets[0])
        name = name.replace('_facial_geo_grp', '')
        return(name)

class RigData:
    '''
    rig_info.json data stuffs

    '''

    name = None
    folder = None
    file_name = None
    def __init__(self, name, file_full_path=None):
        self.name = name
        self.file_name = name + '_rig_info.json'
        self.folder = RigMain.getRigDataPath()
        if file_full_path is not None:
            buf = file_full_path.split('/')[:-1]
            self.folder = '/'.join(buf)
            self.file_name = file_full_path.split('/')[-1]
        #self.folder = "D:/work/tlool/data" #temporary
        self.common_folder = "D:/work/tlool/data" #temporary
        self.common_file_name = 'common_rig_info.json'
    def getName(self):
        return(self.name)
    def getFolder(self):
        return(self.folder)
    def getFileName(self):
        return(self.file_name)
    def getFullFilePath(self):
        full_path = self.folder + '/' + self.file_name
        if os.path.exists(full_path):
            return(full_path)
        else:
            pm.warning("A file(" + full_path + ') does not exists.')
            pm.warning("Creating a new file(" + full_path + ')!')
            self.createNew()
            pm.warning("A new file(" + full_path + ') has been created!')
            #pm.warning("Instead, returning 'common_rig_info.json'.")
            #full_path = self.common_folder + '/' + self.common_file_name
            return(full_path)
    def createNew(self):
        try:
            data = dict()
            data['name'] = self.name
            full_path = self.folder + '/' + self.file_name
            with open(full_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except Exception as e:
            pm.warning("New data file creation failes : "+full_path)
            pm.warning(e.message)
    def saveData(self, key, value):
        pass
    def loadData(self):
        with open(self.getFullFilePath()) as json_file:
            data = json.load(json_file)
            return(data)
    def getKeys(self, type=None):
        '''
        get all keys or keys of a type
        key types = ['vtx', 'area']

        foreheadVtx : choose 5 vertices
        philtrumVtx : choose 3 vertices
        jawDodownVtx : choose 1 vertex
        eyeClownVtx : choose 2 vertices

        '''
        connected_vtx_keys = ['dwLipVtx','upLipVtx', 
                    'rUpEyelidInnerVtx', 'rDwEyelidInnerVtx',
                    'rUpEyelidOuterVtx', 'rDwEyelidOuterVtx',
                    'lUpEyelidInnerVtx', 'lDwEyelidInnerVtx', 
                    'lUpEyelidOuterVtx', 'lDwEyelidOuterVtx']
        unconnneted_vtx_keys =['jawDodownVtx','philtrumVtx','foreheadVtx', 'eyeClownVtx']
        vtx_keys = connected_vtx_keys + unconnneted_vtx_keys
        area_keys = ['dwLipArea','upLipArea', 
                    'rUpEyelidArea', 'rDwEyelidArea', 
                    'lUpEyelidArea', 'lDwEyelidArea']
        falloff_keys = ['upLipFalloff', 'dwLipFalloff', 'eyelidsWeight',
                    'jawDodownFalloff', 'philtrumFalloff', 'foreheadFalloff',
                    'eyeClownFalloff']
        all_keys = []
        if type == 'vtx' or type is None:
            all_keys = all_keys + vtx_keys
        if type == 'area' or type is None:
            all_keys = all_keys + area_keys
        if type == 'falloff' or type is None:
            all_keys = all_keys + falloff_keys
        if type == 'connected_vtx':
            all_keys = connected_vtx_keys
        if type is None:
            pass
            #pm.warning("key types = ['vtx', 'area']")
        return(all_keys)

    def setValue(self, key, value):
        data = self.loadData()
        try:
            if key == 'name':
                data['name'] = value
            elif key in self.getKeys(type='falloff'):
                data[key] = value
            elif key in self.getKeys(type='vtx'):
                if type(value) == type([]):
                    if not len(value) > 0:
                        raise ValueError("Value is an empty list!!!!")
                    elif '_render_' in str(value[0]):
                        raise ValueError("Target mesh is for render mesh!!! Change the selection!!!!!")
                else:
                    print(value)
                    raise ValueError('Unrecognized values!!!')
                if type(value[0]) is not pm.general.MeshVertex:
                    raise ValueError("Value must be a list of vertices when key is {}!!!!".format(key))
                vtx_id_list = tools.getVertexIndicesFromVertices(value)
                data['vertices'][key[:-3]] = vtx_id_list
            elif key in self.getKeys(type='area'):
                if type(value) == type([]):
                    if not len(value) > 0:
                        raise ValueError("Value is an empty list!!!!")
                    elif '_render_' in str(value[0]):
                        raise ValueError("Target mesh is for render mesh!!! Change the selection!!!!!")
                else:
                    print(value)
                    raise ValueError('Unrecognized values!!!')
                if type(value[0]) is not pm.general.MeshFace:
                    raise ValueError("Value must be a list of faces when key is {}!!!!".format(key))
                face_id_list = tools.getFaceIndicesFromFaces(value)
                data['faces'][key[:-4]] = face_id_list            
            else:
                raise ValueError('A unrecognized key : {}'.format(key))            
        except KeyError as e:
            data[e.message] = dict()
            raise Warning(e.message + ' is missing. The key added. So try again!!!!!' )
        finally:
            with open(self.getFolder() + "/" + self.getFileName(), 'w') as json_file:
                json.dump(data, json_file, indent=4)

    def getValue(self, mesh, key, type='component', raise_exception=True, selection_clear=False):
        '''
        mesh =polygon mesh transform
        key_list = ['downLipVtx', 'upLipVtx']
        type = 'component' or 'id'

        ** downLipVtx and upLipVtx shares both ends

        '''
        data = self.loadData()
        try:
            if key == 'name':
                return(data['name'])
            if key in self.getKeys(type='falloff'):
                return(data[key])                
            if key in self.getKeys(type='vtx'):
                vtx_id_list = data['vertices'][key[:-3]]
                vtxs = tools.getVerticesFromVertexIndices(mesh,vtx_id_list)
                ordered_vtxs = vtxs
                # in case of all vertixed should be connected
                if key in self.getKeys(type='connected_vtx'):
                    ordered_vtxs = tools.getOrderedVertices(vtxs)

                if selection_clear:
                    pm.select(clear=True)
                else:
                    pm.select(ordered_vtxs, r=True)
                if type == 'id':
                    return(tools.getVertexIndicesFromVertices(ordered_vtxs))            
                else:
                    return(ordered_vtxs)
            elif key in self.getKeys(type='area'):
                face_id_list = data['faces'][key[:-4]]
                faces = tools.getFacesFromFaceIndices(mesh, face_id_list)
                if selection_clear:
                    pm.select(clear=True)
                else:
                    pm.select(faces, r=True)
                if type == 'id':
                    return(face_id_list)
                else:
                    return(faces)
            else:
                if raise_exception:
                    raise ValueError('A unrecognized key : {}'.format(key))
                else:
                    pm.warning('A unrecognized key : {}'.format(key))
                    return(None)
        except KeyError as e:
            if raise_exception:
                raise KeyError('A key({}) is missing in rig_info.json!!!!'.format(e.message)) 
            else:
                pm.warning('A key({}) is missing in rig_info.json!!!!'.format(e.message))
                return(None)
        except ValueError as e:
            if raise_exception:
                raise ValueError(e.message) 
            else:
                pm.warning(e.message)
                return(vtxs)

class RigChar:
    '''
    character dependent data and rigging functions
    '''

    @classmethod
    def getRigHeadGeo(cls):
        targets = pm.ls('*_body_rig_head_geo')
        if len(targets) > 1:
            raise ValueError('body_rig_head_geo are more than one!!!!')
        return(pm.ls('*_body_rig_head_geo')[0])

    @classmethod
    def getHeadJnt(self):
        return(pm.ls('Head_M')[0])

    char_name = None
    perseus_name = None
    sublip_gro = None
    jntBase_grp = None
    bridge_grp = None
    jntBase_head_geo = None
    sublip_head_geo = None
    bridge_geos = None
    bridge_head_geo = None
    jntBase_jnt_grp = None
    jntBase_head_skin_jnt = None
    jntBase_all_downLip_skin_jnts = None
    jntBase_all_upLip_skin_jnts = None
    lip_ctrl_grp = None
    lip_crv_grp = None
    def __init__(self, char_name, perseus_name):
        self.char_name = char_name
        self.perseus_name = perseus_name
        self.jntBase_head_skin_jnt = self.getHeadSkinJnt().name()+'_jntBase'
        self.createJntBaseTargetGrp()
        self.createJntBaseJntGrp()
        self.createBridgeTargetGrp()
        self.createLipCtrlGrp()
        self.createLipCrvGrp()
        self.getJntBaseHeadGeo()
        jnts = pm.ls('upLip_jntBase_skin_jnt*', type='joint')
        if len(jnts)>0:
            self.jntBase_all_upLip_skin_jnts = pm.ls('upLip_jntBase_skin_jnt*', type='joint')
        jnts = pm.ls('dwLip_jntBase_skin_jnt*', type='joint')
        if len(jnts)>0:
            self.jntBase_all_downLip_skin_jnts = pm.ls('dwLip_jntBase_skin_jnt*', type='joint')

    def getName(self):
        self.getCharName()
    def getCharName(self):
        return(self.char_name)
    def getBaseName(self):
        if self.char_name.endswith('_base'):
            return(self.char_name)
        elif(self.char_name.split('_').__len__()>1):
            buf = self.char_name.split('_')
            buf[-1] = 'base'
            return(buf.join('_'))
        else:
            return(self.char_name+'_base')
    def getPRSName(self):
        return(self.perseus_name)
    def getPRSSetupGeoGrp(self):
        return(self.perseus_name+'_facial_setup_geo_grp')
    def getPRSFinalGeoGrp(self):
        return(self.perseus_name+'_facial_final_geo_grp')
    def getJawCtrl(self):
        return(pm.ls('Jaw_M')[0])
    def getRenderGeoGrp(cls):
        render_geo_grp = RigMain.findCharName()+'_body_render'
        if not pm.objExists(render_geo_grp):
            render_geo_grp = pm.ls('*_body_render', type='transform')[0]
        return(render_geo_grp)
    def getFacialGeoGrp(cls):
        facial_geo_grp = RigMain.findPerseusName()+'_facial_geo_grp' 
        return(facial_geo_grp)
    def getRigHeadSetupGeoGrp(cls):
        setup_geo_grp = RigMain.findPerseusName()+'_facial_setup_geo_grp'
        if pm.objExists(setup_geo_grp):
            return(setup_geo_grp)
        return(setup_geo_grp)
    def getRigHeadGeoGrp(cls):
        rig_geo_grp = RigMain.findCharName()+'_body_rig'
        if not pm.objExists(rig_geo_grp):
            rig_geo_grp = pm.ls('*_body_rig', type='transform')[0]
        return(rig_geo_grp)         
    def getRigHeadSetupGeo(self):
        targets = pm.ls('*_rig_head_geo_setup')
        if len(targets) > 1:
            raise ValueError('rig_head_geo_setup are more than one!!!!')
        return(pm.ls('*_rig_head_geo_setup')[0])
    def getHeadSkinJnt(self):
        return(pm.ls("*_facialHead_jnt_skin", type='joint')[0])
    def getAllLipSkinJnts(self):
        return(pm.ls("*Lip_jnt*_skin", type='joint'))
    def getAllSetupGeos(self):
        all_setup_geos = pm.listRelatives(self.getPRSSetupGeoGrp(), c=True)
        return(all_setup_geos)
    def getAllFinalGeos(self):
        all_final_geos = pm.listRelatives(self.getPRSFinalGeoGrp(), c=True)
        return(all_final_geos)
    def getSublipTargetGrp(self):
        return(self.sublip_grp)
    def createSublipTargetGrp(self):
        self.sublip_grp = tools.createGroup('sublip_target_grp', parent = RigMain.getFacialTargetGrp()) 
        return(self.getSublipTargetGrp())
    def getJntBaseTargetGrp(self):
        return(self.jntBase_grp)
    def createJntBaseTargetGrp(self):
        self.jntBase_grp = tools.createGroup('jntBase_target_grp', parent = RigMain.getFacialTargetGrp()) 
        return(self.getJntBaseTargetGrp())
    def getJntBaseJntGrp(self):
        return(self.jntBase_jnt_grp)
    def createJntBaseJntGrp(self):
        self.jntBase_jnt_grp = tools.createGroup('jntBase_jnt_grp', parent = RigMain.getFacialJntGrp()) 
        return(self.getJntBaseJntGrp())
    def getBridgeTargetGrp(self):
        return(self.bridge_grp)
    def createBridgeTargetGrp(self):
        self.bridge_grp = tools.createGroup('bridge_target_grp', parent = RigMain.getFacialTargetGrp()) 
        return(self.getBridgeTargetGrp())
    def getJntBaseHeadGeo(self):
        self.jntBase_head_geo = str(self.getRigHeadSetupGeo())+"_jntBase"
        return(self.jntBase_head_geo)
    def getSublipHeadGeo(self):
        self.sublip_head_geo = str(self.getRigHeadSetupGeo())+"_sublip"
        return(self.sublip_head_geo)
    def addSetupHeadGeoBlendTarget(self, target_geo):
        bs_name =  str(self.getRigHeadSetupGeo())+'_BS'
        if pm.objExists(bs_name):
            #add targets
            existing_targets = pm.blendShape(bs_name, q=True, t=True)
            pm.blendShape(bs_name, e=True, t=(self.getRigHeadSetupGeo(), len(existing_targets), target_geo, 1.0))
            pm.setAttr(bs_name+'.'+target_geo, 1)
            #pm.blendShape(target_geo, self.getRigHeadSetupGeo(), name=self.getRigHeadSetupGeo().name()+'_BS', foc=True)[0]
        else:
            #craete targets
            bs_name = pm.blendShape(target_geo, self.getRigHeadSetupGeo(), name=bs_name, foc=True)[0]
            pm.setAttr(bs_name+'.'+target_geo, 1)
        return(bs_name)
    def createSublipHeadGeo(self):
        sublip_head_geo_name = self.getSublipHeadGeo
        if pm.objExists(sublip_head_geo_name):
            pm.warning(sublip_head_geo_name + "exits!!! Skipping this!")
            self.sublip_head_geo = sublip_head_geo_name
        else:
            self.sublip_head_geo = pm.duplicate(self.getRigHeadSetupGeo(), rr=True, name=str(self.getRigHeadSetupGeo())+"_sublip")[0]
            # change below to add bs target
            self.addSetupHeadGeoBlendTarget(self.sublip_head_geo.name())
            #jnt_base_to_set_bs = pm.blendShape(self.sublip_head_geo.name(), self.getRigHeadSetupGeo(), name=self.getRigHeadSetupGeo().name()+'_BS', foc=True)[0]
            #pm.setAttr(jnt_base_to_set_bs+'.'+self.sublip_head_geo.name(), 1)
            pm.parent(self.sublip_head_geo, self.createSublipTargetGrp())
            pm.setAttr(str(self.getSublipTargetGrp())+'.v', 0)
        return(self.getSublipHeadGeo())
    def createJntBaseHeadGeo(self):
        jntBase_head_geo_name = self.getJntBaseHeadGeo
        if pm.objExists(jntBase_head_geo_name):
            pm.warning(jntBase_head_geo_name + "exits!!! Skipping this!")
            self.jntBase_head_geo = jntBase_head_geo_name
        else:
            self.jntBase_head_geo = pm.duplicate(self.getRigHeadSetupGeo(), rr=True, name=str(self.getRigHeadSetupGeo())+"_jntBase")[0]
            self.addSetupHeadGeoBlendTarget(self.jntBase_head_geo.name())
            #jnt_base_to_set_bs = pm.blendShape(self.jntBase_head_geo.name(), self.getRigHeadSetupGeo(), name=self.getRigHeadSetupGeo().name()+'_BS', foc=True)[0]
            #pm.setAttr(jnt_base_to_set_bs+'.'+self.jntBase_head_geo.name(), 1)
            pm.parent(self.jntBase_head_geo, self.createJntBaseTargetGrp())
            pm.setAttr(str(self.getJntBaseTargetGrp())+'.v', 0)
        return(self.getJntBaseHeadGeo())
    def getBridgeGeos(self): 
        return(self.bridge_geos)
    def getBridgeHeadGeo(self):
        return(self.bridge_head_geo)    
    def createBridgeGeos(self):
        if self.bridge_geos is not None:
            pm.warning("Bridge geos exists!!!!!")
        self.bridge_geos = []
        brige_geos_existing = pm.listRelatives(self.getBridgeTargetGrp(), c=True)
        if len(brige_geos_existing) > 0:
            self.bridge_geos = brige_geos_existing
        else:
            for geo in self.getAllFinalGeos():
                new_name = geo.name()+"_bridge"
                dup = pm.duplicate(geo, rr=True, name=new_name)[0]
                self.bridge_geos.append(dup)
                #print(dup, self.getBridgeTargetGrp() )
                pm.parent(dup, self.getBridgeTargetGrp())
                bs = pm.blendShape(geo.name(), dup, name=new_name+'_BS')[0]
                pm.setAttr(bs+'.'+geo.name(), 1)
                dup_shp = pm.listRelatives(dup, shapes=True)[0]
                tweak = pm.listConnections(dup_shp, source=True, type='tweak')[0]
                pm.rename(tweak, dup.name()+'_TW')
                if "rig_head_geo_facial" in new_name:
                    self.bridge_head_geo = new_name
        pm.setAttr(str(self.getBridgeTargetGrp())+'.v', 0)
        return(self.getBridgeGeos())
    def getJntBaseHeadSkinJnt(self):
        return(self.jntBase_head_skin_jnt)
    def getJntBaseJntGrp(self):
        return(self.jntBase_jnt_grp)
    def getLipCtrlGrp(self):
        return(self.lip_ctrl_grp)    
    def createLipCtrlGrp(self):
        self.lip_ctrl_grp = tools.createGroup('lip_ctrl_grp', parent=RigMain.getEtcGrp())
        return(self.lip_ctrl_grp)
    def getLipCrvGrp(self):
        return(self.lips_crv_grp)    
    def createLipCrvGrp(self):
        self.lips_crv_grp = tools.createGroup('lips_crv_grp', parent=RigMain.getFacialHiddenGrp())
        return(self.lips_crv_grp)
    def createJntBaseHeadSkinJnt(self):

        if pm.objExists(self.jntBase_head_skin_jnt):
            pm.warning(self.jntBase_head_skin_jnt + " exits!!! Skipping this!!!!")
            return(self.jntBase_head_skin_jnt)
        else:
            self.jntBase_head_skin_jnt = pm.duplicate(self.getHeadSkinJnt(), rr=True, name=self.jntBase_head_skin_jnt)[0]
            pm.parent(self.jntBase_head_skin_jnt, self.getJntBaseJntGrp())
            return(self.jntBase_head_skin_jnt)

    def createLipCrvs(self, rigData, rivet = True):
        # [upLip and downLip]----------------------------------------------
        part_list = ["up", "dw"] # dw means down

        all_set_ctrl_list = []
        all_bind_ctrl_list = []
        all_base_ctrl_list = []


        l_lips_end_pos_list = []
        r_lips_end_pos_list = []
        l_lips_end_pos_proxy_list = []
        r_lips_end_pos_proxy_list = []
        all_lips_pos_list= []
        for part in part_list:
            ctrl_color = None
            if part == 'up':
                ctrl_color = 'blue'
            elif part =='dw':
                ctrl_color = 'red'
            else:
                ctrl_color = 'yellow'

            partLip_crv_grp = self.getLipCrvGrp()
            #base_crv_org = perseus_name + '_'+part+'Lip_baseCurve'
            #base_crv = base_crv_org + '_ep'
            base_crv_name = part+'Lip_baseCurve'
            new_base_d1_crv_name = base_crv_name+'_d1'
            new_base_d3_crv_name = base_crv_name+'_d3'
            new_base_d1_s6_crv_name = base_crv_name+'_d1_s6'
            new_base_d1_s2_crv_name = base_crv_name+'_d1_s2'

            lip_vtx_list = rigData.getValue(self.getJntBaseHeadGeo(), part+'LipVtx')
            vtx_pnts = [pm.pointPosition(vtx, w=True).get()[:3] for vtx in lip_vtx_list]
            knots = [x for x in range(len(vtx_pnts))]
            base_crv = pm.curve(p=vtx_pnts, d=1, n=base_crv_name, k=knots)

            # generate curves
            new_base_d1_crv = pm.duplicate(base_crv, rr=True, name=new_base_d1_crv_name)[0]
            new_base_d3_crv = pm.rebuildCurve(new_base_d1_crv, rpo=0, rt=0, end=1, kr=2, kcp=1, kep=1, kt=0, d=3, tol=0.01, n=new_base_d3_crv_name)

            new_base_d1_s6_crv = tools.rebuildD1curve(new_base_d3_crv, spans=6, name=new_base_d1_s6_crv_name)
            new_base_d1_s2_crv = tools.rebuildD1curve(new_base_d3_crv, spans=4, name=new_base_d1_s2_crv_name)
            
            #new_base_d1_s6_crv = pm.rebuildCurve(new_base_d1_crv, rpo=0, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=6, d=1, tol=0.01, n=new_base_d1_s6_crv_name)
            #new_base_d1_s2_crv = pm.rebuildCurve(new_base_d1_crv, rpo=0, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=2, d=1, tol=0.01, n=new_base_d1_s2_crv_name)
            pm.parent(base_crv, new_base_d1_crv, new_base_d3_crv, new_base_d1_s6_crv, new_base_d1_s2_crv, partLip_crv_grp)
        
            pm.wire(new_base_d1_s6_crv, wire=new_base_d1_s2_crv, name=part+'Lip_wire_s6', dds=(0,10000))
            pm.wire(new_base_d3_crv, wire=new_base_d1_s6_crv, name=part+'Lip_wire_d3', dds=(0,10000))
            pm.wire(new_base_d1_crv, wire=new_base_d3_crv, name=part+'Lip_wire_d1', dds=(0,10000))
            pm.wire(base_crv, wire=new_base_d1_crv, name=part+'Lip_wire_ep', dds=(0,10000))
            

            # [create controllers]
            partLip_ctrl_grp = pm.createNode('transform', name=part+'Lip_ctrl_grp', p=self.getLipCtrlGrp())
            partLip_ctrl_proxy_grp = pm.createNode('transform', name=part+'Lip_ctrl_proxy_grp', p=self.getLipCtrlGrp())
            # first(set) ctrl
            set_ctrl_cluster_node, set_ctrl_cluster_handle = pm.cluster(new_base_d1_s2_crv_name+'.cv[1:3]', name=part+'Lip_set_CLS')
            mv0 = om.MVector(pm.pointPosition(new_base_d1_s2_crv_name+'.cv[1]'))
            mv1 = om.MVector(pm.pointPosition(new_base_d1_s2_crv_name+'.cv[3]'))
            d = (mv1-mv0).length()
            set_ctrl = shapes.makeLipSetCtrlShape(name='LipSet_'+part.upper()+'_M', scale=d, part=part)
            set_pos, set_drv, set_extra = tools.makePosDrvExtra(set_ctrl)
            set_proxy_ctrl = pm.createNode('transform', name='LipSet_'+part.upper()+'_M_proxy')
            set_proxy_pos, set_proxy_drv, set_proxy_extra = tools.makePosDrvExtra(set_proxy_ctrl) 
            pm.matchTransform(set_pos, set_ctrl_cluster_handle)
            pm.matchTransform(set_proxy_pos, set_ctrl_cluster_handle)
            pm.parent(set_ctrl_cluster_handle, set_proxy_ctrl)
            tools.connectAllTransform(set_ctrl, set_proxy_ctrl)
            tools.negateTranslation(set_ctrl, set_drv)
            pm.setAttr(set_ctrl_cluster_handle+'.v', 0)
            pm.parent(set_pos, partLip_ctrl_grp)
            pm.parent(set_proxy_pos, partLip_ctrl_proxy_grp)
            all_set_ctrl_list.append(set_ctrl)
            pm.connectAttr('FacialSettings.firstCtrl',str(set_pos)+'.v')

            # second(bind) ctrl
            #bind_ctrl_grp = pm.createNode('transform', name='lip_down_bind_ctrl_grp', p=etc_grp)
            bind_ctrl_grp = tools.createGroup(part+'Lip_bind_ctrl_grp', parent=partLip_ctrl_grp)
            postfix = tools.makePostfixForSides(7)
            bind_ctrls = []
            bind_proxy_ctrls = []
            bind_pos_list = []
            bind_pos_proxy_list = []
            for i in range(7):
                bind_ctrl_cluster, bind_ctrl_cluster_handle = pm.cluster(new_base_d1_s6_crv_name+'.cv[{}]'.format(i), name=part+'Lip_bind_CLS'+postfix[i])
                ctrl_size = d/10.0*(3.0 - abs(3.0-i)*0.6)/3.0
                cy_value = d/20.0  
                if part == 'dw':
                    cy_value = -1.0*cy_value
                bind_ctrl = pm.circle(name='LipBind_'+part.upper()+postfix[i], r=ctrl_size, cy=cy_value, cz=d/10.0, ch=False)[0]
                tools.setColorIndex(bind_ctrl, ctrl_color)
                bind_pos, bind_drv, bind_extra = tools.makePosDrvExtra(bind_ctrl)
                bind_proxy_ctrl = pm.createNode('transform', name='LipBind_'+part.upper()+postfix[i]+'_proxy')
                bind_pos_proxy, bind_drv_proxy, bind_extra_proxy = tools.makePosDrvExtra(bind_proxy_ctrl)
                pm.matchTransform(bind_pos, bind_ctrl_cluster_handle)
                pm.matchTransform(bind_pos_proxy, bind_ctrl_cluster_handle)
                pm.parent(bind_ctrl_cluster_handle, bind_proxy_ctrl)
                pm.parent(bind_pos, bind_ctrl_grp)
                if postfix[i].endswith('_R'):
                    tools.connectMirroredAllTransform(bind_ctrl, bind_proxy_ctrl)
                    pm.setAttr(str(bind_pos)+'.sx', -1)
                else:                    
                    tools.connectAllTransform(bind_ctrl, bind_proxy_ctrl)
                tools.negateTranslation(bind_ctrl, bind_drv)
                pm.orientConstraint(set_proxy_ctrl, bind_drv_proxy, mo=True)

                pm.setAttr(bind_ctrl_cluster_handle+'.v', 0)
                bind_ctrls.append(bind_ctrl)
                bind_proxy_ctrls.append(bind_proxy_ctrl)
                bind_pos_list.append(bind_pos)
                bind_pos_proxy_list.append(bind_pos_proxy)
                pm.parent(bind_pos, partLip_ctrl_grp)
                pm.parent(bind_pos_proxy, partLip_ctrl_proxy_grp)
                pm.connectAttr('FacialSettings.secondCtrl',str(bind_pos)+'.v')


            l_lips_end_pos_list.append(bind_pos_list[-1])
            r_lips_end_pos_list.append(bind_pos_list[0])
            l_lips_end_pos_proxy_list.append(bind_pos_proxy_list[-1])
            r_lips_end_pos_proxy_list.append(bind_pos_proxy_list[0])
            all_bind_ctrl_list = all_bind_ctrl_list + bind_ctrls
            pm.refresh()

            # third(base) ctrl
            base_ctrl_grp = pm.createNode('transform', name=part+'Lip_base_ctrl_grp', p=partLip_ctrl_grp)
            
            spans = pm.getAttr(base_crv_name+'.spans')
            degree = pm.getAttr(base_crv_name+'.degree')
            cv_cnt = spans+degree
            mv0 = om.MVector(pm.pointPosition(new_base_d1_s2_crv_name+'.cv[1]'))
            mv1 = om.MVector(pm.pointPosition(new_base_d1_s2_crv_name+'.cv[3]'))
            d = (mv1-mv0).length()
            
            poc_postfix = tools.makePostfixForSides(cv_cnt, name="poc")
            ctrl_postfix = tools.makePostfixForSides(cv_cnt, name=None)
            loc_postfix = tools.makePostfixForSides(cv_cnt, name="loc")
            base_pos_list = []
            base_ctrls = []
            base_locs = []
            for i in range(cv_cnt):
                poc = pm.pointOnCurve(base_crv_name, pr=i, top=False, ch=True)
                poc = pm.rename(poc, part+'Lip_base'+poc_postfix[i])
                base_ctrl = tools.makeBallShape('LipBase_'+part.upper()+ctrl_postfix[i], radius=d/40.0)
                tools.setColorIndex(base_ctrl, ctrl_color)
                base_pos, base_drv, base_extra =  tools.makePosDrvExtra(base_ctrl)
                base_ctrl_proxy = pm.createNode('transform', name='LipBase_'+part.upper()+ctrl_postfix[i]+'_proxy')
                base_pos_proxy, base_drv_proxy, base_extra_proxy = tools.makePosDrvExtra(base_ctrl_proxy)

                loc  = pm.spaceLocator(name=part+'Lip_base'+loc_postfix[i])
                locShape = tools.setLocatorLocalScale(loc,0.1)
                pm.parent(loc, self.getJntBaseJntGrp())
                pm.connectAttr(poc+'.position', loc+'.t')
                target_jnt = part+"Lip_jntBase_skin_jnt"+str(i).zfill(2)
                pm.parent(target_jnt, loc)

                tmp_matching_loc = pm.spaceLocator(n='tmp_matching_loc')
                pm.matchTransform(tmp_matching_loc, loc)
                tmp_matching_tc = pm.tangentConstraint(new_base_d3_crv, tmp_matching_loc, aim=(1,0,0), u=(0,1,0), wut='vector', wu=(0,1,0))

                pm.matchTransform(base_pos, tmp_matching_loc)
                pm.matchTransform(base_pos_proxy, tmp_matching_loc)

                pm.delete(tmp_matching_tc)
                pm.delete(tmp_matching_loc)

                if ctrl_postfix[i].endswith('_R'):
                    tools.connectMirroredAllTransform(base_ctrl, base_ctrl_proxy)
                    pm.setAttr(str(base_pos)+'.sx', -1)
                else:                    
                    tools.connectAllTransform(base_ctrl, base_ctrl_proxy)                
                tools.negateTranslation(base_ctrl, base_drv)

                pm.parentConstraint(base_ctrl_proxy,target_jnt, mo=True)
                pm.scaleConstraint(base_ctrl_proxy,target_jnt, mo=True)    
            
                pm.parentConstraint(loc,base_drv_proxy, mo=True)
                pm.scaleConstraint(loc,base_drv_proxy, mo=True)    

                base_pos_list.append(base_pos)
                base_ctrls.append(base_ctrl)
                base_locs.append(loc)
                pm.parent(base_pos, base_ctrl_grp)
                pm.parent(base_pos_proxy, partLip_ctrl_proxy_grp)
                pm.connectAttr('FacialSettings.thirdCtrl',str(base_pos)+'.v')

            bind_proxy_ctrl_decomposeMatrix_node_list = []
            for bind_proxy_ctrl in bind_proxy_ctrls:
                decompose_node = pm.shadingNode('decomposeMatrix', asUtility=True, name=str(bind_proxy_ctrl)+'_dcm')
                bind_proxy_ctrl_decomposeMatrix_node_list.append(decompose_node)
                pm.connectAttr(str(bind_proxy_ctrl)+'.worldMatrix[0]', str(decompose_node)+'.inputMatrix')

            for base_loc in base_locs:
                closest_bind_proxy_ctrl = tools.findClosestNode(base_loc, bind_proxy_ctrls)
                for node in pm.listConnections(closest_bind_proxy_ctrl, d=True):
                    if pm.nodeType(node) == 'decomposeMatrix':
                        pm.connectAttr(str(node)+'.outputRotate', str(base_loc)+'.rotate')
            pm.refresh()
            all_lips_pos_list = all_lips_pos_list + [set_pos]
            all_lips_pos_list = all_lips_pos_list + bind_pos_list
            all_lips_pos_list = all_lips_pos_list + base_pos_list
            all_base_ctrl_list = all_base_ctrl_list + base_ctrls

        # lips ends ctrl
        lips_end_pos_lists = [l_lips_end_pos_list, r_lips_end_pos_list]
        lips_end_pos_proxy_lists = [l_lips_end_pos_proxy_list, r_lips_end_pos_proxy_list]
        all_lips_end_ctrl_list = []
        for side, lips_end_pos_list, lips_end_pos_proxy_list in zip(['_L', '_R'], lips_end_pos_lists, lips_end_pos_proxy_lists):
            lip_end_ctrl = pm.circle(name='LipBindEnd'+side, r=d/10.0, cz=d/5.0, ch=False)[0]
            tools.setColorIndex(lip_end_ctrl, 'yellow')
            lip_end_pos, lip_end_drv, lip_end_extra = tools.makePosDrvExtra(lip_end_ctrl)
            pm.matchTransform(lip_end_pos, lips_end_pos_list[0])

            lip_end_ctrl_proxy = pm.createNode('transform', name='LipBindEnd'+side+'_proxy')
            lip_end_pos_proxy, lip_end_drv_proxy, lip_end_extra_proxy = tools.makePosDrvExtra(lip_end_ctrl_proxy)
            pm.matchTransform(lip_end_pos_proxy, lips_end_pos_list[0])

            tools.connectAllTransform(lip_end_ctrl, lip_end_ctrl_proxy)
            tools.negateTranslation(lip_end_ctrl, lip_end_extra)
            tools.halfTranslation(self.getJawCtrl(), lip_end_drv)
            tools.halfRotation(self.getJawCtrl(), lip_end_drv)

            pm.parent(lips_end_pos_list, lip_end_ctrl)
            pm.parent(lip_end_pos, self.getLipCtrlGrp())
            pm.parent(lips_end_pos_proxy_list, lip_end_ctrl_proxy)
            pm.parent(lip_end_pos_proxy, partLip_ctrl_proxy_grp)

            all_lips_pos_list.append(lip_end_pos)
            all_lips_pos_list.remove(lips_end_pos_list[0])
            all_lips_pos_list.remove(lips_end_pos_list[1])

            all_lips_end_ctrl_list.append(lip_end_ctrl)
            pm.connectAttr('FacialSettings.secondCtrl',str(lip_end_pos)+'.v')
        pm.refresh()
        # rivet all ctrls created in this stage
        # add rivets on rig head geo
        if rivet == True:
            meshShape = pm.listRelatives(self.getRigHeadGeo(), s=True)[0]
            uvSet = pm.polyUVSet(meshShape, q=True, auv=True)[0]
            
            #rivet_target_faces = tools.getFacialFaces(self.getRigHeadGeo(), part=part+'Lip')
            up_lip_faces = rigData.getValue(self.getRigHeadGeo(), 'upLipArea')
            dw_lip_faces = rigData.getValue(self.getRigHeadGeo(), 'dwLipArea')

            follicles=[]
            for node in all_lips_pos_list:
                rivet_target_faces = up_lip_faces
                if '_DW_' in str(node):
                    rivet_target_faces = dw_lip_faces
                follicle = tools.makeRivet([node], rivet_target_faces)[0]
                pm.pointConstraint(follicle, node, mo=True)
                pm.orientConstraint(self.getHeadJnt(), node, mo=True)
                pm.scaleConstraint('Head_M', node, mo=True)
                follicles.append(follicle)
            follcle_grp = tools.createGroup('lip_follicle_grp', parent=self.getLipCtrlGrp())
            pm.parent(follicles, follcle_grp)
            pm.setAttr('lip_follicle_grp.v', 0)
        pm.select(clear=True)
        all_ctrl_set = pm.sets(name='jntBase_all_ctrl_set')
        pm.sets(all_ctrl_set, add=all_set_ctrl_list)
        pm.sets(all_ctrl_set, add=all_bind_ctrl_list)
        pm.sets(all_ctrl_set, add=all_lips_end_ctrl_list)
        pm.sets(all_ctrl_set, add=all_base_ctrl_list)

    def getJntBaseLipSkinJnts(self, part=None):
        if part is None:
            return(self.jntBase_all_downLip_skin_jnts+self.jntBase_all_upLip_skin_jnts)
        if part == 'up':
            return(self.jntBase_all_upLip_skin_jnts)
        if part == 'dw':
            return(self.jntBase_all_downLip_skin_jnts)
        raise ValueError('Hm...... Something has gone wrong!!!')

    def createJntBaseLipSkinJnts(self, rigData):
        # [upLip and downLip]----------------------------------------------
        if self.jntBase_all_downLip_skin_jnts is not None:
            raise ValueError('jntBase_all_downLip_skin_jnts has a value!!!!!')
        if self.jntBase_all_upLip_skin_jnts is not None:
            raise ValueError('jntBase_all_upLip_skin_jnts has a value!!!!!')

        self.jntBase_all_downLip_skin_jnts = []
        self.jntBase_all_upLip_skin_jnts = []

        part_list = ["up", "dw"]

        for part in part_list:
            head_skin_jnt = self.getHeadSkinJnt()
            #all_lip_skin_jnts = self.getAllLipSkinJnts()

            lip_vtx_list = rigData.getValue(self.getJntBaseHeadGeo(), part+'LipVtx')
            vtx_pnts = [pm.pointPosition(vtx, w=True).get()[:3] for vtx in lip_vtx_list]

            for i, pnt in enumerate(vtx_pnts):
                jnt_name = part+'Lip_jntBase_skin_jnt'+str(i).zfill(2)
                new_jnt = pm.joint(name=jnt_name, p=pnt)
                if part == 'up':
                    self.jntBase_all_upLip_skin_jnts.append(new_jnt)
                elif part == 'dw':
                    self.jntBase_all_downLip_skin_jnts.append(new_jnt)

                pm.parent(new_jnt, self.getJntBaseJntGrp())



    def bindJntBaseSkin(self):
        # bind skin to new (jntBase) geo
        print("# bind skin weights : step 1")

        jntBase_sc = str(self.getJntBaseHeadGeo())+'_SC'
        if not pm.objExists(jntBase_sc):
            jntBase_sc = pm.skinCluster(self.getJntBaseHeadGeo(), self.getJntBaseHeadSkinJnt(), self.getJntBaseLipSkinJnts(), name=jntBase_sc, sm=0, mi=8)
        all_infs = pm.skinCluster(jntBase_sc, q=True, inf=True)
        print("# paint skin weights : step 2(head)")
        pm.select(str(self.getJntBaseHeadGeo())+'.vtx[*]', r=True)
        all_vtxes = pm.ls(sl=True, fl=True)
        for vtx in all_vtxes:
            pm.skinPercent(jntBase_sc, vtx, tv=[str(self.getJntBaseHeadSkinJnt()), 1.0])

    def paintJntBaseSkinWeight(self, rigData, init=False, falloffRadiusUp=2.5, falloffRadiusDown=3.5):
        jntBase_sc = tools.getSkinClusterFromMesh(self.getJntBaseHeadGeo())            
        print(self.getJntBaseHeadSkinJnt())
        print(self.getJntBaseHeadGeo())
        if init:
            print("# paint skin weights : step 2(head) : re-done")
            pm.select(str(self.getJntBaseHeadGeo())+'.vtx[*]', r=True)
            all_vtxes = pm.ls(sl=True, fl=True)
            for vtx in all_vtxes:
                pm.skinPercent(jntBase_sc, vtx, tv=[str(self.getJntBaseHeadSkinJnt()), 1.0])
        print("# paint skin weights : step 3(lips)")
        for part in ['upLip','dwLip']:
            #part = 'dwLip'
            
            falloff_radius = None
            
            #tol = 0.1
            if part == 'upLip':
                falloff_radius = falloffRadiusUp
            if part == 'dwLip':
                falloff_radius = falloffRadiusDown
        
            # find lips vertices closest to joints respectively
            faces = rigData.getValue(self.getJntBaseHeadGeo(), part+'Area', type='component')
            vtxs = pm.polyListComponentConversion(faces, fromFace=True, toVertex=True)
            pm.select(vtxs, r=True)
            vtxs = pm.ls(sl=True,fl=True)

            # assign skin weights by falloff radius
            # for every vertex, find joints in radius and add

            for vtx in vtxs:
                jnts_in_radius = []
                closest_jnt = None
                closest_dis = 100000
                weights = []
                mPos_vtx = om.MVector(pm.pointPosition(vtx, w=True))
                for jnt in self.getJntBaseLipSkinJnts(part=part[:-3]):
                    mPos_jnt = om.MVector(pm.xform(jnt, q=True, ws=True, rp=True))
                    dis = (mPos_vtx-mPos_jnt).length()
                    if dis < falloff_radius:
                        jnts_in_radius.append(jnt)
                        weight = pow( (1-dis/falloff_radius),20)
                        weights.append(weight)
                    if dis < closest_dis:
                        closest_jnt=jnt
                        closest_dis = dis
            
                normalized_weights = [weight/sum(weights) for weight in weights]
                head_jnt_weight = 1.0 - max(math.cos(0.5*math.pi*closest_dis/falloff_radius), 0)
                modified_weights = [weight*(1.0-head_jnt_weight) for weight in normalized_weights]
            
                weights_to_assign = modified_weights
                jnts_to_assign = jnts_in_radius
            
                weights_to_assign.append(head_jnt_weight)
                jnts_to_assign.append(self.getJntBaseHeadSkinJnt())
                
                jnts_n_weights = []
                for weight, jnt in zip(weights_to_assign, jnts_to_assign):
                    jnts_n_weights.append((str(jnt), weight))
                
                pm.skinPercent(jntBase_sc, vtx, tv=jnts_n_weights)
            
                #print(sc, jnts_n_weights)
                #pm.skinPercent(sc, vtx, tv=jnts_n_weights)
            #pm.select(vtx, jnts_in_radius)

            pm.select(vtxs)

        print("# copy skin weights complete")

    def createEyeCrvs(self, rigData, rivet=True):
        parts = ['rUp', 'rDw', 'lUp', 'lDw']

        prefix_dict = dict()
        prefix_dict['rUp'] = '_RUp'
        prefix_dict['rDw'] = '_RDown'
        prefix_dict['lUp'] = '_LUp'
        prefix_dict['lDw'] = '_LDown'

        ctrl_dict = dict()
        ctrl_dict['rUp'] = 'EyelidSet_UP_R'
        ctrl_dict['rDw'] = 'EyelidSet_DW_R'
        ctrl_dict['lUp'] = 'EyelidSet_UP_L'
        ctrl_dict['lDw'] = 'EyelidSet_DW_L'

        for part in parts:
            prefix = prefix_dict[part]
            crv_grp = RigMain.findPerseusName()+prefix+'Eye_curve_grp'
            base_crv = RigMain.findPerseusName()+prefix+'Eye_baseCurve'
            bind_crv = RigMain.findPerseusName()+prefix+'Eye_bindCurve'
            base_crv_wire = RigMain.findPerseusName()+prefix+'Eyecurve_wire'
            
            new_bind_d1_s7_crv_name = base_crv + 're_d1_s7'
            new_bind_d1_s7_crv = pm.rebuildCurve(bind_crv, ch=0, rpo=0, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=7, d=1, tol=0.01, n=new_bind_d1_s7_crv_name)[0]
            pm.parent(new_bind_d1_s7_crv, crv_grp)
            #print(base_crv, base_crv_shp, base_crv_wire, new_bind_d1_s7_crv)
            #pm.select(base_crv, base_crv_shp, base_crv_wire, new_bind_d1_s7_crv)

            pm.delete(base_crv_wire)
            
            #blink bs set-up
            eyelid_set_ctrl = ctrl_dict[part] 
            base_crv_blink_bs = RigMain.findPerseusName()+prefix+'Eye_base_blendShape'
            base_crv1 = RigMain.findPerseusName()+prefix+'Eye_baseCurve1'
            persesus_eye_ctrl = RigMain.findPerseusName() + '_'+part[0].upper()+'Eye_target_ctrl'
            eyelid_blink_bs_crv_list = []
            blink_steps = [0.7, 0.5, 0.3, 0.0]
            if 'Dw' in part:
                blink_steps = [0.3, 0.5, 0.7, 1.0]

            for step in blink_steps:
                pm.setAttr(persesus_eye_ctrl+'.blinkSide', step)
                cnt = len(eyelid_blink_bs_crv_list)+1
                eyelid_blink_bs_crv_name = base_crv1 + "_bs_{}_crv".format(str(cnt).zfill(2))
                eyelid_blink_bs_crv = pm.duplicate(base_crv1, name=eyelid_blink_bs_crv_name)[0]
                eyelid_blink_bs_crv_list.append(eyelid_blink_bs_crv)
            base_crv_new_bs_name = base_crv + "_custom_blink_bs"
            new_bs = pm.blendShape(eyelid_blink_bs_crv_list[-1], base_crv, name=base_crv_new_bs_name, foc=True)[0]
            pm.setAttr(new_bs+'.supportNegativeWeights', 1)


            for i, step in enumerate(blink_steps[:-1]):
                print(i,round(1.0-step,2))
                if 'Dw' in part:
                    pm.blendShape(new_bs, edit=True, ib=True, t=(base_crv, 0, eyelid_blink_bs_crv_list[i],round(step,2)))
                else:
                    pm.blendShape(new_bs, edit=True, ib=True, t=(base_crv, 0, eyelid_blink_bs_crv_list[i],round(1.0-step,2)))

            pm.refresh()

            pm.setAttr(persesus_eye_ctrl+'.blinkSide', 0.0)
            y_highest = pm.exactWorldBoundingBox(base_crv)[4]
            y_lowest = pm.exactWorldBoundingBox(base_crv1)[1]
            eyelids_dis = abs(y_highest-y_lowest)

            if 'Dw' in part:
                pm.setAttr(persesus_eye_ctrl+'.blinkSide', 1.0)
                y_highest = pm.exactWorldBoundingBox(base_crv1)[4]
                y_lowest = pm.exactWorldBoundingBox(base_crv)[1]
                eyelids_dis = abs(y_highest-y_lowest)

            tools.multipliedConnection(eyelid_set_ctrl+'.ty', new_bs+'.'+eyelid_blink_bs_crv_list[-1], float(-1.0/eyelids_dis))
            pm.setAttr(persesus_eye_ctrl+'.blinkSide', 0.3)


            #pm.wire(new_bind_d1_s7_crv, wire=bind_crv, n=base_crv_wire, dds=(0,1000))
            #pm.wire(base_crv, wire=new_bind_d1_s7_crv, n=base_crv_wire, dds=(0,1000))

            # second(bind) ctrl
            #part = 'rUp'
            all_pos_list = []
            all_ctrl_list = []
            
            ctrl_color = None
            if 'Up' in part:
                ctrl_color = 'blue'
            elif 'Dw' in part:
                ctrl_color = 'red'
            else:
                ctrl_color = 'yellow'
            eye_ctrl_grp = tools.createGroup('eye_ctrl_grp', parent=RigMain.getEtcGrp())
            partEye_ctrl_grp = pm.createNode('transform', name=part+'Eye_ctrl_grp', p=eye_ctrl_grp)
            partEye_ctrl_proxy_grp = pm.createNode('transform', name=part+'Eye_ctrl_proxy_grp', p=eye_ctrl_grp)
            bind_ctrl_grp = tools.createGroup(part+'Eye_bind_ctrl_grp', parent=partEye_ctrl_grp)

            bind_ctrls = []
            bind_proxy_ctrls = []
            bind_pos_list = []
            bind_pos_proxy_list = []

            mv0 = om.MVector(pm.pointPosition(new_bind_d1_s7_crv_name+'.cv[0]'))
            mv1 = om.MVector(pm.pointPosition(new_bind_d1_s7_crv_name+'.cv[7]'))
            d = (mv1-mv0).length()

            bind_jnt_list = []
            bind_ctrl_cnt = 8 
            for i in range(bind_ctrl_cnt):
                postfix = '_'+str(i+1).zfill(2)+'_'+part[0].upper()
                bind_ctrl_cluster = None
                bind_ctrl_cluster_handle = None

                if part[0] == 'r':
                    bind_ctrl_cluster, bind_ctrl_cluster_handle = pm.cluster(new_bind_d1_s7_crv+'.cv[{}]'.format(i), name=part+'Eye_bind_CLS'+postfix)
                else:
                    bind_ctrl_cluster, bind_ctrl_cluster_handle = pm.cluster(new_bind_d1_s7_crv+'.cv[{}]'.format(bind_ctrl_cnt-i-1), name=part+'Eye_bind_CLS'+postfix)
                ctrl_size = d/15.0*(3.5 - abs(3.5-i)*0.4)/3.5
                cy_value = d/20.0  
                if 'Dw' in part:
                    cy_value = -1.0*cy_value

                bind_ctrl=None
                bind_ctrl_name = 'EyelidBind_'+part[1:].upper()+postfix
                if i==0 or i==bind_ctrl_cnt-1:
                    bind_ctrl = shapes.createHalfMoonShape(name=bind_ctrl_name, scale=ctrl_size*2.0, color=ctrl_color, part=part[1:])
                else:
                    bind_ctrl = pm.circle(name=bind_ctrl_name, r=ctrl_size, cy=cy_value, cz=d/10.0, ch=False)[0]
                    tools.setColorIndex(bind_ctrl, ctrl_color)
                bind_pos, bind_drv, bind_extra = tools.makePosDrvExtra(bind_ctrl)
                bind_proxy_ctrl = pm.createNode('transform', name=part+'EyelidBind_'+postfix+'_proxy')
                bind_pos_proxy, bind_drv_proxy, bind_extra_proxy = tools.makePosDrvExtra(bind_proxy_ctrl)

                bind_jnt = pm.joint(name=part+'EyelidBind'+postfix+'_crv_jnt'+str(i).zfill(2))
                bind_jnt_list.append(bind_jnt)
                pm.matchTransform(bind_pos, bind_ctrl_cluster_handle)
                pm.matchTransform(bind_pos_proxy, bind_ctrl_cluster_handle)
                pm.parent(bind_ctrl_cluster_handle, bind_proxy_ctrl)
                pm.parent(bind_jnt, bind_proxy_ctrl)
                pm.parent(bind_pos, bind_ctrl_grp)
                
                if postfix.endswith('_R'):
                    tools.connectMirroredAllTransform(bind_ctrl, bind_proxy_ctrl)
                    pm.setAttr(str(bind_pos)+'.sx', -1)
                else:                    
                    tools.connectAllTransform(bind_ctrl, bind_proxy_ctrl)
                tools.negateTranslation(bind_ctrl, bind_drv)
                #pm.orientConstraint(set_proxy_ctrl, bind_drv_proxy, mo=True)
                #pm.setAttr(bind_ctrl_cluster_handle+'.v', 0)
                bind_ctrls.append(bind_ctrl)
                bind_proxy_ctrls.append(bind_proxy_ctrl)
                bind_pos_list.append(bind_pos)
                bind_pos_proxy_list.append(bind_pos_proxy)
                pm.parent(bind_pos_proxy, partEye_ctrl_proxy_grp)
            
                pm.connectAttr('FacialSettings.secondCtrl',str(bind_pos)+'.v')
                all_pos_list = all_pos_list + bind_pos_list
                all_ctrl_list = all_ctrl_list + bind_ctrls
            
            pm.skinCluster(base_crv, bind_jnt_list, name = part+'EyelidBind'+postfix+'_crv_SC')

            # disconnect base_crv from bind_crv
            kwd_a = part[0]
            kwd_b = part[1:]
            if kwd_b == 'Dw':
                kwd_b = 'down'
            pm.delete(pm.parentConstraint(RigMain.findPerseusName() +'_{}_{}_eye_ctrl'.format(kwd_a,kwd_b)))

            # wire base_crv with bind_crv. This is for eyelids movement folling a eyeball 
            pm.wire(base_crv, wire=bind_crv, n=base_crv_wire, dds=(0,1000))

            # rivet all ctrls created in this stage
            # add rivets on rig head geo
            if rivet == True:
                meshShape = pm.listRelatives(RigChar.getRigHeadGeo(), s=True)[0]
                uvSet = pm.polyUVSet(meshShape, q=True, auv=True)[0]            
                #rivet_target_faces = tools.getFacialFaces(self.getRigHeadGeo(), part=part+'Lip')
                faces = rigData.getValue(RigChar.getRigHeadGeo(), part+'EyelidArea')
                print(meshShape, uvSet, RigChar.getRigHeadGeo())
                follicles=[]
                for node in all_pos_list:
                    rivet_target_faces = faces
                    #if '_DW_' in str(node):
                    #    rivet_target_faces = dw_lip_faces
                    follicle = tools.makeRivet([node], rivet_target_faces)[0]
                    pm.pointConstraint(follicle, node, mo=True)
                    pm.orientConstraint(RigChar.getHeadJnt(), node, mo=True)
                    pm.scaleConstraint('Head_M', node, mo=True)
                    follicles.append(follicle)
                follcle_grp = tools.createGroup(part+'_eye_follicle_grp', parent=eye_ctrl_grp)
                pm.parent(follicles, follcle_grp)
                pm.setAttr(str(follcle_grp)+'.v', 0)
            pm.select(clear=True)
            pm.setAttr(str(partEye_ctrl_proxy_grp)+'.v', 0)
            #all_ctrl_set = tools.createSet('jntBase_all_ctrl_set')
            #pm.sets(all_ctrl_set, add=all_set_ctrl_list)
            #pm.sets(all_ctrl_set, add=all_bind_ctrl_list)
            #pm.sets(all_ctrl_set, add=all_lips_end_ctrl_list)
            #pm.sets(all_ctrl_set, add=all_base_ctrl_list)
        return(True)

    def createSublip(self, rigData, rivet=True, forehead_falloff=3.5, philtrum_falloff=2.5, jawDodown_falloff=1.5, eyeClown_falloff=1.0):
        sublip_jnt_list = []
        all_pos_list = []
        sublip_ctrl_grp = tools.createGroup('sublip_ctrl_grp', parent=RigMain.getEtcGrp())   
        sublip_rivet_grp = tools.createGroup('sublip_rivet_grp', parent=sublip_ctrl_grp)    
        jawDodown_vtx_list = rigData.getValue(self.getSublipHeadGeo(), 'jawDodownVtx', type='component')
        philtrum_vtx_list = rigData.getValue(self.getSublipHeadGeo(), 'philtrumVtx', type='component')
        forehead_ctrl_grp = tools.createGroup('forehead_ctrl_grp', parent=RigMain.getEtcGrp())        
        forehead_vtx_list = rigData.getValue(self.getSublipHeadGeo(), 'foreheadVtx', type='component')
        eyeClown_vtx_list = rigData.getValue(self.getSublipHeadGeo(), 'eyeClownVtx', type='component')

        if not len(jawDodown_vtx_list) == 1:
            pm.warning('jawDodownVtx must be only one vertex!!!! It has {}!!!'.format(str(len(jawDodown_vtx_list))))
            return(False)

        if not len(philtrum_vtx_list) == 3:
            pm.warning('philtrumVtx must be 3 vertices!!!! It has {}!!!'.format(str(len(philtrum_vtx_list))))
            return(False)

        if not len(forehead_vtx_list) == 5:
            pm.warning('foreheadVtx must be 5 vertices!!!! It has {}!!!'.format(str(len(forehead_vtx_list))))
            return(False)

        if not len(eyeClown_vtx_list) == 2:
            pm.warning('foreheadVtx must be 2 vertices!!!! It has {}!!!'.format(str(len(eyeClown_vtx_list))))
            return(False)

        pm.connectAttr('FacialSettings.secondCtrl',str(sublip_ctrl_grp)+'.v')
        pm.connectAttr('FacialSettings.secondCtrl',str(forehead_ctrl_grp)+'.v')


        # first, create philtrum ctrls
        philtrum_vtx_list = tools.getOrderedVerticesButNotConnected(philtrum_vtx_list)

        l_philtrum_vtx_pos = om.MPoint(pm.pointPosition(philtrum_vtx_list[2], w=True))
        r_philtrum_vtx_pos = om.MPoint(pm.pointPosition(philtrum_vtx_list[0], w=True))
        philtrum_distance = abs(l_philtrum_vtx_pos[0] - r_philtrum_vtx_pos[0])
        
        ctrl_size = philtrum_distance/10.0
        z_offset = philtrum_distance/10.0

        # philtrum set ctrl
        #philtrum_set_ctrl = pm.circle(name='PhiltrumSet_M', r=ctrl_size*2, cz=z_offset, ch=False)[0]
        philtrum_set_ctrl = shapes.createCtrlShape(name='PhiltrumSet_M', shape='philtrumSet', scale=ctrl_size*3.0, 
                                            color='yellow', offset=(0, 0, ctrl_size*2.0))
        philtrum_set_ctrl_pos, philtrum_set_ctrl_drv, philtrum_set_ctrl_extra = tools.makePosDrvExtra(philtrum_set_ctrl)
        all_pos_list.append(philtrum_set_ctrl_pos)        
        philtrum_set_proxy = pm.createNode('transform', name='PhiltrumSet_M_proxy')
        philtrum_set_proxy_pos, philtrum_set_proxy_drv, philtrum_set_proxy_extra = tools.makePosDrvExtra(philtrum_set_proxy) 
        
        cluster_name = 'PhiltrumSet_M'.lower()+'_cls'
        philtrum_set_cluster, philtrum_set_cluster_handle = pm.cluster(philtrum_vtx_list[1], name=cluster_name)
        pm.matchTransform(philtrum_set_ctrl_pos, philtrum_set_cluster_handle)
        pm.matchTransform(philtrum_set_proxy_pos, philtrum_set_cluster_handle)

        tools.connectAllTransform(philtrum_set_ctrl, philtrum_set_proxy)
        tools.negateTranslation(philtrum_set_ctrl, philtrum_set_ctrl_drv)
        pm.delete(philtrum_set_cluster, philtrum_set_cluster_handle)

        tools.setColorIndex(philtrum_set_ctrl, 'yellow')
        pm.parent(philtrum_set_ctrl_pos, philtrum_set_proxy_pos, sublip_ctrl_grp)
        

        # philtrum bind ctrl
        philtrum_ctrl_name_list = ['PhiltrumBind_R', 'PhiltrumBind_M', 'PhiltrumBind_L']
        ctrl_color_list = ['red', 'yellow', 'blue']
        for i,vtx in enumerate(philtrum_vtx_list):
            philtrum_ctrl = pm.circle(name=philtrum_ctrl_name_list[i], r=ctrl_size, cz=z_offset, ch=False)[0]
            philtrum_ctrl_pos, philtrum_ctrl_drv, philtrum_ctrl_extra = tools.makePosDrvExtra(philtrum_ctrl)
            philtrum_ctrl_proxy = pm.createNode('transform', name=philtrum_ctrl_name_list[i]+'_proxy')
            philtrum_ctrl_proxy_pos, philtrum_ctrl_proxy_drv, philtrum_ctrl_proxy_extra = tools.makePosDrvExtra(philtrum_ctrl_proxy)
            philtrum_bind_jnt = pm.joint(name = philtrum_ctrl_name_list[i].lower()+'_siblip_jnt')
            sublip_jnt_list.append(philtrum_bind_jnt)
            #all_pos_list.append(philtrum_ctrl_pos)
            pm.setAttr(philtrum_bind_jnt+'.v', 0)
            pm.parent(philtrum_bind_jnt, philtrum_ctrl_proxy)

            cluster_name = philtrum_ctrl_name_list[i].lower()+'_cls'
            philtrum_cluster, philtrum_cluster_handle = pm.cluster(vtx, name=cluster_name)
            pm.matchTransform(philtrum_ctrl_pos, philtrum_cluster_handle)
            pm.matchTransform(philtrum_ctrl_proxy_pos, philtrum_cluster_handle)
            pm.delete(philtrum_cluster, philtrum_cluster_handle)

            if philtrum_ctrl_name_list[i].endswith('_R'):
                tools.connectMirroredAllTransform(philtrum_ctrl, philtrum_ctrl_proxy)
                pm.setAttr(str(philtrum_ctrl_pos)+'.sx', -1)
            else:                    
                tools.connectAllTransform(philtrum_ctrl, philtrum_ctrl_proxy)

            #tools.negateTranslation(philtrum_ctrl, philtrum_ctrl_drv)
            tools.setColorIndex(philtrum_ctrl, ctrl_color_list[i])
            pm.parent(philtrum_ctrl_pos, philtrum_set_ctrl)
            pm.parent(philtrum_ctrl_proxy_pos, philtrum_set_proxy)

        # second, create jawDodown ctrls
        jawDodown_ctrl_name = 'JawDodown_M'
        jawDodown_ctrl = pm.circle(name=jawDodown_ctrl_name, r=ctrl_size, cz=z_offset, ch=False)[0]
        jawDodown_ctrl_pos, jawDodown_ctrl_drv, jawDodown_ctrl_extra = tools.makePosDrvExtra(jawDodown_ctrl)
        jawDodown_ctrl_proxy = pm.createNode('transform', name=jawDodown_ctrl_name+'_proxy')
        jawDodown_ctrl_proxy_pos, jawDodown_ctrl_proxy_drv, jawDodown_ctrl_proxy_extra = tools.makePosDrvExtra(jawDodown_ctrl_proxy)
        jawDodown_bind_jnt = pm.joint(name = jawDodown_ctrl_name.lower()+'_siblip_jnt')
        sublip_jnt_list.append(jawDodown_bind_jnt)
        all_pos_list.append(jawDodown_ctrl_pos)
        pm.setAttr(jawDodown_bind_jnt+'.v', 0)
        pm.parent(jawDodown_bind_jnt, jawDodown_ctrl_proxy)        

        cluster_name = jawDodown_ctrl_name.lower()+'_cls'
        jawDodown_cluster, jawDodown_cluster_handle = pm.cluster(jawDodown_vtx_list[0], name=cluster_name)
        pm.matchTransform(jawDodown_ctrl_pos, jawDodown_cluster_handle)
        pm.matchTransform(jawDodown_ctrl_proxy_pos, jawDodown_cluster_handle)
        pm.delete(jawDodown_cluster, jawDodown_cluster_handle)
        
        tools.connectAllTransform(jawDodown_ctrl, jawDodown_ctrl_proxy)

        tools.negateTranslation(jawDodown_ctrl, jawDodown_ctrl_drv)
        tools.setColorIndex(jawDodown_ctrl, 'yellow')
        pm.parent(jawDodown_ctrl_pos, jawDodown_ctrl_proxy_pos, sublip_ctrl_grp)


        # third, create forehad ctrls
        forehead_vtx_list = tools.getOrderedVerticesButNotConnected(forehead_vtx_list)

        l_forehead_vtx_pos = om.MPoint(pm.pointPosition(forehead_vtx_list[-1], w=True))
        r_forehead_vtx_pos = om.MPoint(pm.pointPosition(forehead_vtx_list[0], w=True))
        forehead_distance = abs(l_forehead_vtx_pos[0] - r_forehead_vtx_pos[0])
        
        ctrl_size = forehead_distance/14.0
        z_offset = forehead_distance/14.0
        forehead_ctrl_name_list = ['Forehead_01_R', 'Forehead_02_R', 'Forehead_M', 'Forehead_02_L', 'Forehead_01_L']
        ctrl_color_list = ['red', 'red', 'yellow', 'blue', 'blue']
        for i,vtx in enumerate(forehead_vtx_list):
            forehead_ctrl = pm.circle(name=forehead_ctrl_name_list[i], r=ctrl_size, cz=z_offset, ch=False)[0]
            forehead_ctrl_pos, forehead_ctrl_drv, forehead_ctrl_extra = tools.makePosDrvExtra(forehead_ctrl)
            forehead_ctrl_proxy = pm.createNode('transform', name=forehead_ctrl_name_list[i]+'_proxy')
            forehead_ctrl_proxy_pos, forehead_ctrl_proxy_drv, forehead_ctrl_proxy_extra = tools.makePosDrvExtra(forehead_ctrl_proxy)
            forehead_bind_jnt = pm.joint(name = forehead_ctrl_name_list[i].lower()+'_siblip_jnt')
            sublip_jnt_list.append(forehead_bind_jnt)
            all_pos_list.append(forehead_ctrl_pos)
            pm.setAttr(forehead_bind_jnt+'.v', 0)
            pm.parent(forehead_bind_jnt, forehead_ctrl_proxy)
            
            cluster_name = forehead_ctrl_name_list[i].lower()+'_cls'
            forehead_cluster, forehead_cluster_handle = pm.cluster(vtx, name=cluster_name)
            pm.matchTransform(forehead_ctrl_pos, forehead_cluster_handle)
            pm.matchTransform(forehead_ctrl_proxy_pos, forehead_cluster_handle)
            pm.delete(forehead_cluster, forehead_cluster_handle)

            if forehead_ctrl_name_list[i].endswith('_R'):
                tools.connectMirroredAllTransform(forehead_ctrl, forehead_ctrl_proxy)
                pm.setAttr(str(forehead_ctrl_pos)+'.sx', -1)
            else:                    
                tools.connectAllTransform(forehead_ctrl, forehead_ctrl_proxy)

            tools.negateTranslation(forehead_ctrl, forehead_ctrl_drv)
            tools.setColorIndex(forehead_ctrl, ctrl_color_list[i])
            pm.parent(forehead_ctrl_pos, forehead_ctrl_proxy_pos, forehead_ctrl_grp)


        # fourth, create forehad ctrls
        eyeClown_vtx_list = tools.getOrderedVerticesButNotConnected(eyeClown_vtx_list)

        l_eyeClown_vtx_pos = om.MPoint(pm.pointPosition(eyeClown_vtx_list[-1], w=True))
        r_eyeClown_vtx_pos = om.MPoint(pm.pointPosition(eyeClown_vtx_list[0], w=True))
        eyeClown_distance = abs(l_eyeClown_vtx_pos[0] - r_eyeClown_vtx_pos[0])
        
        ctrl_size = eyeClown_distance/20.0
        z_offset = eyeClown_distance/20.0
        eyeClown_ctrl_name_list = ['EyeClown_R', 'EyeClown_L']
        ctrl_color_list = ['red', 'blue']
        for i,vtx in enumerate(eyeClown_vtx_list):
            eyeClown_ctrl = pm.circle(name=eyeClown_ctrl_name_list[i], r=ctrl_size, cz=z_offset, ch=False)[0]
            eyeClown_ctrl_pos, eyeClown_ctrl_drv, eyeClown_ctrl_extra = tools.makePosDrvExtra(eyeClown_ctrl)
            eyeClown_ctrl_proxy = pm.createNode('transform', name=eyeClown_ctrl_name_list[i]+'_proxy')
            eyeClown_ctrl_proxy_pos, eyeClown_ctrl_proxy_drv, eyeClown_ctrl_proxy_extra = tools.makePosDrvExtra(eyeClown_ctrl_proxy)
            eyeClown_bind_jnt = pm.joint(name = eyeClown_ctrl_name_list[i].lower()+'_siblip_jnt')
            sublip_jnt_list.append(eyeClown_bind_jnt)
            all_pos_list.append(eyeClown_ctrl_pos)
            pm.setAttr(eyeClown_bind_jnt+'.v', 0)
            pm.parent(eyeClown_bind_jnt, eyeClown_ctrl_proxy)
            
            cluster_name = eyeClown_ctrl_name_list[i].lower()+'_cls'
            eyeClown_cluster, eyeClown_cluster_handle = pm.cluster(vtx, name=cluster_name)
            pm.matchTransform(eyeClown_ctrl_pos, eyeClown_cluster_handle)
            pm.matchTransform(eyeClown_ctrl_proxy_pos, eyeClown_cluster_handle)
            pm.delete(eyeClown_cluster, eyeClown_cluster_handle)

            if eyeClown_ctrl_name_list[i].endswith('_R'):
                tools.connectMirroredAllTransform(eyeClown_ctrl, eyeClown_ctrl_proxy)
                pm.setAttr(str(eyeClown_ctrl_pos)+'.sx', -1)
            else:                    
                tools.connectAllTransform(eyeClown_ctrl, eyeClown_ctrl_proxy)

            tools.negateTranslation(eyeClown_ctrl, eyeClown_ctrl_drv)
            tools.setColorIndex(eyeClown_ctrl, ctrl_color_list[i])
            pm.parent(eyeClown_ctrl_pos, eyeClown_ctrl_proxy_pos, sublip_ctrl_grp)

        # bind skin to new (sublip) geo
        print("# sublip skin weights : step 1 - bind skin")

        sublip_sc = str(self.getSublipHeadGeo())+'_SC'
        if not pm.objExists(sublip_sc):
            print(sublip_sc, self.getSublipHeadGeo(), self.getJntBaseHeadSkinJnt())
            print(sublip_jnt_list)
            sublip_sc = pm.skinCluster(self.getSublipHeadGeo(), self.getJntBaseHeadSkinJnt(), sublip_jnt_list, name=sublip_sc, sm=0, mi=8)
        
        # paint skin weight
        print("# paint skin weights : step 2 - reset skin weights")
        pm.select(str(self.getSublipHeadGeo())+'.vtx[*]', r=True)
        all_vtxes = pm.ls(sl=True, fl=True)
        all_infs = pm.skinCluster(sublip_sc, q=True, inf=True)

        for vtx in all_vtxes:
            jnts_n_weights = []
            #pm.skinPercent(sublip_sc, vtx, tv=[str('name_facialHead_jnt_skin_jntBase'), 1.0])
            jnts_n_weights.append((str(self.getJntBaseHeadSkinJnt()), 1.0))
            vtx_pos = om.MPoint(pm.pointPosition(vtx, w=True))
            for inf in all_infs:
                inf_pos = om.MPoint(pm.xform(inf, q=True, ws=True, rp=True))
                distance = (vtx_pos-inf_pos).length()

                falloff_radius = 3.0
                if 'forehead' in str(inf):
                    falloff_radius = forehead_falloff
                elif 'philtrum' in str(inf):
                    falloff_radius = philtrum_falloff
                elif 'jawdodown' in str(inf):
                    falloff_radius = jawDodown_falloff
                elif 'eyeClown' in str(inf):
                    falloff_radius = eyeClown_falloff

                if distance < falloff_radius:
                    #print(vtx, inf_pos, distance)
                    weight = max(math.cos(0.5*math.pi*distance/falloff_radius), 0)
                    #print(vtx, inf_pos, distance, weight)
                    jnts_n_weights.append((str(inf), weight))
            #print(jnts_n_weights)
            pm.skinPercent(sublip_sc, vtx, tv=jnts_n_weights, nrm=True)

        #return()
        # rivet all ctrls created in this stage
        # add rivets on rig head geo
        if rivet == True:
            meshShape = pm.listRelatives(RigChar.getRigHeadGeo(), s=True)[0]
            uvSet = pm.polyUVSet(meshShape, q=True, auv=True)[0]            
            #rivet_target_faces = tools.getFacialFaces(self.getRigHeadGeo(), part=part+'Lip')
            #faces = rigData.getValue(RigChar.getRigHeadGeo(), part+'EyelidArea')
            faces = pm.ls(str(RigChar.getRigHeadGeo())+'.f[*]', fl=True)
            #print(meshShape, uvSet, RigChar.getRigHeadGeo())
            follicles=[]
            for node in all_pos_list:
                rivet_target_faces = faces
                #if '_DW_' in str(node):
                #    rivet_target_faces = dw_lip_faces
                follicle = tools.makeRivet([node], rivet_target_faces)[0]
                pm.pointConstraint(follicle, node, mo=True)
                pm.orientConstraint(RigChar.getHeadJnt(), node, mo=True)
                pm.scaleConstraint('Head_M', node, mo=True)
                follicles.append(follicle)
            pm.parent(follicles, sublip_rivet_grp)
            pm.setAttr(str(sublip_rivet_grp)+'.v', 0)
        pm.select(clear=True)

        #pm.setAttr(str(partEye_ctrl_proxy_grp)+'.v', 0)

        return(True)

    def setupSquashStretchHead(self):
        sqst_ctrl_grp = tools.createGroup('sqst_ctrl_grp', parent=RigMain.getEtcGrp())
        sqst_geo_grp = self.perseus_name+'_facial_sqst_geo_grp'

        sqst_geo_list = pm.listRelatives(sqst_geo_grp)
        neck_jnt_pos = pm.xform('Neck_M', q=True, rp=True, ws=True)


        target_geo_list = []
        for geo in sqst_geo_list:
            bbox = pm.exactWorldBoundingBox(geo)
            center_height = (bbox[1]+bbox[4])/2.0
            if center_height > neck_jnt_pos[1]:
                target_geo_list.append(geo)
        for item in target_geo_list:
            skinCluster = tools.getSkinClusterFromMesh(item)
            #print(skinCluster)
            pm.delete(skinCluster)
            pm.setAttr(str(item)+'.v', 1)

        ffd, ffdTransform, ffdBaseTransform = pm.lattice(target_geo_list, name='head_sqst_ffd',
                                                    dv=(2,7,2), oc=True, ol=True, ldv=(2,7,2))
        pm.parent(ffdTransform, ffdBaseTransform, sqst_ctrl_grp)

        ffd_shape = str(ffdTransform)+'Shape'
        ffd_top_pt_list = [ffd_shape+'.pt[0][5][0]',
                        ffd_shape+'.pt[1][5][0]',
                        ffd_shape+'.pt[0][6][0]',
                        ffd_shape+'.pt[1][6][0]',
                        ffd_shape+'.pt[0][5][1]',
                        ffd_shape+'.pt[1][5][1]',
                        ffd_shape+'.pt[0][6][1]',
                        ffd_shape+'.pt[1][6][1]']
        ffd_mid_pt_list = [ffd_shape+'.pt[0][3][0]',
                        ffd_shape+'.pt[1][3][0]',
                        ffd_shape+'.pt[0][4][0]',
                        ffd_shape+'.pt[1][4][0]',
                        ffd_shape+'.pt[0][3][1]',
                        ffd_shape+'.pt[1][3][1]',
                        ffd_shape+'.pt[0][4][1]',
                        ffd_shape+'.pt[1][4][1]']
        ffd_bot_pt_list = [ffd_shape+'.pt[0][1][0]',
                        ffd_shape+'.pt[1][1][0]',
                        ffd_shape+'.pt[0][2][0]',
                        ffd_shape+'.pt[1][2][0]',
                        ffd_shape+'.pt[0][1][1]',
                        ffd_shape+'.pt[1][1][1]',
                        ffd_shape+'.pt[0][2][1]',
                        ffd_shape+'.pt[1][2][1]']

        head_sqst_top_cls, head_sqst_top_clsHandle = pm.cluster(ffd_top_pt_list, name = 'head_sqst_top_cls')
        head_sqst_mid_cls, head_sqst_mid_clsHandle = pm.cluster(ffd_mid_pt_list, name = 'head_sqst_mid_cls')
        head_sqst_bot_cls, head_sqst_bot_clsHandle = pm.cluster(ffd_bot_pt_list, name = 'head_sqst_bot_cls')

        lattice_bbox = pm.exactWorldBoundingBox(ffdTransform)
        ctrl_size = abs(lattice_bbox[0]-lattice_bbox[3])/2.0

        head_sqst_top_ctrl = shapes.createCtrlShape(name='Sqst_01_M', shape='roundSquare', scale=ctrl_size, color='yellow')
        head_sqst_mid_ctrl = shapes.createCtrlShape(name='Sqst_02_M', shape='roundSquare', scale=ctrl_size, color='yellow')
        head_sqst_bot_ctrl = shapes.createCtrlShape(name='Sqst_03_M', shape='roundSquare', scale=ctrl_size, color='yellow')
        top_ctrl_pos, top_ctrl_drv, top_ctrl_extra = tools.makePosDrvExtra(head_sqst_top_ctrl)
        mid_ctrl_pos, mid_ctrl_drv, mid_ctrl_extra = tools.makePosDrvExtra(head_sqst_mid_ctrl)
        bot_ctrl_pos, bot_ctrl_drv, bot_ctrl_extra = tools.makePosDrvExtra(head_sqst_bot_ctrl)

        head_sqst_top_proxy = pm.createNode('transform', name=str(head_sqst_top_ctrl)+'_proxy')
        head_sqst_mid_proxy = pm.createNode('transform', name=str(head_sqst_mid_ctrl)+'_proxy')
        head_sqst_bot_proxy = pm.createNode('transform', name=str(head_sqst_bot_ctrl)+'_proxy')
        top_proxy_pos, top_proxy_drv, top_proxy_extra = tools.makePosDrvExtra(head_sqst_top_proxy)
        mid_proxy_pos, mid_proxy_drv, mid_proxy_extra = tools.makePosDrvExtra(head_sqst_mid_proxy)
        bot_proxy_pos, bot_proxy_drv, bot_proxy_extra = tools.makePosDrvExtra(head_sqst_bot_proxy)

        pm.matchTransform(top_ctrl_pos, head_sqst_top_clsHandle)
        pm.matchTransform(mid_ctrl_pos, head_sqst_mid_clsHandle)
        pm.matchTransform(bot_ctrl_pos, head_sqst_bot_clsHandle)

        pm.matchTransform(top_proxy_pos, head_sqst_top_clsHandle)
        pm.matchTransform(mid_proxy_pos, head_sqst_mid_clsHandle)
        pm.matchTransform(bot_proxy_pos, head_sqst_bot_clsHandle)

        pm.parent(head_sqst_top_clsHandle, head_sqst_top_proxy)
        pm.parent(head_sqst_mid_clsHandle, head_sqst_mid_proxy)
        pm.parent(head_sqst_bot_clsHandle, head_sqst_bot_proxy)

        tools.connectAllTransform(head_sqst_top_ctrl, head_sqst_top_proxy)
        tools.connectAllTransform(head_sqst_mid_ctrl, head_sqst_mid_proxy)
        tools.connectAllTransform(head_sqst_bot_ctrl, head_sqst_bot_proxy)

        tools.halfTranslation(head_sqst_top_ctrl, mid_ctrl_drv)
        tools.halfTranslation(head_sqst_top_proxy, mid_proxy_drv)

        pm.parent(top_ctrl_pos, mid_ctrl_pos, bot_ctrl_pos, sqst_ctrl_grp)
        pm.parent(top_proxy_pos, mid_proxy_pos, bot_proxy_pos, sqst_ctrl_grp)
        pm.parentConstraint('Head_M', top_ctrl_pos, mo=True)
        pm.parentConstraint('Head_M', mid_ctrl_pos, mo=True)
        pm.parentConstraint('Head_M', bot_ctrl_pos, mo=True)
        pm.scaleConstraint('Head_M', top_ctrl_pos, mo=True)
        pm.scaleConstraint('Head_M', mid_ctrl_pos, mo=True)
        pm.scaleConstraint('Head_M', bot_ctrl_pos, mo=True)

        pm.setAttr(str(ffdTransform)+'.v', 0)
        pm.setAttr(str(ffdBaseTransform)+'.v', 0)
        pm.setAttr(str(head_sqst_top_clsHandle)+'.v', 0)
        pm.setAttr(str(head_sqst_mid_clsHandle)+'.v', 0)
        pm.setAttr(str(head_sqst_bot_clsHandle)+'.v', 0)
        pm.connectAttr('FacialSettings.squashStretch',str(top_ctrl_pos)+'.v')
        pm.connectAttr('FacialSettings.squashStretch',str(mid_ctrl_pos)+'.v')
        pm.connectAttr('FacialSettings.squashStretch',str(bot_ctrl_pos)+'.v')
        return(True)