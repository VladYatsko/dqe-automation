import sys
import subprocess

def run_script(script_name):
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"Successfully ran {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

if __name__ == "__main__":
    run_script('main_table.py')
    run_script('main_chart.py')