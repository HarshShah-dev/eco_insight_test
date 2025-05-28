// SensorDashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import "./SensorDashboard.css"; // for basic styling
import Co2Gauge from "./Co2Gauge";
import GaugeMeter from "./GaugeMeter";
import MetricCard from "./MetricCard";



const API_BASE_URL = "/api/data";

const ChartCard = ({ title, data, dataKeys, unit }) => (
  <div className="chart-card">
    <h2 className="chart-title">{title}</h2>
    {data.length > 0 ? (
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          {/* <XAxis dataKey="timestamp" tickFormatter={(str) => str.slice(11, 19)} /> */}
          <XAxis
            dataKey="timestamp"
            tickFormatter={(str) => {
              try {
                return new Date(str).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              } catch {
                return '';
              }
            }}
          />
          <YAxis unit={unit} />
          <Tooltip />
          <Legend />
          {dataKeys.map((key, i) => (
            <Line
              key={i}
              type="monotone"
              dataKey={key}
              stroke={["#8884d8", "#82ca9d", "#ffc658"][i % 3]}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    ) : (
      <p>Loading...</p>
    )}
  </div>
);

export default function SensorDashboard() {
  const [co2Data, setCo2Data] = useState([]);
  const [emData, setEmData] = useState([]);
  const [ocData, setOcData] = useState([]);
  const [emLevel3Data, setEmLevel3Data] = useState([]);
  const [emLevel4Data, setEmLevel4Data] = useState([]);
  const [avgCo2, setAvgCo2] = useState(0);
  const [currentCo2, setCurrentCo2] = useState(0);
  const [currentEnergyL3, setCurrentEnergyL3] = useState(0);
  const [currentEnergyL4, setCurrentEnergyL4] = useState(0);
  const [duration, setDuration] = useState("1h");

  const durationOptions = [
    { label: "Last 1 hour", value: "1h" },
    { label: "Last 24 hours", value: "24h" },
    { label: "Last 7 days", value: "7d" },
    { label: "Last month", value: "1mo" },
    { label: "Last 3 months", value: "3mo" },
    { label: "Last 6 months", value: "6mo" },
    { label: "All time", value: "all" },
  ];


  // const filterByDuration = (data) => {
  //   const now = new Date();

  //   const durationMap = {
  //     "1h": new Date(now.getTime() - 1 * 60 * 60 * 1000),
  //     "24h": new Date(now.getTime() - 24 * 60 * 60 * 1000),
  //     "7d": new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000),
  //     "1mo": new Date(now.setMonth(now.getMonth() - 1)),
  //     "3mo": new Date(now.setMonth(now.getMonth() - 3)),
  //     "6mo": new Date(now.setMonth(now.getMonth() - 6)),
  //   };

  //   if (duration === "all") return data;

  //   // Make a fresh copy of `now` to avoid mutation issues
  //   const cutoff = new Date(durationMap[duration]);
  //   return data.filter((d) => new Date(d.timestamp) >= cutoff);
  // };
  const filterByDuration = (data) => {
    const now = new Date();
    let cutoff;

    switch (duration) {
      case "1h":
        cutoff = new Date(now.getTime() - 1 * 60 * 60 * 1000);
        break;
      case "24h":
        cutoff = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case "7d":
        cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case "1mo":
        cutoff = new Date(now);
        cutoff.setMonth(cutoff.getMonth() - 1);
        break;
      case "3mo":
        cutoff = new Date(now);
        cutoff.setMonth(cutoff.getMonth() - 3);
        break;
      case "6mo":
        cutoff = new Date(now);
        cutoff.setMonth(cutoff.getMonth() - 6);
        break;
      case "all":
      default:
        return data; // no filtering
    }

    return data.filter((d) => new Date(d.timestamp) >= cutoff);
  };




  // const fetchData = async () => {
  //   try {
  //     const [co2Res, emRes, ocRes, emLevel3Res, emLevel4Res] = await Promise.all([
  //       axios.get(`${API_BASE_URL}/co2/history`),
  //       axios.get(`${API_BASE_URL}/em/history`),
  //       axios.get(`${API_BASE_URL}/oc/history`),
  //       axios.get(`${API_BASE_URL}/em/history/level3`),
  //       axios.get(`${API_BASE_URL}/em/history/level4`),
  //     ]);
  //     const sorted = sortByTime(rawData);
  //     const filtered = filterByDuration(sorted);

  //     const sortByTime = (data) =>
  //       data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  //     // setCo2Data(sortByTime(co2Res.data));
  //     // setEmData(sortByTime(emRes.data));
  //     // setOcData(sortByTime(ocRes.data));
  //     // setEmLevel3Data(sortByTime(emLevel3Res.data));
  //     // setEmLevel4Data(sortByTime(emLevel4Res.data));

  //     setCo2Data(filterByDuration(sortByTime(co2Res.data)));
  //     setEmData(filterByDuration(sortByTime(emRes.data)));
  //     setOcData(filterByDuration(sortByTime(ocRes.data)));
  //     setEmLevel3Data(filterByDuration(sortByTime(emLevel3Res.data)));
  //     setEmLevel4Data(filterByDuration(sortByTime(emLevel4Res.data)));


  //     // const co2Values = co2Res.data.map((d) => d.co2);
  //     // const avg = co2Values.reduce((a, b) => a + b, 0) / co2Values.length;
  //     // setAvgCo2(Math.round(avg));

  //     // if (co2Res.data.length > 0) {
  //     //   setCurrentCo2(co2Res.data[co2Res.data.length - 1].co2);
  //     // }
  //     const filteredCo2 = filterByDuration(sortByTime(co2Res.data));
  //     setCo2Data(filteredCo2);
  //     const avg = filteredCo2.reduce((a, b) => a + b.co2, 0) / filteredCo2.length;
  //     setAvgCo2(Math.round(avg));
  //     if (filteredCo2.length > 0) setCurrentCo2(filteredCo2[filteredCo2.length - 1].co2);



  //     if (emLevel3Res.data.length > 0) {
  //       const lastL3 = emLevel3Res.data[emLevel3Res.data.length - 1];
  //       setCurrentEnergyL3(lastL3.total_act_power);
  //     }
  //     if (emLevel4Res.data.length > 0) {
  //       const lastL4 = emLevel4Res.data[emLevel4Res.data.length - 1];
  //       setCurrentEnergyL4(lastL4.total_act_power);
  //     }
  //   } catch (error) {
  //     console.error("Error fetching sensor data:", error);
  //   }
  // };
  const sortByTime = (data) =>
    data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const fetchData = async () => {
    try {
      const [co2Res, emRes, ocRes, emL3Res, emL4Res] = await Promise.all([
        axios.get(`${API_BASE_URL}/co2/history`),
        axios.get(`${API_BASE_URL}/em/history`),
        axios.get(`${API_BASE_URL}/oc/history`),
        axios.get(`${API_BASE_URL}/em/level3`),
        axios.get(`${API_BASE_URL}/em/level4`),
      ]);

      // --- CO2 ---
      const co2Sorted = sortByTime(co2Res.data);
      const co2Filtered = filterByDuration(co2Sorted);
      setCo2Data(co2Filtered);
      const avg = co2Filtered.reduce((a, b) => a + b.co2, 0) / co2Filtered.length;
      setAvgCo2(Math.round(avg) || 0);
      if (co2Filtered.length > 0)
        setCurrentCo2(co2Filtered[co2Filtered.length - 1].co2);

      // --- Energy Level 3 ---
      const l3Sorted = sortByTime(emL3Res.data);
      const l3Filtered = filterByDuration(l3Sorted);
      setEmLevel3Data(l3Filtered);
      if (l3Filtered.length > 0)
        setCurrentEnergyL3(l3Filtered[l3Filtered.length - 1].total_act_power);

      // --- Energy Level 4 ---
      const l4Sorted = sortByTime(emL4Res.data);
      const l4Filtered = filterByDuration(l4Sorted);
      setEmLevel4Data(l4Filtered);
      if (l4Filtered.length > 0)
        setCurrentEnergyL4(l4Filtered[l4Filtered.length - 1].total_act_power);

      // --- Occupancy ---
      const ocSorted = sortByTime(ocRes.data);
      const ocFiltered = filterByDuration(ocSorted);
      setOcData(ocFiltered);
    } catch (error) {
      console.error("Error fetching sensor data:", error);
    }
  };


  // useEffect(() => {
  //   fetchData();
  //   const interval = setInterval(fetchData, 5000);
  //   return () => clearInterval(interval);
  // }, []);
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [duration]); // ✅ add duration as dependency

  return (
    <div className="dashboard">
      <div style={{ padding: "0 24px", marginBottom: "16px" }}>
        <label htmlFor="duration">View duration: </label>
        <select
          id="duration"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          style={{ marginLeft: "8px", padding: "4px 8px" }}
        >
          {durationOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <p style={{ marginLeft: "24px", fontStyle: "italic", color: "#888" }}>
        Showing data: {durationOptions.find((opt) => opt.value === duration)?.label}
      </p>

      <ChartCard title="CO2 Levels (ppm)" data={co2Data} dataKeys={["co2"]} unit="ppm" />
      {/* <ChartCard title="Energy Usage - Power (W)" data={emData} dataKeys={["total_act_power"]} unit="W" /> */}
      <ChartCard title="Occupancy - Entries/Exits" data={ocData} dataKeys={["entries", "exits"]} unit="" />
      <ChartCard title="Level 3 - Energy Usage (W)" data={emLevel3Data} dataKeys={["total_act_power"]} unit="W" />
      <ChartCard title="Level 4 - Energy Usage (W)" data={emLevel4Data} dataKeys={["total_act_power"]} unit="W" />
      {/* <Co2Gauge value={currentCo2} title="Current CO₂ Level" />
      <Co2Gauge value={avgCo2} title="Hourly Avg CO₂ Level" /> */}
      <GaugeMeter value={currentCo2} title="Current CO₂ Level" />
      <GaugeMeter value={avgCo2} title="Hourly Avg CO₂ Level" />
      <MetricCard label="Current Energy - Level 3" value={currentEnergyL3} unit="W" color="#0984e3" />
      <MetricCard label="Current Energy - Level 4" value={currentEnergyL4} unit="W" color="#6c5ce7" />



    </div>
  );
}
