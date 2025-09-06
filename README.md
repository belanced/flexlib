# FlexLib

A collection of flexible utility classes for Python development on POSIX systems (Linux, macOS, and other Unix-like systems).

## Overview

FlexLib provides two main utilities designed to make Python development more productive and intuitive:

- **FlexDict**: A flexible dictionary with dot notation access and automatic nested structure creation
- **FlexPath**: A POSIX-compatible path library that subclasses `str` for seamless path manipulation

## Features

### FlexDict - Enhanced Dictionary with Dot Notation

FlexDict enhances Python's built-in `dict` with user-friendly features similar to `addict` or `easydict`.

**Key Features:**
- **Dict inheritance**: Full compatibility with Python's `dict` interface
- **Dot notation**: Access and set values using `obj.key` syntax
- **Auto-creation**: Automatically creates nested structures on assignment
- **Type conversion**: Converts nested dicts to FlexDict objects automatically

### FlexPath - POSIX-Compatible Path Library

FlexPath provides a powerful interface for path manipulation on Unix-like systems.

**Key Features:**
- **String subclass**: FlexPath objects can be used anywhere strings are expected
- **Immutable**: Operations return new FlexPath instances
- **Standalone**: No external dependencies, uses only Python standard library
- **Cross-platform**: Supports Linux, macOS, and other Unix-like systems
- **POSIX semantics**: Follows POSIX path conventions consistently

## Installation

### From PyPI (when available)

```bash
pip install flexlib
```

### Development Installation

```bash
git clone https://github.com/belanced/flexlib.git
cd flexlib
pip install -e .
```

### Development with Testing Dependencies

```bash
git clone https://github.com/belanced/flexlib.git
cd flexlib
pip install -e .[dev]
```

## Quick Start

### FlexDict Example

```python
from flexlib import FlexDict

# Create and use FlexDict
config = FlexDict()
config.database.host = "localhost"
config.database.port = 5432
config.api.endpoints.users = "/api/v1/users"

# Access using dot notation or brackets
print(config.database.host)  # localhost
print(config["database"]["port"])  # 5432

# Equivalent to:
config2 = FlexDict(database={"host": "localhost", "port": 5432})
```

### FlexPath Example

```python
from flexlib import FlexPath

# Create paths
p = FlexPath("/home/user/documents")
print(p)  # /home/user/documents

# Path manipulation
file_path = p / "report.txt"
backup_path = file_path.with_suffix(".bak")
print(backup_path)  # /home/user/documents/report.bak

# File operations
file_path.write_text("Hello, World!")
content = file_path.read_text()
print(content)  # Hello, World!
```

## Usage Examples

### FlexDict Examples

#### Configuration Management

```python
from flexlib import FlexDict

# Create configuration with nested structure
config = FlexDict()
config.database.host = "localhost"
config.database.port = 5432
config.database.credentials.username = "admin"
config.logging.level = "INFO"
config.logging.handlers.file.enabled = True

# Easy access
print(f"DB: {config.database.host}:{config.database.port}")
if config.logging.handlers.file.enabled:
    print("File logging enabled")
```

#### API Response Processing

```python
from flexlib import FlexDict
import json

# Convert API response to FlexDict
api_data = '{"user": {"name": "Alice", "profile": {"bio": "Engineer"}}}'
data = FlexDict(json.loads(api_data))

# Easy nested access
print(data.user.name)           # Alice
print(data.user.profile.bio)    # Engineer

# Convert back to regular dict
regular_dict = data.to_dict()
```

#### Dynamic Object Creation

```python
from flexlib import FlexDict

# Both approaches are equivalent:
# Approach 1: Direct construction
fd1 = FlexDict(name="John", age=40, abilities={"english": "strong"})

# Approach 2: Dot notation assignment
fd2 = FlexDict()
fd2.name = "John"
fd2.age = 40
fd2.abilities.english = "strong"

# Both produce identical results
assert fd1.name == fd2.name
assert fd1.abilities.english == fd2.abilities.english
```

### FlexPath Examples

#### Basic Path Operations

```python
from flexlib import FlexPath

# Path creation and normalization
p = FlexPath("/home//user/../user/./docs")
print(p)  # /home/user/docs (automatically normalized)

# Path properties
print(p.name)        # docs
print(p.parent)      # /home/user
print(p.parts)       # ('/', 'home', 'user', 'docs')
print(p.stem)        # docs
```

#### File and Directory Operations

```python
from flexlib import FlexPath

# Create directories
project_dir = FlexPath("/tmp/my_project")
project_dir.mkdir(parents=True, exist_ok=True)

# Create and read files
config_file = project_dir / "config.json"
config_file.write_text('{"debug": true}')
settings = config_file.read_text()

# Directory iteration
for item in project_dir.iterdir():
    print(f"Found: {item.name} ({'dir' if item.is_dir() else 'file'})")
```

#### Pattern Matching and Globbing

```python
from flexlib import FlexPath

project = FlexPath("/home/user/project")

# Find all Python files
python_files = list(project.glob("**/*.py"))

# Pattern matching
path = FlexPath("/home/user/document.pdf")
print(path.match("*.pdf"))     # True
print(path.match("**/doc*"))   # True
```

## Detailed Documentation

For comprehensive guides and API references, see the detailed documentation:

- **[FlexDict User Guide](doc/flexdict.md)** - Complete guide to FlexDict usage, features, and best practices
- **[FlexPath User Guide](doc/flexpath.md)** - Complete guide to FlexPath usage, features, and best practices

## Common Use Cases

### FlexDict is Perfect For:
- Configuration management
- API response processing  
- Dynamic data structures
- Nested settings and preferences
- JSON-like data manipulation

### FlexPath is Perfect For:
- File system operations
- Path manipulation
- Directory traversal
- File I/O operations
- Cross-platform path handling (POSIX systems)

## Combining FlexDict and FlexPath

```python
from flexlib import FlexDict, FlexPath

# Configuration with paths
config = FlexDict()
config.paths.home = FlexPath.home()
config.paths.config_dir = config.paths.home / ".config" / "myapp"
config.paths.log_file = config.paths.config_dir / "app.log"

# Ensure directories exist
config.paths.config_dir.mkdir(parents=True, exist_ok=True)

# Write configuration
config_file = config.paths.config_dir / "settings.json"
config_data = config.to_dict()  # Convert FlexDict to regular dict
# Note: Convert FlexPath objects to strings for JSON serialization
config_data['paths'] = {k: str(v) for k, v in config_data['paths'].items()}

import json
config_file.write_text(json.dumps(config_data, indent=2))
```

## Platform Support

FlexLib is designed for POSIX-compatible systems:

- **Linux** (all distributions)
- **macOS** (all versions)
- **Unix-like systems** (BSD, Solaris, etc.)

**Note**: FlexPath is intentionally not supported on Windows due to different path semantics. FlexDict works on all platforms.

## Requirements

- Python 3.8 or higher
- POSIX-compatible operating system (for FlexPath)

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_flexdict.py -v
pytest tests/test_flexpath.py -v

# Run with coverage
pytest tests/ --cov=flexlib
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Changelog

### v0.0.2
- Added FlexDict implementation
- Enhanced documentation with separate user guides
- Improved project structure

### v0.0.1
- Initial release with FlexPath

## License

MIT License - see LICENSE file for details.

## Repository

GitHub: [https://github.com/belanced/flexlib](https://github.com/belanced/flexlib)
