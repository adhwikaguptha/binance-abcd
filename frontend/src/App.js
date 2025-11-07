import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { AuthProvider } from "./context/AuthContext";
import Register from "./pages/Register";
import Signals from "./pages/Signals";
import Positions from "./pages/Positions";
import Orders from "./pages/Orders";
import PnL from "./pages/PnL";
import Risk from "./pages/Risk";
import BinanceTest from "./pages/BinanceTest";
import Health from "./pages/Health";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";
import { ToastProvider } from "./context/ToastContext";
import ErrorBoundary from "./components/ErrorBoundary";
import Trade from "./pages/Trade";

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <ErrorBoundary>

      <Router>
        <div style={{ display: "flex" }}>
          <Sidebar /> {/* optional: show only if logged in */}
          <div style={{ flex: 1 }}>
            <Header /> {/* optional: show only if logged in */}
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/health" element={<Health />} />

              {/* Protected Routes */}
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/signals" element={<ProtectedRoute><Signals /></ProtectedRoute>} />
              <Route path="/positions" element={<ProtectedRoute><Positions /></ProtectedRoute>} />
              <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
              <Route path="/pnl" element={<ProtectedRoute><PnL /></ProtectedRoute>} />
              <Route path="/risk" element={<ProtectedRoute><Risk /></ProtectedRoute>} />
              <Route path="/binance-test" element={<ProtectedRoute><BinanceTest /></ProtectedRoute>} />
              <Route path="/trade" element={<Trade />} />

              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </div>
      </Router>

        </ErrorBoundary>      
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
