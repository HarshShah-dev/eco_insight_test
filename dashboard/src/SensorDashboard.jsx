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

const ChartCard = ({ title, data, dataKeys, unit, duration, onDurationChange, durationOptions }) => (
  <div className="chart-card">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
      <h2 className="chart-title">{title}</h2>
      <select
        value={duration}
        onChange={(e) => onDurationChange(e.target.value)}
        style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid #ccc' }}
      >
        {durationOptions.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
    {data.length > 0 ? (
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={(str) => {
              try {
                const date = new Date(str);
                return date.toLocaleString([], {
                  month: "short",
                  day: "numeric",
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
  const [recommendation, setRecommendation] = useState("Loading...");

  useEffect(() => {
    const fetchRec = async () => {
      try {
        const res = await axios.get("/api/recommendation/");
        setRecommendation(res.data.recommendation || "No recommendation");
      } catch (error) {
        console.error("Failed to fetch recommendation", error);
        setRecommendation("Error fetching recommendation");
      }
    };
    fetchRec();
    const interval = setInterval(fetchRec, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="recommendation-panel">
      <h2 className="chart-title">AI Recommendation</h2>
      <p style={{ fontSize: "18px", padding: "8px", lineHeight: 1.4 }}>{recommendation}</p>
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
  const [avgEnergyL3, setAvgEnergyL3] = useState(0);
  const [avgEnergyL4, setAvgEnergyL4] = useState(0);
  const [peakEnergyL3, setPeakEnergyL3] = useState({ value: 0, time: null });
  const [peakEnergyL4, setPeakEnergyL4] = useState({ value: 0, time: null });
  const [currentTemp, setCurrentTemp] = useState(0);
  const [peoplePresent, setPeoplePresent] = useState(0);
  const [radarData, setRadarData] = useState([]);

  // Individual durations for each chart
  const [co2Duration, setCo2Duration] = useState("1mo");
  const [tempDuration, setTempDuration] = useState("1mo");
  const [energyL3Duration, setEnergyL3Duration] = useState("1mo");
  const [energyL4Duration, setEnergyL4Duration] = useState("1mo");
  const [occupancyDuration, setOccupancyDuration] = useState("1mo");

  const durationOptions = [
    { label: "Last 1 hour", value: "1h" },
    { label: "Last 24 hours", value: "24h" },
    { label: "Last 7 days", value: "7d" },
    { label: "Last month", value: "1mo" },
    { label: "Last 3 months", value: "3mo" },
    { label: "Last 6 months", value: "6mo" },
    { label: "All time", value: "all" },
  ];

  const filterByDuration = (data, selectedDuration) => {
    const now = new Date();
    let cutoff;
    switch (selectedDuration) {
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

  const calculateAverage = (data, key) => {
    if (!data || data.length === 0) return 0;
    const sum = data.reduce((acc, item) => acc + (item[key] || 0), 0);
    return Math.round(sum / data.length);
  };

  const calculatePeak = (data, key) => {
    if (!data || data.length === 0) return { value: 0, time: null };
    let max = -Infinity;
    let maxTime = null;
    data.forEach(item => {
      if ((item[key] || 0) > max) {
        max = item[key] || 0;
        maxTime = item.timestamp;
      }
    });
    return { value: max, time: maxTime };
  };

  const groupOccupancyBySensorSorted = (data) => {
    const grouped = {};

    data.forEach(entry => {
      const sensor = entry.sensor;
      const sensorId = sensor?.sensor_id || "unknown";

      if (!grouped[sensorId]) {
        grouped[sensorId] = {
          sensor,
          data: [],
        };
      }

      grouped[sensorId].data.push(entry);
    });

    // Convert to array and sort by floor
    return Object.entries(grouped).sort(
      ([, a], [, b]) => (a.sensor.floor ?? -1) - (b.sensor.floor ?? -1)
    );
  };

  const getLatestRadarBySensor = (data) => {
    const latest = {};

    for (const entry of data) {
      const id = entry.sensor?.sensor_id;
      if (!id) continue;

      if (!latest[id] || new Date(entry.timestamp) > new Date(latest[id].timestamp)) {
        latest[id] = entry;
      }
    }

    // Convert to sorted array by floor
    return Object.values(latest).sort((a, b) => (a.sensor?.floor ?? -1) - (b.sensor?.floor ?? -1));
  };


  const fetchData = async () => {
    try {
      const [co2Res, emRes, ocRes, emL3Res, emL4Res, radarRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/co2/history`),
        axios.get(`${API_BASE_URL}/em/history`),
        axios.get(`${API_BASE_URL}/oc/history`),
        axios.get(`${API_BASE_URL}/em/history/level3`),
        axios.get(`${API_BASE_URL}/em/history/level4`),
        axios.get(`${API_BASE_URL}/radar/history`),
      ]);

      const co2Sorted = sortByTime(co2Res.data);
      const co2Filtered = filterByDuration(co2Sorted, co2Duration);
      setCo2Data(co2Filtered);
      const avg = co2Filtered.length ? co2Filtered.reduce((a, b) => a + b.co2, 0) / co2Filtered.length : 0;
      setAvgCo2(Math.round(avg));
      if (co2Filtered.length > 0) {
        setCurrentCo2(co2Filtered[co2Filtered.length - 1].co2);
        setCurrentTemp(co2Filtered[co2Filtered.length - 1].temp);
      }

      const l3Sorted = sortByTime(emL3Res.data);
      const l3Filtered = filterByDuration(l3Sorted, energyL3Duration);
      setEmLevel3Data(l3Filtered);
      if (l3Filtered.length > 0) {
        setCurrentEnergyL3(l3Filtered[l3Filtered.length - 1].total_act_power);
        setAvgEnergyL3(calculateAverage(l3Filtered, 'total_act_power'));
        setPeakEnergyL3(calculatePeak(l3Filtered, 'total_act_power'));
      }

      const l4Sorted = sortByTime(emL4Res.data);
      const l4Filtered = filterByDuration(l4Sorted, energyL4Duration);
      setEmLevel4Data(l4Filtered);
      if (l4Filtered.length > 0) {
        setCurrentEnergyL4(l4Filtered[l4Filtered.length - 1].total_act_power);
        setAvgEnergyL4(calculateAverage(l4Filtered, 'total_act_power'));
        setPeakEnergyL4(calculatePeak(l4Filtered, 'total_act_power'));
      }

      setRadarData(radarRes.data);

      const ocSorted = sortByTime(ocRes.data);
      const ocFiltered = filterByDuration(ocSorted, occupancyDuration);
      setOcData(ocFiltered);
      if (ocFiltered.length > 0) {
        const last = ocFiltered[ocFiltered.length - 1];
        const present = Math.max(0, (last.total_entries || 0) - (last.total_exits || 0));
        setPeoplePresent(present);
      } else {
        setPeoplePresent(0);
      }
    } catch (error) {
      console.error("Error fetching sensor data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [co2Duration, tempDuration, energyL3Duration, energyL4Duration, occupancyDuration]);

  return (
    <div className="dashboard">
      {section === "all" && <RecommendationPanel />}

      {(section === "all" || section === "air") && (
        <>
          <ChartCard 
            title="CO2 Levels (ppm)" 
            data={co2Data} 
            dataKeys={["co2"]} 
            unit="ppm" 
            duration={co2Duration}
            onDurationChange={setCo2Duration}
            durationOptions={durationOptions}
          />
          <ChartCard 
            title="Temperature (°C)" 
            data={co2Data} 
            dataKeys={["temp"]} 
            unit="°C" 
            duration={tempDuration}
            onDurationChange={setTempDuration}
            durationOptions={durationOptions}
          />
          <Co2Meter value={currentCo2} title="Current CO₂ Level" />
          <Co2Meter value={avgCo2} title={`Avg CO₂ (${durationOptions.find(opt => opt.value === co2Duration)?.label})`} />
          <TempMeter value={currentTemp} title="Current Temperature" max={45} />
        </>
      )}

      {(section === "all" || section === "energy") && (
        <>
          <ChartCard 
            title="Level 3 - Energy Usage (W)" 
            data={emLevel3Data} 
            dataKeys={["total_act_power"]} 
            unit="W" 
            duration={energyL3Duration}
            onDurationChange={setEnergyL3Duration}
            durationOptions={durationOptions}
          />
          <ChartCard 
            title="Level 4 - Energy Usage (W)" 
            data={emLevel4Data} 
            dataKeys={["total_act_power"]} 
            unit="W" 
            duration={energyL4Duration}
            onDurationChange={setEnergyL4Duration}
            durationOptions={durationOptions}
          />
          <MetricCard 
            label="Current Energy - Level 3" 
            value={currentEnergyL3} 
            unit="W" 
            color="#0984e3" 
          />
          <MetricCard 
            label={`Avg Energy - Level 3 (${durationOptions.find(opt => opt.value === energyL3Duration)?.label})`}
            value={avgEnergyL3}
            unit="W"
            color="#0984e3"
          />
          <MetricCard 
            label={`Peak Energy - Level 3 (${durationOptions.find(opt => opt.value === energyL3Duration)?.label})`}
            value={peakEnergyL3.value}
            unit="W"
            color="#0984e3"
            extra={peakEnergyL3.time ? `at ${new Date(peakEnergyL3.time).toLocaleString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', month: 'short', day: 'numeric' })}` : ''}
          />
          <MetricCard 
            label="Current Energy - Level 4" 
            value={currentEnergyL4} 
            unit="W" 
            color="#6c5ce7" 
          />
          <MetricCard 
            label={`Avg Energy - Level 4 (${durationOptions.find(opt => opt.value === energyL4Duration)?.label})`}
            value={avgEnergyL4}
            unit="W"
            color="#6c5ce7"
          />
          <MetricCard 
            label={`Peak Energy - Level 4 (${durationOptions.find(opt => opt.value === energyL4Duration)?.label})`}
            value={peakEnergyL4.value}
            unit="W"
            color="#6c5ce7"
            extra={peakEnergyL4.time ? `at ${new Date(peakEnergyL4.time).toLocaleString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', month: 'short', day: 'numeric' })}` : ''}
          />
        </>
      )}

      {(section === "all" || section === "occupancy") && (
        <>
          {groupOccupancyBySensorSorted(ocData).map(([sensorId, { sensor, data }]) => {
            const latest = data[data.length - 1];
            const peoplePresent = Math.max(0, (latest?.total_entries || 0) - (latest?.total_exits || 0));
            const floor = sensor?.floor ?? "?";
            const office = sensor?.office ?? "?";

            return (
              <React.Fragment key={sensorId}>
                <ChartCard
                  title={`Occupancy: ${sensorId} (Floor ${floor}, ${office})`}
                  data={data}
                  dataKeys={["total_entries", "total_exits"]}
                  unit=""
                  duration={occupancyDuration}
                  onDurationChange={setOccupancyDuration}
                  durationOptions={durationOptions}
                />
                <MetricCard
                  label={`People Present — ${sensorId}`}
                  value={peoplePresent}
                  unit=""
                  color="#00b894"
                  extra={`Floor ${floor}, ${office}`}
                />
              </React.Fragment>
            );
          })}
          {getLatestRadarBySensor(radarData).map((entry) => (
            <MetricCard
              key={entry.sensor.sensor_id}
              label={`People Detected — ${entry.sensor.sensor_id}`}
              value={entry.num_targets}
              unit=""
              color="#fdcb6e"
              extra={`Floor ${entry.sensor.floor ?? "?"}, ${entry.sensor.office ?? "?"}`}
            />
          ))}
        </>
      )}
    </div>
  );
}
