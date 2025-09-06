# FlexPath User Guide

FlexPath is a POSIX-compatible path library that provides a powerful and intuitive interface for path manipulation on Unix-like systems. It subclasses Python's `str`, making it a drop-in replacement for string paths while offering enhanced functionality similar to `pathlib.Path`.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Path Operations](#path-operations)
- [File System Operations](#file-system-operations)
- [Pattern Matching and Globbing](#pattern-matching-and-globbing)
- [Platform-Specific Features](#platform-specific-features)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

FlexPath is designed specifically for POSIX-compatible systems (Linux, macOS, and other Unix-like systems) and provides:

### Key Features

- **String subclass**: FlexPath objects can be used anywhere strings are expected
- **Immutable**: Operations return new FlexPath instances, ensuring thread safety
- **Standalone**: No external dependencies, uses only Python standard library
- **Cross-platform**: Supports Linux, macOS, and other Unix-like systems
- **POSIX semantics**: Follows POSIX path conventions consistently
- **Rich API**: Comprehensive set of methods for path manipulation and file operations

### Platform Support

- **Linux** (all distributions)
- **macOS** (all versions)
- **Unix-like systems** (BSD, Solaris, etc.)

**Note**: Windows is intentionally not supported due to different path semantics.

## Installation

FlexPath is part of the FlexLib package. Install it using pip:

```bash
pip install flexlib
```

For development installation:

```bash
git clone https://github.com/belanced/flexlib.git
cd flexlib
pip install -e .
```

## Basic Usage

### Importing FlexPath

```python
from flexlib import FlexPath
# or
from flexlib.flexpath import FlexPath
```

### Creating FlexPath Objects

```python
# From string paths
p = FlexPath("/home/user/documents")
p = FlexPath("~/Documents")  # Tilde expansion with expanduser()
p = FlexPath("../relative/path")

# From existing paths
existing = "/tmp/file.txt"
p = FlexPath(existing)

# Current working directory
cwd = FlexPath.cwd()

# User home directory
home = FlexPath.home()
```

### Basic Path Information

```python
p = FlexPath("/home/user/documents/report.txt")

print(p)              # /home/user/documents/report.txt
print(p.name)         # report.txt
print(p.parent)       # /home/user/documents
print(p.suffix)       # .txt
print(p.stem)         # report
print(p.parts)        # ('/', 'home', 'user', 'documents', 'report.txt')
```

## Path Operations

### Path Components

```python
p = FlexPath("/home/user/projects/myapp/src/main.py")

# Path components
print(p.parts)        # ('/', 'home', 'user', 'projects', 'myapp', 'src', 'main.py')
print(p.name)         # main.py
print(p.suffix)       # .py
print(p.suffixes)     # ['.py']
print(p.stem)         # main
print(p.parent)       # /home/user/projects/myapp/src
print(p.parents)      # Tuple of all parent directories

# Root components
print(p.anchor)       # /
print(p.root)         # /
print(p.drive)        # '' (empty on POSIX systems)
```

### Path Manipulation

#### Joining Paths

```python
base = FlexPath("/home/user")
docs = base / "Documents"
project = docs / "myproject" / "src"

print(project)  # /home/user/Documents/myproject/src

# Alternative method
project = base.joinpath("Documents", "myproject", "src")
```

#### Changing Path Components

```python
source = FlexPath("/src/main.py")

# Change filename
backup = source.with_name("main_backup.py")
print(backup)  # /src/main_backup.py

# Change extension
compiled = source.with_suffix(".pyc")
print(compiled)  # /src/main.pyc

# Change stem (filename without extension)
test_file = source.with_stem("test_main")
print(test_file)  # /src/test_main.py
```

#### Relative and Absolute Paths

```python
# Working with relative paths
project_root = FlexPath("/home/user/projects/myapp")
source_file = FlexPath("/home/user/projects/myapp/src/main.py")

# Get relative path
relative = source_file.relative_to(project_root)
print(relative)  # src/main.py

# Check if relative to another path
print(source_file.is_relative_to(project_root))  # True

# Resolve relative paths to absolute
rel_path = FlexPath("../data/config.json")
abs_path = rel_path.resolve()
```

#### Path Normalization

```python
# FlexPath automatically normalizes paths
messy_path = FlexPath("/home//user/../user/./docs")
print(messy_path)  # /home/user/docs

# Expand user directory
user_path = FlexPath("~/Documents/file.txt")
expanded = user_path.expanduser()
print(expanded)  # /home/username/Documents/file.txt (actual username)
```

## File System Operations

### Checking Path Properties

```python
p = FlexPath("/home/user/document.txt")

# Existence checks
print(p.exists())        # True/False
print(p.is_file())       # True if it's a file
print(p.is_dir())        # True if it's a directory
print(p.is_symlink())    # True if it's a symbolic link
print(p.is_mount())      # True if it's a mount point
print(p.is_block_device())  # True if it's a block device
print(p.is_char_device())   # True if it's a character device
print(p.is_fifo())       # True if it's a FIFO
print(p.is_socket())     # True if it's a socket
```

### Directory Operations

#### Creating Directories

```python
# Create a single directory
new_dir = FlexPath("/tmp/new_directory")
new_dir.mkdir()

# Create directory with parents
project_dir = FlexPath("/tmp/projects/myapp/src")
project_dir.mkdir(parents=True, exist_ok=True)

# Set permissions
secure_dir = FlexPath("/tmp/secure")
secure_dir.mkdir(mode=0o700)  # Owner read/write/execute only
```

#### Iterating Directory Contents

```python
project_dir = FlexPath("/home/user/project")

# List all items
for item in project_dir.iterdir():
    print(f"{item.name}: {'DIR' if item.is_dir() else 'FILE'}")

# Filter by type
files = [item for item in project_dir.iterdir() if item.is_file()]
dirs = [item for item in project_dir.iterdir() if item.is_dir()]
```

#### Removing Directories

```python
# Remove empty directory
empty_dir = FlexPath("/tmp/empty")
empty_dir.rmdir()

# For non-empty directories, use shutil
import shutil
non_empty_dir = FlexPath("/tmp/project")
shutil.rmtree(str(non_empty_dir))
```

### File Operations

#### Creating Files

```python
# Create empty file
new_file = FlexPath("/tmp/new_file.txt")
new_file.touch()

# Create with specific permissions
script = FlexPath("/tmp/script.sh")
script.touch(mode=0o755)  # Executable by owner

# Create only if it doesn't exist
new_file.touch(exist_ok=False)  # Raises FileExistsError if exists
```

#### Reading Files

```python
config_file = FlexPath("/etc/hostname")

# Read as text
try:
    content = config_file.read_text()
    print(f"Hostname: {content.strip()}")
except FileNotFoundError:
    print("File not found")
except PermissionError:
    print("Permission denied")

# Read as bytes
binary_file = FlexPath("/tmp/data.bin")
if binary_file.exists():
    data = binary_file.read_bytes()
    print(f"File size: {len(data)} bytes")

# Read with specific encoding
text_file = FlexPath("/tmp/unicode.txt")
content = text_file.read_text(encoding='utf-8')
```

#### Writing Files

```python
output_file = FlexPath("/tmp/output.txt")

# Write text
output_file.write_text("Hello, World!\n")

# Write with specific encoding
output_file.write_text("Hello, 世界!\n", encoding='utf-8')

# Write bytes
binary_file = FlexPath("/tmp/data.bin")
binary_file.write_bytes(b"\x00\x01\x02\x03")

# Append mode requires opening the file
log_file = FlexPath("/tmp/app.log")
with log_file.open('a') as f:
    f.write("Log entry\n")
```

#### Removing Files

```python
temp_file = FlexPath("/tmp/temporary.txt")

# Remove file
temp_file.unlink()

# Remove only if exists (no error if missing)
temp_file.unlink(missing_ok=True)
```

### File Metadata

#### File Statistics

```python
file_path = FlexPath("/home/user/document.txt")

if file_path.exists():
    stat_info = file_path.stat()
    
    print(f"Size: {stat_info.st_size} bytes")
    print(f"Modified: {stat_info.st_mtime}")
    print(f"Permissions: {oct(stat_info.st_mode)}")
    print(f"Owner UID: {stat_info.st_uid}")
    print(f"Group GID: {stat_info.st_gid}")
```

#### Ownership and Permissions

```python
file_path = FlexPath("/home/user/script.sh")

# Get owner and group names
try:
    owner = file_path.owner()
    group = file_path.group()
    print(f"Owner: {owner}, Group: {group}")
except KeyError:
    print("Could not determine owner/group")

# Change permissions
file_path.chmod(0o755)  # rwxr-xr-x

# Check if readable/writable/executable
import os
print(f"Readable: {os.access(file_path, os.R_OK)}")
print(f"Writable: {os.access(file_path, os.W_OK)}")
print(f"Executable: {os.access(file_path, os.X_OK)}")
```

## Pattern Matching and Globbing

### Glob Patterns

```python
project = FlexPath("/home/user/project")

# Find all Python files
python_files = list(project.glob("**/*.py"))
for py_file in python_files:
    print(py_file)

# Find files with specific patterns
config_files = list(project.glob("**/config.*"))
test_files = list(project.glob("**/test_*.py"))
log_files = list(project.glob("logs/*.log"))

# Non-recursive glob
top_level_py = list(project.glob("*.py"))
```

### Recursive Glob (rglob)

```python
project = FlexPath("/home/user/project")

# Recursive search (equivalent to glob("**/*.py"))
all_python = list(project.rglob("*.py"))
all_json = list(project.rglob("*.json"))
all_readme = list(project.rglob("README*"))
```

### Pattern Matching

```python
file_path = FlexPath("/home/user/documents/report.pdf")

# Match patterns
print(file_path.match("*.pdf"))        # True
print(file_path.match("**/report.*"))  # True
print(file_path.match("*.txt"))        # False
print(file_path.match("*/documents/*")) # True

# Case-sensitive matching (default on POSIX)
print(file_path.match("*.PDF"))        # False
```

## Platform-Specific Features

### Linux-Specific Operations

```python
# Working with /proc filesystem
proc_info = FlexPath("/proc/cpuinfo")
if proc_info.exists():
    cpu_info = proc_info.read_text()
    print(f"CPU Info: {cpu_info[:200]}...")

# System directories
sys_dirs = [
    FlexPath("/etc"),
    FlexPath("/var/log"),
    FlexPath("/tmp"),
    FlexPath("/usr/local/bin")
]

for dir_path in sys_dirs:
    if dir_path.exists():
        print(f"{dir_path}: {len(list(dir_path.iterdir()))} items")
```

### macOS-Specific Operations

```python
# macOS application bundles
applications = FlexPath("/Applications")
if applications.exists():
    apps = [app for app in applications.iterdir() 
            if app.suffix == '.app']
    print(f"Found {len(apps)} applications")

# User library directories
user_lib = FlexPath.home() / "Library"
preferences = user_lib / "Preferences"
app_support = user_lib / "Application Support"

print(f"Preferences: {preferences.exists()}")
print(f"App Support: {app_support.exists()}")

# Working with .plist files in preferences
if preferences.exists():
    plist_files = list(preferences.glob("*.plist"))
    print(f"Found {len(plist_files)} preference files")
```

## Advanced Features

### Symbolic Links

```python
# Create symbolic links
source = FlexPath("/home/user/documents/important.txt")
link = FlexPath("/home/user/shortcuts/important_link.txt")

# Ensure parent directory exists
link.parent.mkdir(parents=True, exist_ok=True)

# Create the symbolic link
link.symlink_to(source)

# Work with symbolic links
print(f"Is symlink: {link.is_symlink()}")
print(f"Points to: {link.readlink()}")
print(f"Resolved: {link.resolve()}")

# Read through symlink (follows the link)
if source.exists():
    content = link.read_text()  # Reads from the target file
```

### Hard Links

```python
original = FlexPath("/tmp/original.txt")
original.write_text("Hello, World!")

# Create hard link
hard_link = FlexPath("/tmp/hardlink.txt")
hard_link.link_to(original)

# Both paths refer to the same file
print(f"Same file: {original.samefile(hard_link)}")  # True
print(f"Link count: {original.stat().st_nlink}")     # 2
```

### URI Conversion

```python
# Convert paths to file URIs
document = FlexPath("/home/user/document with spaces.txt")
uri = document.as_uri()
print(uri)  # file:///home/user/document%20with%20spaces.txt

# Useful for web applications or file protocols
config_file = FlexPath("/etc/config.json")
if config_file.exists():
    config_uri = config_file.as_uri()
    print(f"Config URI: {config_uri}")
```

### Path Comparison

```python
path1 = FlexPath("/home/user/doc.txt")
path2 = FlexPath("/home/user/../user/doc.txt")

# Paths are normalized automatically
print(path1 == path2)  # True

# Compare with string paths
print(path1 == "/home/user/doc.txt")  # True (FlexPath subclasses str)

# Check if paths refer to the same file (follows symlinks)
if path1.exists() and path2.exists():
    print(path1.samefile(path2))  # True if same file
```

## API Reference

### Class Methods

#### `FlexPath.cwd()`
Get the current working directory as a FlexPath.

```python
current_dir = FlexPath.cwd()
```

#### `FlexPath.home()`
Get the user's home directory as a FlexPath.

```python
home_dir = FlexPath.home()
```

### Instance Methods

#### Path Properties

- `parts` - Tuple of path components
- `name` - Final component (filename)
- `suffix` - File extension including dot (`.txt`)
- `suffixes` - List of all suffixes ([`.tar`, `.gz`])
- `stem` - Filename without final suffix
- `parent` - Parent directory as FlexPath
- `parents` - Tuple of ancestor directories
- `anchor`, `root`, `drive` - Path anchoring components

#### Path Operations

- `joinpath(*others)` - Join path components
- `with_name(name)` - Return path with different filename
- `with_suffix(suffix)` - Return path with different suffix
- `with_stem(stem)` - Return path with different stem
- `relative_to(*other)` - Get path relative to another path
- `is_relative_to(*other)` - Check if path is relative to another
- `resolve(strict=False)` - Resolve to absolute path
- `expanduser()` - Expand `~` to user home directory

#### File System Queries

- `exists()` - Check if path exists
- `is_file()` - Check if path is a regular file
- `is_dir()` - Check if path is a directory
- `is_symlink()` - Check if path is a symbolic link
- `is_mount()` - Check if path is a mount point
- `is_block_device()` - Check if path is a block device
- `is_char_device()` - Check if path is a character device
- `is_fifo()` - Check if path is a FIFO
- `is_socket()` - Check if path is a socket

#### File System Operations

- `mkdir(mode=0o777, parents=False, exist_ok=False)` - Create directory
- `touch(mode=0o666, exist_ok=True)` - Create empty file or update timestamp
- `unlink(missing_ok=False)` - Remove file
- `rmdir()` - Remove empty directory
- `chmod(mode)` - Change file permissions
- `symlink_to(target, target_is_directory=False)` - Create symbolic link
- `link_to(target)` - Create hard link

#### File I/O

- `open(mode='r', buffering=-1, encoding=None, errors=None, newline=None)` - Open file
- `read_text(encoding=None, errors=None)` - Read file as text
- `write_text(data, encoding=None, errors=None)` - Write text to file
- `read_bytes()` - Read file as bytes
- `write_bytes(data)` - Write bytes to file

#### Directory Operations

- `iterdir()` - Iterate over directory contents
- `glob(pattern)` - Find paths matching glob pattern
- `rglob(pattern)` - Recursive glob search

#### Metadata

- `stat()` - Get file statistics
- `lstat()` - Get file statistics (don't follow symlinks)
- `owner()` - Get file owner name
- `group()` - Get file group name
- `readlink()` - Read symbolic link target
- `samefile(other_path)` - Check if paths refer to same file

#### String/URI Operations

- `as_uri()` - Convert to file URI
- `match(pattern)` - Check if path matches glob pattern

## Examples

### Project Directory Management

```python
from flexlib import FlexPath

def setup_project(project_name, base_dir="/home/user/projects"):
    """Set up a new project directory structure."""
    project_root = FlexPath(base_dir) / project_name
    
    # Create directory structure
    directories = [
        project_root / "src",
        project_root / "tests",
        project_root / "docs",
        project_root / "data",
        project_root / "scripts",
        project_root / "config"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")
    
    # Create initial files
    files = {
        project_root / "README.md": f"# {project_name}\n\nProject description here.\n",
        project_root / "src" / "__init__.py": "",
        project_root / "tests" / "__init__.py": "",
        project_root / ".gitignore": "*.pyc\n__pycache__/\n.DS_Store\n",
        project_root / "requirements.txt": "# Add your dependencies here\n"
    }
    
    for file_path, content in files.items():
        file_path.write_text(content)
        print(f"Created: {file_path}")
    
    return project_root

# Usage
project = setup_project("myawesome_app")
print(f"Project created at: {project}")
```

### Log File Rotation

```python
from flexlib import FlexPath
from datetime import datetime
import shutil

def rotate_logs(log_dir, max_files=5):
    """Rotate log files, keeping only the most recent ones."""
    log_path = FlexPath(log_dir)
    
    if not log_path.exists():
        log_path.mkdir(parents=True)
        return
    
    # Find all log files
    log_files = list(log_path.glob("*.log"))
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Rotate files
    for i, log_file in enumerate(log_files):
        if i == 0:
            # Current log file - rename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = log_file.with_name(f"{log_file.stem}_{timestamp}.log")
            log_file.rename(archived_name)
            print(f"Archived: {log_file} -> {archived_name}")
        elif i >= max_files:
            # Remove old files
            log_file.unlink()
            print(f"Removed old log: {log_file}")

# Usage
rotate_logs("/var/log/myapp")
```

### Configuration File Management

```python
import json
from flexlib import FlexPath

class ConfigManager:
    def __init__(self, app_name):
        self.app_name = app_name
        self.config_dir = FlexPath.home() / ".config" / app_name
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, defaults=None):
        """Load configuration from file."""
        if not self.config_file.exists():
            if defaults:
                self.save_config(defaults)
                return defaults
            return {}
        
        try:
            content = self.config_file.read_text()
            return json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Error reading config: {e}")
            return defaults or {}
    
    def save_config(self, config):
        """Save configuration to file."""
        content = json.dumps(config, indent=2, sort_keys=True)
        self.config_file.write_text(content)
    
    def backup_config(self):
        """Create a backup of the current configuration."""
        if not self.config_file.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.config_file.with_name(f"config_backup_{timestamp}.json")
        
        shutil.copy2(str(self.config_file), str(backup_file))
        return backup_file

# Usage
config_manager = ConfigManager("myapp")

# Load with defaults
defaults = {
    "theme": "dark",
    "language": "en",
    "auto_save": True
}

config = config_manager.load_config(defaults)
print(f"Current config: {config}")

# Modify and save
config["theme"] = "light"
config_manager.save_config(config)
```

### File Synchronization

```python
import hashlib
from flexlib import FlexPath

def calculate_hash(file_path):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with file_path.open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_directories(source_dir, target_dir, dry_run=False):
    """Synchronize files from source to target directory."""
    source = FlexPath(source_dir)
    target = FlexPath(target_dir)
    
    if not source.exists():
        print(f"Source directory does not exist: {source}")
        return
    
    # Ensure target directory exists
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    
    # Find all files in source
    source_files = list(source.rglob("*"))
    source_files = [f for f in source_files if f.is_file()]
    
    for source_file in source_files:
        # Calculate relative path
        rel_path = source_file.relative_to(source)
        target_file = target / rel_path
        
        # Check if sync is needed
        needs_sync = True
        
        if target_file.exists():
            # Compare file hashes
            source_hash = calculate_hash(source_file)
            target_hash = calculate_hash(target_file)
            needs_sync = source_hash != target_hash
        
        if needs_sync:
            if dry_run:
                print(f"Would sync: {rel_path}")
            else:
                # Ensure target directory exists
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                import shutil
                shutil.copy2(str(source_file), str(target_file))
                print(f"Synced: {rel_path}")

# Usage
sync_directories("/home/user/documents", "/backup/documents", dry_run=True)
```

## Best Practices

### 1. Use FlexPath Consistently

Once you start using FlexPath, use it throughout your application for consistency:

```python
# Good
base_dir = FlexPath("/home/user/project")
config_file = base_dir / "config.json"
log_dir = base_dir / "logs"

# Avoid mixing
base_dir = FlexPath("/home/user/project")
config_file = str(base_dir) + "/config.json"  # Don't do this
```

### 2. Handle Exceptions Appropriately

Always handle potential file system exceptions:

```python
config_file = FlexPath("/etc/myapp/config.json")

try:
    config = config_file.read_text()
except FileNotFoundError:
    print("Config file not found, using defaults")
    config = "{}"
except PermissionError:
    print("Permission denied reading config file")
    sys.exit(1)
except UnicodeDecodeError:
    print("Config file contains invalid characters")
    sys.exit(1)
```

### 3. Use Path Properties Instead of String Operations

Leverage FlexPath's properties instead of string manipulation:

```python
file_path = FlexPath("/home/user/document.txt")

# Good
name_without_ext = file_path.stem
extension = file_path.suffix
parent_dir = file_path.parent

# Avoid
name_without_ext = str(file_path).rsplit('.', 1)[0]  # Error-prone
```

### 4. Platform-Aware Code

Write code that's aware of platform differences:

```python
import sys
from flexlib import FlexPath

def get_config_dir(app_name):
    """Get platform-appropriate config directory."""
    if sys.platform == "darwin":  # macOS
        return FlexPath.home() / "Library" / "Application Support" / app_name
    else:  # Linux and other Unix-like
        return FlexPath.home() / ".config" / app_name

config_dir = get_config_dir("myapp")
```

### 5. Use Context Managers for File Operations

Always use context managers when working with files:

```python
log_file = FlexPath("/var/log/app.log")

# Good
with log_file.open('a') as f:
    f.write("Log message\n")

# For simple operations, use read_text/write_text
content = log_file.read_text()
log_file.write_text("New content\n")
```

### 6. Validate Paths Before Operations

Validate paths before performing operations:

```python
def safe_delete(file_path):
    """Safely delete a file with validation."""
    path = FlexPath(file_path)
    
    if not path.exists():
        print(f"File does not exist: {path}")
        return False
    
    if not path.is_file():
        print(f"Path is not a file: {path}")
        return False
    
    if path.is_symlink():
        print(f"Path is a symbolic link: {path}")
        # Decide if you want to delete symlinks
    
    try:
        path.unlink()
        return True
    except PermissionError:
        print(f"Permission denied: {path}")
        return False
```

FlexPath provides a robust and intuitive interface for path operations on POSIX systems, making file system operations more reliable and maintainable.
