const dgram = require('dgram');
const { WebSocketServer } = require('ws');

// ==========================================
// 1. ตั้งค่าคอนฟิกูเรชัน
// ==========================================
const UDP_PORT = 5005;     // พอร์ตสำหรับรับค่าจาก Sensor
const WS_PORT = 8080;      // พอร์ตสำหรับส่งค่าไปหน้าเว็บ Admin

// ==========================================
// 2. สร้าง Servers ทั้งสองระบบ
// ==========================================
const udpServer = dgram.createSocket('udp4');
const wss = new WebSocketServer({ port: WS_PORT });

console.log("=========================================");
console.log("   IoT Gateway Server (UDP + WebSocket)  ");
console.log(`   1. Listening UDP on port   -> ${UDP_PORT}`);
console.log(`   2. WebSocket Server on port -> ws://localhost:${WS_PORT}`);
console.log("=========================================\n");

// คอยมอนิเตอร์ฝั่ง WebSocket Client (หน้าเว็บ Admin)
wss.on('connection', (ws) => {
    console.log('[Dashboard] Web Admin connected.');
});

// ==========================================
// [จุดที่ให้นิสิตฝึกต่อยอด]: รับจาก UDP แล้ว Push ไป WebSocket
// ==========================================
udpServer.on('message', (msg, rinfo) => {
    // 1. รับ Data Bytes จาก UDP แล้วแปลงเป็น String
    const rawData = msg.toString('utf-8');
    console.log(`[UDP Receive] From Sensor (${rinfo.address}) -> ${rawData}`);

    // 2. จัดรูปแบบข้อมูลใหม่ให้อยู่ในรูป JSON ก่อนส่งขึ้น Application Layer
    const payload = JSON.stringify({
        type: "DATA",
        time: new Date().toISOString().replace('T', ' ').substring(0, 19),
        status_value: rawData // ส่งค่าที่ได้จาก Sensor ต่อไปเลย
    });

    // 3. (ภารกิจของนิสิต) วนลูปกระจายข้อมูลออกไปให้เว็บเบราว์เซอร์ทุกตัว
    wss.clients.forEach((client) => {
        if (client.readyState === 1) {
            client.send(payload);
        }
    });
    
    console.log(`   └─> [WS Broadcast] Forwarded to ${wss.clients.size} dashboard(s).`);
});

// เปิดรัน UDP Server
udpServer.bind(UDP_PORT);
