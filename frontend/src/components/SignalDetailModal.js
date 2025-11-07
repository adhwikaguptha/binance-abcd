// src/components/SignalDetailModal.js
import React, { useState } from "react";
import { approveSignal, rejectSignal } from "../api/signals";

const SignalDetailModal = ({ signal, onClose, onAction }) => {
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);

  // Convert JSON context to pretty text
  const prettyJson = signal?.ctx_json
    ? JSON.stringify(JSON.parse(signal.ctx_json), null, 2)
    : "";

  const handleApprove = async () => {
    setLoading(true);
    try {
      await approveSignal(signal.id, { reason });
      onAction?.(); // refresh parent table
      onClose();
    } catch (err) {
      console.error("Approve error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await rejectSignal(signal.id, { reason });
      onAction?.();
      onClose();
    } catch (err) {
      console.error("Reject error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!signal) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h5 className="modal-title">
            Signal #{signal.id} — {signal.symbol} ({signal.side})
          </h5>
          <button className="btn ghost" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="row">
            <div className="col">
              <p>
                <strong>Entry:</strong> {signal.entry}
              </p>
              <p>
                <strong>SL:</strong> {signal.sl}
              </p>
              <p>
                <strong>TP:</strong> {signal.tp ?? "-"}
              </p>
            </div>
            <div className="col">
              <p>
                <strong>Quantity:</strong> {signal.qty}
              </p>
              <p>
                <strong>Status:</strong>{" "}
                <span className={`badge ${signal.status}`}>
                  {signal.status}
                </span>
              </p>
            </div>
          </div>

          {prettyJson && (
            <div style={{ marginTop: "12px" }}>
              <h5>Context JSON</h5>
              <pre
                style={{
                  background: "rgba(255,255,255,0.03)",
                  padding: "10px",
                  borderRadius: "8px",
                  overflowX: "auto",
                  fontFamily: "monospace",
                  fontSize: "12px",
                }}
              >
                {prettyJson}
              </pre>
            </div>
          )}

          <div style={{ marginTop: "12px" }}>
            <label className="label">Reason (optional)</label>
            <textarea
              className="input"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Add a note or reason..."
              rows={3}
            />
          </div>
        </div>

        <div className="modal-footer">
          <button
            className="btn success"
            onClick={handleApprove}
            disabled={loading}
          >
            {loading ? "Approving..." : "Approve"}
          </button>
          <button
            className="btn danger"
            onClick={handleReject}
            disabled={loading}
          >
            {loading ? "Rejecting..." : "Reject"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignalDetailModal;
