import React, {useState} from 'react';
import Map from "./Map.jsx";
import paintMap from "./MapService.js";
import Header from "../../Shared/Header/Header.jsx";

const MapPage = () => {
    const [regionHover, setRegionHover] = useState();
    const [regionInfo, setRegionInfo] = useState({});
    paintMap();
    return (
        <div>
            <Header></Header>
            <h2>{regionHover || "Пока на выбрано"}</h2>
            <Map setRegionHover={setRegionHover} setRegionInfo={setRegionInfo}/>
            {/* <button onClick={paintMap}>Раскрасить</button> */}
        </div>
    );
};

export default MapPage;