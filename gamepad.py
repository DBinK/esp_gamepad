from machine import Pin, ADC
import time

def debounce(delay_ns):
    """装饰器: 防止函数在指定时间内被重复调用"""
    def decorator(func):
        last_call_time = 0
        result = None

        def wrapper(*args, **kwargs):
            nonlocal last_call_time, result
            current_time = time.time_ns()
            if current_time - last_call_time > delay_ns:
                last_call_time = current_time
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator

def time_diff(last_time=[None]):
    """计算两次调用之间的时间差，单位为微秒。"""
    current_time = time.ticks_us()  # 获取当前时间（单位：微秒）

    if last_time[0] is None:  # 如果是第一次调用，更新last_time
        last_time[0] = current_time
        return 0.000_001  # 防止除零错误

    else:  # 计算时间差
        diff = time.ticks_diff(current_time, last_time[0])  # 计算时间差
        last_time[0] = current_time  # 更新上次调用时间
        return diff  # 返回时间差us

def limit_value(value, min_value=-3000, max_value=3000):
    """限制输入的值在给定的范围内。"""
    return min(max(value, min_value), max_value)
    
def map_value(self, value, original_block, target_block):
    """将给定的值映射到给定的目标范围。"""
    original_min, original_max = original_block
    target_min, target_max = target_block
    
    # 计算映射值
    mapped_value = target_min + (value - original_min) * (target_max - target_min) / (original_max - original_min)
    
    return mapped_value



class Button:
    def __init__(self, pin, callback):

        self.pin = pin
        self.callback = callback

        self.KEY = Pin(self.pin, Pin.IN, Pin.PULL_UP)
        self.KEY.irq(self.callback, Pin.IRQ_FALLING | Pin.IRQ_RISING)

    def read(self):
        return self.KEY.value()


class Joystick:
    def __init__(self, x_pin, y_pin):
        self.x_pin = x_pin
        self.y_pin = y_pin
        self.x_axis = ADC(Pin(self.x_pin))
        self.y_axis = ADC(Pin(self.y_pin))
        # self.x_axis.atten(ADC.ATTN_11DB)  # 按需开启衰减器，测量量程增大到3.3V
        # self.y_axis.atten(ADC.ATTN_11DB)

    def read_raw(self):
        x_value = self.x_axis.read()
        y_value = self.y_axis.read()
        return x_value, y_value
    
    def read(self) -> tuple: # int8
        x_value, y_value = self.read_raw()
        x_value = int(map_value(self, x_value, (0, 4095), (0, 255)))
        y_value = int(map_value(self, y_value, (0, 4095), (0, 255)))
        return x_value, y_value


class Gamepad:
    def __init__(self, debug=False):
        self.debug = debug
        self.init_inputs()
        # id, lx, ly, rx, ry, abxy & dpad, ls & rs & start & back, mode
        self.data = [1, 0,0,0,0, 0,0, 6] 

    def set_bit(self, num, bit_position, value):
        """
        设置指定位置的位为1或0
        @param num: 要修改的原始数字
        @param bit_position: 要设置的位的位置（从0开始计数）
        @param value: 要设置的值（0或1）
        @return: 修改后的数字
        """
        if value == 0: 
            return num | (1 << bit_position)  
        elif value == 1: 
            return num & ~(1 << bit_position) 
        
    def init_inputs(self):
        """初始化输入设备，包括按键和摇杆。"""
        self.up = Button(10, self.up_callback)
        self.down = Button(11, self.down_callback)
        self.left = Button(12, self.left_callback)
        self.right = Button(13, self.right_callback)
        
        self.a = Button(16, self.a_callback)
        self.b = Button(21, self.b_callback)
        self.x = Button(14, self.x_callback)
        self.y = Button(15, self.y_callback)
        self.l1 = Button(6, self.l1_callback)
        self.r1 = Button(9, self.r1_callback)

        self.start = Button(0, self.start_callback)
        self.back = Button(1, self.select_callback)

        self.ls = Joystick(4, 5)
        self.rs = Joystick(7, 8)

        self.DIRECTION_MAP = {# 定义方向键映射
            (0, 1, 1, 1): 0,  # 上
            (0, 0, 1, 1): 1,  # 上&右
            (1, 0, 1, 1): 2,  # 右
            (1, 0, 0, 1): 3,  # 右&下
            (1, 1, 0, 1): 4,  # 下
            (1, 1, 0, 0): 5,  # 下&左
            (1, 1, 1, 0): 6,  # 左
            (0, 1, 1, 0): 7,  # 左&上
            (1, 1, 1, 1): 8,  # 无
        }

    # dpad 方向键
    # @debounce(100_000)
    def update_direction(self, state):
        # 获取当前按键状态
        up = self.up.read()
        down = self.down.read()
        left = self.left.read()
        right = self.right.read()

        # 根据按键状态更新 data[5]
        key_state = (up, right, down, left)

        print(key_state, state)

        if state == 1:    # 抬起
            self.data[5] = self.data[5] & ~(self.DIRECTION_MAP[key_state])
        elif state == 0:  # 按下
            self.data[5] = self.data[5] | self.DIRECTION_MAP[key_state]


    # 方向键回调函数
    @debounce(50_000_000)
    def up_callback(self, KEY):
        self.update_direction(KEY.value()) 

    @debounce(50_000_000)
    def down_callback(self, KEY):
        self.update_direction(KEY.value())

    @debounce(50_000_000)
    def left_callback(self, KEY):
        self.update_direction(KEY.value())

    @debounce(50_000_000)
    def right_callback(self, KEY):
        self.update_direction(KEY.value())

    # XABY 按键回调函数
    @debounce(50_000_000)
    def a_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 6, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    @debounce(50_000_000)
    def b_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 5, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    @debounce(50_000_000)
    def x_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 7, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    @debounce(50_000_000)
    def y_callback(self, KEY):
        self.data[5] = self.set_bit(self.data[5], 4, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    # L R & Start & Back 回调函数
    @debounce(50_000_000)
    def l1_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 7, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    @debounce(50_000_000)
    def r1_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 6, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    @debounce(50_000_000)
    def start_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 5, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")

    @debounce(50_000_000)
    def select_callback(self, KEY):
        self.data[6] = self.set_bit(self.data[6], 4, KEY.value())
        if self.debug:
            print(f"key {KEY} pressed")
    
    # 读取数据
    def read(self) -> list:
        self.data[1], self.data[2] = self.ls.read()
        self.data[3], self.data[4] = self.rs.read()

        # abxy_release = self.a.read() and self.b.read() and self.x.read() and self.y.read()
        # dpad_release = self.up.read() and self.down.read() and self.left.read() and self.right.read()

        # if abxy_release and dpad_release:
        #     self.data[5] = self.data[5] | 8

        return self.data

    def test(self):
        print("Gamepad running...")
        while True:
            time.sleep(0.1)
            print(f"ls: {self.ls.read()}, rs: {self.rs.read()}")
            print(f"ls: {self.ls.read_raw()}, rs: {self.rs.read_raw()}")


if __name__ == "__main__":
    gamepad = Gamepad()
    while True: 
        data = gamepad.read()
        print(f"raw: {data}, xaby: {bin(data[5])}, other: {bin(data[6])}, dpad: []" )
        time.sleep(0.1)
    
