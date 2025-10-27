# Laser reflection simulation
I really thought it looks kinda satisfying, idk fite me. Be wary, atroucously unoptimized

# Controls
| button             | action                              |
|--------------------|-------------------------------------|
| Esc                | Exit                                |
| P                  | toggle pretty drawing (slow)        |
| C                  | add Circle at mouse position        |
| L                  | add Line at mouse position          |
| E                  | add Ellipse at mouse position       |
| Mouse Left         | drag laser origin / drag primitives |
| Mouse Right        | aim laser / resize primitives       |
| Mouse Left + Right | rotate Ellipse                      |
| Wheel Click        | remove primitive at mouse position  |
| Wheel              | change max bounces / max distance   |


# Usage
There are [binaries](https://github.com/p1geondove/laser-reflect/releases) as always. But never trust bins, better read trough the code and run that yourself if you think its safe. Also go install [astral/uv](https://docs.astral.sh/uv/getting-started/installation/)

- `git clone git@github.com:p1geondove/laser-reflect.git`
- `cd laser-reflect`
- `uv init`
- `uv add -r requirements.txt`
- `uv run main.py`

# Dev notes
Theres also 2 scripts for making binaries for Linux and Windows. These use `pyinstaller` which needs to get added seperately. Just run `uv add pyinstaller`