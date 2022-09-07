import pymel.core as pm

# create follicle node(transform and shape)
node_name = 'follicle'

transform_node = pm.createNode('transform', n=node_name)
shape_node = pm.createNode('follicle', n=transform_node+"Shape", p=transform_node)
