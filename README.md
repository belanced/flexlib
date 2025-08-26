# FlexLib

A collection of flexible utility classes for Python development on POSIX systems (Linux, macOS, and other Unix-like systems).

## Features

### FlexPath - A POSIX-Compatible Path Library

FlexPath is a pathlib-like path class that subclasses `str`, providing a familiar and powerful interface for path manipulation on POSIX systems.

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

```python
from flexlib.flexpath import FlexPath

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

### Basic Path Operations

```python
from flexlib.flexpath import FlexPath

# Path creation and normalization
p = FlexPath("/home//user/../user/./docs")
print(p)  # /home/user/docs (automatically normalized)

# Path properties
print(p.name)        # docs
print(p.parent)      # /home/user
print(p.parts)       # ('/', 'home', 'user', 'docs')
print(p.suffix)      # (empty for directories)
print(p.stem)        # docs
```

### File and Directory Operations

```python
from flexlib.flexpath import FlexPath

# Create directories
project_dir = FlexPath("/tmp/my_project")
project_dir.mkdir(parents=True, exist_ok=True)

# Create files
config_file = project_dir / "config.json"
config_file.write_text('{"debug": true}')

# Read files
settings = config_file.read_text()
print(settings)  # {"debug": true}

# File operations
data_file = project_dir / "data.bin"
data_file.write_bytes(b"\x00\x01\x02\x03")
binary_data = data_file.read_bytes()

# Directory iteration
for item in project_dir.iterdir():
    print(f"Found: {item.name} ({'dir' if item.is_dir() else 'file'})")
```

### Path Manipulation

```python
from flexlib.flexpath import FlexPath

# Working with file extensions
source = FlexPath("/src/main.py")
compiled = source.with_suffix(".pyc")
backup = source.with_name("main_backup.py")

print(source)    # /src/main.py
print(compiled)  # /src/main.pyc
print(backup)    # /src/main_backup.py

# Path joining
base = FlexPath("/home/user")
documents = base / "Documents" / "Projects"
print(documents)  # /home/user/Documents/Projects

# Relative paths
project_root = FlexPath("/home/user/projects/myapp")
source_file = FlexPath("/home/user/projects/myapp/src/main.py")
relative = source_file.relative_to(project_root)
print(relative)  # src/main.py
```

### Pattern Matching and Globbing

```python
from flexlib.flexpath import FlexPath

# Glob patterns
project = FlexPath("/home/user/project")

# Find all Python files
python_files = list(project.glob("**/*.py"))
for py_file in python_files:
    print(py_file)

# Find specific patterns
test_files = list(project.glob("tests/test_*.py"))
config_files = list(project.glob("**/config.*"))

# Pattern matching
path = FlexPath("/home/user/document.pdf")
print(path.match("*.pdf"))     # True
print(path.match("**/doc*"))   # True
print(path.match("*.txt"))     # False
```

### Platform-Specific Usage

#### Linux Examples

```python
from flexlib.flexpath import FlexPath

# Linux-specific paths
proc_info = FlexPath("/proc/cpuinfo")
if proc_info.exists():
    cpu_info = proc_info.read_text()

# Home directory on Linux
home = FlexPath.home()  # typically /home/username
desktop = home / "Desktop"
downloads = home / "Downloads"
```

#### macOS Examples

```python
from flexlib.flexpath import FlexPath

# macOS-specific paths
preferences = FlexPath("~/Library/Preferences").expanduser()
applications = FlexPath("/Applications")

# macOS home directory
home = FlexPath.home()  # typically /Users/username
desktop = home / "Desktop"
documents = home / "Documents"

# Working with app bundles
app_bundle = applications / "TextEdit.app"
if app_bundle.exists():
    print(f"TextEdit is installed at {app_bundle}")
```

### Advanced Features

#### Symbolic Links

```python
from flexlib.flexpath import FlexPath

# Create symbolic links
source = FlexPath("/path/to/original/file.txt")
link = FlexPath("/path/to/link.txt")

source.write_text("Original content")
link.symlink_to(source)

# Work with symbolic links
print(link.is_symlink())  # True
print(link.readlink())    # /path/to/original/file.txt
print(link.read_text())   # Original content
```

#### File Permissions

```python
from flexlib.flexpath import FlexPath

script = FlexPath("/tmp/script.sh")
script.write_text("#!/bin/bash\necho 'Hello, World!'")

# Make executable
script.chmod(0o755)

# Check permissions
stat_info = script.stat()
print(f"File size: {stat_info.st_size} bytes")
print(f"Owner: {script.owner()}")
print(f"Group: {script.group()}")
```

#### URI Conversion

```python
from flexlib.flexpath import FlexPath

# Convert to file URI
path = FlexPath("/home/user/document with spaces.txt")
uri = path.as_uri()
print(uri)  # file:///home/user/document%20with%20spaces.txt
```

## API Reference

### Class Methods

- `FlexPath.cwd()` - Get current working directory
- `FlexPath.home()` - Get user home directory

### Properties

- `parts` - Tuple of path components
- `name` - Final component (filename)
- `suffix` - File extension (with dot)
- `suffixes` - List of all suffixes
- `stem` - Filename without extension
- `parent` - Parent directory
- `parents` - Tuple of ancestor directories
- `anchor`, `root`, `drive` - Path components (POSIX-specific)

### Path Operations

- `joinpath(*others)` - Join path components
- `with_name(name)` - Replace filename
- `with_suffix(suffix)` - Replace file extension
- `with_stem(stem)` - Replace filename stem
- `relative_to(*other)` - Get relative path
- `is_relative_to(*other)` - Check if path is relative to another

### File System Operations

- `exists()` - Check if path exists
- `is_file()` - Check if path is a file
- `is_dir()` - Check if path is a directory
- `is_symlink()` - Check if path is a symbolic link
- `mkdir(mode, parents, exist_ok)` - Create directory
- `touch(mode, exist_ok)` - Create empty file
- `unlink(missing_ok)` - Remove file
- `rmdir()` - Remove empty directory
- `iterdir()` - Iterate directory contents
- `glob(pattern)` - Find paths matching pattern
- `rglob(pattern)` - Recursive glob

### File I/O

- `read_text(encoding, errors)` - Read file as text
- `write_text(data, encoding, errors)` - Write text to file
- `read_bytes()` - Read file as bytes
- `write_bytes(data)` - Write bytes to file
- `open(mode, ...)` - Open file

### Metadata

- `stat()` - Get file statistics
- `owner()` - Get file owner name
- `group()` - Get file group name
- `chmod(mode)` - Change file permissions

## Platform Support

FlexLib is designed for POSIX-compatible systems:

- **Linux** (all distributions)
- **macOS** (all versions)
- **Unix-like systems** (BSD, Solaris, etc.)

**Note**: Windows is intentionally not supported due to different path semantics.

## Requirements

- Python 3.8 or higher
- POSIX-compatible operating system

## Development

### Running Tests

```bash
# Run all tests
python -m unittest tests.test_flexpath -v

# Run with pytest (if installed)
pytest tests/ -v

# Run platform-specific tests (automatically skipped on other platforms)
python -m unittest tests.test_flexpath.TestFlexPathPlatform -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Repository

GitHub: [https://github.com/belanced/flexlib](https://github.com/belanced/flexlib)
