## CLIUniApp / GUIUniApp – University Management System

| ID | Name |
| --- | --- |
| 25692904 | Kevin Anderson |
| 26043582 | Rithviknath Gali |
| 26044115 | Paranav Singh |
| 26170530 | Eunkwang Shin |

### Project Overview

CLIUniApp and GUIUniApp deliver a shared university management backend with both command-line and graphical front ends.

- **Student workflows**: secure registration, login, password changes, subject enrolment (max 4), subject removal, and viewing marks/grades generated via `utils/grade_calculator.py`.
- **Admin workflows**: list and remove students, clear the datastore, group students by dominant grade, and partition cohorts by pass/fail status.
- **Persistence**: both interfaces rely on a JSON datastore (`students.data`) managed by `db.Database`, ensuring consistent state across runs and interfaces.
- **Architecture**: three-tier design—controllers for presentation, services for business rules, and models/database utilities for persistence.

### System Requirements

- Python **3.10 or newer** – leverages structural pattern matching and modern typing used across services/controllers.
- Operating systems: macOS, Linux, or Windows with access to Python’s standard build.
- Tk 8.6+ (bundled with most Python distributions) to support the CustomTkinter GUI.
- Core third-party libraries installed during setup:
  - `rich` – provides coloured prompts, tables, and feedback in the CLI menus.
  - `customtkinter` – supplies the themed widgets that power the GUI variant of the app.
  - `bcrypt` – hashes and verifies student passwords so credentials are never stored in plaintext.
- Optional packaging tools:
  - `pip` / `venv` (standard Python toolchain).
  - [`uv`](https://github.com/astral-sh/uv) for lockfile-driven environments (supported via `uv.lock`).

### Installation & Setup

#### Quick Start (global Python)

For a fast run on a machine with Python 3.10+ already available:

```bash
python -m pip install rich customtkinter bcrypt
python cli.py
```

#### Option A – Python virtual environment + pip

1. Create a virtual environment.
   ```bash
   python -m venv .venv
   ```
2. Activate it.
   - macOS/Linux: `source .venv/bin/activate`
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
3. Upgrade packaging tools (recommended) and install the project in editable mode.
   ```bash
   pip install --upgrade pip setuptools
   pip install -e .
   ```
   The editable install registers the console scripts `cliuniapp` and `guiuniapp` defined in `pyproject.toml`.

#### Option B – uv-managed environment

1. Ensure `uv` is installed (`pip install uv` or see the uv documentation).
2. Sync dependencies and create the managed virtual environment.
   ```bash
   uv sync
   ```
   This respects `pyproject.toml` and `uv.lock`, generating `.venv/` automatically.
3. Use `uv run` for ad-hoc commands without manual activation, or activate `.venv` as above if you prefer.

> Both options install three runtime dependencies: `rich` for the CLI UI, `customtkinter` for the GUI, and `bcrypt` for secure password hashing.

### Configurations

Key runtime tunables live in `constants.py`:

- `MAX_SUBJECTS_PER_STUDENT` (default 4) limits concurrent enrolments.
- `PASSING_AVERAGE` defines the pass/fail threshold used by admin analytics.
- `DATA_FILE` points to the JSON datastore (`students.data`). Change this to relocate persistent data or to use isolated datasets per environment.
- `MAX_LOGIN_ATTEMPTS` caps consecutive failed logins before returning the user to the main menu.

Additional behaviour is controlled via:

- `messages.py`: centralised CLI copy, colors, and prompt strings used by both student and admin flows.
- `utils/password.py`: password hashing and validation helpers. Adjust policies here if you tighten credential requirements.

Whenever you modify configuration constants, delete or migrate the existing `students.data` file if schema changes are incompatible with previous data.

### Run & Use

#### CLI application

- **pip/venv**: `python cli.py` or `python -m cli`.
- **From console script**: `cliuniapp` (available after `pip install -e .`).
- **uv**: `uv run cli.py` or `uv run cliuniapp`.

CLI navigation highlights:

- Main menu routes to Admin (`a`), Student (`s`), or Exit (`x`).
- Student menu supports registration (`r`), login (`l`), and exit (`x`). Logged-in students can enrol (`e`), remove (`r`), inspect grades (`s`), or change passwords (`c`).
- Admin menu provides list (`s`), remove (`r`), clear datastore (`c`), grade grouping (`g`), and pass/fail partitioning (`p`).

#### GUI application

- **pip/venv**: `python gui.py`.
- **uv**: `uv run gui.py`.

The GUI mirrors the student-facing flows with CustomTkinter windows for login, enrolment management, and password updates. Both interfaces operate on the same backend services, so you can mix usage (e.g., register via CLI, log in via GUI).

#### Data management

- Persistent records live in `students.data`. To reset the system, use the admin "Clear All" action or delete the file manually while the app is closed.
- Passwords are stored hashed with `bcrypt`; do not edit them manually unless you re-hash the replacements.

### Testing & Verification

The repository does not currently include automated tests. Recommended manual checks:

1. **Fresh datastore**: remove `students.data` (or use Clear All) and start the CLI to ensure a clean state.
2. **Student flow**: register a new student, log in, enrol and remove subjects, and confirm grade display.
3. **Admin analytics**: add multiple students with varying averages, then verify grouping (`g`) and pass/fail partitioning (`p`).
4. **GUI parity**: launch `python gui.py`, log in with the CLI-created account, and confirm enrolment changes persist across interfaces.
