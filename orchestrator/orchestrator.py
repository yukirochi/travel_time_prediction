import subprocess
import logging
import os

MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(MAIN_DIR)
dbt_dir = os.path.join(PARENT_DIR, "travel_time_prediction")
model_dir = os.path.join(PARENT_DIR, "model")

logging.basicConfig(
    filename='orch_runs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_command(command, step_name, cwd):
    """Runs a shell command and logs the output."""
    logging.info(f"Starting {step_name}...")
    try:
        # shell=True is used here because Windows handles CLI commands (like dbt) better this way
        result = subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True,
            shell=True 
        )
        logging.info(f"{step_name} completed successfully.\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{step_name} failed.\nError output:\n{e.stderr or e.stdout}")
        return False


def run_orchestration():
    """Runs the full orchestration process."""
    # Step 1: Run dbt models
    
    dbt_run = run_command("dbt run", "DBT Models", cwd=dbt_dir)
       
  
    if dbt_run:
        # Step 2: Run the predictor script
       
        run_command("python predictor.py", "Predictor Script", cwd=model_dir)
    else:
        logging.error("Skipping Predictor Script due to DBT failure.")
    
if __name__ == "__main__":
    run_orchestration()