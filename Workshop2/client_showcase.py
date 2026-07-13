import grpc
import time

import showcase_pb2
import showcase_pb2_grpc

# ฟังก์ชันผู้ช่วยสำหรับสร้างข้อมูลสตรีม (Generator) ไปให้เซิร์ฟเวอร์
def generate_requests():
    items = ["แอปเปิล", "กล้วย", "ส้ม"]
    for item in items:
        print(f"Client กำลังส่งสตรีม: {item}")
        yield showcase_pb2.EchoRequest(message=item)
        time.sleep(0.5)

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = showcase_pb2_grpc.EchoServiceStub(channel)

        print("--- 1. Unary ---")
        response = stub.UnaryEcho(showcase_pb2.EchoRequest(message="สวัสดีจ้า"))
        print(response.message)

        print("\n--- 2. Server Streaming ---")
        # รับค่าเป็น Iterator แล้ววนลูปดึงข้อมูล
        response_iterator = stub.ServerStreamingEcho(showcase_pb2.EchoRequest(message="ขอผลไม้"))
        for response in response_iterator:
            print(f"Client ได้รับ: {response.message}")

        print("\n--- 3. Client Streaming ---")
        # โยน Generator ฟังก์ชันเข้าไปให้ Stub เลย
        response = stub.ClientStreamingEcho(generate_requests())
        print(f"Client ได้รับรวบยอด: {response.message}")

        print("\n--- 4. Bidirectional Streaming ---")
        # โยน Generator เข้าไป และรับค่ากลับมาเป็น Iterator
        response_iterator = stub.BidirectionalStreamingEcho(generate_requests())
        for response in response_iterator:
            print(f"Client ได้รับ: {response.message}")

if __name__ == '__main__':
    run()