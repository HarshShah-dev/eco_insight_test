// // SensorDashboard.jsx
// import React, { useEffect, useState } from "react";
// import axios from "axios";
// import {
//   LineChart,
//   Line,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   ResponsiveContainer,
//   Legend,
// } from "recharts";
// import "./SensorDashboard.css";
// import Co2Meter from "./Co2Meter";
// import TempMeter from "./TempMeter";
// import MetricCard from "./MetricCard";

// const API_BASE_URL = "/api/data";

// const ChartCard = ({
//   title,
//   data,
//   dataKeys,
//   unit,
//   duration,
//   onDurationChange,
//   durationOptions,
//   selectedSensor,
//   onSensorChange,
//   sensorOptions = [],
// }) => (
//   <div className="chart-card">
//     <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", flexWrap: "wrap", gap: "12px" }}>
//       <h2 className="chart-title" style={{ marginRight: "auto" }}>{title}</h2>
//       {sensorOptions.length > 0 && (
//         <select
//           value={selectedSensor}
//           onChange={(e) => onSensorChange(e.target.value)}
//           style={{ padding: "4px 8px", borderRadius: "4px", border: "1px solid #ccc" }}
//         >
//           {sensorOptions.map((opt) => (
//             <option key={opt.id} value={opt.id}>{opt.label}</option>
//           ))}
//         </select>
//       )}
//       <select
//         value={duration}
//         onChange={(e) => onDurationChange(e.target.value)}
//         style={{ padding: "4px 8px", borderRadius: "4px", border: "1px solid #ccc" }}
//       >
//         {durationOptions.map((opt) => (
//           <option key={opt.value} value={opt.value}>
//             {opt.label}
//           </option>
//         ))}
//       </select>
//     </div>
//     {data.length > 0 ? (
//       <ResponsiveContainer width="100%" height={250}>
//         <LineChart data={data}>
//           <CartesianGrid strokeDasharray="3 3" />
//           <XAxis
//             dataKey="timestamp"
//             tickFormatter={(str) => {
//               try {
//                 const date = new Date(str);
//                 return date.toLocaleString([], {
//                   month: "short",
//                   day: "numeric",
//                   hour: "2-digit",
//                   minute: "2-digit",
//                 });
//               } catch {
//                 return "";
//               }
//             }}
//           />
//           <YAxis unit={unit} />
//           <Tooltip />
//           <Legend />
//           {dataKeys.map((key, i) => (
//             <Line
//               key={i}
//               type="monotone"
//               dataKey={key}
//               stroke={["#8884d8", "#82ca9d", "#ffc658", "#ff7675"][i % 4]}
//               dot={false}
//             />
//           ))}
//         </LineChart>
//       </ResponsiveContainer>
//     ) : (
//       <p>Loading...</p>
//     )}
//   </div>
// );

// const RecommendationPanel = () => {
//   const [recommendation, setRecommendation] = useState("Loading...");

//   useEffect(() => {
//     const fetchRec = async () => {
//       try {
//         const res = await axios.get("/api/recommendation/");
//         setRecommendation(res.data.recommendation || "No recommendation");
//       } catch (error) {
//         console.error("Failed to fetch recommendation", error);
//         setRecommendation("Error fetching recommendation");
//       }
//     };
//     fetchRec();
//     const interval = setInterval(fetchRec, 10000);
//     return () => clearInterval(interval);
//   }, []);

//   return (
//     <div className="recommendation-panel">
//       <h2 className="chart-title">AI Recommendation</h2>
//       <p style={{ fontSize: "18px", padding: "8px", lineHeight: 1.4 }}>{recommendation}</p>
//     </div>
//   );
// };


// // --- Helper to filter sensor options ---
// const getSensorOptions = (data) => {
//   const seen = new Set();
//   return data
//     .filter((d) => d.sensor && d.sensor.sensor_id)
//     .filter((d) => {
//       const id = d.sensor.sensor_id;
//       if (seen.has(id)) return false;
//       seen.add(id);
//       return true;
//     })
//     .map((d) => ({
//       id: d.sensor.sensor_id,
//       label: `Sensor ${d.sensor.sensor_id} (Floor ${d.sensor.floor ?? "?"}, ${d.sensor.office ?? "?"})`,
//     }));
// };
// // --- Helper to filter sensor options ---
// const getSensorOptions = (data) => {
//   const seen = new Set();
//   return data
//     .filter((d) => d.sensor && d.sensor.sensor_id)
//     .filter((d) => {
//       const id = d.sensor.sensor_id;
//       if (seen.has(id)) return false;
//       seen.add(id);
//       return true;
//     })
//     .map((d) => ({
//       id: d.sensor.sensor_id,
//       label: `Sensor ${d.sensor.sensor_id} (Floor ${d.sensor.floor ?? "?"}, ${d.sensor.office ?? "?"})`,
//     }));
// };

// export default function SensorDashboard({ section = "all" }) {
//   const [co2Data, setCo2Data] = useState([]);
//   const [emData, setEmData] = useState([]);
//   const [ocData, setOcData] = useState([]);
//   const [emLevel3Data, setEmLevel3Data] = useState([]);
//   const [emLevel4Data, setEmLevel4Data] = useState([]);
//   const [avgCo2, setAvgCo2] = useState(0);
//   const [currentCo2, setCurrentCo2] = useState(0);
//   const [currentEnergyL3, setCurrentEnergyL3] = useState(0);
//   const [currentEnergyL4, setCurrentEnergyL4] = useState(0);
//   const [avgEnergyL3, setAvgEnergyL3] = useState(0);
//   const [avgEnergyL4, setAvgEnergyL4] = useState(0);
//   const [peakEnergyL3, setPeakEnergyL3] = useState({ value: 0, time: null });
//   const [peakEnergyL4, setPeakEnergyL4] = useState({ value: 0, time: null });
//   const [currentTemp, setCurrentTemp] = useState(0);
//   const [peoplePresent, setPeoplePresent] = useState(0);
//   const [radarData, setRadarData] = useState([]);
//   const [lsg01Data, setLsg01Data] = useState([]);
//   const [lsg01Duration, setLsg01Duration] = useState("1mo");
//   const [radarDuration, setRadarDuration] = useState("1mo");


//   // Individual durations for each chart
//   const [co2Duration, setCo2Duration] = useState("1mo");
//   const [tempDuration, setTempDuration] = useState("1mo");
//   const [energyL3Duration, setEnergyL3Duration] = useState("1mo");
//   const [energyL4Duration, setEnergyL4Duration] = useState("1mo");
//   const [occupancyDuration, setOccupancyDuration] = useState("1mo");

//   const [selectedCo2Sensor, setSelectedCo2Sensor] = useState("");
//   const [selectedTempSensor, setSelectedTempSensor] = useState("");
//   const [selectedOccSensor, setSelectedOccSensor] = useState("");
//   const [selectedRadarSensor, setSelectedRadarSensor] = useState("");


//   const durationOptions = [
//     { label: "Last 1 hour", value: "1h" },
//     { label: "Last 24 hours", value: "24h" },
//     { label: "Last 7 days", value: "7d" },
//     { label: "Last month", value: "1mo" },
//     { label: "Last 3 months", value: "3mo" },
//     { label: "Last 6 months", value: "6mo" },
//     { label: "All time", value: "all" },
//   ];

//   const filterByDuration = (data, selectedDuration) => {
//     const now = new Date();
//     let cutoff;
//     switch (selectedDuration) {
//       case "1h":
//         return data.filter((d) => new Date(d.timestamp) >= new Date(now - 1 * 60 * 60 * 1000));
//       case "24h":
//         return data.filter((d) => new Date(d.timestamp) >= new Date(now - 24 * 60 * 60 * 1000));
//       case "7d":
//         return data.filter((d) => new Date(d.timestamp) >= new Date(now - 7 * 24 * 60 * 60 * 1000));
//       case "1mo":
//         cutoff = new Date(); cutoff.setMonth(now.getMonth() - 1); break;
//       case "3mo":
//         cutoff = new Date(); cutoff.setMonth(now.getMonth() - 3); break;
//       case "6mo":
//         cutoff = new Date(); cutoff.setMonth(now.getMonth() - 6); break;
//       default:
//         return data;
//     }
//     return data.filter((d) => new Date(d.timestamp) >= cutoff);
//   };

//   const sortByTime = (data) =>
//     [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

//   const calculateAverage = (data, key) => {
//     if (!data || data.length === 0) return 0;
//     const sum = data.reduce((acc, item) => acc + (item[key] || 0), 0);
//     return Math.round(sum / data.length);
//   };

//   const calculatePeak = (data, key) => {
//     if (!data || data.length === 0) return { value: 0, time: null };
//     let max = -Infinity;
//     let maxTime = null;
//     data.forEach(item => {
//       if ((item[key] || 0) > max) {
//         max = item[key] || 0;
//         maxTime = item.timestamp;
//       }
//     });
//     return { value: max, time: maxTime };
//   };

//   const groupOccupancyBySensorSorted = (data) => {
//     const grouped = {};

//     data.forEach(entry => {
//       const sensor = entry.sensor;
//       const sensorId = sensor?.sensor_id || "unknown";

//       if (!grouped[sensorId]) {
//         grouped[sensorId] = {
//           sensor,
//           data: [],
//         };
//       }

//       grouped[sensorId].data.push(entry);
//     });

//     // Convert to array and sort by floor
//     return Object.entries(grouped).sort(
//       ([, a], [, b]) => (a.sensor.floor ?? -1) - (b.sensor.floor ?? -1)
//     );
//   };

//   const getLatestRadarBySensor = (data) => {
//     const latest = {};

//     for (const entry of data) {
//       const id = entry.sensor?.sensor_id;
//       if (!id) continue;

//       if (!latest[id] || new Date(entry.timestamp) > new Date(latest[id].timestamp)) {
//         latest[id] = entry;
//       }
//     }

//     // Convert to sorted array by floor
//     return Object.values(latest).sort((a, b) => (a.sensor?.floor ?? -1) - (b.sensor?.floor ?? -1));
//   };

//   const fetchData = async () => {
//     try {
//       const [co2Res, emRes, ocRes, emL3Res, emL4Res, radarRes, lsg01Res] = await Promise.all([
//         axios.get(`${API_BASE_URL}/air/unified`),
//         axios.get(`${API_BASE_URL}/em/history`),
//         axios.get(`${API_BASE_URL}/oc/history`),
//         axios.get(`${API_BASE_URL}/em/history/level3`),
//         axios.get(`${API_BASE_URL}/em/history/level4`),
//         axios.get(`${API_BASE_URL}/radar/history`),
//         axios.get(`${API_BASE_URL}/lsg01/history`)

//       ]);

//       const co2Sorted = sortByTime(co2Res.data);
//       const co2Filtered = filterByDuration(co2Sorted, co2Duration);
//       // setCo2Data(co2Filtered);
//       setCo2Data(sortByTime(co2Res.data));
//       const avg = co2Filtered.length ? co2Filtered.reduce((a, b) => a + b.co2, 0) / co2Filtered.length : 0;
//       setAvgCo2(Math.round(avg));
//       if (co2Filtered.length > 0) {
//         setCurrentCo2(co2Filtered[co2Filtered.length - 1].co2);
//         setCurrentTemp(co2Filtered[co2Filtered.length - 1]?.temperature ?? co2Filtered[co2Filtered.length - 1]?.temp ?? 0);
//       }

//       const l3Sorted = sortByTime(emL3Res.data);
//       const l3Filtered = filterByDuration(l3Sorted, energyL3Duration);
//       setEmLevel3Data(l3Filtered);
//       if (l3Filtered.length > 0) {
//         setCurrentEnergyL3(l3Filtered[l3Filtered.length - 1].total_act_power);
//         setAvgEnergyL3(calculateAverage(l3Filtered, 'total_act_power'));
//         setPeakEnergyL3(calculatePeak(l3Filtered, 'total_act_power'));
//       }

//       const l4Sorted = sortByTime(emL4Res.data);
//       const l4Filtered = filterByDuration(l4Sorted, energyL4Duration);
//       setEmLevel4Data(l4Filtered);
//       if (l4Filtered.length > 0) {
//         setCurrentEnergyL4(l4Filtered[l4Filtered.length - 1].total_act_power);
//         setAvgEnergyL4(calculateAverage(l4Filtered, 'total_act_power'));
//         setPeakEnergyL4(calculatePeak(l4Filtered, 'total_act_power'));
//       }

//       // setRadarData(radarRes.data);
//       setRadarData(sortByTime(radarRes.data));

//       const lsgSorted = sortByTime(lsg01Res.data);
//       const lsgFiltered = filterByDuration(lsgSorted, lsg01Duration);
//       setLsg01Data(lsgFiltered);

//       const ocSorted = sortByTime(ocRes.data);
//       const ocFiltered = filterByDuration(ocSorted, occupancyDuration);
//       // setOcData(ocFiltered);
//       setOcData(sortByTime(ocRes.data));
//       if (ocFiltered.length > 0) {
//         const last = ocFiltered[ocFiltered.length - 1];
//         const present = Math.max(0, (last.total_entries || 0) - (last.total_exits || 0));
//         setPeoplePresent(present);
//       } else {
//         setPeoplePresent(0);
//       }
//     } catch (error) {
//       console.error("Error fetching sensor data:", error);
//     }
//   };

//   useEffect(() => {
//     fetchData();
//     const interval = setInterval(fetchData, 10000);
//     return () => clearInterval(interval);
//   }, [co2Duration, tempDuration, energyL3Duration, energyL4Duration, occupancyDuration]);
//   const filteredCo2 = filterByDuration(
//     co2Data.filter((d) => d.sensor?.sensor_id === selectedCo2Sensor),
//     co2Duration
//   );
//   const filteredTemp = filterByDuration(
//     co2Data.filter((d) => d.sensor?.sensor_id === selectedTempSensor),
//     tempDuration
//   );
//   const filteredOcc = filterByDuration(
//     ocData.filter((d) => d.sensor?.sensor_id === selectedOccSensor),
//     occupancyDuration
//   );
//   const filteredRadar = filterByDuration(
//     radarData.filter((d) => d.sensor?.sensor_id === selectedRadarSensor),
//     radarDuration
//   );

//   const co2Sensors = getSensorOptions(co2Data);
//   const occSensors = getSensorOptions(ocData);
//   const radarSensors = getSensorOptions(radarData);

//   return (
//     <div className="dashboard">
//       {(section === "all" || section === "air") && (
//         <>
//           <ChartCard
//             title="CO₂ Levels (ppm)"
//             data={filteredCo2}
//             dataKeys={["co2"]}
//             unit="ppm"
//             duration={co2Duration}
//             onDurationChange={setCo2Duration}
//             selectedSensor={selectedCo2Sensor}
//             onSensorChange={setSelectedCo2Sensor}
//             sensorOptions={co2Sensors}
//             durationOptions={durationOptions}
//           />
//           {filteredCo2.length > 0 && (
//             <Co2Meter
//               value={filteredCo2[filteredCo2.length - 1].co2}
//               title={`Current CO₂ (${selectedCo2Sensor})`}
//             />
//           )}

//           <ChartCard
//             title="Temperature (°C)"
//             data={filteredTemp}
//             dataKeys={["temp"]}
//             unit="°C"
//             duration={tempDuration}
//             onDurationChange={setTempDuration}
//             selectedSensor={selectedTempSensor}
//             onSensorChange={setSelectedTempSensor}
//             sensorOptions={co2Sensors}
//             durationOptions={durationOptions}
//           />
//           {filteredTemp.length > 0 && (
//             <TempMeter
//               value={filteredTemp[filteredTemp.length - 1].temp}
//               title={`Current Temp (${selectedTempSensor})`}
//               max={45}
//             />
//           )}
//         </>
//       )}

//       {(section === "all" || section === "occupancy") && (
//         <>
//           <ChartCard
//             title="Occupancy Entries/Exits"
//             data={filteredOcc}
//             dataKeys={["total_entries", "total_exits"]}
//             unit=""
//             duration={occupancyDuration}
//             onDurationChange={setOccupancyDuration}
//             selectedSensor={selectedOccSensor}
//             onSensorChange={setSelectedOccSensor}
//             sensorOptions={occSensors}
//             durationOptions={durationOptions}
//           />
//         </>
//       )}

//       {(section === "all" || section === "radar") && (
//         <>
//           <ChartCard
//             title="Radar People Count"
//             data={filteredRadar}
//             dataKeys={["people_count"]}
//             unit=""
//             duration={radarDuration}
//             onDurationChange={setRadarDuration}
//             selectedSensor={selectedRadarSensor}
//             onSensorChange={setSelectedRadarSensor}
//             sensorOptions={radarSensors}
//             durationOptions={durationOptions}
//           />
//         </>
//       )}
//     </div>
//   );
// }