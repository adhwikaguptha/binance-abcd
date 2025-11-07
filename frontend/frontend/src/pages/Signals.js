// src/pages/Signals.js
import React, { useEffect, useState, useCallback } from "react";
import {
  getPendingSignals,
  getAllSignals,
  approveSignal,
  rejectSignal,
  getActiveSignals,
  getSignal,
} from "../api/signals";
import SignalDetailModal from "../components/SignalDetailModal";

/**
 * Signals page:
 * - shows table of signals
 * - supports filter: pending / active / all
 * - polls for pending signals every 5s
 * - optimistic UI on approve/reject
 */

const POLL_INTERVAL_MS = 150000;

const formatDate = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString();
};

const Signals = () => {
  const [filter, setFilter] = useState("pending"); // 'pending'|'active'|'all'
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState(null);

  const fetchSignals = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (filter === "pending") data = await getPendingSignals();
      else if (filter === "active") data = await getActiveSignals();
      else data = await getAllSignals();
      setSignals(data || []);
    } catch (err) {
      console.error("Failed to fetch signals", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    // initial fetch
    fetchSignals();

    // polling (only for pending by default to reduce load)
    const interval = setInterval(() => {
      // For 'pending' filter continue polling; if user switched to 'all' maybe still poll
      fetchSignals();
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [fetchSignals]);

  const openDetail = async (sig) => {
    // Optionally fetch single signal detail
    try {
      const data = await getSignal(sig.id);
      setSelected(data || sig);
    } catch {
      setSelected(sig);
    }
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelected(null);
  };

  // optimistic update helper
  const updateLocalStatus = (id, newStatus) => {
    setSignals((prev) => prev.map((s) => (s.id === id ? { ...s, status: newStatus } : s)));
  };

  const handleApprove = async (id, payload = {}) => {
    // Optimistic: mark approved locally
    const prev = signals.find((s) => s.id === id);
    updateLocalStatus(id, "approved");

    try {
      await approveSignal(id, payload);
      // optionally refetch to get authoritative data
      fetchSignals();
    } catch (err) {
      // revert
      updateLocalStatus(id, prev?.status || "pending");
      console.error("Approve API failed", err);
      throw err;
    }
  };

  const handleReject = async (id, payload = {}) => {
    const prev = signals.find((s) => s.id === id);
    updateLocalStatus(id, "rejected");

    try {
      await rejectSignal(id, payload);
      fetchSignals();
    } catch (err) {
      updateLocalStatus(id, prev?.status || "pending");
      console.error("Reject API failed", err);
      throw err;
    }
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3>Signals</h3>
        <div>
          <div className="btn-group" role="group">
            <button className={`btn btn-sm ${filter === "pending" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setFilter("pending")}>
              Pending
            </button>
            <button className={`btn btn-sm ${filter === "active" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setFilter("active")}>
              Active
            </button>
            <button className={`btn btn-sm ${filter === "all" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setFilter("all")}>
              All
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger">
          Error fetching signals: {error?.response?.data?.detail || error.message}
        </div>
      )}

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Symbol</th>
              <th>Side</th>
              <th>Entry</th>
              <th>SL</th>
              <th>TP</th>
              <th>Qty</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="10" className="text-center">Loading...</td>
              </tr>
            ) : signals.length === 0 ? (
              <tr>
                <td colSpan="10" className="text-center">No signals</td>
              </tr>
            ) : (
              signals.map((s) => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.symbol}</td>
                  <td>{s.side}</td>
                  <td>{s.entry}</td>
                  <td>{s.sl}</td>
                  <td>{s.tp || "—"}</td>
                  <td>{s.qty || "—"}</td>
                  <td>
                    <span className={`badge ${s.status === "pending" ? "pending" : s.status === "approved" ? "approved" : s.status === "rejected" ? "rejected" : ""}`}>
                    {s.status}
                    </span>

                  </td>
                  <td>{formatDate(s.created_at || s.ts)}</td>
                  <td>
                    <div className="btn-group" role="group">
                      <button className="btn btn-sm btn-outline-primary" onClick={() => openDetail(s)}>View</button>
                      {s.status === "pending" && (
                        <>
                          <button
                            className="btn btn-sm btn-success"
                            onClick={async () => {
                              try {
                                await handleApprove(s.id, {});
                                // feedback
                                // Optionally: show toast
                              } catch (err) {
                                alert("Approve failed");
                              }
                            }}
                          >
                            Approve
                          </button>
                          <button
                            className="btn btn-sm btn-danger"
                            onClick={async () => {
                              try {
                                await handleReject(s.id, { reason: "Rejected from UI" });
                              } catch (err) {
                                alert("Reject failed");
                              }
                            }}
                          >
                            Reject
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      <SignalDetailModal
        show={modalOpen}
        onClose={closeModal}
        signal={selected}
        onApprove={async (id, opts) => {
          await handleApprove(id, opts);
        }}
        onReject={async (id, opts) => {
          await handleReject(id, opts);
        }}
      />
    </div>
  );
};

export default Signals;
