# 标准库
import time
import json
import network
import espnow
from machine import Pin, ADC, Timer

# 本地库
import gamepad
import lcd

time.sleep(1)  # 防止点停止按钮后马上再启动导致 Thonny 连接不上

# 初始化 wifi
sta = network.WLAN(network.STA_IF)  # 或者使用 network.AP_IF
sta.active(True)
sta.disconnect()  # 对于 ESP8266

# 初始化 espnow
now = espnow.ESPNow()
now.active(True)
peer = b"\xff\xff\xff\xff\xff\xff"  # 使用广播地址
now.add_peer(peer)

# 构建手柄对象
gamepad = gamepad.Gamepad()

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


def data_to_json(data):
    data_dict = {
        "ID": data[0],
        "LX": data[1],
        "LY": data[2],
        "RX": data[3],
        "RY": data[4],
        "XABY/Pad": data[5],
        "LS/RS/Start/Back": data[6],
        "mode": data[7],
    }

    return json.dumps(data_dict)


def main(tim_callback):

    data = gamepad.read()
    lcd.show_gamepad(data)  # 在lcd显示数据

    # data_json = data_to_json(data)  # 将数据转换为 JSON 字符串并发送

    data_json = json.dumps(data)  # 将列表直接转换为 JSON 字符串

    now.send(peer, data_json)

    print(f"发送数据: {data_json}")

    diff = time_diff()
    print(f"延迟us: {diff}, 频率Hz: {1_000_000 / diff}")


# 开启定时器
tim = Timer(1)

@debounce(100_000_000)
def stop_btn_callback(pin):
    if pin.value() == 0:
        tim.deinit()
        print("停止定时器")  # 不然Thonny无法停止程序


stop_btn = Pin(0, Pin.IN, Pin.PULL_UP)
stop_btn.irq(stop_btn_callback, Pin.IRQ_FALLING)

tim.init(period=100, mode=Timer.PERIODIC, callback=main)
