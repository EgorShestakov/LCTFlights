import React from 'react';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';

import "./App.css";


import Redirect from "./Shared/Redirect.jsx";
import MapPage from "./Pages/MapPage/MapPage.jsx";

function App() {
    return (
        <Router>
            <div>
                <Routes>
                    <Route path="/" element={<MapPage/>}/>
                    <Route path="/:region/satat" element={<About/>}/>
                    <Route path="/reports" element={<Contact/>}/>
                    <Route path="/*" element={<Redirect to={'/'}/>}/>
                </Routes>
            </div>
        </Router>
    );
}

const Home = () => <h2>Home Page</h2>;
const About = () => <h2>About Page</h2>;
const Contact = () => <h2>Contact Page</h2>;

export default App;