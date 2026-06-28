const { WebSocketServer } = require('ws');

// ==========================================
// 1. ตั้งค่าคอนฟิกูเรชัน (Configuration)
// ==========================================
const WS_PORT = 8080;

// ==========================================
// 2. สร้าง WebSocket Server
// ==========================================
const wss = new WebSocketServer({ port: WS_PORT });

console.log("=========================================");
console.log("   WebSocket Server (Application Layer)  ");
async console.log(`   Running on port -> ws://localhost:${WS_PORT}`);
console.log("=========================================\n");

// 3. เหตุการณ์เมื่อมี Client (หน้าเว็บ Admin) เชื่อมต่อเข้ามา
wss.on('connection', (ws, req) => {
    const clientIp = req.socket.remoteAddress;
    console.log(`[CONNECTED] New Admin Web Client joined from IP: ${clientIp}`);
    console.log(`[INFO] Current active clients: ${wss.clients.size}`);

    // ส่งข้อความต้อนรับทักทาย Client ที่เข้ามาใหม่
    ws.send(JSON.stringify({ 
        type: "SYSTEM", 
        message: "Connected to Real-time Monitoring Server successfully." 
    }));

    // เหตุการณ์เมื่อ Client ปิดหน้าเว็บหนีไป (Disconnected)
    ws.on('close', () => {
        console.log(`[DISCONNECTED] Admin Client left.`);
        console.log(`[INFO] Remaining active clients: ${wss.clients.size}`);
    });
});

// ==========================================
// 4. จำลองการผลิตข้อมูล (Simulation) ทุกๆ 2 วินาที
// ==========================================
setInterval(() => {
    // ถ้าไม่มีใครเปิดหน้าเว็บรออยู่เลย ก็ไม่ต้องส่งให้เปลืองทรัพยากร
    if (wss.clients.size === 0) return;

    // จำลองค่าสถานะระบบ (สุ่มตัวเลข 1-100)
    const systemStatus = Math.floor(Math.random() * 100) + 1;
    const currentTime = new Date().toISOString().replace('T', ' ').substring(0, 19);

    // แพ็กข้อมูลให้อยู่ในรูปแบบ JSON String (มาตรฐานของ Application Layer บนเว็บ)
    const payload = JSON.stringify({
        type: "DATA",
        time: currentTime,
        status_value: systemStatus
    });

    // วนลูปส่งข้อมูลไปให้ Clients "ทุกตัว" ที่เปิดหน้าเว็บค้างไว้ (Broadcasting)
    wss.clients.forEach((client) => {
        // เช็คสถานะว่าท่อเชื่อมต่อของ Client นั้นยังเปิดปกติอยู่หรือไม่ (1 = OPEN)
        if (client.readyState === 1) { 
            client.send(payload);
        }
    });

    console.log(`[BROADCAST] Sent status [${systemStatus}] to ${wss.clients.size} client(s).`);

}, 2000); // ทำงานทุกๆ 2000 มิลลิวินาที (2 วินาที)
