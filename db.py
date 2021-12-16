import sqlite3
import datetime

import peewee

DB = peewee.SqliteDatabase("bookmarks.db", pragmas={
  "foreign_keys": 1
})

class BaseModel(peewee.Model):
  class Meta:
    database = DB

class Bookmarks(BaseModel):
  id = peewee.AutoField()
  title = peewee.TextField()
  url = peewee.TextField()
  notes = peewee.TextField()
  created_at = peewee.DateTimeField(default=datetime.datetime.now)

  def alltags(self):
    return [bt.tag.name for bt in self.tags]

class Tags(BaseModel):
  id = peewee.AutoField()
  name = peewee.TextField()

class BookmarkTags(BaseModel):
  bookmark = peewee.ForeignKeyField(Bookmarks, backref="tags")
  tag = peewee.ForeignKeyField(Tags, backref="bookmarks")

  class Meta:
    table_name = "bookmark_tags"
    primary_key = peewee.CompositeKey("bookmark", "tag")

#########################################################################

def split_by_groups_of(items, n):
  groups = []
  group = []
  for i, item in enumerate(items):
    if i > 0 and (i % n == 0):
      groups.append(group)
      group = [item]
    else:
      group.append(item)
  if group: groups.append(group)
  return groups

#########################################################################

def get_total_bookmarks_count():
  return Bookmarks.select().count()

def find_bookmark(id=None, url=None, title=None):
  if id:
    return Bookmarks.get_by_id(id)
  elif url:
    return Bookmarks.select().where(Bookmarks.url == url)
  elif title:
    return Bookmarks.select().where(Bookmarks.title == title)

def suggest_tags(words):
  return [tag.name for tag in Tags.select().where(Tags.name.in_(words))]

def get_tags(n_groups=3):
  tags = [tag.name for tag in Tags.select().order_by(Tags.name)]
  return split_by_groups_of(tags, n_groups), len(tags)

def most_recent_bookmarks(limit=100):
  return (Bookmarks
          .select()
          .distinct()
          .join(BookmarkTags)
          .join(Tags)
          .order_by(Bookmarks.created_at.desc())
          .limit(limit))

def random_bookmarks(limit=10):
  return (Bookmarks
          .select()
          .distinct()
          .join(BookmarkTags)
          .join(Tags)
          .order_by(peewee.fn.Random())
          .limit(limit))

def bookmarks_by_tag(name):
  return (Bookmarks
          .select()
          .join(BookmarkTags)
          .join(Tags)
          .where(Tags.name == name)
          .order_by(Bookmarks.created_at.desc()))

def save(bookmark_dict, tags, bookmark_id=None):
  tag_ids = []
  new_tags = set(tags)
  for tag in Tags.select().where(Tags.name.in_(tags)):
    tag_ids.append(tag.id)
    new_tags.remove(tag.name)

  with DB.atomic() as txn:
    if new_tags:
      Tags.insert_many([{"name": name} for name in new_tags]).execute()
      tag_ids.extend(
        tag.id for tag in
        Tags.select().where(Tags.name.in_(new_tags)))

    if bookmark_id:
      Bookmarks.update(**bookmark_dict).where(Bookmarks.id == bookmark_id).execute()
      BookmarkTags.delete().where(BookmarkTags.bookmark_id == bookmark_id).execute()
      bt = [{"bookmark_id": bookmark_id, "tag_id": tag_id} for tag_id in tag_ids]
      BookmarkTags.insert_many(bt).execute()
    else:
      bookmark = Bookmarks.create(**bookmark_dict)
      bt = [{"bookmark_id": bookmark.id, "tag_id": tag_id} for tag_id in tag_ids]
      BookmarkTags.insert_many(bt).execute()

def delete(bookmark_id):
  Bookmarks.get_by_id(bookmark_id).delete_instance()

def search(term):
  if term := term.strip():
    return (Bookmarks
            .select()
            .distinct()
            .join(BookmarkTags)
            .join(Tags)
            .where((Bookmarks.url.contains(term)) |
                   (Bookmarks.title.contains(term)) |
                   (Tags.name == term))
            .order_by(Bookmarks.created_at.desc()))
  else:
    return (Bookmarks
            .select()
            .order_by(Bookmarks.created_at.desc()))
