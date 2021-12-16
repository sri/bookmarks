import os
import random
import re

import db
from env import getenv

from flask import (
  Flask,
  render_template,
  request,
  make_response,
  redirect,
)

from flask_login import (
  LoginManager,
  login_required,
  UserMixin,
  current_user,
  login_user,
  logout_user,
)

app = Flask(
  __name__,
  template_folder="templates",
  static_folder="static")

app.config["SECRET_KEY"] = getenv("SECRET_KEY")

#########################################################################
# Flask login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
  pass

def _getuser(id):
  user = User()
  user.id = id
  return user

@login_manager.user_loader
def user_loader(id):
  return _getuser(id)

#########################################################################
# Routes

@app.route("/login", methods=["POST"])
def login():
  redirect_to = request.form.get("redirect_to", "").strip() or "/"
  resp = make_response(redirect(redirect_to))
  username = request.form["username"]
  password = request.form["password"]
  if username == getenv("USERNAME") and password == getenv("PASSWORD"):
    login_user(_getuser(username))
  return resp

@app.route("/logout", methods=["GET"])
@login_required
def logout():
  logout_user()
  return redirect("/")

@app.route("/", methods=["GET"])
def index():
  if current_user.is_anonymous:
    return render_template("login.html")
  else:
    tag_rows, tag_count = db.get_tags()
    total_bookmarks_count = db.get_total_bookmarks_count()
    return render_template(
      "index.html",
      tag_rows=tag_rows,
      tag_count=tag_count,
      total_bookmarks_count=total_bookmarks_count,
      most_recent=db.most_recent_bookmarks(),
      random_bookmarks=db.random_bookmarks())

@app.route("/tag/<name>", methods=["GET"])
@login_required
def tag(name):
  return render_template(
    "tag.html",
    bookmarks=db.bookmarks_by_tag(name))

def _from_form(form):
  url = form["url"]
  title = form["title"]
  notes = form["notes"]
  tags = form["tags"]
  assert len(url.strip()) > 0, "url required"
  assert len(tags.strip()) > 0, "tags required"
  bookmark_attrs = {
    "url": url,
    "title": title,
    "notes": notes,
  }
  return bookmark_attrs, tags.split()

@app.route("/add", methods=["GET", "POST"])
def add():
  if not current_user.is_authenticated:
    return render_template(
      "login.html",
      redirect_to=request.full_path)

  if request.method == "POST":
    bookmark_attrs, tags = _from_form(request.form)
    db.save(bookmark_attrs, tags)
    return "added"
  else:
    url = request.args.get("url")
    title = request.args.get("title")
    notes = request.args.get("notes")

    existing = (
      db.find_bookmark(url=url) or
      db.find_bookmark(title=title)
    )
    if existing: existing = existing[0]

    words = [re.sub("\W", "", word.lower()) for word in title.split()]
    suggested_tags = db.suggest_tags([w for w in words if w])
    return render_template(
      "add.html",
      url=url,
      title=title,
      notes=notes,
      existing=existing,
      tags=(existing.alltags() if existing else suggested_tags),
    )

@app.route("/bookmark/<bookmark_id>", methods=["GET"])
@login_required
def show_bookmark(bookmark_id):
  bookmark = db.find_bookmark(id=bookmark_id)
  if bookmark:
    return render_template(
      "edit.html",
      bookmark=bookmark,
    )
  else:
    return "bookmark not found"

@app.route("/update_bookmark/<bookmark_id>", methods=["POST"])
@login_required
def update_bookmark(bookmark_id):
  bookmark_attrs, tags = _from_form(request.form)
  db.save(bookmark_attrs, tags, bookmark_id)
  if request.args.get("json"):
    return "added"
  else:
    return redirect("/")

@app.route("/delete_bookmark/<bookmark_id>", methods=["POST"])
@login_required
def delete_bookmark(bookmark_id):
  db.delete(bookmark_id)
  return redirect("/")

@app.route("/search", methods=["GET"])
@login_required
def search():
  term = request.args.get("t")
  return render_template(
    "search.html",
    bookmarks=db.search(term))

def main():
  print("running it now...")
  app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
