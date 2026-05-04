#!/usr/bin/env python3
"""Detect site-packages paths for packages installed from the workspace.

Prints a colon-separated list of directories to stdout.  Called once by the
bash wrapper so the result can be exported as CINTENT_PROJECT_PATHS.

A package is considered "from the workspace" when its PEP 610 direct_url.json
contains a file:// URL that starts with GITHUB_WORKSPACE.
"""

import json
import os
import sys


def detect(workspace):
    try: # For Python >= 3.8
        import importlib.metadata as meta 
    except ImportError: # For Python < 3.8
        import importlib_metadata as meta

    paths = []
    for dist in meta.distributions():
        try:
            du = dist.read_text('direct_url.json')
        except Exception:
            continue
        if not du:
            continue
        try:
            info = json.loads(du)
        except (json.JSONDecodeError, ValueError):
            continue
        url = info.get('url', '')
        if not url.startswith('file://'):
            continue
        local_path = url[7:]
        if not local_path.startswith(workspace):
            continue

        # This distribution was installed from the workspace.
        # Find the actual package directories in site-packages.
        loc = str(dist._path.parent) if hasattr(dist, '_path') else None
        if not loc:
            continue
        top_level = dist.read_text('top_level.txt')
        if top_level:
            for pkg in top_level.strip().splitlines():
                pkg = pkg.strip()
                if not pkg:
                    continue
                pkg_dir = os.path.join(loc, pkg)
                if os.path.isdir(pkg_dir):
                    paths.append(pkg_dir)
                pkg_file = os.path.join(loc, pkg + '.py')
                if os.path.isfile(pkg_file):
                    paths.append(pkg_file)
        else:
            name = dist.metadata.get('Name', '')
            if name:
                norm = name.replace('-', '_').lower()
                pkg_dir = os.path.join(loc, norm)
                if os.path.isdir(pkg_dir):
                    paths.append(pkg_dir)
    return paths


if __name__ == '__main__':
    workspace = os.environ.get('GITHUB_WORKSPACE', '')
    if not workspace:
        sys.exit(0)
    try:
        paths = detect(workspace)
    except:
        paths = []
    if paths:
        print(os.pathsep.join(paths))
