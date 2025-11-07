import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { logout } from "../utils/auth";

const Header = () => {
  const { setToken } = useContext(AuthContext);
  const navigate = useNavigate();
  const username = localStorage.getItem("username") || "Trader";
  const [menuOpen, setMenuOpen] = useState(false);

 const handleLogout = () => {
  logout();
};

  return (
    <header style={headerStyle}>
      <h3>Semi-Auto TradeBot</h3>
      <button onClick={() => setMenuOpen(!menuOpen)} className="mobile-menu-btn">
        ☰
      </button>
      <div style={{ display: menuOpen ? "flex" : "none", flexDirection: "column", gap: "10px" }} className="mobile-menu">
        <span>Hello, {username}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </header>
  );
};

const headerStyle = {
  padding: "10px 20px",
  background: "#1e293b",
  color: "#fff",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

export default Header;
