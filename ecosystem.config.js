module.exports = {
  apps: [
    {
      name: "trading-backend",
      script: "uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 8000 --reload",
      interpreter: "python",
      cwd: "./backend",                // ✅ points to your backend folder
      env: {
        PYTHONPATH: "./backend",
        BINANCE_BASE_URL: "https://testnet.binance.vision",
        ENV: "production",
      },
      autorestart: true,
      watch: false,                     // set true only if you want auto-restart on code change
      max_memory_restart: "512M",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      error_file: "./logs/pm2-error.log",
      out_file: "./logs/pm2-out.log",
      merge_logs: true,
      time: true,
    },
  ],
};
