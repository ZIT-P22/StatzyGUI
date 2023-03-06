# StatzyGUI

instalation guide
    1. open a venv
    2. enter the venv
    3. install flask with
        pip install -r requirements.txt
    4. create the statzy DataBase in your local postgres database
        CREATE DATABASE statzy
    5. import the statzy tables and date in the statzy database
        (first connect to the statzy with \c statzy)
        \i statzy.sql
        \i statzy.siko


run your flask application for development
    1. run the statzy.py with python
        python3 | python | py | py3 /your/path/to/statzy.py
