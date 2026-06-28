const dgram = require('dgram');

// ==========================================
// 1. ตั้งค่าคอนฟิกูเรชัน (Configuration)
// ==========================================
const LISTEN_IP = '0.0.0.0';
const LISTEN_PORT = 5005;

// ==========================================
// 2. สร้าง UDP Socket
// ==========================================
const server = dgram.createSocket('udp4');

// ==========================================
// 3. ลงทะเบียน Event Listeners (กลไกหลักของ Node.js)
// ==========================================

// Event: เมื่อ Server เริ่มทำงานและทำการ Bind Port สำเร็จ
server.on('listening', () => {
    const address = server.address();
    console.log("=========================================");
    console.log("   UDP Receiver (Node.js Server Started) ");
    console.log(`   Listening on -> ${address.address}:${address.port}`);
    console.log("=========================================\n");
});

// Event: เมื่อมี UDP Packet (ข้อมูล) วิ่งเข้ามาหา Server
// - msg: ข้อมูลดิบที่เข้ามาในรูปแบบของ Node.js Buffer (Bytes)
// - rinfo: Remote Information ประกอบด้วย IP และ Port ของผู้ส่ง
server.on('message', (msg, rinfo) => {
    // แปลงข้อมูลจาก Buffer (Bytes) กลับเป็นตัวอักษร String ด้วย .toString()
    const decodedData = msg.toString('utf-8');
    
    // ปรินต์ข้อมูลออกหน้าจอ พร้อมระบุ IP/Port ของผู้ส่ง
    console.log(`[RECEIVE] From ${rinfo.address}:${rinfo.port} -> ${decodedData}`);
});

// Event: จัดการเมื่อเกิดข้อผิดพลาดขึ้นในระบบ Socket
server.on('error', (err) => {
    console.error(`[SERVER ERROR]:\n${err.stack}`);
    server.close();
});

// ==========================================
// 4. สั่งให้ Server ทำการ Bind Port เพื่อรอรับข้อมูล
// ==========================================
server.bind(LISTEN_PORT, LISTEN_IP);
