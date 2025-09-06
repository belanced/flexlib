"""
FlexDict - A flexible dictionary implementation with dot notation access.

This module provides the FlexDict class which enhances Python's built-in dict
with user-friendly features similar to addict or easydict libraries.
"""

from typing import Any, Dict, Iterator, Union


class FlexDict(dict):
    """
    A flexible dictionary that supports dot notation access and automatic creation
    of nested FlexDict objects.
    
    FlexDict inherits from dict, so it can be used as a drop-in replacement for
    regular Python dictionaries while providing additional convenience features.
    
    Examples:
        >>> fd = FlexDict()
        >>> fd.name = "John Doe"
        >>> fd.age = 40
        >>> fd.abilities.english = "strong"
        >>> print(fd.name)  # "John Doe"
        >>> print(fd["age"])  # 40
        >>> print(fd.abilities.english)  # "strong"
        
        >>> fd2 = FlexDict(name="Jane", age=30)
        >>> fd3 = FlexDict({"city": "New York", "country": "USA"})
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize a FlexDict object.
        
        Args:
            *args: Positional arguments passed to dict constructor
            **kwargs: Keyword arguments for initial key-value pairs
            
        Examples:
            >>> FlexDict()  # Empty FlexDict
            >>> FlexDict({"key": "value"})  # From existing dict
            >>> FlexDict(name="John", age=40)  # From keyword arguments
        """
        # Call parent dict constructor
        super().__init__(*args, **kwargs)
        
        # Convert any nested dictionaries to FlexDict objects
        for key, value in self.items():
            if isinstance(value, dict) and not isinstance(value, FlexDict):
                self[key] = FlexDict(value)

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute using dot notation.
        
        Args:
            name: The attribute name to retrieve
            
        Returns:
            The value associated with the key, or a new FlexDict if key doesn't exist
            
        Raises:
            AttributeError: If the name conflicts with private attributes
        """
        # Prevent access to private attributes
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        # Allow access to dict methods normally
        if hasattr(dict, name):
            return getattr(dict, name).__get__(self, type(self))
        
        try:
            return self[name]
        except KeyError:
            # Create a new FlexDict for missing keys (like addict behavior)
            self[name] = FlexDict()
            return self[name]

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set an attribute using dot notation.
        
        Args:
            name: The attribute name to set
            value: The value to set
            
        Raises:
            AttributeError: If trying to set dict methods or private attributes
        """
        # Prevent setting dict methods or private attributes
        if name.startswith('_') or hasattr(dict, name):
            raise AttributeError(f"'{type(self).__name__}' object attribute '{name}' is read-only")
        else:
            # Convert dict values to FlexDict
            if isinstance(value, dict) and not isinstance(value, FlexDict):
                value = FlexDict(value)
            self[name] = value

    def __delattr__(self, name: str) -> None:
        """
        Delete an attribute using dot notation.
        
        Args:
            name: The attribute name to delete
            
        Raises:
            AttributeError: If the attribute doesn't exist or is a dict method
        """
        if name.startswith('_') or hasattr(dict, name):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set an item in the dictionary, converting dict values to FlexDict.
        
        Args:
            key: The key to set
            value: The value to set
        """
        # Convert nested dictionaries to FlexDict objects
        if isinstance(value, dict) and not isinstance(value, FlexDict):
            value = FlexDict(value)
        super().__setitem__(key, value)

    def __deepcopy__(self, memo: Dict[int, Any]) -> 'FlexDict':
        """
        Support for copy.deepcopy().
        
        Args:
            memo: Memoization dictionary for deepcopy
            
        Returns:
            A deep copy of this FlexDict
        """
        import copy
        return FlexDict({key: copy.deepcopy(value, memo) for key, value in self.items()})

    def __repr__(self) -> str:
        """
        Return a string representation of the FlexDict.
        
        Returns:
            A string representation showing it's a FlexDict
        """
        if not self:
            return "FlexDict()"
        
        items = [f"{repr(k)}: {repr(v)}" for k, v in self.items()]
        return f"FlexDict({{{', '.join(items)}}})"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert FlexDict to a regular dictionary recursively.
        
        Returns:
            A regular dictionary with all nested FlexDicts converted to dicts
        """
        result = {}
        for key, value in self.items():
            if isinstance(value, FlexDict):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def update(self, *args, **kwargs) -> None:
        """
        Update the FlexDict with key-value pairs, converting dicts to FlexDicts.
        
        Args:
            *args: Positional arguments (dict-like objects or iterables of pairs)
            **kwargs: Keyword arguments for additional key-value pairs
        """
        # Handle positional arguments
        if args:
            other = args[0]
            if hasattr(other, "items"):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        
        # Handle keyword arguments
        for key, value in kwargs.items():
            self[key] = value