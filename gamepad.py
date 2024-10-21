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
        self.KEY.irq(self.callback, Pin.IRQ_FALLING)

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
    def __init__(self):
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

    def run(self):
        print("Gamepad running...")
        while True:
            time.sleep(0.1)
            
            print(f"ls: {self.ls.read()}, rs: {self.rs.read()}")
            print(f"ls: {self.ls.read_raw()}, rs: {self.rs.read_raw()}")

    @debounce(100_000_000)
    def up_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def down_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def left_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def right_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def a_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def b_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def x_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def y_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def l1_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def r1_callback(self, KEY):
        print(f"key {KEY} pressed")

    @debounce(100_000_000)
    def start_callback(self, KEY):
        print(f"key {KEY} pressed")
    
    @debounce(100_000_000)
    def select_callback(self, KEY):
        print(f"key {KEY} pressed")
    


if __name__ == "__main__":
    gamepad = Gamepad()
    gamepad.run()
    
