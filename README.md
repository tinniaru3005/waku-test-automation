# Waku Test Automation Framework

This project provides a **comprehensive test automation framework** for testing **Waku nodes** using Docker containers, Python, and pytest.

---

## 📖 Overview

The framework is built on **pytest** and consists of two main test suites:

1. **Basic Node Operation**
   Tests single-node functionality.

2. **Inter-Node Communication**
   Tests communication between two Waku nodes.

---

## 🛠️ Prerequisites

* Python **3.8+**
* `pip` (Python package manager)

---

## ⚙️ Installation

1. **Clone or download the project**

   ```bash
   git clone git@github.com:tinniaru3005/waku-test-automation.git
   cd waku-test-automation
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## 📂 Project Structure

```
waku-test-automation/
├── README.md
├── requirements.txt
├── pytest.ini
├── conftest.py
├── src/
│   ├── __init.py
│   ├── waku_client.py 
│   └── docker_manager.py
├── tests/
│   ├── __init__.py
│   ├── test_basic_node_operation.py
│   └── test_inter_node_communication.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

---

## 🚀 Usage

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

```bash
# Basic node operation only
pytest -m basic

# Inter-node communication only
pytest -m advanced
```

### Run with Detailed Output

```bash
pytest -v -s
```

### Generate HTML Report

```bash
pytest --html=reports/report.html --self-contained-html
```

---

## ⚡ Configuration

Test parameters can be modified in `conftest.py`:

* Port mappings
* IP addresses
* Timeouts
* Test topics and messages

---

## 📝 Logs

* Test execution logs are saved to:

  ```
  test_automation.log
  ```

---

## 📦 Dependencies

* `pytest` → Test framework
* `requests` → HTTP client for REST API calls
* `docker` → Docker container management
* `pytest-html` → Generate HTML reports
* `pytest-timeout` → Handle test timeouts

---

## 🖥️ Screenshot

### Terminal outputs

<img width="1470" height="956" alt="Screenshot 2025-08-27 at 6 03 54 PM" src="https://github.com/user-attachments/assets/0810d126-ed62-4e7f-8bdd-f6daec540d99" />


### Full HTML Report

<img width="1470" height="880" alt="Screenshot 2025-08-27 at 6 04 17 PM" src="https://github.com/user-attachments/assets/650f62f0-bc23-4a69-9cef-a756325d8bb9" />





