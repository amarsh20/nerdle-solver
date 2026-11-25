"""Update the past answers list used by nerdle_solver.html.

Usage (from anywhere):
    python3 update_past_answers.py                       # copy past_solution_list.json into the page
    python3 update_past_answers.py 12+35=47 9*8-6=66     # add answers to the JSON file, then copy
    python3 update_past_answers.py --publish 12+35=47    # ...and commit + push so GitHub Pages updates

The page carries its own copy of the list, so run this after every change to
past_solution_list.json. The notebook reads the same JSON file, so both stay in step.
The live page (https://amarsh20.github.io/nerdle-solver/) only changes after --publish
(or your own git commit + push); GitHub Pages takes a minute or so to redeploy.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JSON_FILE = HERE / "past_solution_list.json"
PAGE = HERE / "nerdle_solver.html"
BLOCK = re.compile(r'(<script id="past-data" type="application/json">).*?(</script>)', re.S)
ANSWER = re.compile(r"^[0-9+\-*/]+=[0-9]+$")


def main(new_answers):
    past = json.loads(JSON_FILE.read_text())

    bad = [a for a in new_answers if len(a) != 8 or not ANSWER.match(a)]
    if bad:
        sys.exit("Not valid 8-character equations: " + ", ".join(bad))

    added = [a for a in dict.fromkeys(new_answers) if a not in set(past)]
    if added:
        past.extend(added)
        JSON_FILE.write_text(json.dumps(past))
        print(f"Added {len(added)} answer(s) to {JSON_FILE.name}: {', '.join(added)}")
    elif new_answers:
        print("Those answers were already in the list.")

    html = PAGE.read_text()
    data = json.dumps(past, separators=(",", ":"))
    html, n = BLOCK.subn(lambda m: m.group(1) + data + m.group(2), html)
    if n != 1:
        sys.exit(f"Couldn't find the past-answers block in {PAGE.name}.")
    PAGE.write_text(html)
    print(f"{PAGE.name} now excludes {len(past)} past answers.")
    return len(past)


def publish(count):
    git = lambda *args: subprocess.run(["git", "-C", str(HERE), *args], check=True)
    git("add", JSON_FILE.name, PAGE.name)
    if subprocess.run(["git", "-C", str(HERE), "diff", "--cached", "--quiet"]).returncode == 0:
        print("Nothing new to publish.")
        return
    git("commit", "-q", "-m", f"Update past answers ({count})")
    git("push", "-q")
    print("Pushed. The live page updates in a minute or so.")


if __name__ == "__main__":
    args = sys.argv[1:]
    do_publish = "--publish" in args
    count = main([a for a in args if a != "--publish"])
    if do_publish:
        publish(count)
