// src/pages/Dashboard.js
import React, { useEffect, useState } from "react";
import { getPendingSignals, getActiveSignals } from "../api/signals";
import { getPositions } from "../api/positions";
import { getTodayPnL } from "../api/pnl";
import { getOrders } from "../api/orders";
import axios from "../api/fetcher";
import Spinner from "../components/Spinner";
import { useToast } from "../context/ToastContext";

const container = {
  padding: 20,
  fontFamily: "Inter, sans-serif",
  color: "#e6eef8",
};

const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
  gap: 12,
  marginBottom: 18,
};

const card = {
  padding: 14,
  borderRadius: 12,
  background: "rgba(255,255,255,0.02)",
  border: "1px solid rgba(255,255,255,0.03)",
  boxShadow: "0 6px 18px rgba(2,6,23,0.6)",
};

const small = { fontSize: 12, color: "#9aa4b2" };
const value = { fontSize: 20, fontWeight: 700, marginTop: 8 };

const listStyle = {
  listStyle: "none",
  padding: 0,
  margin: 0,
};

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [pendingCount, setPendingCount] = useState(0);
  const [activeCount, setActiveCount] = useState(0);
  const [positionsCount, setPositionsCount] = useState(0);
  const [todayPnl, setTodayPnl] = useState(null);
  const [recentOrders, setRecentOrders] = useState([]);
  const [positions, setPositions] = useState([]);
  const [health, setHealth] = useState(null);
  const [username, setUsername] = useState(""); // 🟢 New state for username

  const { addToast } = useToast?.() || { addToast: () => {} };

  // Fetch dashboard stats
  const fetchAll = async () => {
    setLoading(true);
    try {
      const [pending, active, positionsData, pnl, orders, healthRes] =
        await Promise.all([
          getPendingSignals().catch(() => []),
          getActiveSignals().catch(() => []),
          getPositions().catch(() => []),
          getTodayPnL().catch(() => null),
          getOrders().catch(() => []),
          axios.get("/health/").catch(() => null),
        ]);

      setPendingCount(Array.isArray(pending) ? pending.length : pending.count ?? 0);
      setActiveCount(Array.isArray(active) ? active.length : active.count ?? 0);
      setPositionsCount(Array.isArray(positionsData) ? positionsData.length : 0);
      setPositions(positionsData);
      setTodayPnl(pnl || null);
      setRecentOrders(Array.isArray(orders) ? orders.slice(0, 6) : []);
      setHealth(healthRes?.data || null);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
      addToast && addToast("Failed to load dashboard data", "error");
    } finally {
      setLoading(false);
    }
  };

  // 🟢 Fetch username from backend
  const fetchUser = async () => {
    try {
      const res = await axios.get("/auth/me");
      setUsername(res.data.username || "");
    } catch (err) {
      console.error("Failed to fetch user:", err);
    }
  };

  useEffect(() => {
    fetchAll();
    fetchUser(); // 🟢 fetch username once
    const id = setInterval(fetchAll, 100000);
    return () => clearInterval(id);
  }, []);

  if (loading)
    return (
      <div style={{ padding: 40 }}>
        <Spinner />
      </div>
    );

  return (
    <div style={container}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <h2 style={{ margin: 0 }}>Dashboard</h2>
        <div style={small}>
          Hello {username ? `: ${username}` : ""}{" "}
        </div>
      </div>

      <div style={grid}>
        <div style={card}>
          <div style={small}>Pending Signals</div>
          <div style={value}>{pendingCount}</div>
        </div>

        <div style={card}>
          <div style={small}>Active Signals</div>
          <div style={value}>{activeCount}</div>
        </div>

        <div style={card}>
          <div style={small}>Today's PnL</div>
          <div style={value}>
            {todayPnl
              ? (
                  Number(todayPnl.realized || 0) +
                  Number(todayPnl.unrealized || 0)
                ).toFixed(2)
              : "—"}
          </div>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 320px",
          gap: 12,
        }}
      >
        <div style={card}>
          <h4 style={{ marginTop: 0 }}>Recent Orders</h4>
          {recentOrders.length ? (
            <ul style={listStyle}>
              {recentOrders.map((o) => (
                <li
                  key={o.id}
                  style={{
                    padding: "8px 0",
                    borderBottom: "1px dashed rgba(255,255,255,0.03)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 700 }}>
                        {o.symbol ||
                          (o.binance_order_id
                            ? `Binance order ID-${o.binance_order_id}`
                            : "order")}
                      </div>
                      <div style={small}>
                        {(() => {
                          const position = positions.find((p) => p.order_id === o.id);
                          const posStatus = position ? position.status : "-";
                          return `${o.side} • qty ${o.qty} • ${posStatus}`;
                        })()}
                      </div>
                    </div>
                    <div style={{ textAlign: "right", minWidth: 90 }}>
                      <div style={{ fontWeight: 700 }}>{o.price ?? "-"}</div>
                      <div style={small}>
                        {o.ts ? new Date(o.ts).toLocaleString() : "-"}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div style={small}>No recent orders.</div>
          )}
        </div>

        <div style={card}>
          <h4 style={{ marginTop: 0 }}>Quick Actions</h4>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <button
              className="btn primary"
              onClick={async () => {
                addToast && addToast("Refreshing dashboard...", "info");
                await fetchAll();
                addToast && addToast("Refreshed", "success");
              }}
            >
              Refresh
            </button>

            <button
              className="btn ghost"
              onClick={async () => {
                try {
                  const res = await axios.get("/binance-test/ping");
                  addToast && addToast("Binance ping OK", "success");
                } catch (err) {
                  addToast && addToast("Binance ping failed", "error");
                }
              }}
            >
              Ping Binance
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
