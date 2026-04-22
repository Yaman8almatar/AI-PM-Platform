# Running the Tests

This guide explains how to execute the different test suites for the AI PM Platform.

## 1. Prerequisites
 Ensure all Python dependencies are installed:
 ```Bash:
  pip install -r backend\requirements-test.txt

 # Install Playwright browsers:
 ```Bash:
 npx playwright install
 
2. ## Unit and Integration Tests (Pytest)
 # Navigate to the backend directory and run:
 ```Bash:
 PYTHONPATH=. pytest tests\ -v

 3. ## Performance Testing (Locust)
 # Start the backend server:
 ```Bash:
 uvicorn app.main:app
 # In a new terminal, run the Locust script:
 ```Bash:
 locust -f backend\tests\locustfile.py
 Open http:\\localhost:8089 in your browser to configure and start the load test.

4. ## End-to-End (E2E) Testing (Playwright)

 **Important Note: Make sure to run both the Backend server and the Frontend before starting.**

 Start the Backend server (Terminal 1):
 ```Bash:
 cd backend
 uvicorn app.main:app

 Start the Frontend dashboard (Terminal 2):
 ```Bash:
 cd "Front-end Dashboard"
 npm run dev

 Run the Playwright tests (Terminal 3):

 ```Bash:
 cd "Front-end Dashboard"
 npx playwright test tests/e2e.spec.js --ui
