
# 🚀 Automated Trading & Risk Management Dashboard

A full-stack trading analytics and control system designed to monitor signals, analyze positions, update risk settings, and visualize Profit & Loss — built using **React.js (Frontend)** and **FastAPI (Backend)**.

This system supports **semi-automated trading workflows**, offering real-time decision support, authentication, and intuitive visualization of market data and strategy performance.

---

## ✨ Features

| Feature                     | Description                                        |
| --------------------------- | -------------------------------------------------- |
| 🔐 **User Authentication**  | Secure Login & Register using JWT tokens           |
| 📊 **Dashboard Overview**   | Unified access to all trading modules              |
| 🚦 **Signal Management**    | View, Approve, or Reject generated trading signals |
| 🧾 **Orders & Positions**   | Monitor open and closed trades easily              |
| 📈 **PnL Visualization**    | Real-time Profit & Loss graph using Recharts       |
| ⚙️ **Risk Control Module**  | Adjust capital, risk %, and max loss dynamically   |
| 🔍 **Backend Health Check** | Displays API connectivity and server status        |
| 🧩 **Modular Architecture** | Clean structure, scalable and maintainable         |

---

## 🏗 Technology Stack

| Layer                 | Technology                                               |
| --------------------- | -------------------------------------------------------- |
| Frontend              | **React.js**, React Router, Axios, Recharts, Context API |
| Backend               | **FastAPI**, Python, SQLAlchemy, Pydantic                |
| Database              | PostgreSQL                                               |
| Auth                  | JWT (Bearer Token)                                       |
| Deployment (optional) | Docker / Render / Railway / Vercel                       |

---

## 📂 Project Structure

```
frontend/
│
├── .env                         # Environment variables (API base URL)
├── package.json
├── public/
│   └── index.html
└── src/
    ├── api/                     # API Request Handlers
    │   ├── auth.js
    │   ├── signals.js
    │   ├── orders.js
    │   ├── positions.js
    │   ├── pnl.js
    │   ├── risk.js
    │   └── trade.js
    │
    ├── context/
    │   └── AuthContext.js       # Global Auth State (JWT)
    │
    ├── components/
    │   ├── Sidebar.js
    │   ├── Header.js
    │   ├── ProtectedRoute.js
    │   ├── Toast.js
    │   └── LoadingSpinner.js
    │
    ├── pages/
    │   ├── Login.js
    │   ├── Register.js
    │   ├── Dashboard.js
    │   ├── Signals.js
    │   ├── Orders.js
    │   ├── Positions.js
    │   ├── PnL.js
    │   ├── Risk.js
    │   ├── BinanceTest.js
    │   └── Health.js
    │
    └── App.js                   # Routes + Layout Structure
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>/frontend
```

### 2️⃣ Install Dependencies

```bash
npm install
```

### 3️⃣ Configure Environment Variables

Create a `.env` file inside the **frontend** folder:

```
REACT_APP_API_URL=http://127.0.0.1:8000
```

> Ensure the backend FastAPI server runs at the same URL.

### 4️⃣ Start the Frontend

```bash
npm start
```

Your app will be available at:

```
http://localhost:3000/
```

---

## 🔗 Backend API Requirements

The frontend communicates with the following backend endpoints:

| Endpoint                | Method | Description                    |
| ----------------------- | ------ | ------------------------------ |
| `/auth/login`           | POST   | Authenticate and get JWT token |
| `/auth/register`        | POST   | Register new account           |
| `/signals`              | GET    | Fetch all trade signals        |
| `/signals/pending`      | GET    | Fetch pending approval signals |
| `/signals/{id}/approve` | POST   | Approve a signal               |
| `/signals/{id}/reject`  | POST   | Reject a signal                |
| `/orders`               | GET    | Get list of orders             |
| `/positions`            | GET    | Get current open positions     |
| `/pnl/today`            | GET    | Get today’s Profit & Loss      |
| `/pnl/summary`          | GET    | Get performance summary        |
| `/risk/update`          | PUT    | Update risk parameters         |
| `/health/`              | GET    | Check backend system status    |

---

## 🎨 UI Highlights

* Smooth transitions & responsive design
* Collapsible sidebar with active state tracking
* Real-time toast notifications for feedback
* Loading indicators for API calls
* Clean dashboard layout with intuitive navigation

---

## 🧪 Testing Summary

| Test Case                    | Result                       |
| ---------------------------- | ---------------------------- |
| Login with valid credentials | ✅ Success                    |
| Invalid login                | ✅ Proper error handling      |
| Unauthorized navigation      | ✅ Redirects to Login         |
| Update risk settings         | ✅ Updated correctly          |
| Load PnL Chart               | ✅ Dynamic rendering verified |

---

## 🚀 Future Enhancements

* WebSocket-based live updates
* Role-based admin dashboard
* Trade execution directly from UI
* Automated strategy builder interface
* Dark/Light theme toggle

---

## 🏁 Conclusion

This project delivers a **scalable, interactive, and visually clean trading dashboard** powered by **React + FastAPI**, enabling real-time performance tracking, signal control, and risk management for semi-automated trading systems.

---

