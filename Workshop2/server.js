const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const protobuf = require('protobufjs');
const path = require('path');

const PROTO_PATH = path.join(__dirname, 'telemetry.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true });
const iotTelemetry = grpc.loadPackageDefinition(packageDefinition).iot_telemetry;

const root = protobuf.loadSync(PROTO_PATH);
const TelemetryDataType = root.lookupType('iot_telemetry.TelemetryData');

// สารบบเก็บท่อเชื่อมต่อตรง [device_id -> grpc_call_stream]
const activeStreams = new Map();

function streamTelemetry(call) {
    let deviceId = null;
    console.log("\n📥 [Main Server] บอร์ดจำลองต่อสายสตรีมตรงเข้ามาหาเซิร์ฟเวอร์แล้ว...");

    call.on('data', (telemetry) => {
        // ลงทะเบียนท่อทันทีที่ข้อมูลชุดแรกมาถึง
        if (!deviceId) {
            deviceId = telemetry.device_id;
            activeStreams.set(deviceId, call);
            console.log(`📌 [Main Server Registry] ลงทะเบียนท่อขาลงสำเร็จสำหรับ: ${deviceId}`);
        }

        // 🌟 วัดขนาดข้อมูลทางเน็ตเวิร์กที่วิ่งเข้ามาในระบบ gRPC
        const encodedBuffer = TelemetryDataType.encode(telemetry).finish();
        console.log(`   💾 [Save] Device: ${telemetry.device_id} | Volt: ${telemetry.voltage.toFixed(2)}V | Size: ${encodedBuffer.length} bytes`);
    });

    const cleanup = () => {
        if (deviceId) {
            activeStreams.delete(deviceId);
            console.log(`❌ [Main Server Registry] บอร์ดจำลอง ${deviceId} ออฟไลน์แล้ว`);
        }
    };
    call.on('end', cleanup); call.on('error', cleanup);
}

function resetDevice(call, callback) {
    const { device_id, reason } = call.request;
    console.log(`\n🚨 [Main Server <- Monitor] ได้รับคำสั่งสั่งรีเซ็ตไอดี: ${device_id}`);

    const targetCallStream = activeStreams.get(device_id);

    if (targetCallStream) {
        console.log(`📤 [Main Server -> Device] พบท่อตรง! กำลังยิงคำสั่ง RemoteReset กลับลงไป...`);
        targetCallStream.write({ device_id, reason }); // สตรีมคำสั่งสวนทางกลับลงไปทันที
        callback(null, { success: true });
    } else {
        console.log(`❌ [Main Server] ไม่พบอุปกรณ์ชื่อ ${device_id} ออนไลน์อยู่ในระบบ`);
        callback(null, { success: false });
    }
}

function main() {
    const server = new grpc.Server();
    server.addService(iotTelemetry.DeviceService.service, {
        streamTelemetry: streamTelemetry,
        resetDevice: resetDevice
    });

    server.bindAsync('0.0.0.0:50051', grpc.ServerCredentials.createInsecure(), (err, port) => {
        if (err) return console.error(err);
        console.log(`🚀 Central gRPC Server (No Gateway) ออนไลน์ที่พอร์ต ${port}...`);
    });
}
main();