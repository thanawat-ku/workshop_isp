const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const protobuf = require('protobufjs');
const path = require('path');

const PROTO_PATH = path.join(__dirname, 'telemetry.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true });
const iotTelemetry = grpc.loadPackageDefinition(packageDefinition).iot_telemetry;

const root = protobuf.loadSync(PROTO_PATH);
const ResetRequestType = root.lookupType('iot_telemetry.ResetRequest');

// เชื่อมตรงเข้าเซิร์ฟเวอร์หลักที่พอร์ต 50051
const client = new iotTelemetry.DeviceService('localhost:50051', grpc.credentials.createInsecure());

console.log("🤖 [Mock Pico] กำลังเปิดช่องสตรีมมิงสองทิศทางตรงหา Server...");
const stream = client.streamTelemetry();

// 🌟 1. ขาลง: รอรับคำสั่ง RemoteReset สวนทางมาจาก Server
stream.on('data', (resetRequest) => {
    // คำนวณขนาดไบนารีข้อมูลที่วิ่งข้ามเน็ตเวิร์กมาจริง
    const encodedSize = ResetRequestType.encode(resetRequest).finish().length;
    
    console.log(`\n🚨 [Mock Pico <- Wire] ได้รับคำสั่ง REMOTE RESET! (ขนาดก้อนข้อมูล: ${encodedSize} bytes)`);
    console.log(`   -> เหตุผลจากระบบ: "${resetRequest.reason}"`);
    console.log(`🔄 [Mock Pico] กำลัง Reboot อุปกรณ์จำลองใน 3 วินาที...`);
    
    setTimeout(() => {
        console.log("💥 [Reboot] จำลองการตัดไฟและเริ่มระบบใหม่สำเร็จ!");
        process.exit(0); // ปิดโปรเซสตัวเองเสมือนโดนสั่งบูตเครื่องใหม่
    }, 3000);
});

stream.on('error', (err) => { console.error("❌ ท่อสตรีมขัดข้อง:", err.message); });
stream.on('end', () => { console.log("🔌 เซิร์ฟเวอร์ปิดท่อการเชื่อมต่อ"); });

// 🌟 2. ขาขึ้น: วนลูปส่งข้อมูล Telemetry จำลองไปหา Server ทุกๆ 5 วินาที
const deviceId = "PicoW-Sensor01";
setInterval(() => {
    const telemetryPacket = {
        device_id: deviceId,
        voltage: +(3.2 + Math.random() * 0.1).toFixed(2), // จำลองแรงดันไฟฟ้าสุ่ม 3.2 - 3.3V
        timestamp: Date.now()
    };

    console.log(`📤 [Mock Pico -> Server] กำลังสตรีมข้อมูลแรงดัน: ${telemetryPacket.voltage}V`);
    stream.write(telemetryPacket); // ดันข้อมูลลงสตรีม
}, 5000);