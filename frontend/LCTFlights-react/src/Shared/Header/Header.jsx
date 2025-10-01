import React from 'react';
import {NavLink} from "react-router-dom";

import {contracts} from "../../contracts.js";


import * as h_style from "./Header.module.css";

const getActiveClass = (({isActive}) => isActive ? h_style.active : "");

const Header = () => {
    return (
        <>
            <div className={h_style.header}>
                <NavLink to={"/map"} className={getActiveClass}>Карта</NavLink>
                {/* <NavLink to={"/:region/satat"} className={getActiveClass}>О регионе</NavLink> */}
                <NavLink to={"/reports"} className={getActiveClass}>Отчет</NavLink>
                {/* style={{display: "flex", justifyContent: "space-between", flexDirection: "column"}} */}
                <div >
                    <input type="file" name="iFile" id="iFile" accept={".xlsx"}
                    onChange={e => {
                        if (e.target.files[0]) {
                            uploadFile(e.target.files[0]);
                        }
                    }}
                    />
                </div>

            </div>
            <hr />
        </>
    );
};

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(contracts.postFile, {
            method: 'POST',
            body: formData
            // Не устанавливай Content-Type - браузер сам установит с boundary
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Файл загружен:', result);
        } else {
            console.error('Ошибка загрузки');
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

export default Header;