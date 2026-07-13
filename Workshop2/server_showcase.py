import grpc
from concurrent import futures
import time

import showcase_pb2
import showcase_pb2_grpc

class EchoServicer(showcase_pb2_grpc.EchoServiceServicer):

    # 1. Unary: ทำงานปกติ รับ-ตอบ ทันที
    def UnaryEcho(self, request, context):
        return showcase_pb2.EchoResponse(message=f"Server ได้รับ: {request.message}")

    # 2. Server Streaming: ส่งข้อมูลกลับไปหลายๆ ชิ้น
    def ServerStreamingEcho(self, request, context):
        print(f"Server Streaming: ได้รับ '{request.message}' จะทยอยส่งกลับ 3 ชิ้น")
        for i in range(1, 4):
            time.sleep(0.5) # จำลองการใช้เวลาประมวลผล
            # ใช้ yield เพื่อทยอยส่งข้อมูลทีละชิ้น
            yield showcase_pb2.EchoResponse(message=f"ชิ้นที่ {i} สำหรับ {request.message}")

    # 3. Client Streaming: รอรับข้อมูลหลายๆ ชิ้นจนจบ แล้วตอบรวบยอด
    def ClientStreamingEcho(self, request_iterator, context):
        messages = []
        # request_iterator เป็น iterable ที่รับข้อมูลจาก Client เรื่อยๆ
        for request in request_iterator:
            messages.append(request.message)
            print(f"Client Streaming: ทยอยได้รับ '{request.message}'")
            
        summary = " และ ".join(messages)
        # ส่ง return รวบยอดครั้งเดียว
        return showcase_pb2.EchoResponse(message=f"Server ได้รับทั้งหมดคือ: {summary}")

    # 4. Bidirectional Streaming: รับข้อมูลมาแล้วส่งกลับทันที ทำงานขนานกันไป
    def BidirectionalStreamingEcho(self, request_iterator, context):
        for request in request_iterator:
            print(f"Bidi Streaming: ได้รับ '{request.message}' -> กำลังส่งกลับ")
            # รับมาปุ๊บ ส่งกลับปั๊บ ทันที
            yield showcase_pb2.EchoResponse(message=f"สะท้อนกลับ: {request.message}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showcase_pb2_grpc.add_EchoServiceServicer_to_server(EchoServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("เซิร์ฟเวอร์เปิดแล้วบนพอร์ต 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()