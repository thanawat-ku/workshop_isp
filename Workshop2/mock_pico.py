import grpc
import time
import random
import threading
import sys

import telemetry_pb2
import telemetry_pb2_grpc

def telemetry_generator(device_id):
    """ฟังก์ชันคอยสร้างข้อมูลสตรีมส่งขึ้นเซิร์ฟเวอร์ทุกๆ 5 วินาที"""
    while True:
        telemetry_packet = telemetry_pb2.TelemetryData(
            device_id=device_id,
            voltage=round(random.uniform(3.2, 3.3), 2),
            timestamp=int(time.time() * 1000)
        )
        print(f"📤 [Mock Pico -> Server] กำลังสตรีมข้อมูลแรงดัน: {telemetry_packet.voltage}V")
        yield telemetry_packet
        time.begin_sleep = time.sleep(5)

def listen_for_commands(response_stream):
    """ฟังก์ชันคอยเงี่ยหูฟังคอมมานด์ที่ไหลสวนทางกลับมาจากเซิร์ฟเวอร์"""
    try:
        for reset_request in response_stream:
            # คำนวณขนาดไบนารีข้อมูลที่ส่งข้ามเน็ตเวิร์กมาจริง
            encoded_size = reset_request.ByteSize()
            
            print(f"\n🚨 [Mock Pico <- Wire] ได้รับคำสั่ง REMOTE RESET! (ขนาดก้อนข้อมูล: {encoded_size} bytes)")
            print(f"   -> เหตุผลจากระบบ: \"{reset_request.reason}\"")
            print("🔄 [Mock Pico] กำลัง Reboot อุปกรณ์จำลองใน 3 วินาที...")
            
            time.sleep(3)
            print("💥 [Reboot] จำลองการตัดไฟและเริ่มระบบใหม่สำเร็จ!")
            sys.exit(0) # บูตระบบใหม่โดยการปิดโปรเซสตัวเอง
    except grpc.RpcError as e:
        print(f"❌ ท่อสตรีมขัดข้อง: {e.details()}")

def run():
    device_id = "PicoW-Sensor01"
    
    # เชื่อมต่อตรงไปที่เซิร์ฟเวอร์หลัก
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = telemetry_pb2_grpc.DeviceServiceStub(channel)
        print("🤖 [Mock Pico] กำลังเปิดช่องสตรีมมิงสองทิศทางตรงหา Server...")
        
        # 🌟 เปิดท่อสตรีมมิ่งสองทิศทางโดยการส่ง Generator ข้อมูลขาขึ้นไป
        response_stream = stub.StreamTelemetry(telemetry_generator(device_id))
        
        # แยก Thread ออกไปเพื่อรอรับฟังข้อมูลขาลงโดยเฉพาะ (ไม่ให้บล็อกลูปส่งข้อมูล)
        cmd_thread = threading.Thread(target=listen_for_commands, args=(response_stream,), daemon=True)
        cmd_thread.start()
        
        # ปล่อยให้โปรแกรมหลักทำงานค้างไว้ตราบใดที่ Thread ฟังคำสั่งยังทำงานอยู่
        while cmd_thread.is_alive():
            time.sleep(0.5)

if __name__ == '__main__':
    run()