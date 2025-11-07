// src/pages/Register.js
import { useState, useEffect } from "react";
import { registerUser } from "../api/auth";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const el = document.getElementById("reg-username");
    if (el) el.focus();
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();

    // Frontend validation
    if (!username.trim()) {
      alert("Username is required.");
      return;
    }
    if (!email.includes("@") || email.length < 5) {
      alert("Please enter a valid email address.");
      return;
    }
    if (password.length < 6) {
      alert("Password must be at least 6 characters long.");
      return;
    }

    setSubmitting(true);
    try {
      await registerUser( username, email, password );
      alert("Registration successful! Please login.");
      navigate("/"); // redirect to login
    } catch (err) {
      console.error("Registration error:", err?.response || err);
      const detail = err?.response?.data?.detail;
      const msg = detail ? `Registration failed: ${JSON.stringify(detail)}` : "Registration failed! Try again.";
      alert(msg);
    } finally {
      setSubmitting(false);
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
    maxWidth: 520,
    borderRadius: 16,
    padding: "28px 28px 22px",
    background: "linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02))",
    boxShadow: "0 10px 30px rgba(2,6,23,0.6)",
    border: "1px solid rgba(255,255,255,0.04)",
    backdropFilter: "blur(6px)",
    zIndex: 20,
  };

  const header = { display: "flex", flexDirection: "column", gap: 6, marginBottom: 12 };
  const title = { fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: "-0.2px", color: "#ffffff" };
  const subtitle = { margin: 0, color: "rgba(230,238,248,0.7)", fontSize: 13 };

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
    background: "linear-gradient(90deg,#06b6d4,#7c3aed)",
    color: "white",
    boxShadow: "0 6px 18px rgba(7,11,40,0.45)",
    transformOrigin: "center",
    transition: "transform 120ms ease, box-shadow 180ms ease, opacity 180ms",
    opacity: submitting ? 0.9 : 1,
  };

  const secondaryLink = { fontSize: 13, color: "rgba(230,238,248,0.8)", textAlign: "center", marginTop: 8 };

  const blobCommon = {
    position: "absolute",
    filter: "blur(40px)",
    opacity: 0.8,
    zIndex: 10,
    mixBlendMode: "screen",
  };

  return (
    <div style={page}>
      {/* internal styles & keyframes */}
      <style>{`
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
        .reg-input:focus {
          box-shadow: 0 6px 22px rgba(2,6,23,0.6), 0 0 18px rgba(37,99,235,0.10);
          border-color: rgba(37,99,235,0.9);
          transform: translateY(-1px);
        }
        .reg-button:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 10px 30px rgba(7,11,40,0.6); }
        .blob-1 { animation: floatX 7s ease-in-out infinite; }
        .blob-2 { animation: floatY 9s ease-in-out infinite; }
        .blob-3 { animation: floatX 11s ease-in-out infinite; }
        .card-pop { transform: translateY(18px); opacity: 0; animation: popIn 520ms cubic-bezier(.2,.9,.2,1) forwards; }
        @keyframes popIn { to { transform: translateY(0); opacity: 1; } }
        @media (max-width: 520px) { .card-pop { padding: 20px !important; border-radius: 12px !important; } }
      `}</style>

      {/* decorative blobs */}
      <div
        style={{
          ...blobCommon,
          left: "-8%",
          top: "-10%",
          width: 420,
          height: 420,
          background:
            "radial-gradient(circle at 30% 30%, rgba(6,182,212,0.44), rgba(124,58,237,0.22) 40%, rgba(124,58,237,0.06) 70%)",
          borderRadius: "48%",
        }}
        className="blob-1"
        aria-hidden
      />
      <div
        style={{
          ...blobCommon,
          right: "-10%",
          bottom: "-6%",
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
          right: "52%",
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

      {/* register card */}
      <div style={card} className="card-pop" role="region" aria-label="Register panel">
        <div style={header}>
          <h1 style={title}>Create your account</h1>
          <p style={subtitle}>Sign up to start using Semi-Automated TradeBot — demo & paper trading only.</p>
        </div>

        <form style={form} onSubmit={handleRegister} aria-live="polite">
          <div>
            <label style={label} htmlFor="reg-username">Username</label>
            <input
              id="reg-username"
              className="reg-input"
              style={inputBase}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Choose a username"
              aria-label="username"
              required
            />
          </div>

          <div>
            <label style={label} htmlFor="reg-email">Email</label>
            <input
              id="reg-email"
              type="email"
              className="reg-input"
              style={inputBase}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              aria-label="email"
              required
            />
          </div>

          <div>
            <label style={label} htmlFor="reg-password">Password</label>
            <input
              id="reg-password"
              type="password"
              className="reg-input"
              style={inputBase}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              aria-label="password"
              required
            />
          </div>

          <div style={actions}>
            <button
              type="submit"
              className="reg-button"
              style={{ ...button, ...(submitting ? { opacity: 0.9, cursor: "not-allowed" } : {}) }}
              disabled={submitting}
            >
              {submitting ? "Creating..." : "Create account"}
            </button>

            <div style={secondaryLink}>
              <small>
                Already have an account?{" "}
                <a href="/" style={{ color: "#7c3aed", fontWeight: 700, textDecoration: "none" }}>
                  Sign in
                </a>
              </small>
            </div>
          </div>
        </form>

        <div style={{ marginTop: 14, display: "flex", justifyContent: "center", gap: 10, alignItems: "center" }}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: 999,
              background: "#06b6d4",
              animation: "pulseOutline 2.6s infinite ease-out",
            }}
            aria-hidden
          />
          <small style={{ color: "rgba(230,238,248,0.6)" }}>No credit card • Paper trading • Demo environment</small>
        </div>
      </div>
    </div>
  );
};

export default Register;