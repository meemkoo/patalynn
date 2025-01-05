# Copyright (C) 2025  Arsenic Vapor
# patalynn is a file viewer/manager targeted for use with iOS media dumps

licencestring = """# Copyright (C) 2025  Arsenic Vapor
# patalynn is a file viewer/manager targeted for use with iOS media dumps
"""

import toml, os

pyproject = toml.load("pyproject.toml")
where = pyproject["tool"]["setuptools"]["packages"]["find"]["where"]

sources = []
for dir in where:
    for dirpath, subdirs, files in os.walk(dir):
        for x in files:
            if x.endswith(".py"):
                sources.append(os.path.join(dirpath, x))

for file in sources:
    with open(file, 'r') as rf:
        text = rf.read()
        if len(text) > 0:
            if "Copyright (C) 2025  Arsenic Vapor" in text.splitlines()[0]:
                continue

    with open(file, 'w') as wf:
        text = f"{licencestring}\n{text}"
        wf.write(text)
