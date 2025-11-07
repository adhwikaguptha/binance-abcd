// src/pages/Login.js
import { useState, useContext, useEffect } from "react";
import { loginUser } from "../api/auth";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  // small UX: focus first input when mounted
  useEffect(() => {
    const el = document.getElementById("login-username");
    if (el) el.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await loginUser(username, password);
      login(res.access_token);
      // small delay for animation feel
      setTimeout(() => navigate("/dashboard"), 300);
    } catch (err) {
      setSubmitting(false);
      // prettier error message
      const msg = err?.response?.data?.detail || "Login failed — check credentials and try again.";
      alert(msg);
    }
  };

  // Inline style objects
  const page = {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    overflow: "hidden",
    fontFamily: `'Inter', system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial`,
    color: "#e6eef8",
    padding: 20,
  };

  const card = {
    width: "100%",
    maxWidth: 480,
    borderRadius: 16,
    padding: "28px 28px 22px",
    background: "linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02))",
    boxShadow: "0 10px 30px rgba(2,6,23,0.6)",
    border: "1px solid rgba(255,255,255,0.04)",
    backdropFilter: "blur(6px)",
    zIndex: 20,
    transform: "translateY(0)",
    transition: "transform 400ms cubic-bezier(.2,.9,.2,1), opacity 400ms",
    opacity: 1,
  };

  const header = {
    display: "flex",
    flexDirection: "column",
    gap: 6,
    marginBottom: 12,
  };

  const title = {
    fontSize: 22,
    fontWeight: 700,
    margin: 0,
    letterSpacing: "-0.2px",
    color: "#ffffff",
  };

  const subtitle = {
    margin: 0,
    color: "rgba(230,238,248,0.7)",
    fontSize: 13,
  };

  const form = { display: "flex", flexDirection: "column", gap: 12, marginTop: 8 };

  const inputBase = {
    width: "100%",
    padding: "12px 14px",
    borderRadius: 10,
    border: "1px solid rgba(255,255,255,0.06)",
    background: "rgba(255,255,255,0.02)",
    color: "#e6eef8",
    outline: "none",
    fontSize: 14,
    transition: "box-shadow 220ms, transform 180ms, border-color 220ms",
  };

  const label = { fontSize: 13, color: "rgba(230,238,248,0.7)", marginBottom: 6 };

  const actions = { display: "flex", flexDirection: "column", gap: 10, marginTop: 6 };

  const button = {
    padding: "10px 12px",
    borderRadius: 10,
    border: "none",
    cursor: submitting ? "not-allowed" : "pointer",
    fontWeight: 700,
    letterSpacing: "0.3px",
    background: "linear-gradient(90deg,#7c3aed,#06b6d4)",
    color: "white",
    boxShadow: "0 6px 18px rgba(7,11,40,0.45)",
    transformOrigin: "center",
    transition: "transform 120ms ease, box-shadow 180ms ease, opacity 180ms",
    opacity: submitting ? 0.8 : 1,
  };

  const secondaryLink = { fontSize: 13, color: "rgba(230,238,248,0.8)", textAlign: "center", marginTop: 8 };

  // floating decorative blobs (absolutely positioned)
  const blobCommon = {
    position: "absolute",
    filter: "blur(40px)",
    opacity: 0.8,
    zIndex: 10,
    mixBlendMode: "screen",
  };

  return (
    <div style={page}>
      {/* Inject keyframes & small helper CSS (self-contained) */}
      <style>{`
        /* keyframes for blobs and card pop */
        @keyframes floatX {
          0% { transform: translateY(0) translateX(0) rotate(0deg); }
          50% { transform: translateY(-12px) translateX(6px) rotate(6deg); }
          100% { transform: translateY(0) translateX(0) rotate(0deg); }
        }
        @keyframes floatY {
          0% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-18px) scale(1.03); }
          100% { transform: translateY(0) scale(1); }
        }
        @keyframes pulseOutline {
          0% { box-shadow: 0 0 0 0 rgba(37,99,235,0.12); }
          70% { box-shadow: 0 0 0 14px rgba(37,99,235,0); }
          100% { box-shadow: 0 0 0 0 rgba(37,99,235,0); }
        }

        /* input focus glow */
        .login-input:focus {
          box-shadow: 0 6px 22px rgba(2,6,23,0.6), 0 0 18px rgba(37,99,235,0.10);
          border-color: rgba(37,99,235,0.9);
          transform: translateY(-1px);
        }

        .login-button:active { transform: translateY(1px) scale(0.997); }
        .login-button:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 10px 30px rgba(7,11,40,0.6); }

        /* floating blob animations */
        .blob-1 { animation: floatX 7s ease-in-out infinite; }
        .blob-2 { animation: floatY 9s ease-in-out infinite; }
        .blob-3 { animation: floatX 11s ease-in-out infinite; }

        /* subtle entrance */
        .card-entrance { transform: translateY(18px); opacity: 0; animation: popIn 520ms cubic-bezier(.2,.9,.2,1) forwards; }
        @keyframes popIn {
          to { transform: translateY(0); opacity: 1; }
        }

        /* small responsive tweak */
        @media (max-width: 520px) {
          .card-entrance { padding: 20px !important; border-radius: 12px !important; }
        }
      `}</style>

      {/* decorative blobs */}
      <div
        style={{
          ...blobCommon,
          left: "-6%",
          top: "-8%",
          width: 420,
          height: 420,
          background:
            "radial-gradient(circle at 30% 30%, rgba(124,58,237,0.44), rgba(6,182,212,0.22) 40%, rgba(6,182,212,0.06) 70%)",
          borderRadius: "48%",
        }}
        className="blob-1"
        aria-hidden
      />
      <div
        style={{
          ...blobCommon,
          right: "-10%",
          bottom: "-8%",
          width: 360,
          height: 360,
          background:
            "radial-gradient(circle at 70% 70%, rgba(16,185,129,0.36), rgba(56,189,248,0.14) 40%, rgba(124,58,237,0.04) 70%)",
          borderRadius: "44%",
        }}
        className="blob-2"
        aria-hidden
      />
      <div
        style={{
          ...blobCommon,
          left: "60%",
          top: "6%",
          width: 220,
          height: 220,
          background:
            "radial-gradient(circle at 20% 20%, rgba(249,115,22,0.28), rgba(252,211,77,0.06) 40%)",
          borderRadius: "50%",
        }}
        className="blob-3"
        aria-hidden
      />

      {/* login card */}
      <div style={card} className="card-entrance" role="region" aria-label="Login panel">
        <div style={header}>
          <h1 style={title}>Welcome back.</h1>
          <p style={subtitle}>Sign in to your Semi-Automated TradeBot account</p>
        </div>

        <form style={form} onSubmit={handleSubmit} aria-live="polite">
          <div>
            <label style={label} htmlFor="login-username">Username</label>
            <input
              id="login-username"
              className="login-input"
              style={inputBase}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g., alice"
              aria-label="username"
              required
            />
          </div>

          <div>
            <label style={label} htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              className="login-input"
              style={inputBase}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Your password"
              aria-label="password"
              required
            />
          </div>

          <div style={actions}>
            <button
              type="submit"
              className="login-button"
              style={{ ...button, ...(submitting ? { transform: "scale(0.997)", opacity: 0.9 } : {}) }}
              disabled={submitting}
            >
              {submitting ? "Signing in..." : "Sign in"}
            </button>

            <div style={secondaryLink}>
              <small>
                Don't have an account?{" "}
                <a href="/register" style={{ color: "#7c3aed", fontWeight: 700, textDecoration: "none" }}>
                  Create one
                </a>
              </small>
            </div>
          </div>
        </form>

        {/* subtle footer / animated ring */}
        <div style={{ marginTop: 14, display: "flex", justifyContent: "center", gap: 10, alignItems: "center" }}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: 999,
              background: "#2563eb",
              animation: "pulseOutline 2.6s infinite ease-out",
            }}
            aria-hidden
          />
          <small style={{ color: "rgba(230,238,248,0.6)" }}>Secure · Paper trading only · Demo mode</small>
        </div>
      </div>
    </div>
  );
};

export default Login;