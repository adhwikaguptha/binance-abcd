import subprocess
import sys
import os
import logging
from datetime import datetime

# Set up logging
log_file = 'all_stages.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_stage(stage_num):
    """Run a single stage script and log the result."""
    script_name = f'run_stage{stage_num}.py'
    if not os.path.exists(script_name):
        logger.error(f"Script {script_name} not found!")
        return False
    
    logger.info(f"Starting Stage {stage_num}: {script_name}")
    try:
        result = subprocess.run(['python', script_name], capture_output=True, text=True, timeout=300)  # 5-min timeout per stage
        if result.returncode == 0:
            logger.info(f"Stage {stage_num} completed successfully. Output: {result.stdout}")
            # Check for expected output file
            output_csv = f'trade_suggestions_stage{stage_num}.csv'
            output_json = f'trade_suggestions_stage{stage_num}.json'
            if os.path.exists(output_csv) or os.path.exists(output_json):
                logger.info(f"Stage {stage_num} output files confirmed: {output_csv}, {output_json}")
            else:
                logger.warning(f"Stage {stage_num} output files not found—check script.")
            return True
        else:
            logger.error(f"Stage {stage_num} failed with code {result.returncode}. Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"Stage {stage_num} timed out!")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in Stage {stage_num}: {e}")
        return False

def main():
    logger.info("=== Starting All Stages Orchestration ===")
    start_time = datetime.now()
    
    stages = [2, 3, 4]  # Run stage 2 -> 3 -> 4
    success = True
    for stage in stages:
        if not run_stage(stage):
            success = False
            break  # Stop on first failure, or remove to continue
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info(f"=== All stages completed successfully in {duration} ===")
        # Optional: Merge final outputs or notify
        final_csv = 'trade_suggestions_stage4.csv'  # Adjust if stage 4 outputs differently
        if os.path.exists(final_csv):
            logger.info(f"Final output ready: {final_csv}")
            # You could add code here to merge with backtest_summary.csv if needed
    else:
        logger.error("=== Orchestration failed - check logs ===")
        sys.exit(1)

if __name__ == "__main__":
    main()