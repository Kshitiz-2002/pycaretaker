# PyCareTaker User Plugins

Drop your custom `.py` plugin scripts here.

## How to write a plugin

Each plugin must define a `run(context)` function:

```python
def run(context: dict) -> None:
    """
    context contains:
      - installed_packages: dict of {name: version}
      - (more fields may be added in future versions)
    """
    packages = context.get("installed_packages", {})
    print(f"  Checking {len(packages)} packages …")
    # Your custom logic here
```

## Running plugins

```bash
python package_manager.py plugins
# or specify a custom directory:
python package_manager.py plugins --dir /path/to/plugins
```

## Example plugins

See `pycaretaker/plugins/examples/` for reference implementations.
