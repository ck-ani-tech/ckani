import pymel.core as pm

def createFollicles(follicle_name='follicle'):
    
    param = (0.5, 0.5)
    
    if len(pm.ls(sl=True)) == 0:
        print("# Select a polygon mesh or a nurbs surface and run")
        return

    target_shape = pm.ls(sl=True)[0]
    
    if pm.nodeType(target_shape) == 'transform':
       target_shape = pm.listRelatives(target_shape, s=True)[0]
    
    mesh_shape_name = target_shape
    
    # create follicle node(transform and shape)
    transform_node = pm.createNode('transform', n=follicle_name)
    shape_node = pm.createNode('follicle', n=transform_node+'Shape', p=transform_node)
    
    pm.connectAttr(shape_node+'.outRotate', transform_node+'.rotate')
    pm.connectAttr(shape_node+'.outTranslate', transform_node+'.translate')
    
    # connect shape and follicle
    if pm.nodeType(target_shape) == 'mesh':
        pm.connectAttr(mesh_shape_name+'.worldMatrix[0]', shape_node+'.inputWorldMatrix')
        pm.connectAttr(mesh_shape_name+'.outMesh', shape_node+'.inputMesh')
    elif pm.nodeType(target_shape) == 'nurbsSurface':
        pm.connectAttr(mesh_shape_name+'.worldMatrix[0]', shape_node+'.inputWorldMatrix')
        pm.connectAttr(mesh_shape_name+'.local', shape_node+'.inputSurface')
    
    # set parameter U and V
    pm.setAttr(shape_node + '.parameterU', param[0])
    pm.setAttr(shape_node + '.parameterV', param[1])

#createFollicles()
