# Hack Library

Real crypto hacks, explained simply. A learning-in-public project by [0xeduard1](https://x.com/0xeduard1).

Live: https://0xeduard1.github.io/hacks/

- `data/hacks/*.json`: one file per hack (facts checked against the linked sources)
- `data/monsters.json`: the "bug monsters", one per vulnerability class
- `build.py`: builds the static site into `docs/` (served by GitHub Pages)

Add a hack: copy any file in `data/hacks/`, fill it in, run `python3 build.py`, commit, push.
