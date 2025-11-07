import React from "react";

const spinnerStyle = {
  display: "inline-block",
  width: "40px",
  height: "40px",
  border: "4px solid rgba(0,0,0,0.1)",
  borderTop: "4px solid #2563eb",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
};

const Spinner = () => <div style={spinnerStyle}></div>;

export default Spinner;
