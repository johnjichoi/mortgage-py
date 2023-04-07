# dotenv
python -m venv env
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\env\Scripts\activate

# pip
pip freeze > requirements.txt
pip install -r requirements.txt
