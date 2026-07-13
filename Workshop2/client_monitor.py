import grpc
import telemetry_pb2
import telemetry_pb2_grpc

def run():
    # เชื่อมต่อไปยังเซิร์ฟเวอร์หลักหลังบ้านโดยตรง
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = telemetry_pb2_grpc.DeviceServiceStub(channel)
        
        print("🖥️ [Pi 5 Monitor] ส่งคำสั่ง RemoteReset ไปยังเครื่อง Server หลัก...")
        
        # จัดเตรียมข้อมูล ResetRequest
        request = telemetry_pb2.ResetRequest(
            device_id="PicoW-Sensor01",
            reason="Python Monitor GUI triggered automated safety reboot"
        )
        
        # ยิงคำสั่งแบบ Unary RPC เข้าเซิร์ฟเวอร์หลักตรงๆ
        response = stub.ResetDevice(request)
        
        if response.success:
            print("✅ [ผลลัพธ์] คำสั่งส่งผ่านเรียบร้อย อุปกรณ์เป้าหมายกำลังรีบูต")
        else:
            print("❌ [ผลลัพธ์] รีเซ็ตไม่สำเร็จ (อุปกรณ์ดังกล่าวอาจไม่ได้ออนไลน์อยู่)")

if __name__ == '__main__':
    run()