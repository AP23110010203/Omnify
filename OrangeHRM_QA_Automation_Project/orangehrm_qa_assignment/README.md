# OrangeHRM QA Automation Assignment

## Tools
- Python
- Selenium
- Pytest
- Page Object Model (POM)

## Workflow
1. Login to OrangeHRM
2. Navigate to PIM
3. Add four employees
4. Verify employees in Employee List
5. Print `Name Verified`
6. Logout

## Installation
```bash
python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Set credentials if required:

```bash
export ORANGEHRM_USERNAME=Admin
export ORANGEHRM_PASSWORD=admin123
```

On Windows PowerShell:

```powershell
$env:ORANGEHRM_USERNAME="Admin"
$env:ORANGEHRM_PASSWORD="admin123"
```

Run the test:

```bash
pytest -s tests/test_orangehrm.py
```

> Note: OrangeHRM is a live demo application. UI locators or behavior may change over time, so Selenium selectors may need minor updates.
