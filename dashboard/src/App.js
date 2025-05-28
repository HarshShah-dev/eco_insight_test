import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { FaHome, FaBolt, FaWind, FaUsers, FaMoon, FaSun } from "react-icons/fa";
import Home from "./pages/Home";
import Energy from "./pages/Energy";
import AirQuality from "./pages/AirQuality";
import Occupancy from "./pages/Occupancy";
import "./App.css";

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  const menuItems = [
    { path: "/", icon: <FaHome />, label: "Home" },
    { path: "/energy", icon: <FaBolt />, label: "Energy" },
    { path: "/air-quality", icon: <FaWind />, label: "Air Quality" },
    { path: "/occupancy", icon: <FaUsers />, label: "Occupancy" },
  ];

  return (
    <Router>
      <div className={`app-layout ${darkMode ? "dark" : "light"}`}>
        <nav className={`sidebar ${collapsed ? "collapsed" : ""}`}>
          <button className="collapse-button" onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? ">" : "<"}
          </button>
          {!collapsed && <h2>Dashboard</h2>}
          <ul>
            {menuItems.map((item, index) => (
              <li key={index} className="nav-item">
                <Link to={item.path} className="nav-link" title={collapsed ? item.label : ""}>
                  {item.icon}
                  {!collapsed && <span className="nav-label">{item.label}</span>}
                </Link>
              </li>
            ))}
          </ul>
          <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)} title="Toggle Theme">
            {darkMode ? <FaSun /> : <FaMoon />}
          </button>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/energy" element={<Energy />} />
            <Route path="/air-quality" element={<AirQuality />} />
            <Route path="/occupancy" element={<Occupancy />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;