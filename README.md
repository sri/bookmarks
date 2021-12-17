This is extracted from a simple bookmark service that I run on my personal server.

### What this app uses
* Python 3: https://github.com/python/cpython
* Flask: https://github.com/pallets/flask
* Flask-Login: https://github.com/maxcountryman/flask-login
* peewee: for ORM; https://github.com/coleifer/peewee
* Poetry: to install dependencies; https://github.com/python-poetry/poetry
* SQLite: for the db, https://www.sqlite.org/index.html

### Install and Run

```
poetry install
```

1. Populate `.env` with the necessary values and run `./run`.
2. Run: `sqlite3 bookmarks.db < db/init.schema`
3. Run: `./run`
4. Login with username and password set in the `.env` file.
   And see https://flask.palletsprojects.com/en/2.0.x/config/ on how to create a SECRET_KEY.
5. Use the following bookmarklet to bookmark websites from the tab you are on:
```
javascript:q=location.href;if(document.getSelection){d=document.getSelection();}else{d='';};p=document.title;void(open('http://localhost:5000/add?showtags=yes&url='+encodeURIComponent(q)+'&notes='+encodeURIComponent(d)+'&title='+encodeURIComponent(p),'Bookmarks', 'toolbar=no,width=700,height=600'));
```
