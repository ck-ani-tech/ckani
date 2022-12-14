import maya.api.OpenMaya as om
import pymel.core as pm
import json, os

class UndoContext(object):
    def __enter__(self):
        pm.undoInfo(openChunk=True)
    def __exit__(self, *exc_info):
        pm.undoInfo(closeChunk=True)

def offsetCtrlShape(ctrls, offset=(0,0,0)):
    for ctrl in ctrls:
        if pm.nodeType(ctrl) == 'transform':
            ctrl=pm.listRelatives(ctrl, s=True)[0]
        if pm.nodeType(ctrl) == 'nurbsCurve':
            pnt_list = []
            for cv in pm.ls(str(ctrl)+'.cv[*]', fl=True):
                old_pnt = pm.pointPosition(cv, w=True)
                new_pnt = (old_pnt[0]+offset[0], old_pnt[1]+offset[1], old_pnt[2]+offset[2])
                pm.xform(cv, t=new_pnt, ws=True)
        else:
            return(None)

def findCenterPos(targets, shape=False):
    pos_sum = om.MVector()
    for target in targets:
        pos=None
        if shape is True:
            local_sum = om.MVector()
            cvs = pm.ls(target+'.cv[*]', fl=True)
            for cv in cvs:
                local_sum = local_sum + om.MVector(pm.pointPosition(cv, w=True))
            pos = local_sum/float(len(cvs))
        else:        
            pos = om.MVector(pm.xform(target, q=True, rp=True, ws=True))
        pos_sum = pos_sum+pos
    center = pos_sum/float(len(targets))
    return((center[0],center[1],center[2]))

def findClosestNode(source, targets):
    src_pnt = om.MPoint(pm.xform(source, q=True, ws=True, rp=True))
    closest_target = targets[0]
    tgt_pnt = om.MPoint(pm.xform(closest_target, q=True, ws=True, rp=True))
    closest_distance = om.MVector(tgt_pnt-src_pnt).length()
    for target in targets[1:]:
        tgt_pnt = om.MPoint(pm.xform(target, q=True, ws=True, rp=True))
        new_distance = om.MVector(tgt_pnt-src_pnt).length()
        if new_distance < closest_distance:
            closest_distance = new_distance
            closest_target = target
    return(closest_target)

def rebuildD1curve(crv_name, spans=6, name=None):
    if name is None:
        name = crv_name + '_rebuilt'
    pnts = []
    for i in range(spans+1):
        pr = float(i)/float(spans)
        pnt = pm.pointOnCurve(crv_name, pr = pr, top=True)
        pnts.append(pnt)
    rebuilt_curve = pm.curve(d=1, p=pnts, name=name)
    return(rebuilt_curve)

def growSelection(items):
    index_list = getVertexIndicesFromVertices(items)
    mSelList = om.MSelectionList()
    mesh = str(items[0]).split('.')[0]
    mSelList.add(str(items[0]))
    shapeDagPath = mSelList.getDagPath(0)
    itMeshVertex = om.MItMeshVertex(shapeDagPath)
    mGrownSelection = om.MIntArray()
    while not itMeshVertex.isDone():
        if itMeshVertex.index() in index_list:
            mGrownSelection = mGrownSelection + itMeshVertex.getConnectedVertices()
            #print(itMeshVertex.index(), itMeshVertex.getConnectedVertices())
        itMeshVertex.next()
    return(getVerticesFromVertexIndices(mesh, mGrownSelection))


def removeTheFirstAndTheLasetFromListByIndex(given_list):
    '''
    This removes the first and the last item from a list
    ex) a = [0,1,2,3,4,5]
        removeLowAndHighFromListByIndex(a)
        # [1,2,3,4]
    
    '''
    new_list = list(given_list)
    low_number, low_item = 100000, None
    high_number, high_item = -10000, None
    for item in new_list:
        index = int(filter(str.isdigit, str(item)))
        if index < low_number:
            low_number = index
            low_item = item
        if index > high_number:
            high_number = index
            high_item = item
    new_list.remove(high_item)
    new_list.remove(low_item)
    return(new_list)



def getFaceIndexsFromSelection(faces):
    new_face_list = []
    for face in faces:
        pm.select(face, r=True)
        new_face_list.append(pm.ls(sl=True,fl=True)[0])
    index_list = []
    for face in new_face_list:
        index = str(face).split('[')[1].split(']')[0]
        index_list.append(int(index))
    return(index_list)

def getVertexIndicesFromVertices(vtxs):
    index_list = []
    for vtx in vtxs:
        i = int(str(vtx).split('[')[1].split(']')[0])
        index_list.append(i)
    return(index_list)

def getVerticesFromVertexIndices(mesh, index_list):
    meshShape = getMeshShape(mesh)
    vtxs = []
    for index in index_list:
        vtx = str(meshShape)+'.vtx[{}]'.format(str(index))
        vtxs.append(vtx)
    vtx_transforms = []
    for vtx in vtxs:
        pm.select(vtx, r=True)
        vtx_transforms.append(pm.ls(sl=True)[0])
    return(vtx_transforms)

def getFaceIndicesFromFaces(faces):
    index_list = []
    for face in faces:
        index = str(face).split('[')[1].split(']')[0]
        index_list.append(int(index))
    return(index_list)

def getFacesFromFaceIndices(mesh, index_list):
    meshShape = getMeshShape(mesh)
    faces = []
    for index in index_list:
        face = str(meshShape)+'.f[{}]'.format(str(index))
        faces.append(face)
    pm.select(faces, r=True)
    return(pm.ls(sl=True, fl=True))

def getOrderedVerticesButNotConnected(vtx_list):
    ordered_vtx_list = []
    vtx_pos_list = []
    for vtx in vtx_list:
        pos = om.MPoint(pm.pointPosition(vtx, w=True))
        vtx_pos_list.append(pos)
    
    order_dict = dict()
    for pos1, vtx in zip(vtx_pos_list, vtx_list):
        order_index = 0
        for pos2 in vtx_pos_list:
            if pos1[0] > pos2[0]:
                order_index = order_index + 1
        order_dict[order_index] = vtx
    for i in range(len(vtx_list)):
        ordered_vtx_list.append(order_dict[i])
    return(ordered_vtx_list)

def getOrderedVertices(connected_vertices):
    '''
    return list of vertices in order, left(-x) to right(+x)
    '''
    mesh = str(connected_vertices[0].split('.')[0])
    vtx_id_list = getVertexIndicesFromVertices(connected_vertices)
    mSelList = om.MSelectionList()
    mSelList.add(mesh)
    shapeDagPath = mSelList.getDagPath(0)
    itMeshVertex = om.MItMeshVertex(shapeDagPath)
    connected_data = {}
    while not itMeshVertex.isDone():
        if itMeshVertex.index() in vtx_id_list:
            connected = []
            for mInt in itMeshVertex.getConnectedVertices():
                if mInt in vtx_id_list:
                    connected.append(mInt)
            if len(connected) == 0:
                pm.select(connected_vertices, r=True)
                raise ValueError('Vertices are not connected!!!!!')
            else:
                connected_data[itMeshVertex.index()]= connected
        itMeshVertex.next()
    each_ends = []
    for key in connected_data:
        if len(connected_data[key]) < 2:
            each_ends.append(key)
    if len(each_ends) > 2:
        pm.select(connected_vertices, r=True)
        raise ValueError('Vertices are not connected!!!!!')        

    end_vtxs = getVerticesFromVertexIndices(mesh,each_ends)
    ordered_vtxs = end_vtxs
    pnt0 = pm.pointPosition(ordered_vtxs[0], w=True)
    pnt1 = pm.pointPosition(ordered_vtxs[1], w=True)
    if pnt0.x > pnt1.x:
        ordered_vtxs.reverse()
    #pm.select(ordered_vtxs[0])
    ordered_vtx_ids = getVertexIndicesFromVertices(ordered_vtxs)
    current_id = ordered_vtx_ids[0]
    previsou_id = None
    for i in range(2000):
        ids = list(connected_data[current_id])

        if previsou_id is not None and previsou_id in ids:
            ids.remove(previsou_id)
        if ids[0] != ordered_vtx_ids[-1]:
            next_id = ids[0]
            ordered_vtx_ids.insert(-1,next_id)
            previsou_id = current_id
            current_id = next_id
        else:
            break
    return(getVerticesFromVertexIndices(mesh,ordered_vtx_ids))

def getMeshShape(mesh):
    if pm.nodeType(mesh) == 'transform':
        meshShape = pm.listRelatives(mesh, s=True)[0]
    elif pm.nodeType(mesh) == 'mesh':
        meshShape = mesh
    else:
        raise ValueError('mesh must be a transform or a mesh')
    return(meshShape)

def getFacialFaces(mesh, part='dwLip'):
    mSelList = om.MSelectionList()
    mSelList.add(str(mesh))
    shapeDagPath = mSelList.getDagPath(0)
    itMeshFace = om.MItMeshFaceVertex(shapeDagPath)

    face_id_list = []
    while not itMeshFace.isDone():
        norm = itMeshFace.getNormal()
        if part == "dwLip":
            if norm.y > 0:
                face_id_list.append(itMeshFace.faceId())
        elif part == 'upLip':                
            if norm.y < 0:
                face_id_list.append(itMeshFace.faceId())
        else:
            raise ValueError("a part '{}' is not defined!".format(part))
        itMeshFace.next()

    face_id_list = set(face_id_list)
    return(getFacesFromFaceIndices(mesh, face_id_list))


def minusTranslation(source1, source2, target):
    util_node = str(source1)+str(source2)+str(target)+'_pma'
    util_node = pm.shadingNode('plusMinusAverage', asUtility=True, name=util_node)

    pm.setAttr(util_node+'.operation', 2)    
    pm.connectAttr(source1+'.t', util_node+'.input3D[0]')
    pm.connectAttr(source2+'.t', util_node+'.input3D[1]')
    pm.connectAttr(util_node+'.output3D', target+'.t')    

def halfTranslation(source, target):
    md_node = str(source)+str(target)+'_md'
    md_node = pm.shadingNode('multiplyDivide', asUtility=True, name=md_node)

    pm.connectAttr(source+'.t', md_node+'.input1')
    pm.connectAttr(md_node+'.output', target+'.t')
    pm.setAttr(md_node+'.input2X', 0.5)
    pm.setAttr(md_node+'.input2Y', 0.5)
    pm.setAttr(md_node+'.input2Z', 0.5)

    return(md_node)

def halfRotation(source, target):
    md_node = str(source)+str(target)+'_md'
    md_node = pm.shadingNode('multiplyDivide', asUtility=True, name=md_node)

    pm.connectAttr(source+'.r', md_node+'.input1')
    pm.connectAttr(md_node+'.output', target+'.r')
    pm.setAttr(md_node+'.input2X', 0.5)
    pm.setAttr(md_node+'.input2Y', 0.5)
    pm.setAttr(md_node+'.input2Z', 0.5)

    return(md_node)

def negateTranslation(source, target):
    md_node = str(source)+str(target)+'_md'
    md_node = pm.shadingNode('multiplyDivide', asUtility=True, name=md_node)

    pm.connectAttr(source+'.t', md_node+'.input1')
    pm.connectAttr(md_node+'.output', target+'.t')
    pm.setAttr(md_node+'.input2X', -1)
    pm.setAttr(md_node+'.input2Y', -1)
    pm.setAttr(md_node+'.input2Z', -1)

    return(md_node)

def connectMirroredAllTransform(source, target):
    md_node = str(source)+str(target)+'_mirrored_t_md'
    md_node = pm.shadingNode('multiplyDivide', asUtility=True, name=md_node)
    pm.connectAttr(source+'.t', md_node+'.input1')
    pm.connectAttr(md_node+'.output', target+'.t')
    pm.setAttr(md_node+'.input2X', -1)
    pm.setAttr(md_node+'.input2Y', 1)
    pm.setAttr(md_node+'.input2Z', 1)

    md_node = str(source)+str(target)+'_mirrored_r_md'
    md_node = pm.shadingNode('multiplyDivide', asUtility=True, name=md_node)
    pm.connectAttr(source+'.r', md_node+'.input1')
    pm.connectAttr(md_node+'.output', target+'.r')
    pm.setAttr(md_node+'.input2X', 1)
    pm.setAttr(md_node+'.input2Y', -1)
    pm.setAttr(md_node+'.input2Z', -1)

    pm.connectAttr(source+'.s', target+'.s')


def connectAllTransform(source, target):
    pm.connectAttr(source+'.t', target+'.t')
    pm.connectAttr(source+'.r', target+'.r')
    pm.connectAttr(source+'.s', target+'.s')

def multipliedConnection(source_attr, target_attr, multiplier):
    md_node = str(source_attr)+str(target_attr)+'_md'
    md_node = pm.shadingNode('multiplyDivide', asUtility=True, name=md_node)

    pm.connectAttr(source_attr, md_node+'.input1X')
    pm.connectAttr(md_node+'.outputX', target_attr)
    pm.setAttr(md_node+'.input2X', multiplier)
    pm.setAttr(md_node+'.input2Y', multiplier)
    pm.setAttr(md_node+'.input2Z', multiplier)    

def djRivetHideFollicleChannels(fol, fols):
    # credit : David Johnson, david@djx.com.au
    attrs = ['tx','ty','tz', 'rx','ry','rz', 'sx','sy','sz']
    for attr in attrs:
        pm.setAttr(fol+'.'+attr, k=False, cb=False)
    
    attrs = ['rsp','ptl','sim','sdr','fld','ovd','cld','dmp','stf', 'fsl', 'sgl']
    attrs = attrs + ['lfl','cwm','dml','cml','ctf','brd','cbl','cr','cg','cb','sdn','dgr','sct','ad','clumpWidth']
    for attr in attrs:
        pm.setAttr(fols+'.'+attr, k=False, cb=False)

def djRivetUnlockChannels(surf):
    # credit : David Johnson, david@djx.com.au
    attrs = ['tx','ty','tz', 'rx','ry','rz', 'sx','sy','sz']
    for attr in attrs:
        pm.setAttr(surf+'.'+attr, lock=False)
    
def djRivetIsTransformLocked(dag):
    # credit : David Johnson, david@djx.com.au
    locked = pm.listAttr(dag, locked=True)
    if len(locked) == 0:
        return(False)
    for attr in locked:
        if attr in ['translateX', 'translateY','translateZ','rotateX','rotateY','rotateZ']:
            return(True)
    return(False)

def djRivetIsTransformAnimated(node):
    # credit : David Johnson, david@djx.com.au
    animated = pm.listConnections(node, s=True, d=False)
    if len(animated) == 0:
        return(False)
    for con in animated:
        b = con.split("_")[1]
        if b in ['translateX', 'translateY','translateZ','rotateX','rotateY','rotateZ']:
            return(True)
    return(False)

def makeRivetOnFaces(ctrls, mesh):
    '''
    mesh is a list of faces.
    '''
    mSelList = om.MSelectionList()
    for item in mesh:
        mSelList.add(str(item))

    shapeDagPath = mSelList.getDagPath(0)
    mMesh = om.MFnMesh(shapeDagPath)
    uvSet = mMesh.getUVSetNames()[0]

    face_index_list = getFaceIndexsFromSelection(mesh)
    dup = pm.duplicate(mMesh.name(), rr=True)[0]
    faces = getFacesFromFaceIndices(dup, face_index_list)
    pm.select(dup.name()+'.f[*]', r=True)
    pm.select(faces, toggle=True)
    pm.delete(pm.ls(sl=True))

    mSelListDup = om.MSelectionList()
    mSelListDup.add(dup.name())
    shapeDagPathDup = mSelListDup.getDagPath(0)
    mMeshDup = om.MFnMesh(shapeDagPathDup)
    uvSetDup = mMeshDup.getUVSetNames()[0]

    fc_list = []
    for ctrl in ctrls:
        pnt = pm.xform(ctrl, q=True, ws=True, rp=True)
        u,v,faceId = mMeshDup.getUVAtPoint(om.MPoint(pnt), uvSet=uvSetDup)
        follicle = pm.createNode('follicle', name=str(ctrl)+'_fcShape')
        follicleTransform = pm.listRelatives(follicle, p=True)[0]
        follicleTransform = pm.rename(follicleTransform, str(ctrl)+'_fc')
        pm.connectAttr(mMesh.name()+'.worldMatrix[0]',follicle+'.inputWorldMatrix')
        pm.connectAttr(mMesh.name()+'.worldMesh[0]',follicle+'.inputMesh')
        pm.connectAttr(follicle+'.outRotate',follicleTransform+'.rotate')
        pm.connectAttr(follicle+'.outTranslate',follicleTransform+'.translate')
        pm.setAttr(follicle+'.mapSetName', uvSet, type='string')
        pm.setAttr(follicle+'.parameterU', u)
        pm.setAttr(follicle+'.parameterV', v)
        
        fc_list.append(follicleTransform)
    
    pm.delete(dup)
    return(fc_list)

def makeRivet(ctrls, mesh):
    '''
    ctrls is a list of transforms.
    mesh could be a transform, a mesh(shape) or even faces(a list of faces).
    
    '''

    mSelList = om.MSelectionList()
    if isinstance(mesh, list):
        return(makeRivetOnFaces(ctrls, mesh))
        
    mSelList = om.MSelectionList()
    mSelList.add(mesh.name())

    shapeDagPath = mSelList.getDagPath(0)
    mMesh = om.MFnMesh(shapeDagPath)
    uvSet = mMesh.getUVSetNames()[0]

    fc_list = []
    for ctrl in ctrls:
        pnt = pm.xform(ctrl, q=True, ws=True, rp=True)
        u,v,faceId = mMesh.getUVAtPoint(om.MPoint(pnt), uvSet=uvSet)
        follicle = pm.createNode('follicle', name=str(ctrl)+'_fcShape')
        follicleTransform = pm.listRelatives(follicle, p=True)[0]
        follicleTransform = pm.rename(follicleTransform, str(ctrl)+'_fc')
        pm.connectAttr(mMesh.name()+'.worldMatrix[0]',follicle+'.inputWorldMatrix')
        pm.connectAttr(mMesh.name()+'.worldMesh[0]',follicle+'.inputMesh')
        pm.connectAttr(follicle+'.outRotate',follicleTransform+'.rotate')
        pm.connectAttr(follicle+'.outTranslate',follicleTransform+'.translate')
        pm.setAttr(follicle+'.mapSetName', uvSet, type='string')
        pm.setAttr(follicle+'.parameterU', u)
        pm.setAttr(follicle+'.parameterV', v)
        
        fc_list.append(follicleTransform)
    return(fc_list)

def getSkinClusterFromMesh(mesh):
    items = pm.listHistory(mesh)
    for item in items:
        if item.nodeType() == 'skinCluster':
            return(item)
    return(None)

def createSet(set_name, parent=None):
    new_set = None
    if not pm.objExists(set_name):
        if parent is None:
            new_set = pm.sets(name=set_name)
        else:
            new_set = pm.sets(name=set_name)
            print("###############")
            print(parent,new_set)
            print("------------")
            pm.sets(parent, str(new_set), edit=True, fe=True)
    else:
        print("# warning : "+set_name+" exists !!!")
        new_set = pm.ls(set_name, ap=True)[0]
    return(new_set)


def createGroup(grp_name, parent=None, warning=False):
    new_grp = None
    if not pm.objExists(grp_name):
        if parent is None:
            new_grp = pm.createNode('transform', name=grp_name)
        else:
            new_grp = pm.createNode('transform', name=grp_name, p=parent)
    else:
        if warning:
            print("# warning : "+grp_name+" exists !!!")
        new_grp = pm.ls(grp_name, ap=True)[0]
    return(new_grp)

def setLocatorLocalScale(loc, s):
    locShape = pm.listRelatives(loc, shapes=True)[0]
    pm.setAttr(locShape+'.localScaleX', s)
    pm.setAttr(locShape+'.localScaleY', s)
    pm.setAttr(locShape+'.localScaleZ', s)
    return(locShape)

def makePostfixForSides(cnt, name=None):
    side_cv_cnt = (cnt - 1)/2
    postfix=[]
    middle_name = ''
    if name is not None:
        middle_name = '_'+name
    for i in range(side_cv_cnt):
        postfix.append('_'+str(i+1).zfill(2)+middle_name+"_R")
    postfix.append(middle_name+"_M")
    for i in range(side_cv_cnt):
        postfix.append('_'+str(side_cv_cnt-i).zfill(2)+middle_name+"_L")
    return(postfix)

def makePosDrvExtra(ctrl):
    set_pos = pm.createNode('transform', name=ctrl+'_Pos')
    set_drv = pm.createNode('transform', name=ctrl+'_Drv', p=set_pos)
    set_extra = pm.createNode('transform', name=ctrl+'_Extra', p=set_drv)
    pm.parent(ctrl, set_extra)
    return(set_pos, set_drv, set_extra)

def makeBallShape(name='ctrl', radius=1):
    c1 = pm.circle(name=name,nr=(0,1,0), r=radius)[0]
    c2 = pm.circle(name=name+'SHP2',nr=(1,0,0), r=radius)[0]
    c3 = pm.circle(name=name+'SHP3',nr=(0,0,1), r=radius)[0]
    pm.delete(c1,c2,c3, ch=True)
    
    shp2 = pm.listRelatives(c2, shapes=True)[0]
    shp3 = pm.listRelatives(c3, shapes=True)[0]
    
    pm.parent(shp2, c1, r=True, s=True)
    pm.parent(shp3, c1, r=True, s=True)
    
    pm.delete(c2,c3)
    pm.select(c1)
    return(c1)

def setColorIndex(new_ctrl, color):
    color_index=0
    if color == "yellow":
        color_index = 17
    if color == "red":
        color_index = 13
    if color == "blue":
        color_index = 6
    pm.setAttr(new_ctrl+'.overrideEnabled', 1)
    pm.setAttr(new_ctrl+'.overrideColor', color_index)



def resetAllKeyale(items):
    for item in items:
        keyable_attrs = pm.listAttr(item, keyable=True)
        for attr in keyable_attrs:
            default_values = pm.attributeQuery(attr, node=item, ld=True)
            if len(default_values) > 0:
                if len(default_values) > 1:
                    try:
                        pm.setAttr(item+'.'+attr, default_values)
                    except:
                        pass
                else:
                    try:
                        pm.setAttr(item+'.'+attr, default_values[0])
                    except:
                        pass

def resetAllCtrls():
    ctrl_sets = ['firstCtrl_set','secondCtrl_set','ThirdCtrl_set']
    for set in ctrl_sets:
        items = pm.sets(set, q=True)
        resetAllKeyale(items)


def makeParent(item, org=False):
    result = pm.ls(item)

    if len(result) == 0:
        raise ValueError(item +' does not exits!!!!!')
    elif len(result) > 1:
        raise ValueError(item +' are more than one!!!!')

    parent_node = pm.listRelatives(item, parent=True, f=True)[0]
    tmp_org_node = pm.createNode('transform', name='tmp_org')    

    new_parent_name = item.split('|')[-1] + '_org'
    new_parent_node = pm.createNode('transform', name=new_parent_name, parent=tmp_org_node)
    if not org:
        pm.matchTransform(new_parent_node, item)
    
    if parent_node is not None:
        new_parent_node = pm.parent(new_parent_node, parent_node)[0]
    else:
        pm.parent(new_parent_node, w=True)

    item = pm.parent(item, new_parent_node)[0]
    pm.delete(tmp_org_node)
    pm.select(item, r=True)
    return(pm.ls(item)[0])