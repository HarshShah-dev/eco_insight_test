// MetricCard.jsx
import React from "react";

export default function MetricCard({ label, value, unit = "", color = "#2d3436" }) {
  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <p className="metric-value" style={{ color: color }}>
        {value.toLocaleString()} {unit}
      </p>
    </div>
  );
}
