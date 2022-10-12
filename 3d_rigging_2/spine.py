import maya.api.OpenMaya as om
import pymel.core as pm

# spine name
spine_name = 'spine'
spine_top = 'Chest'
spine_bot = 'Pelvis'

# setting
division = 10

# create group
rig_grp = pm.createNode('transform', n=spine_name+'_rig_grp')
notMoving_grp = pm.createNode('transform', n=spine_name+'_notMoving_grp', p=rig_grp)

# if Chest or Pelvis are not given, create them
if not pm.objExists(spine_top):
    loc = pm.spaceLocator(n=spine_top)
    pm.xform(loc, t=(0,0,4))

if not pm.objExists(spine_bot):
    loc = pm.spaceLocator(n=spine_bot)
    pm.xform(loc, t=(0,0,-4))

# get positions and length
spine_top_pos = pm.xform(spine_top, q=True, rp=True, ws=True)
spine_bot_pos = pm.xform(spine_bot, q=True, rp=True, ws=True)
spine_center = (om.MVector(spine_top_pos)+om.MVector(spine_bot_pos))/2
spine_length = (om.MVector(spine_top_pos)-om.MVector(spine_bot_pos)).length()

# create  control joint
pm.select(clear=True)
spine_top_jnt = pm.joint(n=spine_name+"_top_jnt", p=(0,0,spine_length/2))
pm.select(clear=True)
spine_bot_jnt = pm.joint(n=spine_name+"_bot_jnt", p=(0,0,spine_length/-2))
pm.select(clear=True)
spine_mid_jnt = pm.joint(n=spine_name+"_mid_jnt", p=(0,0,0))

# create nurbs and bind skin
spine_nbs = pm.nurbsPlane(lr=spine_length, ax=(0,1,0), v=4, n=spine_name+"_nbs", ch=0)
pm.skinCluster(spine_nbs, spine_top_jnt, spine_mid_jnt, spine_bot_jnt)


# create curve and bind skin
crv_pts = [(0,0,spine_length/2), (0,0,spine_length*5/12), (0,0,spine_length/4), (0,0,0),
            (0,0,spine_length/-4), (0,0,spine_length*5/-12), (0,0,spine_length/-2)]
spine_crv = pm.curve(d=3, p=crv_pts, k=(0,0,0,1,2,3,4,4,4), n=spine_name+"_crv")
pm.skinCluster(spine_crv, spine_top_jnt, spine_mid_jnt, spine_bot_jnt)

pm.parent(spine_nbs, spine_crv, notMoving_grp)


# create uvPin, locators and joints
uvPin_grp = pm.createNode('transform', n=spine_name+'_uvPin_grp', p=rig_grp)
bindJnt_grp = pm.createNode('transform', n=spine_name+'_bindJnt_grp', p=rig_grp)

uvPin = pm.createNode('uvPin', n=spine_name+"_uvPin")
spine_nbs_shp = pm.listRelatives(spine_nbs, s=True)
pm.connectAttr(spine_nbs_shp[0]+'.worldSpace[0]', uvPin+'.deformedGeometry')
pm.connectAttr(spine_nbs_shp[1]+'.worldSpace[0]', uvPin+'.originalGeometry')

for i in range(division+1):
    loc = pm.spaceLocator(n=spine_name+"_nbs_loc{}".format(str(i).zfill(2)))
    pm.setAttr(loc+'.localScaleX', 0.1)
    pm.setAttr(loc+'.localScaleY', 0.1)
    pm.setAttr(loc+'.localScaleZ', 0.1)
    pm.setAttr(uvPin+'.coordinate[{}].coordinateU'.format(i), 0.5)
    pm.setAttr(uvPin+'.coordinate[{}].coordinateV'.format(i), i/division)
    
    pm.connectAttr(uvPin+'.outputMatrix[{}]'.format(i), loc+'.offsetParentMatrix')
   
    pm.select(clear=True)
    jnt = pm.joint(rad=0.2, n=spine_name+'_ik_bind_jnt{}'.format(str(i).zfill(2)))
    pm.connectAttr(loc+'.worldMatrix[0]'.format(i), jnt+'.offsetParentMatrix')
    pm.tangentConstraint(spine_crv, jnt, w=1, aim=(-1,0,0), u=(0,1,0), wut='objectrotation', wu=(1,0,0), wuo=loc)

    pm.parent(loc, uvPin_grp)
    pm.parent(jnt, bindJnt_grp)

# mid spine adjustment
spine_mid_nbs = pm.nurbsPlane(lr=spine_length, ax=(0,1,0), v=2, n=spine_name+"_mid_nbs", ch=0)
pm.skinCluster(spine_mid_nbs, spine_top_jnt, spine_bot_jnt)

mid_crv_pts = [(0,0,spine_length/2), (0,0,spine_length*2/6), (0,0,0),
                (0,0,spine_length*2/-6), (0,0,spine_length/-2)]
spine_mid_crv = pm.curve(d=3, p=mid_crv_pts, k=(0,0,0,1,2,2,2), n=spine_name+"_mid_crv")
pm.skinCluster(spine_mid_crv, spine_top_jnt, spine_bot_jnt)


midSpine_uvPin = pm.createNode('uvPin', n=spine_name+"_mid_uvPin")
spine_mid_nbs_shp = pm.listRelatives(spine_mid_nbs, s=True)
pm.connectAttr(spine_mid_nbs_shp[0]+'.worldSpace[0]', midSpine_uvPin+'.deformedGeometry')
pm.connectAttr(spine_mid_nbs_shp[1]+'.worldSpace[0]', midSpine_uvPin+'.originalGeometry')

mid_loc = pm.spaceLocator(n=spine_name+"_mid_nbs_loc")
pm.setAttr(mid_loc+'.localScaleX', 0.2)
pm.setAttr(mid_loc+'.localScaleY', 0.2)
pm.setAttr(mid_loc+'.localScaleZ', 0.2)
pm.setAttr(midSpine_uvPin+'.coordinate[0].coordinateU', 0.5)
pm.setAttr(midSpine_uvPin+'.coordinate[0].coordinateV', 0.5)
pm.connectAttr(midSpine_uvPin+'.outputMatrix[0]', mid_loc+'.offsetParentMatrix')

spine_mid_offset = pm.createNode('transform', n=spine_name+"_mid_offset")
pm.parent(spine_mid_jnt, spine_mid_offset)
pm.connectAttr(mid_loc+'.worldMatrix[0]', spine_mid_offset+'.offsetParentMatrix')
pm.tangentConstraint(spine_mid_crv, spine_mid_offset, w=1, aim=(0,0,-1), u=(0,1,0), wut='objectrotation', wu=(1,0,0), wuo=mid_loc)
pm.setAttr(spine_mid_offset+'.tx', lock=True)
pm.setAttr(spine_mid_offset+'.ty', lock=True)
pm.setAttr(spine_mid_offset+'.tz', lock=True)

pm.parent(mid_loc, spine_mid_nbs, spine_mid_crv, notMoving_grp)

controlJnt_grp = pm.createNode('transform', n=spine_name+'_controlJnt_grp', p=rig_grp)
pm.parent(spine_top_jnt, spine_bot_jnt, spine_mid_offset, controlJnt_grp)


# move spines
pm.xform(spine_bot_jnt, t=spine_bot_pos)
#pm.xform(spine_mid_jnt, t=spine_center)
pm.xform(spine_top_jnt, t=spine_top_pos)    
    
    
    
