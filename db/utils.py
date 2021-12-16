from collections import defaultdict

def group_bookmarks_by_tag(bookmarks):
  result = defaultdict(list)
  for bookmark in bookmarks:
    for tag in bookmark["tags"].split():
      result[tag].append(bookmark)
      break
  return result

def bookmark_tags(bookmarks):
  tags = set()
  for bookmark in bookmarks:
    tags.update(bookmark["tags"].split())
  return sorted(tags)