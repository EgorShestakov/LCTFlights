// import http from 'http';
// import fs from 'fs';
// import path from 'path';
// import {fileURLToPath} from 'url';
//
// // Чтобы получить __dirname в ES-модулях
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);
//
// const port = 3000;
//
// const jsonData = JSON.parse(fs.readFileSync("public/flight_statistics.json"));
//
// // Функция для определения Content-Type по расширению
// function getContentType(filePath) {
//     const ext = path.extname(filePath).toLowerCase();
//     const mimeTypes = {
//         '.html': 'text/html',
//         '.js': 'text/javascript',
//         '.css': 'text/css',
//         '.json': 'application/json',
//         '.png': 'image/png',
//         '.jpg': 'image/jpeg',
//         '.jpeg': 'image/jpeg',
//         '.gif': 'image/gif',
//         '.svg': 'image/svg+xml',
//         '.ico': 'image/x-icon',
//         '.txt': 'text/plain',
//     };
//     return mimeTypes[ext] || 'application/octet-stream';
// }
//
//     const server = http.createServer((req, res) => {
//         if (req.method === 'GET') {
//             if (req.url === '/update') {
//                 // Отдать JSON
//                 res.writeHead(200, {'Content-Type': 'application/json'});
//                 res.end(JSON.stringify(jsonData));
//             } else {
//                 // Отдать файл из папки public
//                 let filePath = req.url === '/' ? '/index.html' : req.url;
//                 filePath = path.join(__dirname, 'public', filePath);
//
//                 fs.stat(filePath, (err, stats) => {
//                     if (err || !stats.isFile()) {
//                         res.writeHead(404, {'Content-Type': 'text/plain'});
//                         res.end('Файл не найден');
//                         return;
//                     }
//
//                     const contentType = getContentType(filePath);
//                     res.writeHead(200, {'Content-Type': contentType});
//
//                     const stream = fs.createReadStream(filePath);
//                     stream.pipe(res);
//
//                     stream.on('error', () => {
//                         res.writeHead(500);
//                         res.end('Ошибка чтения файла');
//                     });
//                 });
//             }
//         } else {
//             res.writeHead(405, {'Content-Type': 'text/plain'});
//             res.end('Метод не поддерживается');
//         }
//     });
//
// process.on('SIGINT', () => {
//     console.log('Received SIGINT. Shutting down gracefully');
//     server.close(() => {
//         console.log('Server closed');
//         process.exit(0);
//     });
// });
//
// process.on('SIGTERM', () => {
//     console.log('Received SIGTERM. Shutting down gracefully');
//     server.close(() => {
//         console.log('Server closed');
//         process.exit(0);
//     });
// });
//
// server.listen(port, () => {
//     console.log(`Сервер запущен на http://localhost:${port}`);
// });
