const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

const PROTO_PATH = path.join(__dirname, 'telemetry.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true });
const iotTelemetry = grpc.loadPackageDefinition(packageDefinition).iot_telemetry;

function main() {
    // เชื่อมต่อไปที่ Server หลักโดยตรง
    const client = new iotTelemetry.DeviceService('localhost:50051', grpc.credentials.createInsecure());

    console.log(`🖥️ [Pi 5 Monitor] ส่งคำสั่ง RemoteReset ไปยังเครื่อง Server หลัก...`);

    client.resetDevice({
        device_id: "PicoW-Sensor01",
        reason: "Monitor UI triggered automated factory reset"
    }, (err, response) => {
        if (err) return console.error("❌ เกิดข้อผิดพลาด:", err);
        
        if (response.success) {
            console.log("✅ [ผลลัพธ์] คำสั่งส่งผ่านเรียบร้อย อุปกรณ์เป้าหมายกำลังรีบูต");
        } else {
            console.log("❌ [ผลลัพธ์] รีเซ็ตไม่สำเร็จ (อุปกรณ์ดังกล่าวอาจไม่ได้ออนไลน์อยู่)");
        }
    });
}
main();