// MetricCard.jsx
import React from "react";

export default function MetricCard({ label, value, unit = "", color = "#2d3436", extra }) {
  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <p className="metric-value" style={{ color: color }}>
        {value.toLocaleString()} {unit}
      </p>
      {extra && (
        <p style={{ fontSize: '18px', color: '#636e72', margin: 0 }}>{extra}</p>
      )}
    </div>
  );
}
