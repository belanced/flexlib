# FlexDict User Guide

FlexDict is a flexible dictionary implementation that enhances Python's built-in `dict` with dot notation access and automatic creation of nested structures, similar to popular libraries like `addict` and `easydict`.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

FlexDict provides the convenience of dot notation access while maintaining full compatibility with Python's standard dictionary interface. It automatically creates nested FlexDict objects when needed, making it perfect for configuration files, API responses, and any scenario where you need flexible data structures.

### Key Features

- **Dict inheritance**: Full compatibility with Python's `dict` interface
- **Dot notation**: Access and set values using `obj.key` syntax
- **Auto-creation**: Automatically creates nested structures on assignment
- **Type conversion**: Automatically converts nested dicts to FlexDict objects
- **Immutable keys**: Protects dict methods and private attributes from modification

## Installation

FlexDict is part of the FlexLib package. Install it using pip:

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

### Importing FlexDict

```python
from flexlib import FlexDict
# or
from flexlib.flexdict import FlexDict
```

### Creating FlexDict Objects

#### Empty FlexDict

```python
fd = FlexDict()
print(fd)  # FlexDict()
```

#### From existing dictionary

```python
data = {"name": "John", "age": 30, "city": "New York"}
fd = FlexDict(data)
print(fd.name)  # John
print(fd.age)   # 30
```

#### From keyword arguments

```python
fd = FlexDict(name="John Doe", age=40, abilities={"english": "strong"})
print(fd.name)  # John Doe
print(fd.abilities.english)  # strong
```

#### The Two Equivalent Approaches

These two approaches produce identical results:

```python
# Approach 1: Direct construction
fd1 = FlexDict(name="John Doe", age=40, abilities={"english": "strong"})

# Approach 2: Dot notation assignment
fd2 = FlexDict()
fd2.name = "John Doe"
fd2.age = 40
fd2.abilities.english = "strong"

# Both produce the same result
assert fd1.name == fd2.name
assert fd1.age == fd2.age
assert fd1.abilities.english == fd2.abilities.english
```

### Basic Operations

#### Setting and Getting Values

```python
fd = FlexDict()

# Using dot notation
fd.username = "alice"
fd.settings.theme = "dark"
fd.settings.notifications.email = True

# Using bracket notation
fd["password"] = "secret"
fd["settings"]["language"] = "en"

# Mixed access
print(fd.username)  # alice
print(fd["settings"].theme)  # dark
print(fd.settings["notifications"].email)  # True
```

#### Automatic Nested Structure Creation

```python
fd = FlexDict()

# This automatically creates the entire nested structure
fd.user.profile.personal.address.street = "123 Main St"

print(fd.user.profile.personal.address.street)  # 123 Main St
print(type(fd.user))  # <class 'flexlib.flexdict.FlexDict'>
```

## Advanced Features

### Dictionary Compatibility

FlexDict inherits from `dict`, so all standard dictionary operations work:

```python
fd = FlexDict(a=1, b=2, c=3)

# Standard dict methods
print(list(fd.keys()))     # ['a', 'b', 'c']
print(list(fd.values()))   # [1, 2, 3]
print(list(fd.items()))    # [('a', 1), ('b', 2), ('c', 3)]

# Dict operations
print(len(fd))         # 3
print('a' in fd)       # True
print(fd.get('d', 0))  # 0

# Pop and update
value = fd.pop('a')
fd.update({'d': 4, 'e': 5})
```

### Nested Dictionary Conversion

FlexDict automatically converts nested dictionaries:

```python
nested_data = {
    "user": {
        "name": "Alice",
        "preferences": {
            "theme": "dark",
            "language": "en"
        }
    },
    "settings": {
        "debug": True
    }
}

fd = FlexDict(nested_data)

# All nested dicts are now FlexDict objects
print(type(fd.user))                    # <class 'flexlib.flexdict.FlexDict'>
print(type(fd.user.preferences))        # <class 'flexlib.flexdict.FlexDict'>
print(fd.user.preferences.theme)        # dark
```

### Converting Back to Regular Dict

Use the `to_dict()` method to convert back to regular Python dictionaries:

```python
fd = FlexDict()
fd.user.name = "Bob"
fd.user.age = 25
fd.settings.theme = "light"

regular_dict = fd.to_dict()
print(type(regular_dict))           # <class 'dict'>
print(type(regular_dict['user']))   # <class 'dict'>
print(regular_dict)
# {'user': {'name': 'Bob', 'age': 25}, 'settings': {'theme': 'light'}}
```

### Deep Copying

FlexDict supports deep copying with the `copy` module:

```python
import copy

fd = FlexDict()
fd.user.scores = [90, 85, 88]
fd.user.name = "Charlie"

fd_copy = copy.deepcopy(fd)

# Modify original
fd.user.name = "David"
fd.user.scores.append(92)

# Copy remains unchanged
print(fd_copy.user.name)     # Charlie
print(fd_copy.user.scores)   # [90, 85, 88]
```

### Update Operations

FlexDict supports various update operations:

```python
fd = FlexDict(a=1, b=2)

# Update with dict
fd.update({'b': 20, 'c': 30})

# Update with another FlexDict
fd2 = FlexDict(d=40, e=50)
fd.update(fd2)

# Update with keyword arguments
fd.update(f=60, g=70)

print(fd)  # FlexDict({'a': 1, 'b': 20, 'c': 30, 'd': 40, 'e': 50, 'f': 60, 'g': 70})
```

## API Reference

### Constructor

```python
FlexDict(*args, **kwargs)
```

Creates a new FlexDict instance. Accepts the same arguments as the built-in `dict` constructor.

### Instance Methods

#### `to_dict()`

Converts the FlexDict to a regular dictionary recursively.

```python
regular_dict = fd.to_dict()
```

#### `update(*args, **kwargs)`

Updates the FlexDict with key-value pairs, converting nested dicts to FlexDict objects.

```python
fd.update(other_dict)
fd.update(key1=value1, key2=value2)
```

### Special Behavior

#### Protected Attributes

FlexDict protects dictionary methods and private attributes from being overwritten:

```python
fd = FlexDict()

# These will raise AttributeError
try:
    fd.keys = "something"  # AttributeError
except AttributeError:
    print("Cannot overwrite dict methods")

try:
    fd._private = "value"  # AttributeError
except AttributeError:
    print("Cannot set private attributes")
```

#### Deletion

You can delete attributes using `del`:

```python
fd = FlexDict(name="Alice", age=30)
del fd.name

# After deletion, accessing the key auto-creates a new FlexDict
new_fd = fd.name
print(type(new_fd))  # <class 'flexlib.flexdict.FlexDict'>
print(len(new_fd))   # 0
```

## Examples

### Configuration Management

```python
from flexlib import FlexDict

# Loading configuration
config = FlexDict()
config.database.host = "localhost"
config.database.port = 5432
config.database.name = "myapp"
config.database.credentials.username = "admin"
config.database.credentials.password = "secret"

config.logging.level = "INFO"
config.logging.handlers.file.enabled = True
config.logging.handlers.file.path = "/var/log/app.log"

# Easy access
print(f"Connecting to {config.database.host}:{config.database.port}")
if config.logging.handlers.file.enabled:
    print(f"Logging to {config.logging.handlers.file.path}")
```

### API Response Processing

```python
from flexlib import FlexDict
import json

# Simulated API response
api_response = """
{
    "user": {
        "id": 123,
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "profile": {
            "bio": "Software Engineer",
            "location": "San Francisco",
            "social": {
                "twitter": "@alice",
                "linkedin": "alice-johnson"
            }
        }
    },
    "metadata": {
        "timestamp": "2023-12-01T10:00:00Z",
        "version": "1.0"
    }
}
"""

# Parse and convert to FlexDict
data = FlexDict(json.loads(api_response))

# Easy access to nested data
print(f"User: {data.user.name}")
print(f"Email: {data.user.email}")
print(f"Twitter: {data.user.profile.social.twitter}")
print(f"Location: {data.user.profile.location}")

# Convert back for JSON serialization
response_dict = data.to_dict()
json_output = json.dumps(response_dict, indent=2)
```

### Dynamic Object Creation

```python
from flexlib import FlexDict

def create_user_profile(name, **kwargs):
    """Create a user profile with flexible attributes."""
    profile = FlexDict()
    profile.personal.name = name
    
    # Add any additional attributes dynamically
    for key, value in kwargs.items():
        # Support nested keys using dot notation in string
        if '.' in key:
            keys = key.split('.')
            current = profile
            for k in keys[:-1]:
                if k not in current:
                    setattr(current, k, FlexDict())
                current = getattr(current, k)
            setattr(current, keys[-1], value)
        else:
            setattr(profile, key, value)
    
    return profile

# Usage
user = create_user_profile(
    "John Doe",
    age=30,
    email="john@example.com"
)

print(user.personal.name)  # John Doe
print(user.age)           # 30
print(user.email)         # john@example.com
```

### Settings and Preferences

```python
from flexlib import FlexDict

class AppSettings:
    def __init__(self):
        self.settings = FlexDict()
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default settings."""
        self.settings.ui.theme = "light"
        self.settings.ui.language = "en"
        self.settings.ui.font_size = 12
        
        self.settings.network.timeout = 30
        self.settings.network.retry_attempts = 3
        
        self.settings.features.auto_save = True
        self.settings.features.notifications = True
    
    def update_setting(self, path, value):
        """Update a setting using dot notation path."""
        keys = path.split('.')
        current = self.settings
        for key in keys[:-1]:
            if not hasattr(current, key):
                setattr(current, key, FlexDict())
            current = getattr(current, key)
        setattr(current, keys[-1], value)
    
    def get_setting(self, path, default=None):
        """Get a setting using dot notation path."""
        try:
            keys = path.split('.')
            current = self.settings
            for key in keys:
                current = getattr(current, key)
            return current
        except AttributeError:
            return default

# Usage
app = AppSettings()
print(app.get_setting('ui.theme'))  # light

app.update_setting('ui.theme', 'dark')
app.update_setting('advanced.debug.enabled', True)

print(app.get_setting('ui.theme'))            # dark
print(app.get_setting('advanced.debug.enabled'))  # True
```

## Best Practices

### 1. Use FlexDict for Configuration

FlexDict is excellent for configuration management where you need flexible, nested structures:

```python
# Good
config = FlexDict()
config.database.host = "localhost"
config.api.endpoints.users = "/api/v1/users"

# Instead of
config = {
    "database": {
        "host": "localhost"
    },
    "api": {
        "endpoints": {
            "users": "/api/v1/users"
        }
    }
}
```

### 2. Convert to Regular Dict for Serialization

When serializing to JSON or other formats, convert to regular dict:

```python
import json

fd = FlexDict()
fd.user.name = "Alice"
fd.user.age = 30

# Convert before serialization
json_str = json.dumps(fd.to_dict())
```

### 3. Use Type Hints

When using FlexDict in functions, consider type hints:

```python
from typing import Any
from flexlib import FlexDict

def process_config(config: FlexDict) -> None:
    """Process configuration settings."""
    if config.database.enabled:
        connect_to_database(config.database.host)

def create_response(data: dict[str, Any]) -> FlexDict:
    """Create a FlexDict response object."""
    return FlexDict(data)
```

### 4. Defensive Programming

When accessing potentially undefined keys, use defensive patterns:

```python
# Good - using get with default
theme = fd.get('ui', {}).get('theme', 'light')

# Or with FlexDict auto-creation
if hasattr(fd, 'ui') and hasattr(fd.ui, 'theme'):
    theme = fd.ui.theme
else:
    theme = 'light'

# FlexDict auto-creates, but you might want to check
if fd.ui.theme:  # This creates fd.ui if it doesn't exist
    theme = fd.ui.theme
```

### 5. Avoid Conflicts with Dict Methods

Don't use attribute names that conflict with dict methods:

```python
# Avoid these names as attributes
fd = FlexDict()
# fd.keys = []      # Will raise AttributeError
# fd.values = []    # Will raise AttributeError
# fd.items = []     # Will raise AttributeError

# Use descriptive names instead
fd.key_list = []
fd.value_list = []
fd.item_list = []
```

FlexDict provides a powerful and intuitive way to work with nested data structures while maintaining the familiarity and compatibility of Python dictionaries.
