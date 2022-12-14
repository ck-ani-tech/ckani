import tools, shapes
import maya.api.OpenMaya as om
import pymel.core as pm
import json, os, math

class Perseus:
    '''
    Perseus comustiming methods
    '''
    @classmethod
    def getNewCtrlSetList(cls):
        return(['zeroCtrl', 'firstCtrl', 'secondCtrl', 'thirdCtrl',
				'tongueCtrl', 'teethCtrl', 'eyeTarget', 'skinJointVis',    
				'squashStretch', 'softModVis'])

    @classmethod
    def getEyeBaseCrvs(cls, perseus_name='name'):
        crv_list = [perseus_name+'_RUpEye_baseCurve', perseus_name+'_RDownEye_baseCurve']
        pm.select(crv_list)
        return(crv_list)

    @classmethod
    def getRigHeadSetupGeo(cls):
        targets = pm.ls('*_rig_head_geo_setup')
        if len(targets) > 1:
            raise ValueError('rig_head_geo_setup are more than one!!!!')
        return(pm.ls('*_rig_head_geo_setup')[0])

    @classmethod
    def getCtrls(cls, key, perseus_name='name'):
        ctrl_list = []
        if key == 'firstCtrl':
            ctrl_list = [perseus_name+'_c_brows_ctrl', perseus_name+'_jaw_ctrl', perseus_name+'_l_brows_a_ctrl', 
                        perseus_name+'_l_brows_b_ctrl', perseus_name+'_l_brows_c_ctrl', perseus_name+'_l_brows_d_ctrl', 
                        perseus_name+'_r_brows_a_ctrl', perseus_name+'_r_brows_b_ctrl', perseus_name+'_r_brows_c_ctrl', 
                        perseus_name+'_r_brows_d_ctrl', perseus_name+'_l_down_eye_ctrl', perseus_name+'_l_Up_eye_ctrl', 
                        perseus_name+'_r_down_eye_ctrl', perseus_name+'_r_Up_eye_ctrl', perseus_name+'_l_Nose_ctrl', 
                        perseus_name+'_Nose_ctrl', perseus_name+'_r_Nose_ctrl', perseus_name+'_l_Lip_ctrl', perseus_name+'_r_Lip_ctrl', 
                        perseus_name+'_upLip_ctrl', perseus_name+'_downLip_ctrl']
        elif key == 'secondCtrl':
            ctrl_list = [perseus_name+'_l_up_cheek_ctrl', perseus_name+'_l_cheek_ctrl', perseus_name+'_l_jaw_cheek_ctrl', 
                        perseus_name+'_r_cheek_ctrl', perseus_name+'_r_up_cheek_ctrl', perseus_name+'_r_jaw_cheek_ctrl', 
                        perseus_name+'_up_Nose_ctrl', perseus_name+'_l_down_eye_border_ctrl', perseus_name+'_l_down_r_eye_ctrl', 
                        perseus_name+'_l_down_l_eye_ctrl', perseus_name+'_l_Up_r_eye_ctrl', perseus_name+'_l_Up_l_eye_ctrl', 
                        perseus_name+'_l_Up_border_eye_ctrl', perseus_name+'_r_down_eye_border_ctrl', perseus_name+'_r_down_l_eye_ctrl', 
                        perseus_name+'_r_down_r_eye_ctrl', perseus_name+'_r_Up_r_eye_ctrl', perseus_name+'_r_Up_l_eye_ctrl', 
                        perseus_name+'_r_Up_border_eye_ctrl', perseus_name+'_l_nose_cheek_ctrl', perseus_name+'_r_nose_cheek_ctrl', 
                        perseus_name+'_r_upCornerLip_ctrl', perseus_name+'_l_upCornerLip_ctrl', perseus_name+'_r_upLip_ctrl', 
                        perseus_name+'_l_upLip_ctrl', perseus_name+'_r_downCornerLip_ctrl', perseus_name+'_l_downCornerLip_ctrl', 
                        perseus_name+'_r_downLip_ctrl', perseus_name+'_l_downLip_ctrl']
        elif key == 'thirdCtrl':
            ctrl_list = [perseus_name+'_r_eye_cheek_ctrl', perseus_name+'_l_eye_cheek_ctrl', perseus_name+'_l_down_cheek_ctrl', 
                        perseus_name+'_r_down_cheek_ctrl', perseus_name+'_jaw_lip_r_1_ctrl', perseus_name+'_jaw_lip_r_0_ctrl', 
                        perseus_name+'_jaw_lip_l_1_ctrl', perseus_name+'_jaw_lip_l_0_ctrl', perseus_name+'_jaw_lip_c_ctrl', 
                        perseus_name+'_l_Right_eye_ctrl', perseus_name+'_l_Left_eye_ctrl', perseus_name+'_l_Right_eye_border_ctrl', 
                        perseus_name+'_l_Left_eye_border_ctrl', perseus_name+'_l_down_r_eye_border_ctrl', perseus_name+'_l_down_l_eye_border_ctrl', 
                        perseus_name+'_l_up_l_eye_border_ctrl', perseus_name+'_l_up_r_eye_border_ctrl', perseus_name+'_r_Right_eye_ctrl', 
                        perseus_name+'_r_Left_eye_ctrl', perseus_name+'_r_Right_eye_border_ctrl', perseus_name+'_r_Left_eye_border_ctrl', 
                        perseus_name+'_r_down_l_eye_border_ctrl', perseus_name+'_r_down_r_eye_border_ctrl', perseus_name+'_r_up_r_eye_border_ctrl', 
                        perseus_name+'_r_up_l_eye_border_ctrl', perseus_name+'_l_b_Nose_ctrl', perseus_name+'_r_b_Nose_ctrl', perseus_name+'_down_Nose_ctrl']
        elif key == 'tongueCtrl':
            ctrl_list = [perseus_name+'_tongue_1_ctrl', perseus_name+'_tongue_2_ctrl', perseus_name+'_tongue_3_ctrl', perseus_name+'_tongue_4_ctrl', perseus_name+'_tongue_5_ctrl']
        elif key == 'teethCtrl':
            ctrl_list = [perseus_name+'_up_teeth_ctrl', perseus_name+'_down_teeth_ctrl']
        elif key == 'eyeTarget':
            ctrl_list = [perseus_name+'_REye_target_ctrl', perseus_name+'_Eye_Target_ctrl', perseus_name+'_LEye_target_ctrl']
        elif key == 'elementCtrl' or key == 'zeroCtrl':
            ctrl_list = [perseus_name+'_upLip_Move_ctrl', perseus_name+'_l_brows_Move_ctrl', perseus_name+'_downLip_Move_ctrl',
                        perseus_name+'_lEye_Move_ctrl', perseus_name+'_r_brows_Move_ctrl', perseus_name+'_Lip_Move_ctrl',
                        perseus_name+'_nose_Move_ctrl', perseus_name+'_rEye_Move_ctrl']
        else:
        	pass

        pm.select(ctrl_list)
        return(pm.ls(sl=True))

    @classmethod
    def getMatchingName(cls, perseus_ctrl_name, perseus_name='name'):
        perseus_ctrl_name = str(perseus_ctrl_name)
        new_name = perseus_ctrl_name[len(perseus_name)+1:]
        
        matching_name_dic = {}
        matching_name_dic['Eye_Target_ctrl'] = 'EyeTarget_M'
        matching_name_dic['nose_Move_ctrl'] = 'NoseMove_M'
        matching_name_dic['Nose_ctrl'] = 'Nose_M'
        matching_name_dic['jaw_ctrl'] = 'Jaw_M'
        matching_name_dic['Lip_Move_ctrl'] = 'LipMove_M'
        matching_name_dic['up_Nose_ctrl'] = 'Nose_UP_M'
        matching_name_dic['down_Nose_ctrl'] = 'Nose_DW_M'
        matching_name_dic['c_brows_ctrl'] = 'Eyebrow_M'        

        matching_name_dic['r_Up_eye_ctrl'] = 'EyelidSet_UP_R'
        matching_name_dic['r_down_eye_ctrl'] = 'EyelidSet_DW_R'
        matching_name_dic['rEye_Move_ctrl'] = 'EyeMove_R'
        matching_name_dic['REye_target_ctrl'] = 'EyeTarget_R'
        matching_name_dic['r_brows_Move_ctrl'] = 'EyebrowMove_R'
        matching_name_dic['r_Nose_ctrl'] = 'Nose_R'
        matching_name_dic['r_nose_cheek_ctrl'] = 'NoseCheek_R'
        matching_name_dic['rEye_Move_ctrl'] = 'EyeMove_R'

        matching_name_dic['l_Up_eye_ctrl'] = 'EyelidSet_UP_L'
        matching_name_dic['l_down_eye_ctrl'] = 'EyelidSet_DW_L'
        matching_name_dic['lEye_Move_ctrl'] = 'EyeMove_L'
        matching_name_dic['LEye_target_ctrl'] = 'EyeTarget_L'
        matching_name_dic['l_brows_Move_ctrl'] = 'EyebrowMove_L'
        matching_name_dic['l_Nose_ctrl'] = 'Nose_L'
        matching_name_dic['l_nose_cheek_ctrl'] = 'NoseCheek_L'
        matching_name_dic['lEye_Move_ctrl'] = 'EyeMove_L'

        matching_name_dic['r_eye_cheek_ctrl'] = 'EyeCheek_R'
        matching_name_dic['l_eye_cheek_ctrl'] = 'EyeCheek_L'

        matching_name_dic['r_down_r_eye_border_ctrl'] = 'EyelidBorderBind_DW_01_R'
        matching_name_dic['r_down_eye_border_ctrl'] = 'EyelidBorderBind_DW_02_R'
        matching_name_dic['r_down_l_eye_border_ctrl'] = 'EyelidBorderBind_DW_03_R'

        matching_name_dic['r_up_r_eye_border_ctrl'] = 'EyelidBorderBind_UP_01_R'
        matching_name_dic['r_Up_border_eye_ctrl'] = 'EyelidBorderBind_UP_02_R'
        matching_name_dic['r_up_l_eye_border_ctrl'] = 'EyelidBorderBind_UP_03_R'

        matching_name_dic['l_down_l_eye_border_ctrl'] = 'EyelidBorderBind_DW_01_L'
        matching_name_dic['l_down_eye_border_ctrl'] = 'EyelidBorderBind_DW_02_L'
        matching_name_dic['l_down_r_eye_border_ctrl'] = 'EyelidBorderBind_DW_03_L'

        matching_name_dic['l_up_r_eye_border_ctrl'] = 'EyelidBorderBind_UP_01_L'
        matching_name_dic['l_Up_border_eye_ctrl'] = 'EyelidBorderBind_UP_02_L'
        matching_name_dic['l_up_l_eye_border_ctrl'] = 'EyelidBorderBind_UP_03_L'

        matching_name_dic['r_Left_eye_border_ctrl'] = 'EyelidBorderBind_IN_R'
        matching_name_dic['l_Right_eye_border_ctrl'] = 'EyelidBorderBind_IN_L'
        matching_name_dic['l_Left_eye_ctrl'] = 'EyelidBind_OT_L'
        matching_name_dic['l_Right_eye_ctrl'] = 'EyelidBind_IN_L'
        matching_name_dic['r_Right_eye_border_ctrl'] = 'EyelidBorderBind_OT_R'
        matching_name_dic['r_Left_eye_ctrl'] = 'EyelidBind_IN_R'
        matching_name_dic['r_Right_eye_ctrl'] = 'EyelidBind_OT_R'
        matching_name_dic['l_Left_eye_border_ctrl'] = 'EyelidBorderBind_OT_L'

        matching_name_dic['r_down_cheek_ctrl'] = 'Cheek_DW_R'
        matching_name_dic['l_down_cheek_ctrl'] = 'Cheek_DW_L'

        matching_name_dic['jaw_lip_r_1_ctrl'] = 'JawLip_01_R'
        matching_name_dic['jaw_lip_r_0_ctrl'] = 'JawLip_02_R'
        matching_name_dic['jaw_lip_c_ctrl'] = 'JawLip_M'
        matching_name_dic['jaw_lip_l_0_ctrl'] = 'JawLip_02_L'
        matching_name_dic['jaw_lip_l_1_ctrl'] = 'JawLip_01_L'

        matching_name_dic['l_cheek_ctrl'] = 'Cheek_L'
        matching_name_dic['l_jaw_cheek_ctrl'] = 'JawCheek_L'
        matching_name_dic['l_up_cheek_ctrl'] = 'Cheek_UP_L'
        matching_name_dic['r_cheek_ctrl'] = 'Cheek_R'
        matching_name_dic['r_jaw_cheek_ctrl'] = 'JawCheek_R'
        matching_name_dic['r_up_cheek_ctrl'] = 'Cheek_UP_R'

        matching_name_dic['tongue_1_ctrl'] = 'Tongue_01_M'
        matching_name_dic['tongue_2_ctrl'] = 'Tongue_02_M'
        matching_name_dic['tongue_3_ctrl'] = 'Tongue_03_M'
        matching_name_dic['tongue_4_ctrl'] = 'Tongue_04_M'
        matching_name_dic['tongue_5_ctrl'] = 'Tongue_05_M'

        matching_name_dic['up_teeth_ctrl'] = 'Teeth_UP_M'
        matching_name_dic['down_teeth_ctrl'] = 'Teeth_DW_M'

        matching_name_dic['r_brows_a_softMod_ctrl'] = 'BrowSoftMod_IN_02_R'
        matching_name_dic['r_brows_a_softMod_ctrl_CtrlGrp'] = 'BrowSoftMod_OT_02_R'
        matching_name_dic['r_brows_c_softMod_ctrl'] = 'BrowSoftMod_IN_01_R'
        matching_name_dic['r_brows_c_softMod_ctrl_CtrlGrp'] = 'BrowSoftMod_OT_01_R'
        matching_name_dic['l_brows_a_softMod_ctrl'] = 'BrowSoftMod_IN_02_L'
        matching_name_dic['l_brows_a_softMod_ctrl_CtrlGrp'] = 'BrowSoftMod_OT_02_L'
        matching_name_dic['l_brows_c_softMod_ctrl'] = 'BrowSoftMod_IN_01_L'
        matching_name_dic['l_brows_c_softMod_ctrl_CtrlGrp'] = 'BrowSoftMod_OT_01_L'
        matching_name_dic['nose_softMod_ctrl'] = 'NoseSoftMod_IN_M'
        matching_name_dic['nose_softMod_ctrl_CtrlGrp'] = 'NoseSoftMod_OT_M'
        matching_name_dic['chin_softMod_ctrl'] = 'JawSoftMod_IN_M'
        matching_name_dic['chin_softMod_ctrl_CtrlGrp'] = 'JawSoftMod_OT_M'

        matching_name_dic['r_cheek_softMod_ctrl'] = 'CheekSoftMod_IN_R'
        matching_name_dic['r_cheek_softMod_ctrl_CtrlGrp'] = 'CheekSoftMod_OT_R'
        matching_name_dic['l_cheek_softMod_ctrl'] = 'CheekSoftMod_IN_L'
        matching_name_dic['l_cheek_softMod_ctrl_CtrlGrp'] = 'CheekSoftMod_OT_L'

        matching_name_dic['r_lip_softMod_ctrl'] = 'LipSoftMod_IN_R'
        matching_name_dic['r_lip_softMod_ctrl_CtrlGrp'] = 'LipSoftMod_OT_R'
        matching_name_dic['l_lip_softMod_ctrl'] = 'LipSoftMod_IN_L'
        matching_name_dic['l_lip_softMod_ctrl_CtrlGrp'] = 'LipSoftMod_OT_L'

        if new_name in matching_name_dic.keys():
            new_name = matching_name_dic[new_name]
        return(new_name)

    @classmethod
    def customizePerseus(cls, perseus_name='name', stage_name = 'customizePerseus'):
        # [after Perseus build]
        #perseus_name = "name"

        # [step 0] : preparation
        face_ctrl_grp = perseus_name + '_face_ctrl_grp'
        eye_target_ctrl_grp = tools.makeParent(perseus_name+'_Eye_Target_ctrl', org=True)

        # hide perseus contrllers which are not being used
        pm.setAttr(perseus_name+'_downLip_Move_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_upLip_Move_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_Lip_All_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_l_b_Nose_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_r_b_Nose_ctrl_grp.v', 0)
        if pm.objExists('FKAimEye_R'):
            pm.setAttr('FKAimEye_R.v', 0)
        if pm.objExists('FKAimEye_L'):
            pm.setAttr('FKAimEye_L.v', 0)
        if pm.objExists('FKOffsetJaw_M'):
            pm.setAttr('FKOffsetJaw_M.v', 0)
        pm.setAttr(perseus_name+'_r_Up_r_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_r_Up_l_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_r_down_l_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_r_down_r_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_l_Up_r_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_l_Up_l_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_l_down_l_eye_ctrl_grp.v', 0)
        pm.setAttr(perseus_name+'_l_down_r_eye_ctrl_grp.v', 0)

        # to avoid cycles on jaw_ctrl
        pm.disconnectAttr(perseus_name+'_jaw_ctrl_grp.tx')
        pm.disconnectAttr(perseus_name+'_jaw_ctrl_grp.ty')
        pm.disconnectAttr(perseus_name+'_jaw_ctrl_grp.tz')

        # rename advanced skeleton Jaw_M to AdvancedSkelton_Jaw_M to use Jaw_M for new ctrl
        if pm.objExists("Jaw_M"):
            pm.rename("Jaw_M", "AdvancedSkelton_Jaw_M")

        new_facial_setting_ctrl_name = 'FacialSettings'

        if pm.objExists(new_facial_setting_ctrl_name):
            pm.warning('FacialSetting are already processed, it seems!!!!!!')
            return

        # cycles on name_r_brows_Move_ctrl, name_r_brows_ctrl_All_grp caused by expression "name_brows"
        # remove lines on expression "name_brows"
        exp_name = perseus_name+"_brows"
        exp_str = pm.expression(exp_name, q=True, s=True)
        buf = exp_str.split('\n')
        new_buf = [buf[0]]+buf[7:]
        new_exp_str = '\n'.join(new_buf)

        pm.delete(exp_name)
        pm.expression(name=exp_name, s=new_exp_str)

        brow_move_ctrl = perseus_name + '_r_brows_Move_ctrl'
        brows_ctrl_all_grp = perseus_name + '_r_brows_ctrl_All_grp'

        md_t_name = brow_move_ctrl + "_t_md"
        md_r_name = brow_move_ctrl + "_r_md"
        md_t_name = pm.shadingNode('multiplyDivide', asUtility=True, name = md_t_name)
        pm.setAttr(md_t_name+'.input2X', -1)
        md_r_name = pm.shadingNode('multiplyDivide', asUtility=True, name = md_r_name)
        pm.setAttr(md_r_name+'.input2Y', -1)
        pm.setAttr(md_r_name+'.input2Z', -1)

        pm.connectAttr(brow_move_ctrl+'.t', md_t_name+'.input1')
        pm.connectAttr(brow_move_ctrl+'.r', md_r_name+'.input1')
        pm.connectAttr(md_t_name+'.output', brows_ctrl_all_grp+'.t')
        pm.connectAttr(md_r_name+'.output', brows_ctrl_all_grp+'.r')

        # [step 1]
        # facial setting ctrl
        #facial_setting_ctrl = perseus_name+"_facial_settings"
        #pm.rename(facial_setting_ctrl, new_facial_setting_ctrl_name)
        facial_setting_ctrl = perseus_name+"_facial_settings"
        new_facial_setting_ctrl_name = 'FacialSettings'
        existing_attrs = pm.listAttr(facial_setting_ctrl, keyable=True, userDefined=True)
        new_facial_setting_ctrl_name = pm.duplicate(facial_setting_ctrl, name=new_facial_setting_ctrl_name)[0]
        for attr in existing_attrs:
            pm.deleteAttr(new_facial_setting_ctrl_name, at=attr)
            pm.setAttr(facial_setting_ctrl+'.'+attr, 1, lock=True)

        for attr in cls.getNewCtrlSetList():
            if attr in ['tongueCtrl', 'teethCtrl', 'eyeTarget']:
                #pm.setAttr(facial_setting_ctrl+'.'+src_attr, lock=False)
                #pm.addAttr(new_facial_setting_ctrl_name, ln=attr, proxy=facial_setting_ctrl+'.'+src_attr)
                #pm.setAttr(new_facial_setting_ctrl_name+'.'+attr, 0)
                pm.addAttr(new_facial_setting_ctrl_name, ln=attr, at='bool', keyable=True) 
                pm.setAttr(facial_setting_ctrl+'.'+attr, lock=False)
                pm.connectAttr(new_facial_setting_ctrl_name+'.'+attr,  facial_setting_ctrl+'.'+attr)
            elif attr in ['skinJointVis', 'softModVis']:
                pm.addAttr(new_facial_setting_ctrl_name, ln=attr, at='bool', keyable=False) 
                pm.setAttr(new_facial_setting_ctrl_name+'.'+attr, e=True, cb=True)
                pm.setAttr(facial_setting_ctrl+'.'+attr, lock=False)
                pm.connectAttr(new_facial_setting_ctrl_name+'.'+attr,  facial_setting_ctrl+'.'+attr)
            elif attr in ['squashStretch']:
                pm.addAttr(new_facial_setting_ctrl_name, ln=attr, at='bool', keyable=False)
                pm.setAttr(new_facial_setting_ctrl_name+'.'+attr, cb=True)
                pm.setAttr(facial_setting_ctrl+'.squashstretch', lock=False)
                pm.setAttr(facial_setting_ctrl+'.squashstretch', 0)
                pm.setAttr(facial_setting_ctrl+'.squashstretch', lock=True)
            else:
                pm.addAttr(new_facial_setting_ctrl_name, ln=attr, at='bool', keyable=True)
            if attr in ['zeroCtrl', 'firstCtrl']:
                pm.setAttr(new_facial_setting_ctrl_name+'.'+attr, 1)
        # initial setting
        pm.setAttr(facial_setting_ctrl+'.v', lock=False)
        pm.setAttr(facial_setting_ctrl+'.v', 0)
        pm.setAttr(facial_setting_ctrl+'.v', lock=True)

        # [step1.5] : remapping facial setting
        l_ear_ctrl_parent_node = pm.listRelatives('Ear_02_L',p=True)[0]
        r_ear_ctrl_parent_node = pm.listRelatives('Ear_02_R',p=True)[0]
        pm.connectAttr(new_facial_setting_ctrl_name+'.zeroCtrl', str(l_ear_ctrl_parent_node)+'.v', f=True)
        pm.connectAttr(new_facial_setting_ctrl_name+'.zeroCtrl', str(r_ear_ctrl_parent_node)+'.v', f=True)

        # [step 2]
        # repalce controllers
        set_list = []
        for target in cls.getNewCtrlSetList():

            ctrl_list = cls.getCtrls(target, perseus_name=perseus_name)
            new_ctrl_list = []
            ctrl_set_name = target+'_set'
            if pm.objExists(ctrl_set_name):
                pm.warning(ctrl_set_name+' exits!! You might have done this already! Skipping this!')
            else:
                for ctrl in ctrl_list:
                    # ctrl is joint
                    jnt_pa = pm.listRelatives(ctrl, p=True)[0]
                    jnt_shp = pm.listRelatives(ctrl, s=True)[0]
                    color_index = pm.getAttr(ctrl+'.overrideColor')
                
                    jnt_r = 1.0

                    if pm.attributeQuery('radius', node=ctrl, exists=True):
                        jnt_r = pm.getAttr(ctrl+'.radius')

                    #new_ctrl_name = ctrl[len(perseus_name)+1:]
                    new_ctrl_name = cls.getMatchingName(ctrl, perseus_name=perseus_name)

                    new_ctrl = pm.circle(r=jnt_r, name=new_ctrl_name)[0]
                    pm.delete(new_ctrl, ch=True)
                    pm.setAttr(new_ctrl+'.overrideEnabled', 1)
                    pm.setAttr(new_ctrl+'.overrideColor', color_index)
                    new_ctrl_pa = pm.createNode('transform', name='SDK'+new_ctrl)
                    pm.parent(new_ctrl, new_ctrl_pa)
                    pm.parent(new_ctrl_pa, jnt_pa)
                    #pm.matchTransform(new_ctrl, ctrl)
                    pm.matchTransform(new_ctrl_pa, ctrl)
                    if str(new_ctrl) in ["LipMove_M"]:
                        pm.pointConstraint(new_ctrl, ctrl, mo=True)
                    else:
                        pm.parentConstraint(new_ctrl, ctrl, mo=True)
                    new_ctrl_list.append(new_ctrl)
                
                    pm.disconnectAttr(ctrl+'.v')
                    pm.setAttr(ctrl+'.v', 0)
                    if 'tongue' in str(ctrl):
                        pm.setAttr(ctrl+'.v', 1)
                        pm.setAttr(ctrl+'.drawStyle', 2)
                    
                    new_target = target
                    if 'EyelidBorderBind' in str(new_ctrl_pa) or 'EyelidBind' in str(new_ctrl_pa):
                        new_target = 'secondCtrl'
                    pm.connectAttr(new_facial_setting_ctrl_name+'.'+new_target, new_ctrl_pa+'.v')
                    
                    pm.setAttr(new_ctrl+'.v', lock=True, keyable=False)
                    pm.setAttr(new_ctrl+'.sx', lock=True, keyable=False)
                    pm.setAttr(new_ctrl+'.sy', lock=True, keyable=False)
                    pm.setAttr(new_ctrl+'.sz', lock=True, keyable=False)            

                    # changing shapes
                    shape_changed = shapes.changeCircleCtrlShape(new_ctrl, scale=1.0)
                    if shape_changed is None:
                        source_shp = pm.listRelatives(ctrl, shapes=True)[0]
                        target_shp = pm.listRelatives(new_ctrl, shapes=True)[0]

                        for i in range(8):
                            pos = pm.pointPosition(source_shp+'.cv[{}]'.format(i))
                            pm.xform(target_shp+'.cv[{}]'.format(i), ws=True, t=pos)

                    pm.delete(jnt_shp)       
                new_set = pm.sets(new_ctrl_list, name=ctrl_set_name)
                set_list.append(new_set)
        pm.sets(set_list, name='FaceBuilderSet')

        # [step2.5] rename softmode controls
        softmod_ctrl_list = ['r_brows_a_softMod_ctrl', 'r_brows_a_softMod_ctrl_CtrlGrp',
                            'r_brows_c_softMod_ctrl', 'r_brows_c_softMod_ctrl_CtrlGrp',
                            'l_brows_a_softMod_ctrl', 'l_brows_a_softMod_ctrl_CtrlGrp',
                            'l_brows_c_softMod_ctrl', 'l_brows_c_softMod_ctrl_CtrlGrp',
                            'nose_softMod_ctrl', 'nose_softMod_ctrl_CtrlGrp',
                            'chin_softMod_ctrl', 'chin_softMod_ctrl_CtrlGrp',
                            'r_cheek_softMod_ctrl', 'r_cheek_softMod_ctrl_CtrlGrp',
                            'l_cheek_softMod_ctrl', 'l_cheek_softMod_ctrl_CtrlGrp',
                            'r_lip_softMod_ctrl', 'r_lip_softMod_ctrl_CtrlGrp',
                            'l_lip_softMod_ctrl', 'l_lip_softMod_ctrl_CtrlGrp',
                            ]


        for soft_ctrl in softmod_ctrl_list:
            soft_ctrl_full = perseus_name+'_'+soft_ctrl
            pm.rename(soft_ctrl_full, cls.getMatchingName(soft_ctrl_full, perseus_name=perseus_name))

        # [step3]
        # fix controller positions
        r_eyebrow_grp_pos = pm.xform(perseus_name+'_r_brows_Move_ctrl_grp',q=True, rp=True, ws=True)
        l_eyebrow_grp_pos = pm.xform(perseus_name+'_l_brows_Move_ctrl_grp',q=True, rp=True, ws=True)
        medium_pos_z = (r_eyebrow_grp_pos[2]+l_eyebrow_grp_pos[2])/2.0
        pm.xform(perseus_name+'_r_brows_Move_ctrl_grp', t=(r_eyebrow_grp_pos[0], r_eyebrow_grp_pos[1], medium_pos_z), ws=True)
        pm.xform(perseus_name+'_l_brows_Move_ctrl_grp', t=(l_eyebrow_grp_pos[0], l_eyebrow_grp_pos[1], medium_pos_z), ws=True)

        head_pos = pm.xform('Head_M', q=True, rp=True, ws=True)
        nose_pos = pm.xform('NoseMove_M', q=True, rp=True, ws=True)
        head_nose_distance = nose_pos[2]-head_pos[2]
        for ctrl in ['JawLip_01_R', 'JawLip_02_R', 'JawLip_M', 'JawLip_02_L', 'JawLip_01_L', 'Cheek_DW_R', 'Cheek_DW_L']:
            tools.offsetCtrlShape([ctrl], offset=(0,0,head_nose_distance/16.0))

        # [step4]
        # adding new controllers
        pm.setAttr("name_rDownEyeBorder_jnt_4_bind_grp_pc.name_rDownEyeBorder_jnt_3_bindW0", 0)
        pm.setAttr("name_rDownEyeBorder_jnt_2_bind_grp_pc.name_rDownEyeBorder_jnt_3_bindW1", 0)
        pm.setAttr("name_rTopEyeBorder_jnt_4_bind_grp_pc.name_rTopEyeBorder_jnt_3_bindW0", 0)
        pm.setAttr("name_rTopEyeBorder_jnt_2_bind_grp_pc.name_rTopEyeBorder_jnt_3_bindW1", 0)
        pm.setAttr("name_lDownEyeBorder_jnt_4_bind_grp_pc.name_lDownEyeBorder_jnt_3_bindW0", 0)
        pm.setAttr("name_lDownEyeBorder_jnt_2_bind_grp_pc.name_lDownEyeBorder_jnt_3_bindW0", 0)
        pm.setAttr("name_lTopEyeBorder_jnt_4_bind_grp_pc.name_lTopEyeBorder_jnt_3_bindW0", 0)
        pm.setAttr("name_lTopEyeBorder_jnt_2_bind_grp_pc.name_lTopEyeBorder_jnt_3_bindW1", 0)

        r_up_ctrls = ['EyelidBorderBind_UP_01_R', 'EyelidBorderBind_UP_02_R', 'EyelidBorderBind_UP_03_R']
        r_dw_ctrls = ['EyelidBorderBind_DW_01_R', 'EyelidBorderBind_DW_02_R', 'EyelidBorderBind_DW_03_R']
        l_up_ctrls = ['EyelidBorderBind_UP_01_L', 'EyelidBorderBind_UP_02_L', 'EyelidBorderBind_UP_03_L']
        l_dw_ctrls = ['EyelidBorderBind_DW_01_L', 'EyelidBorderBind_DW_02_L', 'EyelidBorderBind_DW_03_L']

        distance = None

        for ctrl_list in [r_up_ctrls, r_dw_ctrls, l_up_ctrls, l_dw_ctrls]:
            center_pos = tools.findCenterPos(ctrl_list)
            part = 'up' if '_UP_' in ctrl_list[0] else 'dw'
            side = ctrl_list[0][-2:]
            eye_move_ctrl = 'EyeMove'+side
            eye_ctrl_pos = tools.findCenterPos(['EyeMove'+side], shape=True)
            eyelid_border_ctrl_pos = (eye_ctrl_pos[0], center_pos[1], eye_ctrl_pos[2])

            if distance is None:
                distance = (om.MVector(eyelid_border_ctrl_pos)-om.MVector(eye_ctrl_pos)).length()

            name = 'EyelidBorderSet_'+part.upper()+side.upper()
            eyelid_border_ctrl = shapes.createCtrlShape(name=name, color='yellow',
                        shape='tri',scale=distance*0.45, part=part, offset=(0,0,0))
            set_pos, set_drv, set_extra = tools.makePosDrvExtra(eyelid_border_ctrl)
            pm.xform(set_pos, t=eyelid_border_ctrl_pos, a=True, ws=True)
            pm.connectAttr(new_facial_setting_ctrl_name+'.secondCtrl', set_pos+'.v')

            for ctrl in ctrl_list:
                parent_of_ctrl = pm.listRelatives(ctrl, parent=True)[0]
                ctrl_pos, ctrl_drv, ctrl_extra = tools.makePosDrvExtra(parent_of_ctrl)
                pm.parent(ctrl_pos, eyelid_border_ctrl)
            pm.parent(set_pos, face_ctrl_grp)            

        # recover jaw ctrl movement
        preseuse_jaw_ctrl = perseus_name+'_jaw_ctrl'
        pm.delete(pm.parentConstraint(preseuse_jaw_ctrl, q=True))
        jaw_ctrl_rot_proxy = pm.spaceLocator(name='jaw_ctrl_rot_proxy')
        pm.matchTransform(jaw_ctrl_rot_proxy, 'Jaw_M')
        pm.parent(jaw_ctrl_rot_proxy, face_ctrl_grp)
        pm.orientConstraint('Jaw_M', jaw_ctrl_rot_proxy)
        pm.connectAttr(jaw_ctrl_rot_proxy+'.r', preseuse_jaw_ctrl+'.r')

        jaw_ctrl_pivot_proxy = pm.spaceLocator(name='jaw_ctrl_pivot_proxy')
        jaw_ctrl_pivot_proxy_end = pm.spaceLocator(name='jaw_ctrl_pivot_proxy_end')
        pm.matchTransform(jaw_ctrl_pivot_proxy_end, 'Jaw_M')
        pm.matchTransform(jaw_ctrl_pivot_proxy, perseus_name+'_facialJaw_jnt_skin')
        pm.parent(jaw_ctrl_pivot_proxy_end, jaw_ctrl_pivot_proxy)
        pm.parent(jaw_ctrl_pivot_proxy, face_ctrl_grp)
        pm.connectAttr('Jaw_M.r', jaw_ctrl_pivot_proxy+'.r')
        pm.pointConstraint(jaw_ctrl_pivot_proxy_end, "SDKJaw_M", mo=True)

        jaw_ctrl_pos_proxy_0 = pm.spaceLocator(name='jaw_ctrl_pos_proxy_0')
        jaw_ctrl_pos_proxy_1 = pm.spaceLocator(name='jaw_ctrl_pos_proxy_1')
        pm.parent(jaw_ctrl_pos_proxy_0, jaw_ctrl_pos_proxy_1, face_ctrl_grp)
        pm.pointConstraint('Jaw_M', jaw_ctrl_pos_proxy_0, mo=True)
        pm.pointConstraint(jaw_ctrl_pivot_proxy_end, jaw_ctrl_pos_proxy_1, mo=True)
        tools.minusTranslation(jaw_ctrl_pos_proxy_0, jaw_ctrl_pos_proxy_1, preseuse_jaw_ctrl)

        for item in [jaw_ctrl_rot_proxy, jaw_ctrl_pivot_proxy, jaw_ctrl_pivot_proxy_end, jaw_ctrl_pos_proxy_0, jaw_ctrl_pos_proxy_1]:
            pm.setAttr(str(item)+'.v', 0)

        # additional settings
        pm.setAttr('AimOffsetEye.v', 0)
        pm.setAttr('FacialSettings.zeroCtrl', 1)
        pm.setAttr('FacialSettings.firstCtrl', 1)
        pm.setAttr('FacialSettings.secondCtrl', 1)
        pm.setAttr('FacialSettings.eyeTarget', 1)
        pm.setAttr(eye_target_ctrl_grp+'.v', 1)

        pm.select()
        print("# "+stage_name+" complete")        
        return(True)

    @classmethod
    def applyWeightedBlendForEyelids(cls, rigData, perseus_name='name', weight=0.7):
        print("==================", weight)
        sides = ['rUp','rDw', 'lUp', 'lDw']

        setup_geo_sc = tools.getSkinClusterFromMesh(cls.getRigHeadSetupGeo())
        pm.setAttr(setup_geo_sc.name()+'.skinningMethod', 2)

        for side in sides:
            try:
                # find the skin cluster of rig_head_setup_geo
                outerVtxs = rigData.getValue(cls.getRigHeadSetupGeo(), side+'EyelidOuterVtx')
                innerVtxs = rigData.getValue(cls.getRigHeadSetupGeo(), side+'EyelidInnerVtx')

                faces = rigData.getValue(cls.getRigHeadSetupGeo(), side+'EyelidArea')
                vtxs = pm.polyListComponentConversion(faces, fromFace=True, toVertex=True)
                pm.select(vtxs, r=True)
                vtxs = pm.ls(sl=True,fl=True)

                outer_pnt = om.MPoint(pm.pointPosition(outerVtxs[7]))
                inner_pnt = om.MPoint(pm.pointPosition(innerVtxs[7]))
                maybe_farthest_distance = om.MVector(outer_pnt-inner_pnt).length()

                for vtx in vtxs:
                    pnt = om.MPoint(pm.pointPosition(vtx))
                    closest_distance = maybe_farthest_distance
                    closest_outline_vtx = None
                    for outline_vtx in outerVtxs+innerVtxs:
                        outline_pnt = om.MPoint(pm.pointPosition(outline_vtx))
                        distance = om.MVector(outline_pnt-pnt).length()
                        if distance < closest_distance:
                            closest_outline_vtx = outline_vtx
                            closest_distance = distance
                    #print(maybe_farthest_distance, weight)
                    weight_to_apply = math.sin(math.pi*closest_distance/maybe_farthest_distance*weight)         
                    vtx_id = vtx.name().split('[')[1].split(']')[0]
                    #print(vtx, vtx_id, closest_distance, weight_to_apply)
                    pm.setAttr(setup_geo_sc.name()+'.bw[{}]'.format(vtx_id),weight_to_apply) 
            except KeyError as e:
                pm.warning(e.message)
                continue
        return(True)