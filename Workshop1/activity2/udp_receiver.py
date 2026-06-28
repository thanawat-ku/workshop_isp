import socket

# ==========================================
# 1. ตั้งค่าคอนฟิกูเรชัน (Configuration)
# ==========================================
# '0.0.0.0' หมายความว่า ให้ Server รอรับข้อมูลจากทุกๆ Network Interface ในเครื่อง 
# (ไม่ว่าจะส่งมาจาก Localhost หรือ IP วง LAN เดียวกันก็รับหมด)
LISTEN_IP = "0.0.0.0" 
LISTEN_PORT = 5005
BUFFER_SIZE = 1024 # ขนาดสูงสุดของข้อมูลที่สามารถรับได้ต่อหนึ่งครั้ง (1 KB)

# ==========================================
# 2. สร้าง UDP Socket และทำการ Bind Port
# ==========================================
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind คือการสั่งให้ระบบปฏิบัติการจอง Port 5005 ไว้ให้โปรแกรมนี้แต่เพียงผู้เดียว
server_socket.bind((LISTEN_IP, LISTEN_PORT))

print("=========================================")
print("   UDP Receiver (Server Started)         ")
print(f"   Listening on -> {LISTEN_IP}:{LISTEN_PORT}")
print("=========================================\n")

try:
    # 3. ลูปเปิดประตูรอรับข้อมูลตลอดเวลา
    while True:
        # ฟังก์ชัน .recvfrom() จะ "บล็อก" (หยุดรอ) จนกว่าจะมี UDP Packet วิ่งเข้ามา
        # เมื่อมีข้อมูลมา มันจะคืนค่ากลับมา 2 อย่างพร้อมกัน (Tuple):
        # - data: ข้อมูลดิบในรูปแบบ Bytes
        # - address: ที่อยู่ของผู้ส่ง ประกอบด้วย (IP, Port)
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        
        # แปลงข้อมูลจาก Bytes กลับมาเป็นข้อความ (String) เพื่อให้อ่านออก
        decoded_data = data.decode('utf-8')
        
        # แยกที่อยู่ผู้ส่งออกมาดู
        sender_ip = address[0]
        sender_port = address[1]
        
        # แสดงผลออกทางหน้าจอ Console
        print(f"[RECEIVE] From {sender_ip}:{sender_port} -> {decoded_data}")

except KeyboardInterrupt:
    print("\n[INFO] Shutting down UDP Server...")
    
finally:
    # 4. ปิด Socket เมื่อปิดเซิร์ฟเวอร์
    server_socket.close()
    print("[INFO] Server socket closed.")
