import grpc
from concurrent import futures
import time
import queue

import telemetry_pb2
import telemetry_pb2_grpc

# 🌟 สารบบเก็บ Queue สำหรับส่งคอมมานด์ลงท่อสตรีม [device_id -> queue.Queue]
active_queues = {}

class DeviceServiceServicer(telemetry_pb2_grpc.DeviceServiceServicer):

    def StreamTelemetry(self, request_iterator, context):
        device_id = None
        print("\n📥 [Main Server] บอร์ดจำลองต่อสายสตรีมตรงเข้ามาหาเซิร์ฟเวอร์แล้ว...")

        # เปิดคิวเฉพาะสำหรับบอร์ดนี้เพื่อรอรับคอมมานด์ขาลง
        q = queue.Queue()

        # ลอจิกย่อย: คอยดึงคำสั่งจาก Queue พ่นสวนกลับลงไปหาบอร์ดจำลอง
        def command_generator():
            while context.is_active():
                try:
                    # รอรับคอมมานด์รีเซ็ตจาก Queue (Timeout เพื่อไม่ให้บล็อกเธรดค้าง)
                    cmd = q.get(timeout=1.0)
                    print(f"📤 [Main Server -> Device] กำลังดันคำสั่ง RemoteReset ลงท่อสตรีมย้อนกลับ...")
                    yield cmd
                except queue.Empty:
                    continue

        # เริ่มอ่านสตรีมข้อมูลขาขึ้นที่บอร์ดส่งมา
        for telemetry in request_iterator:
            if not device_id:
                device_id = telemetry.device_id
                active_queues[device_id] = q
                print(f"📌 [Main Server Registry] ลงทะเบียนท่อขาลงสำเร็จสำหรับ: {device_id}")

            # 🌟 วัดขนาดข้อมูลจริงทางเน็ตเวิร์ก (ก่อนแกะเป็นอ็อบเจกต์)
            wire_size = telemetry.ByteSize()
            print(f"   💾 [Save] Device: {telemetry.device_id} | Volt: {telemetry.voltage:.2f}V | Size: {wire_size} bytes")

        # เคลียร์ข้อมูลออกจากสารบบเมื่อบอร์ดวางสาย
        if device_id in active_queues:
            del active_queues[device_id]
            print(f"❌ [Main Server Registry] บอร์ดจำลอง {device_id} ออฟไลน์แล้ว")

        # ส่งฟังก์ชัน Generator กลับไปให้ gRPC จัดการสตรีมขาลง
        return command_generator()

    def ResetDevice(self, request, context):
        device_id = request.device_id
        reason = request.reason
        print(f"\n🚨 [Main Server <- Monitor] ได้รับคำสั่งสั่งรีเซ็ตไอดี: {device_id}")

        # ค้นหาคิวส่งคำสั่งที่ผูกไว้กับ ID บอร์ดนี้
        target_queue = active_queues.get(device_id)

        if target_queue:
            # ดันคอมมานด์เข้าคิวเพื่อให้ท่อสตรีมดึงไปพ่นใส่บอร์ด
            reset_request = telemetry_pb2.ResetRequest(device_id=device_id, reason=reason)
            target_queue.put(reset_request)
            return telemetry_pb2.ResetResponse(success=True)
        else:
            print(f"❌ [Main Server] ไม่พบอุปกรณ์ชื่อ {device_id} ออนไลน์อยู่ในระบบ")
            return telemetry_pb2.ResetResponse(success=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetry_pb2_grpc.add_device_service_to_server(DeviceServiceServicer(), server)
    server.add_insecure_port('0.0.0.0:50051')
    print("🚀 Central Python gRPC Server (No Gateway) ออนไลน์ที่พอร์ต 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()