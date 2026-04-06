#!/usr/bin/env python3

import re
import os
import yaml
import copy
import posixpath

from navigation import  ITEM_ORDER


# ── Locate repo root ─────────────────────────────────────
class DirectoryNotFound(Exception):
    pass


class FileNotFound(Exception):
    pass

ROOT = os.path.dirname(__file__).rsplit(".github", 1)[0]
if not os.path.isdir(ROOT) and not os.path.isdir:
    raise DirectoryNotFound(f"Failed to locate directory {ROOT}")

CONFIG = os.path.join(ROOT, "_config.yml")
if not os.path.isfile(CONFIG):
    raise FileNotFound(f"Failed to locate configuration file: {CONFIG}")

DOCS_DIR = os.path.join(ROOT, "_docs")
if not os.path.isdir(DOCS_DIR):
    raise DirectoryNotFound(f"Failed to locate directory {DOCS_DIR}")

# support functions
def __extract_title(md_path):
    """Extract `title` from YAML front matter of a Markdown file"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
    if match:
        yaml_content = match.group(1)
        for line in yaml_content.splitlines():
            if line.strip().startswith("title:"):
                # remove 'title:' and any quotes/spaces
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None

def __order_items(section, items):
    order = ITEM_ORDER.get(section)
    if not order:
        return items

    ordered = []
    remaining = {item["slug"]: item for item in items}

    for slug in order:
        if slug in remaining:
            ordered.append(remaining.pop(slug))

    # append any items not listed
    ordered.extend(remaining.values())

    return ordered

def __order_sections(nav_dict, section_order):
    ordered = []

    for section in section_order:
        if section in nav_dict:
            items = __order_items(section, nav_dict[section])
            ordered.append({
                "title": section,
                "items": items
            })

    # add sections not listed
    for section, items in nav_dict.items():
        if section not in section_order:
            ordered.append({
                "title": section,
                "items": items
            })

    return ordered

def __dict_to_nav_list(nav_dict):
    """
    Convert a dict keyed by section name into a list of dicts suitable for _config.yml

    Input:
      {
          'Getting Started': [
              {'slug': 'getting-started', 'title': 'Introduction', 'file': '...'},
              ...
          ],
          ...
      }

    Output:
      [
          {
              'title': 'Getting Started',
              'items': [
                  {'slug': 'getting-started', 'title': 'Introduction', 'file': '...'},
                  ...
              ]
          },
          ...
      ]
    """
    nav_list = []
    # preserve order if Python >=3.7, else sort keys manually
    for section_name, items in nav_dict.items():
        nav_list.append({
            "title": section_name,
            "items": items
        })

    nav_list = __order_sections(nav_dict, ITEM_ORDER)
    return nav_list



# ── Read `_config.yml` ─────────────────────────────────────
# "last" _config.yaml file
with open(CONFIG) as f:
    config = yaml.safe_load(f)

# ── Get directories within `DOCS_DIR` ─────────────────────────────────────
# current file struct
ROOT_PATHS = {}
for root, _, file in os.walk(DOCS_DIR): # <-- there are no sub/sub dirs at the moment
    dir_name = "root"
    if root:
        if '/' in root:
            dir_name = root.rsplit('/', 1)[-1]
        elif '\\' in root:
            dir_name = root.rsplit('\\', 1)[-1]
    if ROOT_PATHS.get(dir_name) is None:
        ROOT_PATHS[dir_name] = []

    if file and isinstance(file, list):
        for fname in file:
            if not (fname.endswith(".") or fname == "README.md"):
                ROOT_PATHS[dir_name].append({
                    "slug": os.path.splitext(fname)[0],
                    "title": __extract_title(md_path=os.path.join(root, fname)),
                    "file": posixpath.join(dir_name, fname)
                })
    elif file and not (file.endswith(".") or file == "README.md"):
        ROOT_PATHS[dir_name].append({
            "slug": os.path.splitext(file)[0],
            "title": __extract_title(md_path=os.path.join(DOCS_DIR, file)),
            "file": posixpath.join(file)
        })

navs = copy.deepcopy(ROOT_PATHS)
for key in ROOT_PATHS:
    if not navs.get(key) and navs.get(key) is not None:
        navs.pop(key)
ROOT_PATHS = copy.deepcopy(navs)

# ── Convert to nav logic (slug) ─────────────────────────────────────
config["nav"] = __dict_to_nav_list(nav_dict=ROOT_PATHS)
with open(CONFIG, 'w') as f:
    yaml.dump(config, f, sort_keys=False)
