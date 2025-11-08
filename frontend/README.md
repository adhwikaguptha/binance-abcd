 Automated Trading & Risk Management Dashboard

A full-stack trading analytics and control system designed to monitor signals, analyze positions, update risk settings, and visualize Profit & Loss — with **React.js (Frontend)** and **FastAPI (Backend)** integration.

This system is built to support real-time decision making for semi-automated or automated trading strategies, with secure authentication, modular UI components, and clean API communication.

---

 Features

| Feature | Description |
|--------|-------------|
|  User Authentication | Secure Login & Register with JWT |
|  Dashboard Overview | Unified access to all system modules |
| Signal Management | View, Approve, Reject trading signals |
| Orders & Positions | Track live and closed trades easily |
| PnL Visualization | Real-time Profit & Loss chart with Recharts |
| Risk Control Module | Update capital, risk %, max loss dynamically |
| Backend Health Check | System availability & API connectivity |
| Modular Architecture | Easy to maintain, extend and deploy |

---

 Technology Stack

| Layer | Technology |
|------|------------|
| Frontend | **React.js**, React Router, Axios, Recharts, Context API |
| Backend | **FastAPI**, Python, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Auth | JWT (Bearer Token) |
| Deployment (optional) | Docker / Render / Railway / Vercel |

---

##  Project Structure

frontend/
│
├── .env # Contains REACT_APP_API_URL
├── package.json
├── public/
│ └── index.html
└── src/
├── api/ # API Request Handlers
│ ├── auth.js
│ ├── signals.js
│ ├── orders.js
│ ├── positions.js
│ ├── pnl.js
│ ├── risk.js
│ └── trade.js
│
├── context/
│ └── AuthContext.js # Global Auth State (JWT)
│
├── components/
│ ├── Sidebar.js
│ ├── Header.js
│ ├── ProtectedRoute.js
│ ├── Toast.js
│ └── LoadingSpinner.js
│
├── pages/
│ ├── Login.js
│ ├── Register.js
│ ├── Dashboard.js
│ ├── Signals.js
│ ├── Orders.js
│ ├── Positions.js
│ ├── PnL.js
│ ├── Risk.js
│ ├── BinanceTest.js
│ └── Health.js
│
└── App.js # Routes + Layout Structure

yaml
Copy code

---

## Installation & Setup

### Clone the Repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>/frontend
 Install Dependencies
bash
Copy code
npm install
 Configure Environment Variables
Create .env in the frontend folder:

ini
Copy code
REACT_APP_API_URL=http://127.0.0.1:8000
Make sure backend is running at this URL.

 Start the Frontend
bash
Copy code
npm start
The app runs on:

arduino
Copy code
http://localhost:3000/
 Backend API Requirements
The frontend expects the backend to expose the following routes:

Endpoint	Method	Description
/auth/login	POST	Login and get token
/auth/register	POST	Register account
/signals	GET	Get all signals
/signals/pending	GET	Get pending signals
/signals/{id}/approve	POST	Approve signal
/signals/{id}/reject	POST	Reject signal
/orders	GET	Get orders
/positions	GET	Get open positions
/pnl/today	GET	PnL for current day
/pnl/summary	GET	Overall performance summary
/risk/update	PUT	Update risk parameters
/health/	GET	Check backend status

 UI Highlights
Animated Login & Register screens

Collapsible Sidebar with smooth slide transition

Global Toast notification system for feedback

Loading indicators during API calls

Fully responsive layout

 Testing Summary
Test Case	Result
Login with valid credentials	 Successful
Invalid login	 Error shown
Navigate without token	 Redirect to Login
Update risk settings	 Updated successfully
Load PnL Chart	Smooth dynamic rendering

 Future Enhancements
WebSocket-based live updates

Role-based admin dashboard

Trade execution directly from UI

Automated trading strategy builder UI

Dark/Light theme toggle

 Conclusion
This project demonstrates a modern, scalable and interactive trading dashboard built with React + FastAPI, providing real-time monitoring, risk control, and analysis features suitable for both educational and production use.

 Show Your Support
If you found this project useful, please star the repository 
It helps others discover it and keeps the project growing!


