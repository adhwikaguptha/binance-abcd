import React, { useState } from "react";
import { NavLink } from "react-router-dom";

const Sidebar = () => {
  const [open, setOpen] = useState(true);

  const linkStyle = { color: "#e6eef8", textDecoration: "none", margin: "8px 0" };
  const activeStyle = { fontWeight: "bold", color: "#2563eb" }; // used now

  return (
    <div style={{ ...sidebarStyle, width: open ? "200px" : "60px" }}>
      <button onClick={() => setOpen(!open)} style={{ marginBottom: "15px" }}>
        {open ? "⏴" : "⏵"}
      </button>
      {[
        { path: "/dashboard", label: "Dashboard" },
        { path: "/signals", label: "Signals" },
        { path: "/positions", label: "Positions" },
        { path: "/orders", label: "Orders" },
        { path: "/pnl", label: "PnL" },
        //{ path: "/risk", label: "Risk Settings" },
        { path: "/binance-test", label: "Binance Test" },
        { path: "/health", label: "Health" },
      ].map((link) => (
        <NavLink
          key={link.path}
          to={link.path}
          style={({ isActive }) => (isActive ? { ...linkStyle, ...activeStyle } : linkStyle)}
        >
          {link.label}
        </NavLink>
      ))}
    </div>
  );
};

const sidebarStyle = {
  minHeight: "100vh",
  background: "#0f172a",
  color: "#e6eef8",
  padding: "20px",
  display: "flex",
  flexDirection: "column",
};

export default Sidebar;
