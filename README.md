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

# Compile notes
There are 2 scripts for making binaries for Linux and Windows. These use `pyinstaller` which needs to get added seperately.
- `uv add pyinstaller`
- activate the venv
  - Linux `source .venv/bin/activate`
  - Windows `.\.venv\Scripts\activate.ps1`
- make script executable
  - Linux `chmod +x compile.sh`
  - Windows: open powershell as admin and enter `Set-ExecutionPolicy unrestricted`
- run script
  - Linux `./compile.sh`
  - Windows `.\compile.ps1`

# Homework
Knowing myself i wont add to this project and call it finished. Altho theres a bunch you can add / improve. First i would suggest adding more primitives like a circle arc, bezier or hyperbolas. If you get all of the primitives in place you can make svg converter, hardest part i think is parseing Path objects and mapping them to the right prims. At this point you probably move most of the stuff from main.py to a proper window manager. Or if you want something simple you can try to make the laser fade over distance