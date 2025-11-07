import ccxt
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
import time
import requests
import zipfile
from io import BytesIO
import tempfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT']  # 7 symbols
TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '12h', '1d']
DATA_DIR = 'data'
LIMIT = 1000  # Binance API limit per request (fixed max; optimal for all timeframes)
BASE_URL = 'https://data.binance.vision/data/spot/monthly/klines'

# Timeframe to retention period mapping (in days)
RETENTION_DAYS = {
    tf: 365 * 2 if tf != '1d' else 365 * 5 for tf in TIMEFRAMES
}

# For updates, use API for last 30 days to bridge to ZIP historical
HISTORICAL_CUTOFF_DAYS = 30

def create_symbol_dir(symbol):
    """Create directory for symbol if it doesn't exist."""
    symbol_name = symbol.replace('/', '')
    dir_path = os.path.join(DATA_DIR, symbol_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def get_start_date(timeframe):
    """Get start date based on retention period."""
    retention_days = RETENTION_DAYS[timeframe]
    start_date = datetime.now() - timedelta(days=retention_days)
    return start_date

def load_existing_data(file_path):
    """Load CSV from ZIP and return the last timestamp."""
    if os.path.exists(file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                csv_name = [name for name in zf.namelist() if name.endswith('.csv')][0]
                with zf.open(csv_name) as csv_file:
                    df = pd.read_csv(csv_file)
                    if not df.empty and 'ts' in df.columns:
                        last_ts = pd.to_datetime(df['ts'].iloc[-1])
                        return last_ts
        except Exception as e:
            logger.warning(f"Error loading existing data from {file_path}: {e}")
    return None

def download_monthly_zip(symbol, timeframe, year, month):
    """Download monthly ZIP from Binance data vision and save as-is."""
    symbol_name = symbol.replace('/', '')
    zip_filename = f"{symbol_name}-{timeframe}-{year}-{month:02d}.zip"
    url = f"{BASE_URL}/{symbol_name}/{timeframe}/{zip_filename}"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Save raw ZIP to disk (in timeframe subdir)
        tf_dir = os.path.join(DATA_DIR, symbol_name, timeframe)
        os.makedirs(tf_dir, exist_ok=True)
        local_zip_path = os.path.join(tf_dir, f"{year}-{month:02d}.zip")
        
        with open(local_zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded raw ZIP: {local_zip_path}")
        return local_zip_path  # Return path for potential use
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.info(f"ZIP not found (normal for future months): {zip_filename}")
        else:
            logger.warning(f"Error downloading {zip_filename}: {e}")
    except Exception as e:
        logger.warning(f"Error saving {zip_filename}: {e}")
    return None

def fetch_historical_zip_data(symbol, timeframe, start_date):
    """Download historical monthly ZIPs (saved as-is)."""
    cutoff_date = datetime.now() - timedelta(days=HISTORICAL_CUTOFF_DAYS)
    
    year = start_date.year
    month = start_date.month
    current_date = start_date.replace(day=1)
    
    downloaded_zips = []
    while current_date < cutoff_date:
        zip_path = download_monthly_zip(symbol, timeframe, year, month)
        if zip_path:
            downloaded_zips.append(zip_path)
        
        # Next month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        current_date = current_date.replace(year=year, month=month)
    
    logger.info(f"Downloaded {len(downloaded_zips)} historical ZIPs for {symbol} {timeframe}")
    return downloaded_zips  # List of ZIP paths

def fetch_ohlcv_api(exchange, symbol, timeframe, since=None):
    """Fetch recent OHLCV data from Binance API, handling chunking."""
    all_data = []
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=LIMIT)
            if not ohlcv:
                break

            all_data.extend(ohlcv)
            logger.info(f"Fetched {len(ohlcv)} recent candles for {symbol} {timeframe}, up to {datetime.fromtimestamp(ohlcv[-1][0] / 1000)}")

            since = ohlcv[-1][0] + 1
            if len(ohlcv) < LIMIT:
                break

            time.sleep(0.1)  # Rate limit respect

        except Exception as e:
            logger.error(f"Error fetching recent data for {symbol} {timeframe}: {e}")
            break

    return all_data

def process_recent_data(all_data):
    """Process raw API OHLCV into DataFrame."""
    if not all_data:
        return pd.DataFrame()

    df_new = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_new['ts'] = pd.to_datetime(df_new['timestamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
    df_new = df_new[['ts', 'open', 'high', 'low', 'close', 'volume']]
    df_new[['open', 'high', 'low', 'close', 'volume']] = df_new[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df_new.drop_duplicates(subset=['ts'], keep='last', inplace=True)
    df_new.sort_values('ts', inplace=True)
    df_new.reset_index(drop=True, inplace=True)
    return df_new

def extract_and_merge_zips(zip_paths):
    """Extract and merge DataFrames from list of ZIP paths."""
    all_data = []
    for zip_path in zip_paths:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                csv_name = [name for name in zf.namelist() if name.endswith('.csv')][0]
                with zf.open(csv_name) as csv_file:
                    df_month = pd.read_csv(csv_file, header=None)
                    df_month.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 
                                        'close_time', 'quote_asset_volume', 'number_of_trades',
                                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
                    df_month = df_month[['open_time', 'open', 'high', 'low', 'close', 'volume']]
                    df_month['ts'] = pd.to_datetime(df_month['open_time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
                    df_month = df_month[['ts', 'open', 'high', 'low', 'close', 'volume']]
                    df_month[['open', 'high', 'low', 'close', 'volume']] = df_month[['open', 'high', 'low', 'close', 'volume']].astype(float)
                    df_month.drop_duplicates(subset=['ts'], keep='last', inplace=True)
                    df_month.sort_values('ts', inplace=True)
                    all_data.append(df_month)
        except Exception as e:
            logger.warning(f"Error extracting {zip_path}: {e}")
    
    if all_data:
        df_historical = pd.concat(all_data, ignore_index=True)
        df_historical.drop_duplicates(subset=['ts'], keep='last', inplace=True)
        df_historical.sort_values('ts', inplace=True)
        df_historical.reset_index(drop=True, inplace=True)
        return df_historical
    return pd.DataFrame()

def merge_and_save(df_historical, df_recent, file_path):
    """Merge historical + recent data, save uncompressed CSV inside a ZIP (compressed storage, text content)."""
    if df_historical.empty and df_recent.empty:
        return

    df_combined = pd.concat([df_historical, df_recent], ignore_index=True) if not df_historical.empty else df_recent
    if not df_historical.empty and not df_recent.empty:
        # Filter recent to avoid overlap
        hist_last = pd.to_datetime(df_historical['ts'].iloc[-1])
        df_recent_filtered = df_recent[df_recent['ts'] > hist_last.strftime('%Y-%m-%d %H:%M:%S')]
        df_combined = pd.concat([df_historical, df_recent_filtered], ignore_index=True)

    df_combined.drop_duplicates(subset=['ts'], keep='last', inplace=True)
    df_combined.sort_values('ts', inplace=True)
    df_combined.reset_index(drop=True, inplace=True)

    parent_dir = os.path.dirname(file_path)
    os.makedirs(parent_dir, exist_ok=True)
    
    # Save uncompressed CSV to temp
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as temp_csv:
        df_combined.to_csv(temp_csv.name, index=False)
        temp_csv_path = temp_csv.name
    
    # Create ZIP and add the CSV
    with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(temp_csv_path, 'full_history.csv')  # Add as 'full_history.csv' inside ZIP
    
    # Clean up temp
    os.unlink(temp_csv_path)
    
    logger.info(f"Saved {len(df_combined)} total rows in ZIP: {file_path} (uncompressed CSV inside, ~70% size reduction via ZIP)")

def main():
    """Main function: Download raw ZIPs for historical + API for recent, merge into ZIP with text CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)

    exchange = ccxt.binance({'enableRateLimit': True})

    for symbol in SYMBOLS:
        symbol_dir = create_symbol_dir(symbol)
        logger.info(f"Processing symbol: {symbol}")

        for timeframe in TIMEFRAMES:
            file_path = os.path.join(symbol_dir, f"{timeframe}.zip")  # Final merged ZIP
            existing_last_ts = load_existing_data(file_path)

            start_date = get_start_date(timeframe)
            cutoff_date = datetime.now() - timedelta(days=HISTORICAL_CUTOFF_DAYS)
            since_for_api = int(cutoff_date.timestamp() * 1000)

            # Download historical raw ZIPs
            logger.info(f"Downloading historical ZIPs for {symbol} {timeframe} from {start_date} to {cutoff_date}")
            historical_zips = fetch_historical_zip_data(symbol, timeframe, start_date)

            # Extract/merge historical
            df_historical = extract_and_merge_zips(historical_zips)

            # Fetch recent via API from cutoff to now
            logger.info(f"Fetching recent API data for {symbol} {timeframe} from {cutoff_date}")
            all_recent = fetch_ohlcv_api(exchange, symbol, timeframe, since=since_for_api)
            df_recent = process_recent_data(all_recent)

            # If existing data, merge with it only if newer
            if existing_last_ts:
                logger.info(f"Existing data up to {existing_last_ts}; merging if needed")
                try:
                    with zipfile.ZipFile(file_path, 'r') as zf:
                        csv_name = [name for name in zf.namelist() if name.endswith('.csv')][0]
                        with zf.open(csv_name) as csv_file:
                            existing_df = pd.read_csv(csv_file)
                            df_combined = pd.concat([existing_df, df_historical, df_recent], ignore_index=True)
                            df_combined.drop_duplicates(subset=['ts'], keep='last', inplace=True)
                            df_combined.sort_values('ts', inplace=True)
                            df_combined.reset_index(drop=True, inplace=True)
                            df_historical = df_combined  # Reuse for save
                except Exception as e:
                    logger.warning(f"Error merging existing: {e}")

            merge_and_save(df_historical, df_recent, file_path)

    logger.info("Data download completed.")

if __name__ == "__main__":
    main()