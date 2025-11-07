import ccxt

exchange = ccxt.binance({
    'apiKey': 'pTUzwvPZGwuNVDdGuPOYfM8oiP3Fjgg8eZl5IDhVPCjUimq5ZufYctorSSO7MuwD',  # Use the same key
    'secret': 'IS7Ws0uS8UJ37o2GfM7HCd3G5r7rPQuLx86ro5DICVh2QuRRmnKwvRa12ofWKVdk',   # Use the same secret
    'enableRateLimit': True,
    'test': True
})

try:
    markets = exchange.load_markets()
    print("Authentication successful! Markets loaded:", len(markets))
except Exception as e:
    print("Authentication failed:", str(e))