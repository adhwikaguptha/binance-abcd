import React, { useEffect, useState } from "react";
import { getPositions } from "../api/positions";

const container = {
  padding: "20px",
  color: "#e6eef8",
  fontFamily: "Inter, sans-serif",
};

const tableStyle = {
  width: "100%",
  borderCollapse: "collapse",
};

const thTd = {
  padding: "10px",
  textAlign: "left",
  borderBottom: "1px solid rgba(255,255,255,0.1)",
  fontSize: "14px",
};

const Positions = () => {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const data = await getPositions();
        setPositions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPositions();
  }, []);

  if (loading) return <div style={container}>Loading positions...</div>;

  return (
    <div style={container}>
      <h2>Open Positions</h2>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th style={thTd}>Symbol</th>
            <th style={thTd}>Qty</th>
            <th style={thTd}>Avg Price</th>
            <th style={thTd}>SL</th>
            <th style={thTd}>TP</th>
            <th style={thTd}>Side</th>
            <th style={thTd}>Status</th>
            <th style={thTd}>Opened At</th>
            <th style={thTd}>Closed At</th>
            <th style={thTd}>Exit Price</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((p) => (
            <tr key={p.id}>
              <td style={thTd}>{p.symbol}</td>
              <td style={thTd}>{p.qty}</td>
              <td style={thTd}>{p.avg_price}</td>
              <td style={thTd}>{p.sl}</td>
              <td style={thTd}>{p.tp}</td>
              <td style={thTd}>{p.side}</td>
              <td style={thTd}>{p.status}</td>
              <td style={thTd}>{new Date(p.opened_at).toLocaleString()}</td>
              <td style={thTd}>
                {p.closed_at ? new Date(p.closed_at).toLocaleString() : "-"}
              </td>
              <td style={thTd}>{p.exit_price ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Positions;
