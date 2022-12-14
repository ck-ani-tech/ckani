import tools
import pymel.core as pm

def printCircleCvPosition(node):
    mesh_name = str(node)
    cvs = pm.ls(str(node)+'.cv[*]', fl=True)
    for i in range(len(cvs)):
        cv = mesh_name + '.cv[{}]'.format(str(i))
        pnt = pm.pointPosition(cv, l=True)
        print(pnt)    

def changeCircleCtrlShape(ctrl_obj, scale=1.0):
    '''
    Assume the controller shape is a circle, move circle cvs to change its shape.

    '''

    pnts = []
    color = None

    if str(ctrl_obj) == 'NoseMove_M':
        pnts = [
            [2.00047913192, 1.04217477914, 0.378803622723],
            [0.000479131922475, 0.982571804678, 0.378803622723],
            [-1.99952086808, 1.04217477914, 0.378803622723],
            [-1.99952086808, 0.0, 0.378803622723],
            [-1.99952086808, -1.04217477914, 0.378803622723],
            [0.000479131922475, -0.982571804678, 0.378803622723],
            [2.00047913192, -1.04217477914, 0.378803622723],
            [2.00047913192, 0.0, 0.378803622723]
        ]
    elif str(ctrl_obj) == 'LipMove_M':
        pnts = [
            [3.50045792192, 1.45904469079, 1.26544588787],
            [0.000457921920519, 1.37560052655, 1.26544588787],
            [-3.49954207808, 1.45904469079, 1.26544588787],
            [-3.49954207808, 0.0, 1.26544588787],
            [-3.49954207808, -1.45904469079, 1.26544588787],
            [0.000457921920519, -1.37560052655, 1.26544588787],
            [3.50045792192, -1.45904469079, 1.26544588787],
            [3.50045792192, 0.0, 1.26544588787]
        ]
    elif str(ctrl_obj) == 'Nose_UP_M':
        pnts = [
            [0.231549526138, -0.231549526138, 1.23471210141e-17],
            [3.01864603073e-17, -0.492982308504, -7.40827260845e-17],
            [-0.231549526138, -0.231549526138, 3.70413630423e-17],
            [-0.492982308504, -2.5556289927e-17, -2.74161160754e-33],
            [-0.231549526138, 0.231549526138, -1.23471210141e-17],
            [-4.93823750089e-17, 0.492982308504, 9.87769681127e-17],
            [0.231549526138, 0.231549526138, -3.70413630423e-17],
            [0.492982308504, 6.72278233495e-17, 0.0]
        ]
    elif str(ctrl_obj) == 'Nose_DW_M':
        pnts = [
            [0.231549526138, -0.231549526138, 1.0],
            [3.01864603073e-17, -0.492982308504, 1.0],
            [-0.231549526138, -0.231549526138, 1.0],
            [-0.492982308504, -2.5556289927e-17, 1.0],
            [-0.231549526138, 0.231549526138, 1.0],
            [-4.93823750089e-17, 0.492982308504, 1.0],
            [0.231549526138, 0.231549526138, 1.0],
            [0.492982308504, 6.72278233495e-17, 1.0]
        ]
    elif str(ctrl_obj) == 'Eyebrow_M':
        pnts = [
            [0.381936299801, 0.381936299801, 0.0],
            [4.97919609085e-17, 0.813164431462, -2.22044604925e-16],
            [-0.381936299801, 0.381936299801, 1.11022302463e-16],
            [-0.813164431462, 4.21545877211e-17, 1.23259516441e-32],
            [-0.381936299801, -0.381936299801, -1.11022302463e-16],
            [-8.14552372482e-17, -0.813164431462, -2.22044604925e-16],
            [0.381936299801, -0.381936299801, -1.11022302463e-16],
            [0.813164431462, -1.10890946408e-16, 0.0]
        ]
    elif str(ctrl_obj) == 'EyeMove_R' or str(ctrl_obj) == 'EyeMove_L' :
        pnts = [
            [0.575072209011, -0.575072209011, 1.55719265933],
            [-2.13552593792e-16, -0.813274917327, 1.55719265933],
            [-0.575072209011, -0.575072209011, 1.55719265933],
            [-0.813274917327, -4.21603153278e-17, 1.55719265933],
            [-0.575072209011, 0.575072209011, 1.55719265933],
            [-3.44817624702e-16, 0.813274917327, 1.55719265933],
            [0.575072209011, 0.575072209011, 1.55719265933],
            [0.813274917327, 1.10906013326e-16, 1.55719265933]
        ]
    elif str(ctrl_obj) == 'EyebrowMove_R' or str(ctrl_obj) == 'EyebrowMove_L' :
        pnts = [
            [3.92954993032, -0.14886002252, -0.980586643082],
            [0.402864523003, 1.1522458907, 0.12],
            [-3.54213902288, 1.38970808269, 0.12],
            [-3.48524646709, 0.179194762798, 0.12],
            [-3.50773483151, -0.765705532482, 0.12],
            [0.232474699744, -0.604633312585, 0.12],
            [3.39628496412, -2.15907528287, -0.980586643082],
            [3.76219616424, -0.990547743698, -0.980586643082]
        ]
        if str(ctrl_obj) == 'EyeMove_L':
            for i in range(len(pnts)):
                pnts[i] = (-1.0*pnts[i][0], pnts[i][1], pnts[i][2])             
    elif str(ctrl_obj) in ['EyelidSet_UP_R', 'EyelidSet_UP_L', 'EyelidSet_DW_R', 'EyelidSet_DW_L'] :
        color='yellow'
        pnts = [
            [1.00684146754, -0.371223048868, 0.847179554632],
            [-8.00990373051e-16, 0.0360060035748, 0.847179554632],
            [-1.00684146754, -0.371223048868, 0.847179554632],
            [-1.42388885856, -0.451499069608, 0.847179554632],
            [-1.00684146754, -0.531775090347, 0.847179554632],
            [-1.0308103405e-15, -0.191048870952, 0.847179554632],
            [1.00684146754, -0.531775090347, 0.847179554632],
            [1.42388885856, -0.451499069608, 0.847179554632]
        ]
    if len(pnts) == 0:
        #pm.warning("No shape data!!!!")
        return(None)
    else:
        for i in range(8):
            cv = str(ctrl_obj)+'.cv[{}]'.format(str(i))
            pm.xform(cv, os=True, t=pnts[i])
        if color is not None:
            tools.setColorIndex(ctrl_obj, color=color)
        return(ctrl_obj)

def createCtrlShape(name='ctrl', shape='tri', scale=1.0, color=None, part='up', offset=(0,0,0)):
    pnt = []
    if shape == 'tri':
        pnt = [(0,1,0),(-1,-0.72,0),(1,-0.72,0),(0,1,0)]

        for i in range(len(pnt)):
            pnt[i] = (scale*pnt[i][0], scale*pnt[i][1], scale*pnt[i][2])
        if part in ['down', 'dw']:
            for i in range(len(pnt)):
                pnt[i] = (pnt[i][0], -1.0*pnt[i][1], pnt[i][2])
        for i in range(len(pnt)):
            pnt[i] = (pnt[i][0]+offset[0], pnt[i][1]+offset[1], pnt[i][2]+offset[2])

        ctrl_obj = pm.curve(name=name, d=1, p=pnt,k=(0,1,2,3))

    if shape == 'roundSquare':
        cv_pos_list = [
                    [1.05530223577, 4.7719865081e-17, -1.05530223577],
                    [5.96815388289e-17, 5.96815388289e-17, -0.974673495581],
                    [-1.05530223577, 4.7719865081e-17, -1.05530223577],
                    [-0.974673495581, 1.23718828662e-34, -1.03977052496e-17],
                    [-1.05530223577, -4.7719865081e-17, 1.05530223577],
                    [-9.76337106621e-17, -5.96815388289e-17, 0.974673495581],
                    [1.05530223577, -4.7719865081e-17, 1.05530223577],
                    [0.974673495581, -1.11089330611e-32, 1.73045421333e-16]
                    ]        
        ctrl_obj = pm.circle(name=name,nr=(0,1,0), r=1)[0]
        for i,pos in enumerate(cv_pos_list):
            pm.xform(ctrl_obj+'.cv[{}]'.format(i), t=[scale*pos[0],scale*pos[1],scale*pos[2]])
        pm.delete(ctrl_obj, ch=True)

    if shape == 'philtrumSet':
        cv_pos_list = [
                    [1.18327218735, 0.349045959576, 0.0],
                    [-2.98886672524e-16, 0.349334151618, 0.0],
                    [-1.18327218735, 0.349045959576, 0.0],
                    [-1.29740190434, 0.349608908625, 0.0],
                    [-1.46122769282, 0.3499024919, 0.0],
                    [-2.13370090077, 0.332318197035, -0.466428681621],
                    [-2.16156238308, 0.172020556854, -0.466428681621],
                    [-2.17459815928, 1.27386843596e-16, -0.466428681621],
                    [-2.16156238308, -0.172020556854, -0.466428681621],
                    [-2.18177197786, -0.332318197035, -0.466428681621],
                    [-1.46122769282, -0.360918125185, 0.0],
                    [-1.29740190434, -0.360721049551, 0.0],
                    [-1.18327218735, -0.36053202832, 0.0],
                    [-5.46752205737e-16, -0.360725484945, 0.0],
                    [1.18327218735, -0.36053202832, 0.0],
                    [1.29740190434, -0.360721049551, 0.0],
                    [1.46122769282, -0.360918125185, 0.0],
                    [2.18177197786, -0.332318197035, -0.466428681621],
                    [2.16156238308, -0.172020556854, -0.466428681621],
                    [2.17459815928, -5.73401315775e-16, -0.466428681621],
                    [2.16156238308, 0.172020556854, -0.466428681621],
                    [2.13370090077, 0.332318197035, -0.466428681621],
                    [1.46122769282, 0.3499024919, 0.0],
                    [1.29740190434, 0.349608908625, 0.0]
                    ]
        ctrl_obj = pm.circle(name=name,nr=(0,1,0), r=1, s=24)[0]
        for i,pos in enumerate(cv_pos_list):
            pm.xform(ctrl_obj+'.cv[{}]'.format(i), t=[scale*pos[0]+offset[0],scale*pos[1]+offset[1],scale*pos[2]+offset[2]])
        pm.delete(ctrl_obj, ch=True)
    if color is not None:
        tools.setColorIndex(ctrl_obj, color=color)    
    return(ctrl_obj)

def createHalfMoonShape(name='ctrl', scale=1.0, color="yellow", part='up'):
    cv_pos_list = [
                [0.63706171545, 0.685228795382, 0.778825108012],
                [5.5166745069e-17, 0.923980999927, 0.778825108012],
                [-0.63706171545, 0.685228795382, 0.778825108012],
                [-0.900941318057, 0.124973560641, 0.778825108012],
                [-0.63706171545, 0.0989589726359, 0.778825108012],
                [-9.02479080116e-17, 0.0810053816443, 0.778825108012],
                [0.63706171545, 0.0989589726359, 0.778825108012],
                [0.900941318057, 0.124973560641, 0.778825108012]
                ]
    if part.lower() in ['down','dw'] :
        for i in range(len(cv_pos_list)):
            cv_pos_list[i] = (cv_pos_list[i][0], -1.0*cv_pos_list[i][1], cv_pos_list[i][2])    
    c0 = pm.circle(name=name,nr=(0,1,0), r=1)[0]
    for i,pos in enumerate(cv_pos_list):
        pm.xform(c0+'.cv[{}]'.format(i), t=[scale*pos[0],scale*pos[1],scale*pos[2]])
    pm.delete(c0, ch=True)
    tools.setColorIndex(c0, color)

    return(c0)

def makeLipSetCtrlShape(name='ctrl', scale=1.0, color="yellow", part='down'):
    #scale=scale/8.0
    cv_pos_list = [
                [0.32765666931, -0.00373457176307, 0.237260906854],
                [0.0, -0.0150164119214, 0.237260906854],
                [-0.32765666931, -0.00373457176307, 0.237260906854],
                [-0.512369097806, -0.00687171516075, 0.237260906854],
                [-0.318346170289, -0.148182141566, 0.237260906854],
                [0.0, -0.0519588781562, 0.237260906854],
                [0.318346170289, -0.148182141566, 0.237260906854],
                [0.512369097806, -0.00687171516075, 0.237260906854]]

    if part.lower() == 'up':
        for i in range(len(cv_pos_list)):
            cv_pos_list[i] = (cv_pos_list[i][0], -1.0*cv_pos_list[i][1], cv_pos_list[i][2])

    c0 = pm.circle(name=name,nr=(0,1,0), r=1)[0]
    for i,pos in enumerate(cv_pos_list):
        pm.xform(c0+'.cv[{}]'.format(i), t=[scale*pos[0],scale*pos[1],scale*pos[2]])
    pm.delete(c0, ch=True)
    tools.setColorIndex(c0, color)

    return(c0)