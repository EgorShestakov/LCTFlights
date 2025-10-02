import http from 'http';
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';

import {mapStats} from "./data_mapStats.js";
import {regionAnalytics} from "./data_regionAnalitics.js";
import {contracts} from "./LCTFlights-react/src/contracts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const port = 3000;

const jsonData = JSON.parse(fs.readFileSync("data2.json"));

function getContentType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.txt': 'text/plain',
    };
    return mimeTypes[ext] || 'application/octet-stream';
}

function parseQueryParams(url) {
    const query = {};
    const queryString = url.split('?')[1];
    if (queryString) {
        queryString.split('&').forEach(param => {
            const [key, value] = param.split('=');
            query[key] = value ? decodeURIComponent(value) : true;
        });
    }
    return query;
}

const server = http.createServer((req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:5173');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    if (req.method === 'GET') {
        // ✅ Соответствует contracts.mapStats
        // if (req.url === '/map/stats' || /^\/map\/stats\?/.test(req.url)) {
        if (req.url === "/flights_percent" || /^\/map\/stats\?/.test(req.url)) {
            const queryParams = parseQueryParams(req.url);
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(mapStats));
        }
        // ✅ Соответствует contracts.flights
        else if (req.url === '/flights' || /^\/flights\?/.test(req.url)) {
            const flightsData = {
                flights: [
                    {
                        region_id: 23,
                        timestamp_start: "2024-01-15T08:00:00Z",
                        timestamp_end: "2024-01-15T08:45:30Z",
                        duration_seconds: 2730,
                        distance_meters: 15200,
                        status: "completed",
                        violations: [],
                        operator_id: "operator_7",
                        operator_name: "Аэротехнологии",
                        drone_model: "DJI Matrice 300",
                        drone_serial: "DJI123456789"
                    }
                ],
                pagination: {
                    page: 1,
                    limit: 20,
                    total_count: 1,
                    total_pages: 1
                }
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(flightsData));
        }
        // Дополнительные endpoints
        else if (req.url === '/update') {
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(jsonData));
        } else if (/^\/regions\/\d+\/analytics(\?.*)?$/.test(req.url)) {
            const match = req.url.match(/\/regions\/(\d+)\/analytics/);
            const regionId = match ? match[1] : '1';

            const response = {
                ...regionAnalytics,
                region_id: parseInt(regionId)
            };

            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(response));
        } else if (req.url === '/regions') {
            const regionsData = {
                regions: {
                    "23": {name: "Алтайская область", code: "ALT", area_sq_km: 167996},
                    "14": {name: "Томская область", code: "TOM", area_sq_km: 314391}
                },
                total_count: 2
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(regionsData));
        } else {
            // Статические файлы
            let filePath = req.url === '/' ? '/index.html' : req.url;
            filePath = path.join(__dirname, 'LCTFlights-react','dist', filePath);
            // filePath = path.join(__dirname, 'public', filePath);

            fs.stat(filePath, (err, stats) => {
                if (err || !stats.isFile()) {
                    res.writeHead(404, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({error: 'Файл не найден'}));
                    return;
                }

                const contentType = getContentType(filePath);
                res.writeHead(200, {'Content-Type': contentType});

                const stream = fs.createReadStream(filePath);
                stream.pipe(res);
                stream.on('error', () => {
                    res.writeHead(500, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({error: 'Ошибка чтения файла'}));
                });
            });
        }
    } else if (req.method === 'POST') {
        // ✅ Соответствует contracts.postFile
        if (req.url === '/post') {
            const contentType = req.headers['content-type'];

            if (!contentType || !contentType.includes('multipart/form-data')) {
                res.writeHead(400, {'Content-Type': 'application/json'});
                res.end(JSON.stringify({error: 'Только multipart/form-data поддерживается'}));
                return;
            }

            let body = Buffer.alloc(0);

            req.on('data', (chunk) => {
                body = Buffer.concat([body, chunk]);
            });

            req.on('end', () => {
                try {
                    // Простая имитация обработки файла
                    console.log('📁 Файл получен через /post');
                    console.log(`   Размер данных: ${body.length} байт`);
                    console.log(`   Content-Type: ${contentType}`);

                    res.writeHead(200, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({
                                               success: true,
                                               message: 'Файл успешно загружен через /post',
                                               size: body.length
                                           }));

                } catch (error) {
                    console.error('Ошибка обработки файла:', error);
                    res.writeHead(500, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({error: 'Ошибка обработки файла'}));
                }
            });
        }
        // ✅ Соответствует contracts.generateReport
        else if (req.url === '/reports/generate') {
            let body = '';
            req.on('data', chunk => {
                body += chunk.toString();
            });
            req.on('end', () => {
                console.log('📊 Генерация отчета с данными:', body);

                res.writeHead(200, {'Content-Type': 'application/json'});
                res.end(JSON.stringify({
                                           success: true,
                                           message: 'Отчет поставлен в очередь на генерацию',
                                           job_id: 'report_' + Date.now(),
                                           status: 'processing'
                                       }));
            });
        } else {
            res.writeHead(404, {'Content-Type': 'application/json'});
            res.end(JSON.stringify({error: 'Endpoint не найден'}));
        }
    } else {
        res.writeHead(405, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({error: 'Метод не поддерживается'}));
    }
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Received SIGINT. Shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('Received SIGTERM. Shutting down gracefully');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

server.listen(port, () => {
    console.log(`🚀 Сервер запущен на http://localhost:${port}`);
    console.log('📡 Доступные endpoints:');
    console.log('   GET  /map/stats        ✅');
    console.log('   GET  /flights          ✅');
    console.log('   POST /post             ✅');
    console.log('   POST /reports/generate ✅');
    console.log('   GET  /regions');
    console.log('   GET  /regions/{id}/analytics');
});