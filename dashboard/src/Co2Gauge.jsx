// // Co2Gauge.jsx
// import React from "react";
// import {
//   RadialBarChart,
//   RadialBar,
//   Legend,
//   ResponsiveContainer,
//   Tooltip,
// } from "recharts";

// export default function Co2Gauge({ value, title, max = 2000 }) {
//   const data = [
//     {
//       name: "CO2",
//       value,
//       fill: value < 800 ? "#00b894" : value < 1200 ? "#fdcb6e" : "#d63031",
//     },
//   ];

//   return (
//     <div className="chart-card">
//       <h2 className="chart-title">{title}</h2>
//       <ResponsiveContainer width="100%" height={250}>
//         <RadialBarChart
//           cx="50%"
//           cy="50%"
//           innerRadius="70%"
//           outerRadius="100%"
//           barSize={15}
//           data={data}
//           startAngle={180}
//           endAngle={0}
//         >
//           <RadialBar
//             minAngle={15}
//             background
//             clockWise
//             dataKey="value"
//             cornerRadius={10}
//           />
//           <Tooltip />
//         </RadialBarChart>
//       </ResponsiveContainer>
//       <p style={{ textAlign: "center", fontSize: "18px", fontWeight: 500 }}>
//         {value} ppm
//       </p>
//     </div>
//   );
// }


// Co2Gauge.jsx
import React from "react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function Co2Gauge({ value, title, max = 2000 }) {
  const percent = Math.min(value / max, 1); // Ensure it's within bounds
  const angle = 180 - percent * 180; // Map to semicircle (180° to 0°)

  const needleStyle = {
    transform: `rotate(${angle}deg)`,
    transformOrigin: "bottom center",
    position: "absolute",
    left: "50%",
    bottom: "120px",
    width: "2px",
    height: "100px",
    backgroundColor: "red",
  };

  const data = [
    {
      name: "CO2",
      value,
      fill: value < 800 ? "#00b894" : value < 1200 ? "#fdcb6e" : "#d63031",
    },
  ];

  return (
    <div className="chart-card" style={{ position: "relative" }}>
      <h2 className="chart-title">{title}</h2>
      <div style={{ position: "relative", height: 250 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="100%"
            innerRadius="80%"
            outerRadius="100%"
            barSize={15}
            startAngle={180}
            endAngle={0}
            data={data}
          >
            <RadialBar
              minAngle={15}
              background
              clockWise
              dataKey="value"
              cornerRadius={10}
            />
            <Tooltip />
          </RadialBarChart>
        </ResponsiveContainer>
        <div style={needleStyle}></div>
      </div>
      <p style={{ textAlign: "center", fontSize: "18px", fontWeight: 500 }}>
        {value} ppm
      </p>
    </div>
  );
}
