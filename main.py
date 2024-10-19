import json  # 导入 ujson 库，用于处理 JSON 格式
import network
import espnow
from machine import Pin, ADC, Timer
import time

# 初始化 wifi
sta = network.WLAN(network.STA_IF)  # 或者使用 network.AP_IF
sta.active(True)
sta.disconnect()  # 对于 ESP8266

# 初始化 espnow
now = espnow.ESPNow()
now.active(True)
peer = b'\xff\xff\xff\xff\xff\xff'  # 使用广播地址
now.add_peer(peer)      


led = Pin(15, Pin.OUT, value=1)
cnt = 0
blink_speed = 20
def blink_led():
    """ 闪烁LED  """
    global cnt, blink_speed
    cnt += 1
    if cnt % blink_speed == 0:
        led.value(not led.value())
        cnt = 0

def time_diff(last_time=[None]):
    """计算两次调用之间的时间差，单位为微秒。"""
    current_time = time.ticks_us()  # 获取当前时间（单位：微秒）

    if last_time[0] is None: # 如果是第一次调用，更新last_time
        last_time[0] = current_time
        return 0.000_001 # 防止除零错误
    
    else: # 计算时间差
        diff = time.ticks_diff(current_time, last_time[0])  # 计算时间差
        last_time[0] = current_time  # 更新上次调用时间
        return diff  # 返回时间差us

def main(tim_callback):
    global ls_sw
    
    if ls_sw:
        lx_raw  = 8191 - lx.read() - 3050
        ly_raw  = 8191 - ly.read() - 3080
        rx_raw  = 8191 - rx.read() - 3160
        ry_raw  = 8191 - ry.read() - 3000

        data = {
            "lx": lx_raw, "ly": ly_raw, "ls": ls_sw,
            "rx": rx_raw, "ry": ry_raw, "rs": rs_sw,
        }
    else:
        data = {
            "lx": 0, "ly": 0, "ls": ls_sw,
            "rx": 0, "ry": 0, "rs": rs_sw,
        }

    data_json = json.dumps(data)  # 将数据转换为 JSON 字符串并发送
    now.send(peer, data_json)  
    print(f"发送数据: {data_json}")

    blink_led()

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

tim.init(period=10, mode=Timer.PERIODIC, callback=main)