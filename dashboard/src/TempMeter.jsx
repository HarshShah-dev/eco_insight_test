// TempMeter.jsx
import React from "react";
import ReactSpeedometer from "react-d3-speedometer";

export default function TempMeter({ value, max = 40000, title = "Gauge" }) {
  return (
    <div className="chart-card" style={{ textAlign: "center" }}>
      <h2 className="chart-title">{title}</h2>
      <ReactSpeedometer
        value={value}
        minValue={0}
        maxValue={max}
        segments={5}
        segmentColors={["#74b9ff", "#55efc4", "#ffeaa7", "#fab1a0", "#d63031"]}
        needleColor="#2d3436"
        currentValueText={`${value} °C`}
        height={200}
        customSegmentStops={[0, 18000, 22000, 26000, 30000, 40000]}
        ringWidth={30}
        needleHeightRatio={0.7}
        valueFormat={"d"}
      />
    </div>
  );
}