import pymel.core as pm

follicle_name = 'follicle'
nurbs_shape_name = 'nurbs_aShape'

param = (0.5, 0.5)

# create follicle node(transform and shape)
transform_node = pm.createNode('transform', n=follicle_name)
shape_node = pm.createNode('follicle', n=transform_node+'Shape', p=transform_node)

pm.connectAttr(shape_node+'.outRotate', transform_node+'.rotate')
pm.connectAttr(shape_node+'.outTranslate', transform_node+'.translate')

# connect nurbs and follicle
pm.connectAttr(nurbs_shape_name+'.worldMatrix[0]', shape_node+'.inputWorldMatrix')
pm.connectAttr(nurbs_shape_name+'.local', shape_node+'.inputSurface')

# set parameter U and V
pm.setAttr(shape_node + '.parameterU', param[0])
pm.setAttr(shape_node + '.parameterV', param[1])
