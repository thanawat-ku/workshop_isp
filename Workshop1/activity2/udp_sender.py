import socket
import random
import time
from datetime import datetime

# ==========================================
# 1. ตั้งค่าคอนฟิกูเรชัน (Configuration)
# ==========================================
# สำหรับทดสอบในเครื่องตัวเองให้ใช้ '127.0.0.1' (Localhost)
# ถ้าจะส่งข้ามเครื่อง ให้เปลี่ยนเป็น IP ของเครื่อง Server จริง
SERVER_IP = "127.0.0.1" 
SERVER_PORT = 5005

# ==========================================
# 2. สร้าง UDP Socket
# ==========================================
# socket.AF_INET  = ตัวแทนของ IPv4
# socket.SOCK_DGRAM = ตัวแทนของ UDP (Datagram)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("=========================================")
print("   UDP Sender (Sensor Node Simulation)   ")
print(f"   Sending to target -> {SERVER_IP}:{SERVER_PORT}")
print("=========================================\n")

try:
    # 3. ลูปส่งข้อมูลทุกๆ 1 วินาที
    while True:
        # จำลองการอ่านค่าพารามิเตอร์ (สุ่มตัวเลข 1-100)
        sensor_value = random.randint(1, 100)
        
        # ดึงเวลาปัจจุบันมาใส่เพื่อให้ข้อมูลดูสมจริง (มีประโยชน์ตอนทำ Data Logging)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # จัดรูปแบบข้อความ (Payload) ที่จะส่ง
        payload = f"Time: {current_time} | Meter_PM2230_Value: {sensor_value}"
        
        # สั่งส่งข้อมูลผ่าน UDP 
        # **ข้อควรระวัง**: ข้อมูลที่ส่งผ่าน Socket ต้องแปลงเป็น Bytes เสมอ จึงต้องใช้ .encode()
        client_socket.sendto(payload.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        
        print(f"[SUCCESS] Sent data: {payload}")
        
        # หน่วงเวลา 1 วินาทีตามโจทย์
        time.sleep(1)

except KeyboardInterrupt:
    # เผื่อกรณีนิสิตกด Ctrl+C เพื่อหยุดโปรแกรม
    print("\n[INFO] Stopping UDP Sender...")
    
finally:
    # 4. ปิด Socket เมื่อเลิกใช้งาน (Good Practice)
    client_socket.close()
    print("[INFO] Socket closed successfully.")
