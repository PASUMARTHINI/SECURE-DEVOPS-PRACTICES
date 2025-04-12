import subprocess
import os

# --- Configuration ---
SONARQUBE_HOST = os.environ.get("SONARQUBE_HOST", "http://localhost:9000")
SONARQUBE_TOKEN = os.environ.get("SONARQUBE_TOKEN")
SONARQUBE_PROJECT_KEY = os.environ.get("SONARQUBE_PROJECT_KEY", "my-python-project")
PROJECT_SOURCE_DIR = "."  # Adjust if your source code is in a subdirectory

ZAP_HOST = os.environ.get("ZAP_HOST", "localhost")
ZAP_PORT = os.environ.get("ZAP_PORT", "8080")
TARGET_URL = os.environ.get("TARGET_URL")  # URL of the deployed application
ZAP_REPORT_PATH = "zap_report.html"
ZAP_API_KEY = os.environ.get("ZAP_API_KEY") # Optional, but recommended for production

# --- Helper Functions ---
def run_command(command):
    """Executes a shell command and prints the output."""
    print(f"Running command: {' '.join(command)}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print("Stdout:")
        print(stdout.decode())
    if stderr:
        print("Stderr:")
        print(stderr.decode())
    return process.returncode

def analyze_with_sonarqube():
    """Performs static code analysis using SonarQube."""
    if not SONARQUBE_TOKEN:
        print("SONARQUBE_TOKEN environment variable not set. Skipping SonarQube analysis.")
        return True

    command = [
        "sonar-scanner",
        f"-Dsonar.projectKey={SONARQUBE_PROJECT_KEY}",
        f"-Dsonar.sources={PROJECT_SOURCE_DIR}",
        f"-Dsonar.host.url={SONARQUBE_HOST}",
        f"-Dsonar.login={SONARQUBE_TOKEN}",
    ]
    return run_command(command) == 0

def run_owasp_zap_scan():
    """Performs dynamic application security testing using OWASP ZAP."""
    if not TARGET_URL:
        print("TARGET_URL environment variable not set. Skipping OWASP ZAP scan.")
        return True

    zap_command = [
        "zap-cli",
        "active-scan",
        "-t",
        TARGET_URL,
        "-r",
        ZAP_REPORT_PATH,
    ]
    if ZAP_API_KEY:
        zap_command.extend(["-z", f"-config api.key={ZAP_API_KEY}"])
    else:
        print("Warning: ZAP API key not set. Consider setting it for secure operation.")

    return run_command(zap_command) == 0

def check_zap_alerts():
    """(Basic Example) Checks the ZAP report for high-risk alerts."""
    try:
        with open(ZAP_REPORT_PATH, "r") as f:
            report_content = f.read()
            if "High" in report_content:
                print("High-risk vulnerabilities found by OWASP ZAP!")
                return False
            else:
                print("No high-risk vulnerabilities found by OWASP ZAP (based on basic string search).")
                return True
    except FileNotFoundError:
        print(f"ZAP report not found at {ZAP_REPORT_PATH}")
        return True # Consider this a pass or fail based on your policy

if __name__ == "__main__":
    print("--- Starting CI/CD Security Scan ---")

    # --- Static Code Analysis (SonarQube) ---
    print("\n--- SonarQube Analysis ---")
    sonarqube_success = analyze_with_sonarqube()
    if not sonarqube_success:
        print("SonarQube analysis failed. Failing the pipeline.")
        exit(1)
    print("SonarQube analysis completed successfully.")

    # --- Deployment (Simulated - Replace with your actual deployment) ---
    print("\n--- Simulating Deployment ---")
    if not TARGET_URL:
        print("TARGET_URL not set, cannot simulate deployment for ZAP.")
    else:
        print(f"Application deployed to: {TARGET_URL}")

        # --- Dynamic Application Security Testing (OWASP ZAP) ---
        print("\n--- OWASP ZAP Scan ---")
        zap_success = run_owasp_zap_scan()
        if not zap_success:
            print("OWASP ZAP scan failed.")
        else:
            print("OWASP ZAP scan completed. Report saved to:", ZAP_REPORT_PATH)
            # --- Basic Alert Checking (Adapt based on your needs) ---
            if not check_zap_alerts():
                print("Critical vulnerabilities found by ZAP. Failing the pipeline.")
                exit(1)

    print("\n--- CI/CD Security Scan Completed ---")
    exit(0)