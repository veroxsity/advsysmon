# Scripts Directory

This directory contains utility scripts for the Advanced System Monitor project.

## Scripts

### `install.sh`
Universal installation script that works on any Linux system. Installs the system monitor to `/usr/local` and creates a desktop entry.

**Usage:**
```bash
./scripts/install.sh
```

### `build.sh`
Builds distribution packages including Python wheels, source distributions, and installation archives.

**Usage:**
```bash
./scripts/build.sh
```

**Output:** Creates packages in the `releases/` directory.

### `push-to-github.sh`
Automated script for committing and pushing changes to GitHub.

**Usage:**
```bash
./scripts/push-to-github.sh
```

**Features:**
- Automatically detects uncommitted changes
- Prompts for commit message (or generates one automatically)
- Commits and pushes to the current branch
- Provides helpful error messages and next steps

## File Structure Requirements

All scripts expect to be run from the project root directory or will automatically navigate there. The project structure should be:

```
/opt/SysMon/
├── src/
│   └── advsysmon.py
├── scripts/
│   ├── install.sh
│   ├── build.sh
│   └── push-to-github.sh
├── docs/
├── releases/
├── requirements.txt
├── setup.py
├── README.md
└── LICENSE
```
