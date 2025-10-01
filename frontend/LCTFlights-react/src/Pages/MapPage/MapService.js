import {contracts} from "../../contracts.js";

export default async function paintMap() {
    try {
        // Получаем данные с сервера
        // const response = await fetch('/map/stats');
        const response = await fetch(contracts.mapStats);
        if (!response.ok) {
            throw new Error('Ошибка получения данных с сервера');
        }

        const data = await response.json();

        const regions = document.querySelectorAll("path.region");
        if (!regions) return;

        // Вычисляем общее количество полетов из данных сервера
        const totalFlights = Object.values(data.regions).reduce((total, region) => {
            return total + (region.total_flights || 0);
        }, 0);

        regions.forEach(i => {
            // цвет на основе процентного соотношения
            const regNumStr = i.attributes["reg-num"]?.value; // исправлено nodeValue на value
            if (!regNumStr) return;

            const regNum = Number(regNumStr);
            const regionData = data.regions[regNum];

            // Используем total_flights из данных сервера
            const flightsCount = regionData?.total_flights || 0;
            const percent = totalFlights > 0 ? (flightsCount / totalFlights) * 100 : 0;

            const color = getColor(percent);
            i.style.fill = color;

            // Добавляем tooltip с информацией
            i.setAttribute('title', `Регион: ${regionData?.name || regNum}\nПолетов: ${flightsCount}\nДоля: ${percent.toFixed(1)}%`);
        });

        // console.log('Карта окрашена на основе данных сервера');

    } catch (error) {
        console.error('Ошибка при окрашивании карты:', error);
        // Можно добавить fallback на случай ошибки
        fallbackPaint();
    }
}

function getColor(percent) {
    if (percent >= 60) return "#ff4444";     // красный
    else if (percent >= 40) return "#ffaa00"; // оранжевый
    else if (percent >= 10) return "#ffff00"; // желтый
    else if (percent >= 1) return "#44ff44";  // зеленый
    else return "#cccccc";                    // серый
}

// Fallback на случай если сервер недоступен
function fallbackPaint() {
    const regions = document.querySelectorAll("path.region");
    regions.forEach(i => {
        i.style.fill = "#cccccc"; // серый по умолчанию
    });
}




// export default function paintMap(data) {
//     data = {
//         "23": {
//             "name": "",
//             "drone_count": 1
//         },
//         "14": {
//             "name": "",
//             "drone_count": 20
//         },
//         "49": {
//             "name": "",
//             "drone_count": 10
//         },
//         "39": {
//             "name": "",
//             "drone_count": 15
//         },
//         "89": {
//             "name": "",
//             "drone_count": 50
//         },
//         "totalDroneCount": 96
//     };
//
//     const regions = document.querySelectorAll("path.region");
//     if (!regions) return;
//
//     regions.forEach(i => {
//         // цвет на основе процентного соотношения
//         const regNumStr = i.attributes["reg-num"]?.nodeValue; // строка
//         if (regNumStr) {var regNum = Number(regNumStr);} else {return;}
//         const persent = ((data[regNum]?.drone_count / data?.totalDroneCount) * 100) || 0;
//         // console.log(persent);
//         const color = getColor(persent);
//         // console.log(color);
//         i["style"].fill = color;
//         // console.log(data[regNum]);
//     });
// }
//
// function getColor(percent) {
//     if (percent >= 60) return "red";
//     else if (percent >= 40) return "orange";
//     else if (percent >= 10) return "yellow";
//     else if (percent >= 1) return "green";
//     else return "gray";
// }