import React, { useEffect, useState } from "react";
import { getOrders } from "../api/orders";

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

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const data = await getOrders("ETHUSDT"); // default symbol
        setOrders(data);
      } catch (err) {
        console.error("Error fetching orders:", err.response || err);
        setError(err.response?.data?.detail || "Failed to fetch orders");
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  if (loading) return <div style={container}>Loading orders...</div>;
  if (error) return <div style={container}>Error: {error}</div>;

  return (
    <div style={container}>
      <h2>Orders</h2>
      {orders.length === 0 ? (
        <p>You havent place any order yet!!!.</p>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thTd}>Signal ID</th>
              <th style={thTd}>Side</th>
              <th style={thTd}>Qty</th>
              <th style={thTd}>Price</th>
              <th style={thTd}>SL</th>
              <th style={thTd}>TP</th>
              <th style={thTd}>Binance ID</th>
              <th style={thTd}>Status</th>
              <th style={thTd}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={`order-${o.id}`}>
                <td style={thTd}>{o.signal_id}</td>
                <td style={thTd}>{o.side}</td>
                <td style={thTd}>{o.qty}</td>
                <td style={thTd}>{o.price}</td>
                <td style={thTd}>{o.sl ?? "-"}</td>
                <td style={thTd}>{o.tp ?? "-"}</td>
                <td style={thTd}>{o.binance_order_id ?? "-"}</td>
                <td style={thTd}>{o.status}</td>
                <td style={thTd}>
                  {o.ts ? new Date(o.ts).toLocaleString() : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Orders;
