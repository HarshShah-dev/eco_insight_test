// import React from "react";
// import SensorDashboard from "../SensorDashboard";

// export default function Home() {
//   return <SensorDashboard section="all" />;
// }

// Home.js (with dummy thermostat control)
import React, { useState } from "react";
import SensorDashboard from "../SensorDashboard";
import "./Home.css";

export default function Home() {
  const [thermostat, setThermostat] = useState(22);

  const handleChange = (e) => {
    setThermostat(parseInt(e.target.value));
  };

  return (
    <>
      <div className="thermostat-card">
        <h3>Thermostat Control</h3>
        <input
          type="range"
          min="16"
          max="30"
          value={thermostat}
          onChange={handleChange}
        />
        <p>Set temperature: <strong>{thermostat}°C</strong></p>
        {/* <p style={{ fontStyle: "italic", fontSize: "13px" }}>Note: This is a simulated control.</p> */}
      </div>
      <SensorDashboard section="all" />
    </>
  );
}
