# DEPLOYMENT GUIDE: PYTHONANYWHERE

## 1. Create your PythonAnywhere account
- **Sign up** at [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/).
- **Pick your username carefully**; it appears in your live URL. Example: username `taskorganiser` → `https://taskorganiser.pythonanywhere.com/`.

## 2. Start a Bash console
- From the PythonAnywhere dashboard, go to **Consoles → Start a new console → Bash**.

## 3. Copy this project to PythonAnywhere
```bash
cd ~
git clone https://github.com/Sheeesh-R/Task_Organiser_App.git
cd Task_Organiser_App
mkdir -p instance
mkdir -p static/images/uploads
```

## 4. Create a virtual environment and install dependencies
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
# or
# source venv/bin/activate  # On Linux/Mac
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Initialize the SQLite database
```bash
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
flask --app app init-db
deactivate
```
- Confirm the database exists: `ls instance/` should list `taskmanager.db`.

## 6. Configure the web app (Web tab)
1. Open the **Web** tab → **Add a new web app** → **Manual configuration** → select **Python 3.10**.
2. Set **Working directory** to `/home/yourusername/Task_Organiser_App` (replace `yourusername`).
3. Set **Virtualenv** to `/home/yourusername/Task_Organiser_App/venv`.
4. Under **Static files**, add a mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/Task_Organiser_App/static/`

## 7. Update the WSGI file
- Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py` so it contains:
```python
import sys
import os

project_home = '/home/yourusername/Task_Organiser_App'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from run import app as application  # noqa
```
- Save the file and click **Reload** in the Web tab.

## 8. Reload and test
- In the Web tab, press **Reload**.
- Visit `https://yourusername.pythonanywhere.com/` in your browser.
- If there is an error, check the **Error log** linked from the Web tab.

## 9. Optional maintenance tips
- To pull new code changes:
  ```bash
  cd ~/Task_Organiser_App
git pull
  ```
- After pulling, reactivate the virtualenv if dependencies changed: `source venv/bin/activate && pip install -r requirements.txt`.
- Reload the web app after any code or dependency changes.

## 10. Docker and CI notes
- A `Dockerfile` is included for container-based deployment and local development.
- A GitHub Actions workflow is available at `.github/workflows/ci.yml` for automated testing on pushes and pull requests.
