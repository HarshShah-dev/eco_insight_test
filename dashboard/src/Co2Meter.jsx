// Co2Meter.jsx
import React from "react";
import ReactSpeedometer from "react-d3-speedometer";

export default function Co2Meter({ value, max = 2000, title = "Gauge" }) {
  return (
    <div className="chart-card" style={{ textAlign: "center" }}>
      <h2 className="chart-title">{title}</h2>
      <ReactSpeedometer
        value={value}
        minValue={0}
        maxValue={max}
        segments={5}
        segmentColors={["#00b894", "#55efc4", "#ffeaa7", "#fab1a0", "#d63031"]}
        needleColor="#2d3436"
        currentValueText={`${value} ppm`}
        height={200}
        customSegmentStops={[0, 600, 800, 1000, 1400, max]}
        ringWidth={30}
        needleHeightRatio={0.7}
        valueFormat={"d"}
      />
    </div>
  );
}

