const dgram = require('dgram');

// ==========================================
// 1. ตั้งค่าคอนฟิกูเรชัน (Configuration)
// ==========================================
const SERVER_IP = '127.0.0.1';
const SERVER_PORT = 5005;

// ==========================================
// 2. สร้าง UDP Socket ('udp4' หมายถึง IPv4)
// ==========================================
const client = dgram.createSocket('udp4');

console.log("=========================================");
console.log("   UDP Sender (Node.js Sensor Node)     ");
console.log(`   Sending to target -> ${SERVER_IP}:${SERVER_PORT}`);
console.log("=========================================\n");

// 3. ตั้งเวลาส่งข้อมูลทุกๆ 1 วินาที (1000 มิลลิวินาที)
const sendInterval = setInterval(() => {
    // จำลองค่าพารามิเตอร์ (สุ่มตัวเลข 1-100)
    const sensorValue = Math.floor(Math.random() * 100) + 1;
    
    // ดึงเวลาปัจจุบันมาฟอร์แมตให้อ่านง่าย
    const currentTime = new Date().toISOString().replace('T', ' ').substring(0, 19);
    
    // จัดรูปแบบข้อความ Payload
    const payload = `Time: ${currentTime} | Meter_PM2230_Value: ${sensorValue}`;

    // สั่งส่งข้อมูลผ่าน UDP
    // ข้อดีของ Node.js: ในฟังก์ชัน .send() เราสามารถโยนข้อความ String เข้าไปตรงๆ ได้เลย 
    // ตัวระบบจะทำการแปลงเป็น Buffer (Bytes) ให้เราเบื้องหลังโดยอัตโนมัติ
    client.send(payload, SERVER_PORT, SERVER_IP, (err) => {
        if (err) {
            console.error("[ERROR] Failed to send data:", err);
        } else {
            console.log(`[SUCCESS] Sent data: ${payload}`);
        }
    });

}, 1000);

// จัดการกรณีที่ผู้ใช้กด Ctrl+C เพื่อปิดโปรแกรม
process.on('SIGINT', () => {
    console.log("\n[INFO] Stopping UDP Sender...");
    clearInterval(sendInterval);
    client.close();
    process.exit();
});
