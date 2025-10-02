import React, {useState} from 'react';
import Map from "./Map.jsx";
import paintMap from "./MapService.js";
import Header from "../../Shared/Header/Header.jsx";

import SimpleGraph from "./SimpleGraph.jsx";

const MapPage = () => {
    const [regionHover, setRegionHover] = useState();
    const [regionInfo, setRegionInfo] = useState({});

    const chartDay =


        paintMap();
    return (
        <div>
            <Header></Header>
            <h2>{regionHover || "Пока на выбрано"}</h2>
            <Map setRegionHover={setRegionHover} setRegionInfo={setRegionInfo}/>
            {/* <button onClick={paintMap}>Раскрасить</button> */}
            {regionInfo.region_id ?
                <>
                    <h2>Регион {regionInfo.region_name} ({regionInfo.region_id})</h2>
                    <div style={
                        {
                            display: "flex",
                            flexDirection: "row",
                            // alignItems: "flex-start",
                            justifyContent: "space-around"
                        }
                    }>
                        <div style={{
                            display: "flex",
                            flexDirection: "column",
                        }}><h3>Период</h3>
                            <p>Начало: {regionInfo.period.start_date}</p>
                            <p>Конец {regionInfo.period.end_date}</p></div>

                        <div style={{
                            display: "flex",
                            flexDirection: "column",
                        }}>
                            <h3>Общие</h3>
                            <p>Всего полетов: {regionInfo.summary.total_flights}</p>
                            <p>Успешных полетов: {regionInfo.summary.successful_flights}</p>
                            <p>Неудачных полетов: {regionInfo.summary.failed_flights}</p>
                            <p>Процент успеха: {regionInfo.summary.success_rate}%</p>
                            <p>Общее время
                               полетов: {Math.round(regionInfo.summary.total_duration_seconds / 3600)} часов</p>
                            <p>Общее расстояние: {Math.round(regionInfo.summary.total_distance_meters / 1000)} км</p>
                            <p>Средняя продолжительность
                               полета: {Math.round(regionInfo.summary.avg_flight_duration / 60)} минут</p>
                            <p>Количество нарушений: {regionInfo.summary.violations_count}</p>
                        </div>
                        {/* flights_by_hour */}
                    </div>
                    <div style={{display:"flex", flexDirection: "row", justifyContent: "space-around"}}>
                        <div><SimpleGraph data={regionInfo.trends.flights_by_day} title={"Полеты по дням"}/></div>
                        <div><SimpleGraph data={regionInfo.trends.flights_by_hour} title={"Полеты по часам"}/></div>
                    </div>
                </> : ""}
        </div>
    );
};

export default MapPage;