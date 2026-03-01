# 🛡️ PyCareTaker v0.1

**A smart Python package manager companion** — manage, monitor, visualize, and analyze your Python environment with optional AI insights.

> Not just another pip wrapper, but a developer assistant.

---

## ✨ Features

### Core Features
| Command | Description |
|---------|-------------|
| `install <pkg>` | Install a package and auto-update requirements.txt |
| `remove <pkg>` | Uninstall a package |
| `deps` | Visualize dependency graph (networkx + matplotlib) |
| `outdated` | Compare installed versions against PyPI latest |
| `diff` | Compare current env vs saved requirements.txt |
| `memwatch` | Live memory + CPU profiler with dual graphs |
| `security` | Vulnerability scan (pip-audit + PyPI + AI) |
| `plugins` | Run custom user plugins |
| `interactive` | Interactive shell with all commands |

### AI Features (optional)
| Command | Description |
|---------|-------------|
| `ai "Add a web framework"` | Natural language → pip actions |
| Auto-recommendations | AI suggests related packages after install |
| Security insights | AI analyzes CVE databases |
| Profiling analysis | AI interprets memory/CPU graphs |

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install networkx requests packaging colorama psutil matplotlib

# Run help
python package_manager.py --help

# Examples
python package_manager.py deps                          # Dependency graph
python package_manager.py deps --text                   # Text tree
python package_manager.py outdated                      # Version check
python package_manager.py diff                          # Env diff
python package_manager.py memwatch                      # CPU + Memory profiler
python package_manager.py memwatch --export usage.csv   # Export on exit
python package_manager.py security                      # Vulnerability scan
python package_manager.py plugins                       # Run user plugins
python package_manager.py interactive                   # Interactive mode
```

### With AI
```bash
# Using OpenAI API
python package_manager.py --api-key sk-... ai "Add a web framework"

# Using local Ollama (auto-detected)
python package_manager.py ai "Remove all testing libraries"

# Environment variable
export OPENAI_API_KEY=sk-...
python package_manager.py ai "What packages do I need for data science?"
```

---

## 🔌 Plugin System

Drop `.py` scripts in the `plugins/` folder. Each must define:

```python
def run(context: dict) -> None:
    packages = context["installed_packages"]  # {name: version}
    # Your custom logic
```

See `pycaretaker/plugins/examples/license_check.py` for a reference.

---

## 📁 Project Structure

```
PyCareTaker/
├── package_manager.py          # Entry point
├── pycaretaker/
│   ├── cli.py                  # CLI dispatcher
│   ├── core/                   # Non-AI features
│   │   ├── packages.py         # Install/remove/freeze
│   │   ├── monitor.py          # Background change detection
│   │   ├── deps.py             # Dependency visualization
│   │   ├── outdated.py         # PyPI version tracking
│   │   ├── diff.py             # Environment diffing
│   │   ├── profiler.py         # Memory + CPU profiler
│   │   └── export.py           # CSV/JSON export
│   ├── ai/                     # AI features (optional)
│   │   ├── backend.py          # Flexible LLM backend
│   │   ├── nlp_commands.py     # Natural language → actions
│   │   ├── recommendations.py  # Package suggestions
│   │   ├── security.py         # CVE/vulnerability analysis
│   │   └── analysis.py         # Profiling interpretation
│   └── plugins/                # Plugin loader + examples
├── plugins/                    # User plugin drop folder
├── tests/                      # Unit tests
└── requirements.txt
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/test_core.py -v
```

---

## 📄 License

MIT License

Copyright (c) [year] [Full name or organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.