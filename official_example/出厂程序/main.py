'''
实验名称：pyController遥控手柄-出厂例程
版本：v1.0
日期：2022.4
作者：01Studio
'''

#导入相关模块
import game,tftlcd,controller,time,os
import ble_simple_central,test
from machine import Timer

#定义颜色RGB值
WHITE = (255,255,255)
BLACK = (0,0,0)

#LCD初始化
l = tftlcd.LCD15()

#手柄按键初始化
gamepad = controller.CONTROLLER()

#NES游戏
nes = game.NES()

#显示图片
l.Picture(0, 0, 'picture/GAME.jpg')

time_node = 0

#获取手柄按键数据
def key(num):
    
    return gamepad.read()[num]

#定时器
def fun(tim):

    global count,time_node
    time_node = 1

#开启定时器1
tim = Timer(1)
tim.init(period=20, mode=Timer.PERIODIC,callback=fun)

item = 0

#NES游戏选择
def game_select():
    
    select = 0 #游戏选择 
    games = os.listdir('/nes') #获取所有游戏信息，最多5个;
    print(games)
    
    #清屏，白色
    l.fill((255,255,255))
    
    #线框
    for i in range(4):
        
        l.drawRect(0, 48*(i+1), 239, 2, BLACK, border=1, fillcolor=BLACK)
    
    #游戏列表显示,最多显示5个
    #for i in range(len(games) if len(games)<6 else 5):
    for i in range(min(len(games),5)):
        
        l.printStr(games[i],2,6+i*49,color=(0,0,0),size=3)
    
    #显示箭头
    l.Picture(219, 9+select*49, 'picture/arrow.jpg')
    
    while True:
        
        if key(5) == 0 : #上键
            
            l.Picture(219, 9+select*49, 'picture/arrow_none.jpg')
            select = select - 1            
            if select < 0:
                select =0
            l.Picture(219, 9+select*49, 'picture/arrow.jpg')

        if key(5) == 4 : #下键
            l.Picture(219, 9+select*49, 'picture/arrow_none.jpg')
            select = select + 1            
            if select>min(len(games)-1,4):                
                select = min(len(games)-1,4)
            l.Picture(219, 9+select*49, 'picture/arrow.jpg')
        
        if key(6) == 32: #start键
            
            nes.start('/nes/'+games[select])
        
        time.sleep_ms(100)

#菜单选择
while True:
    
    if time_node == 1 :
        
        if item == 0: #nes游戏
        
            if key(6) == 32: #A键
                game_select()
                
            if key(5) == 2: #右键
                l.Picture(0, 0, 'picture/pyCar.jpg')
                item = item+1
                
                #防止连按出错
                if item > 3:
                    item = 3

        if item == 1: #pyCar
        
            if key(6) == 32: #start键
                
                while True:
                    
                    ble_simple_central.ble_connect('pyCar')
            
            if key(5) == 6: #左键
                l.Picture(0, 0, 'picture/GAME.jpg')                
                item = item - 1

            if key(5) == 2: #右键
                l.Picture(0, 0, 'picture/pyDrone.jpg')
                item = item+1

        if item == 2: #pyDrone
        
            if key(6) == 32: #start键
                
                while True:
                    
                    ble_simple_central.ble_connect('pyDrone')
            
            if key(5) == 6: #左键
                l.Picture(0, 0, 'picture/pyCar.jpg')                
                item = item - 1

            if key(5) == 2: #右键
                l.Picture(0, 0, 'picture/TEST.jpg')
                item = item+1
                
        if item == 3: #Factory Test
        
            if key(6) == 32: #start键
                #test.init(l)
                test.factory_test(l,gamepad)
            
            if key(5) == 6: #左键
                l.Picture(0, 0, 'picture/pyDrone.jpg')                
                item = item - 1

                #防止连按出错
                if item < 0:
                    item=0
                    
        time_node = 0