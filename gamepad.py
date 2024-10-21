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
        self.x_axis.atten(ADC.ATTN_11DB)  # 开启衰减器，测量量程增大到3.3V
        self.y_axis.atten(ADC.ATTN_11DB)

    def read(self):
        x_value = self.x_axis.read()
        y_value = self.y_axis.read()
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
        while True:
            time.sleep(0.1)
            print(self.ls.read())

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
    
