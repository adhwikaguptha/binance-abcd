import React, { useState } from "react";
import { placeTrade } from "../api/trade";

const Trade = () => {
  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState("BUY");
  const [qty, setQty] = useState(0);

  const handleTrade = async () => {
    try {
      await placeTrade({ symbol, side, qty });
      alert("Trade executed successfully!");
    } catch (err) {
      alert("Trade execution failed!");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Manual Trade</h2>
      <input placeholder="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
      <select value={side} onChange={(e) => setSide(e.target.value)}>
        <option value="BUY">BUY</option>
        <option value="SELL">SELL</option>
      </select>
      <input
        type="number"
        placeholder="Quantity"
        value={qty}
        onChange={(e) => setQty(Number(e.target.value))}
      />
      <button onClick={handleTrade}>Execute Trade</button>
    </div>
  );
};

export default Trade;
