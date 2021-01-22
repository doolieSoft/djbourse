
echo off
call C:\Users\c158492\ProjetPerso\djbourse\venv\Scripts\activate.bat

call python manage.py runserver --settings djbourse.settings.dev

call C:\Users\c158492\ProjetPerso\djbourse\venv\Scripts\deactivate.bat