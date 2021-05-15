import numpy as np
import matplotlib.pyplot as plt
import cantera as ct
import win32api
import time
import math
import os
from test import combustor, residence_time

combustor = None
residence_time = None

def inject_parameters(x1, x2, x3, x4, x5):
    file1 = "‪C:\\Users\\86183\\Element_area.txt"
    file2 = "‪C:\\Users\\86183\\Element_diameter.txt"
    # 42, 43, 44, 51, 52
    f1 = open(file=file1, mode='r')
    data1 = f1.readlines()
    f1.close()
    data1[41] = str(x1) + '\n'
    data1[42] = str(x2) + '\n'
    data1[43] = str(x3) + '\n'
    data1[50] = str(x4) + '\n'
    data1[51] = str(x5) + '\n'
    f2 = open(file=file2, mode='r')
    data2 = f2.readlines()
    f2.close()
    data2[41] = str((4*x1/math.pi)**0.5) + '\n'
    data2[42] = str((4*x2/math.pi)**0.5) + '\n'
    data2[43] = str((4*x3/math.pi)**0.5) + '\n'
    data2[50] = str((4*x4/math.pi)**0.5) + '\n'
    data2[51] = str((4*x5/math.pi)**0.5) + '\n'
    f1 = open(file=file1, mode='w')
    for l in data1:
        f1.write(l)
    f1.close()
    f2 = open(file=file2, mode='w')
    for l in data2:
        f2.write(l)
    f2.close()

def mdot(t):
    global combustor
    global residence_time
    return combustor.mass / residence_time
    # return 0.1

def compute(X):

    global combustor
    global residence_time

    x1, x2, x3, x4, x5 = X
    inject_parameters(x1, x2, x3, x4, x5)

    #导入network计算
    win32api.ShellExecute(0, 'open', 'C:\\Users\\86183\\network_flow.exe', '', '', 1)
    #停止程序执行，等待network计算结果
    time.sleep(8)
    #识别result文件中某几行的数据之和
    path = os.getcwd()+ "\\result.dat"
    f=open(path,'r')
    data=f.readlines()
    f.close()

    for i in range(len(data)):
        line=data[i].split()[1]
        data[i]=float(line)

# print(data)
    result=np.sum(data[1:2]+data[2:3])
    # print(result)
    # print(result/3)

    #CRN 化学反应网络法
    # 设置反应器气体
    gas = ct.Solution('gri30.yaml')

    # 确定油气等效比、燃气温度、燃气压强
    equiv_ratio =result/3 
    gas.TP = 300.0, 101325
    gas.set_equivalence_ratio(equiv_ratio, 'CH4:1.0', 'O2:1.0, N2:3.76')
    inlet = ct.Reservoir(gas)

# 让反应器达到平衡状态
    gas.equilibrate('HP')
    combustor = ct.IdealGasReactor(gas)
    combustor.volume = 1.0

# 设置出口排放
    exhaust = ct.Reservoir(gas)

# 计算进出口质量流量

    inlet_mfc = ct.MassFlowController(inlet, combustor, mdot=mdot)

    outlet_mfc = ct.PressureController(combustor, exhaust, master=inlet_mfc, K=0.01)

    sim = ct.ReactorNet([combustor])

# 设置驻留时间，计算驻留时间逐渐减小所对应的反应器温度
    states = ct.SolutionArray(gas, extra=['tres'])

    temperatureList=[]
    while combustor.T > 500:
        sim.set_initial_time(0.0) 
        sim.advance_to_steady_state()
        # print('tres = {:.2e}; T = {:.1f}'.format(residence_time, combustor.T))
        states.append(combustor.thermo.state, tres=residence_time)
        residence_time *= 0.9  
        temperatureList.append(combustor.T)
    # print(temperatureList)

    maxT=max(temperatureList)
    return (-1)*maxT

# print(maxT)#读取反应器最大温度
    
# # 输出对应滞留时间的反应器温度图像
# f, ax1 = plt.subplots(1, 1)
# ax1.plot(states.tres, states.heat_release_rate, '.-', color='C0')
# ax2 = ax1.twinx()
# ax2.plot(states.tres[:-1], states.T[:-1], '.-', color='C1')
# ax1.set_xlabel('residence time [s]')
# ax1.set_ylabel('heat release rate [W/m$^3$]', color='C0')
# ax2.set_ylabel('temperature [K]', color='C1')
# f.tight_layout()
# plt.show()
