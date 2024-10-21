#请输入你的答案
import cv2
import numpy as np
import math

def process_img(original_img):
    resized_img = cv2.resize(original_img, (640, 480)) 
    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)  
    _, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)  
    cv2.imshow('Resized Image', resized_img) 
    cv2.imshow('Binary Image', binary_img)  
    return resized_img, binary_img 

def adjust(rect):
    c, (w, h), angle = rect
    if w > h:
        w, h = h, w
        angle = (angle + 90) % 360
        angle = angle - 360 if angle > 180 else angle - 180 if angle > 90 else angle
    return c, (w, h), angle

def find_light(resized_img, binary_img):
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for contour in contours:
        if len(contour) >= 5:
            rect = cv2.minAreaRect(contour)
            area = cv2.contourArea(contour)
            if area < 50:
                continue
            rect = adjust(rect)
            if -35 < rect[2] < 35:
                box = cv2.boxPoints(rect)
                box = np.int64(box)
                rects.append(rect)
                cv2.drawContours(resized_img, [box], 0, (0, 255, 0), 2)
    cv2.imshow('Detected Rotated Rectangles', resized_img)
    return resized_img, rects

def is_close(rect1, rect2, light_angle_tol, line_angle_tol, height_tol, width_tol, cy_tol):
    (cx1, cy1), (w1, h1), angle1 = rect1
    (cx2, cy2), (w2, h2), angle2 = rect2
    distance = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)
    if distance > 20:
        angle_diff = min(abs(angle1 - angle2), 360 - abs(angle1 - angle2))
        if angle_diff <= light_angle_tol:
            if abs(h1 - h2) <= height_tol and abs(w1 - w2) <= width_tol:
                line_angle = math.degrees(math.atan2(cy2 - cy1, cx2 - cx1))
                if line_angle > 90:
                    line_angle -= 180
                elif line_angle < -90:
                    line_angle += 180
                if (abs(line_angle - angle1) <= line_angle_tol or abs(line_angle - angle2) <= line_angle_tol or abs(cy1 - cy2) < cy_tol):
                    return True
    return False

def is_armor(img, lights, light_angle_tol=5, line_angle_tol=7, height_tol=10, width_tol=10, cy_tol=5):
    lights_matched = []
    processed_indices = set()
    lights_count = len(lights)
    for i in range(lights_count):
        if i in processed_indices:
            continue
        light1 = lights[i]
        close_lights = [j for j in range(lights_count) if j != i and is_close(light1, lights[j], light_angle_tol, line_angle_tol, height_tol, width_tol, cy_tol)]
        if close_lights:
            group = [light1] + [lights[j] for j in close_lights]
            lights_matched.append(group)
            processed_indices.update([i] + close_lights)
    armors = []
    for light_matched in lights_matched:
        if light_matched:
            points = np.concatenate([cv2.boxPoints(light) for light in light_matched])
            armor_raw = cv2.minAreaRect(points)
            if 200 <= armor_raw[1][0] * armor_raw[1][1] <= 11000:
            # if True:
                armor_flit = adjust(armor_raw)
                if 1 <= armor_flit[1][1] / armor_flit[1][0] <= 3.5:
                    armors.append(adjust(armor_flit))
    armors_center = []
    for armor in armors:
        center, (width, height), angle = armor
        max_size = max(width, height)
        box = cv2.boxPoints(((center[0], center[1]), (max_size, max_size), angle)).astype(int)
        cv2.drawContours(img, [box], 0, (255, 0, 255), 2)
        cv2.circle(img, (int(center[0]), int(center[1])), 5, (255, 0, 255), -1)
        (center_x, center_y) = map(int, armor[0])
        cv2.putText(img, f"({center_x}, {center_y})", (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 255, 255), 1)  # 在图像上标记坐标
        armor_center = (center_x, center_y)
        armors_center.append(armor_center)
        cv2.imshow("armor", img)
    return armors_center

def detector(img_raw):
    resized_img, binary_img = process_img(img_raw)
    drawn_img, rects = find_light(resized_img, binary_img)
    armors_center = is_armor(drawn_img, rects)
    return armors_center

if __name__ == "__main__" :
    
    img_raw = cv2.imread("D:\IT\esp_gamepad\\test\image.png")
    armors_center = detector(img_raw)
    print(armors_center)
    cv2.waitKey(0)
    cv2.destroyAllWindows()