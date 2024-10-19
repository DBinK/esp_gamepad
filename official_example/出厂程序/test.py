#手柄测试
import tftlcd,controller,time
from machine import ADC,Pin

#LCD屏颜色值
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
BLUE = (0,0,255)

led=Pin(46,Pin.OUT) #构建led对象，输出

#初始化界面
def init(l=None):

    l.fill(WHITE) #填充白色
    l.drawCircle(60,115,15,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(60,175,15,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(30,145,15,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(90,145,15,color=BLACK,border=2,fillcolor=WHITE)

    l.drawCircle(180,20,15,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(180,80,15,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(150,50,15,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(210,50,15,color=BLACK,border=2,fillcolor=WHITE)
    
    l.drawCircle(30,85,10,color=BLACK,border=2,fillcolor=WHITE)
    l.drawCircle(210,105,10,color=BLACK,border=2,fillcolor=WHITE)
    
    l.drawRect(90, 90, 25, 15, color=BLACK, border=2, fillcolor=WHITE)
    l.drawRect(125, 90, 25, 15, color=BLACK, border=2, fillcolor=WHITE)

def factory_test(l=None,gamepad=None):
    
    init(l)
    
    #点亮指示灯
    led.value(1) #点亮LED
    
    #锂电池电压
    bat = ADC(Pin(2)) 
    
    num = 0
    while True:
        
        v = gamepad.read()
            
        l.printStr('L-X: '+str(v[1])+'  ',10,15,color=BLACK,size=2)
        l.printStr('L-Y: '+str(v[2])+'  ',10,45,color=BLACK,size=2)
        
        l.printStr('R-X: '+str(v[3])+'  ',130,120,color=BLACK,size=2)
        l.printStr('R-Y: '+str(v[4])+'  ',130,150,color=BLACK,size=2)
        
        L = v[5]%16
        if L == 0:
            l.drawCircle(60,115,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(60,115,15,color=BLACK,border=2,fillcolor=WHITE)

        if L == 4:
            l.drawCircle(60,175,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(60,175,15,color=BLACK,border=2,fillcolor=WHITE)

        if L == 6:
            l.drawCircle(30,145,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(30,145,15,color=BLACK,border=2,fillcolor=WHITE)
            
        if L == 2:
            l.drawCircle(90,145,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(90,145,15,color=BLACK,border=2,fillcolor=WHITE)
        
        
        if v[5] & 1<<4: #Y
            l.drawCircle(180,20,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(180,20,15,color=BLACK,border=2,fillcolor=WHITE)
        
        if v[5] & 1<<6: #A
            l.drawCircle(180,80,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(180,80,15,color=BLACK,border=2,fillcolor=WHITE)
            
        if v[5] & 1<<7:
            l.drawCircle(150,50,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(150,50,15,color=BLACK,border=2,fillcolor=WHITE)
        
        if v[5] & 1<<5: #B
            l.drawCircle(210,50,15,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(210,50,15,color=BLACK,border=2,fillcolor=WHITE)
        
        if v[6] & 1<<4: #back
            l.drawRect(90, 90, 25, 15, color=BLACK, border=2, fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawRect(90, 90, 25, 15, color=BLACK, border=2, fillcolor=WHITE)

        if v[6] & 1<<5: #start
            l.drawRect(125, 90, 25, 15, color=BLACK, border=2, fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawRect(125, 90, 25, 15, color=BLACK, border=2, fillcolor=WHITE)
        
        if v[6] & 1<<6: #右摇杆确认键
            l.drawCircle(210,105,10,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(210,105,10,color=BLACK,border=2,fillcolor=WHITE)

        if v[6] & 1<<7: #左摇杆确认键
            l.drawCircle(30,85,10,color=BLACK,border=2,fillcolor=BLACK)
            time.sleep_ms(200)
            l.drawCircle(30,85,10,color=BLACK,border=2,fillcolor=WHITE)
        
        num = num + 1
        if num == 50: #每秒刷新一次
            
            b=(bat.read()/4096*1-0.03)*5 #计算锂电池电压
            
            l.printStr(' Battery: '+str('%.2f'%b)+'V',0,200,color=RED,size=2)
            
            if 4 < b: #高电量
                l.Picture(188, 203, 'picture/power_3.jpg')
                
            elif  3.7 <= b <= 4: #中电量
                l.Picture(188, 203, 'picture/power_2.jpg')
                
            else : #低电量
                l.Picture(188, 203, 'picture/power_1.jpg')
                
            num=0
            
        time.sleep_ms(20) #20ms检测一次
