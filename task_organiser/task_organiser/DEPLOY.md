# DEPLOYMENT GUIDE: PYTHONANYWHERE

## 1. Create your PythonAnywhere account
- **Sign up** at [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/).
- **Pick your username carefully**; it appears in your live URL. Example: username `rjsandbox1` → `https://rjsandbox1.pythonanywhere.com/`.

## 2. Start a Bash console
- From the PythonAnywhere dashboard, go to **Consoles → Start a new console → Bash**.

## 3. Copy this project to PythonAnywhere
```bash
cd ~
git clone https://github.com/Mr-Zamora/rjsandbox1.git
mkdir -p ~/rjsandbox1/instance
mkdir -p ~/rjsandbox1/static/images/uploads
```

## 4. Create a virtual environment and install dependencies
```bash
cd ~/rjsandbox1
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## 5. Initialize the SQLite database
```bash
cd ~/rjsandbox1
source venv/bin/activate
flask --app app init-db
deactivate
```
- Confirm the database exists: `ls ~/rjsandbox1/instance/` should list `recipes.db`.

## 6. Configure the web app (Web tab)
1. Open the **Web** tab → **Add a new web app** → **Manual configuration** → select **Python 3.10**.
2. Set **Working directory** to `/home/yourusername/rjsandbox1` (replace `yourusername`).
3. Set **Virtualenv** to `/home/yourusername/rjsandbox1/venv`.
4. Under **Static files**, add a mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/rjsandbox1/static/`

## 7. Update the WSGI file
- Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py` so it contains:
```python
import sys
import os

project_home = '/home/yourusername/rjsandbox1'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app
application = create_app()
```
- Save the file.

## 8. Reload and test
- In the Web tab, press **Reload**.
- Visit `https://yourusername.pythonanywhere.com/` in your browser.
- If there is an error, check the **Error log** linked from the Web tab.

## 9. Optional maintenance tips
- To pull new code changes:
  ```bash
  cd ~/rjsandbox1
git pull
  ```
- After pulling, reactivate the virtualenv if dependencies changed: `source venv/bin/activate && pip install -r requirements.txt`.
- Reload the web app after any code or dependency changes.
