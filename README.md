# Sequence and Programs Browser App

Initialize the database (this takes a while, but you can also hit CTRL-C after a few minutes for a partial database):

```bash
./update_database.py
```

Prepare the Flask App:

```bash
python3 -m venv venv
. venv/bin/activate
pip install Flask
```

Start the app:

```bash
export FLASK_APP=finder_app
flask run
```
