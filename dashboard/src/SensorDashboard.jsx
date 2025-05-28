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
import "./SensorDashboard.css";
import Co2Meter from "./Co2Meter";
import MetricCard from "./MetricCard";
import TempMeter from "./TempMeter";

const API_BASE_URL = "/api/data";

const ChartCard = ({ title, data, dataKeys, unit }) => (
  <div className="chart-card">
    <h2 className="chart-title">{title}</h2>
    {data.length > 0 ? (
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={(str) => {
              try {
                return new Date(str).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                });
              } catch {
                return "";
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

const RecommendationPanel = () => {
  const dummyRecommendations = [
    "Reduce HVAC load in unoccupied zones: Occupancy sensors indicate low presence on Level 3.",
    "Increase ventilation on Level 4: CO₂ levels exceed 1000 ppm, suggesting limited fresh air.",
    "Shift non-critical equipment usage to off-peak hours: High energy draw detected between 2–4 PM.",
  ];

  return (
    <div className="recommendation-panel">
      <h2 className="chart-title">AI Recommendations</h2>
      <ul>
        {dummyRecommendations.map((rec, index) => (
          <li key={index} style={{ marginBottom: "8px", fontSize: "16px" }}>{rec}</li>
        ))}
      </ul>
    </div>
  );
};

export default function SensorDashboard({ section = "all" }) {
  const [co2Data, setCo2Data] = useState([]);
  const [emData, setEmData] = useState([]);
  const [ocData, setOcData] = useState([]);
  const [emLevel3Data, setEmLevel3Data] = useState([]);
  const [emLevel4Data, setEmLevel4Data] = useState([]);
  const [avgCo2, setAvgCo2] = useState(0);
  const [currentCo2, setCurrentCo2] = useState(0);
  const [currentEnergyL3, setCurrentEnergyL3] = useState(0);
  const [currentEnergyL4, setCurrentEnergyL4] = useState(0);
  const [duration, setDuration] = useState("1mo");
  const [currentTemp, setCurrentTemp] = useState(0);

  const durationOptions = [
    { label: "Last 1 hour", value: "1h" },
    { label: "Last 24 hours", value: "24h" },
    { label: "Last 7 days", value: "7d" },
    { label: "Last month", value: "1mo" },
    { label: "Last 3 months", value: "3mo" },
    { label: "Last 6 months", value: "6mo" },
    { label: "All time", value: "all" },
  ];

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
        cutoff = new Date();
        cutoff.setMonth(now.getMonth() - 1);
        break;
      case "3mo":
        cutoff = new Date();
        cutoff.setMonth(now.getMonth() - 3);
        break;
      case "6mo":
        cutoff = new Date();
        cutoff.setMonth(now.getMonth() - 6);
        break;
      case "all":
      default:
        return data;
    }
    return data.filter((d) => new Date(d.timestamp) >= cutoff);
  };

  const sortByTime = (data) => data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

  const fetchData = async () => {
    try {
      const [co2Res, emRes, ocRes, emL3Res, emL4Res] = await Promise.all([
        axios.get(`${API_BASE_URL}/co2/history`),
        axios.get(`${API_BASE_URL}/em/history`),
        axios.get(`${API_BASE_URL}/oc/history`),
        axios.get(`${API_BASE_URL}/em/history/level3`),
        axios.get(`${API_BASE_URL}/em/history/level4`),
      ]);

      const co2Filtered = filterByDuration(sortByTime(co2Res.data));
      setCo2Data(co2Filtered);
      const avg = co2Filtered.length ? co2Filtered.reduce((a, b) => a + b.co2, 0) / co2Filtered.length : 0;
      setAvgCo2(Math.round(avg));
      if (co2Filtered.length > 0) {
        setCurrentCo2(co2Filtered[co2Filtered.length - 1].co2);
        setCurrentTemp(co2Filtered[co2Filtered.length - 1].temp);
      }

      const l3Filtered = filterByDuration(sortByTime(emL3Res.data));
      setEmLevel3Data(l3Filtered);
      if (l3Filtered.length > 0)
        setCurrentEnergyL3(l3Filtered[l3Filtered.length - 1].total_act_power);

      const l4Filtered = filterByDuration(sortByTime(emL4Res.data));
      setEmLevel4Data(l4Filtered);
      if (l4Filtered.length > 0)
        setCurrentEnergyL4(l4Filtered[l4Filtered.length - 1].total_act_power);

      setOcData(filterByDuration(sortByTime(ocRes.data)));
    } catch (error) {
      console.error("Error fetching sensor data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [duration]);

  return (
    <div className="dashboard">
      {section === "all" && <RecommendationPanel />}
      {section === "all" && (
        <div style={{ padding: "0 24px", marginBottom: "16px" }}>
          <label htmlFor="duration">View duration: </label>
          <select
            id="duration"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            style={{ marginLeft: "8px", padding: "4px 8px" }}
          >
            {durationOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      )}

      {(section === "all" || section === "air") && (
        <>
          <ChartCard title="CO2 Levels (ppm)" data={co2Data} dataKeys={["co2"]} unit="ppm" />
          <ChartCard title="Temperature (°C)" data={co2Data} dataKeys={["temp"]} unit="°C" />
          <Co2Meter value={currentCo2} title="Current CO₂ Level" />
          <Co2Meter value={avgCo2} title={`Avg CO₂ (${durationOptions.find(opt => opt.value === duration)?.label})`} />
          <TempMeter value={currentTemp} title="Current Temperature" max={40000} />
        </>
      )}

      {(section === "all" || section === "energy") && (
        <>
          <ChartCard title="Level 3 - Energy Usage (W)" data={emLevel3Data} dataKeys={["total_act_power"]} unit="W" />
          <ChartCard title="Level 4 - Energy Usage (W)" data={emLevel4Data} dataKeys={["total_act_power"]} unit="W" />
          <MetricCard label="Current Energy - Level 3" value={currentEnergyL3} unit="W" color="#0984e3" />
          <MetricCard label="Current Energy - Level 4" value={currentEnergyL4} unit="W" color="#6c5ce7" />
        </>
      )}

      {(section === "all" || section === "occupancy") && (
        <ChartCard title="Occupancy - Entries/Exits" data={ocData} dataKeys={["entries", "exits"]} unit="" />
      )}
    </div>
  );
}
