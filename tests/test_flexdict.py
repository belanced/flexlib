"""
Comprehensive test cases for FlexDict class.

This module tests all functionality of the FlexDict class including:
- Basic instantiation and usage
- Dot notation access
- Dictionary compatibility
- Nested structure handling
- Edge cases and error conditions
"""

import copy
import pytest
from flexlib.flexdict import FlexDict


class TestFlexDictInstantiation:
    """Test various ways to instantiate FlexDict."""

    def test_empty_instantiation(self):
        """Test creating an empty FlexDict."""
        fd = FlexDict()
        assert len(fd) == 0
        assert isinstance(fd, dict)
        assert isinstance(fd, FlexDict)

    def test_from_dict_instantiation(self):
        """Test creating FlexDict from a regular dictionary."""
        sample_dict = {"varname": 40}
        fd = FlexDict(sample_dict)
        assert fd["varname"] == 40
        assert fd.varname == 40

    def test_from_kwargs_instantiation(self):
        """Test creating FlexDict from keyword arguments."""
        fd = FlexDict(name="John Doe", age=40)
        assert fd.name == "John Doe"
        assert fd.age == 40
        assert fd["name"] == "John Doe"
        assert fd["age"] == 40

    def test_complex_nested_instantiation(self):
        """Test creating FlexDict with nested dictionaries."""
        fd = FlexDict(name="John Doe", age=40, abilities={"english": "strong"})
        assert fd.name == "John Doe"
        assert fd.age == 40
        assert fd.abilities.english == "strong"
        assert isinstance(fd.abilities, FlexDict)


class TestDotNotationAccess:
    """Test dot notation access functionality."""

    def test_dot_notation_assignment(self):
        """Test assigning values using dot notation."""
        fd = FlexDict()
        fd.name = "John Doe"
        fd.age = 40
        fd.abilities.english = "strong"
        
        assert fd.name == "John Doe"
        assert fd.age == 40
        assert fd.abilities.english == "strong"

    def test_dot_notation_retrieval(self):
        """Test retrieving values using dot notation."""
        fd = FlexDict(name="Jane", age=30, city="New York")
        assert fd.name == "Jane"
        assert fd.age == 30
        assert fd.city == "New York"

    def test_auto_creation_of_nested_dicts(self):
        """Test automatic creation of nested FlexDict objects."""
        fd = FlexDict()
        # This should create nested structure automatically
        fd.user.profile.settings.theme = "dark"
        
        assert fd.user.profile.settings.theme == "dark"
        assert isinstance(fd.user, FlexDict)
        assert isinstance(fd.user.profile, FlexDict)
        assert isinstance(fd.user.profile.settings, FlexDict)

    def test_dot_notation_deletion(self):
        """Test deleting attributes using dot notation."""
        fd = FlexDict(name="John", age=40)
        del fd.name
        
        assert "name" not in fd
        assert fd.age == 40
        
        # After deletion, accessing the key should auto-create a new FlexDict (addict behavior)
        new_fd = fd.name
        assert isinstance(new_fd, FlexDict)
        assert len(new_fd) == 0


class TestDictionaryCompatibility:
    """Test that FlexDict works like a regular dictionary."""

    def test_bracket_notation_access(self):
        """Test accessing values using bracket notation."""
        fd = FlexDict(name="John", age=40)
        assert fd["name"] == "John"
        assert fd["age"] == 40

    def test_bracket_notation_assignment(self):
        """Test assigning values using bracket notation."""
        fd = FlexDict()
        fd["name"] = "John"
        fd["age"] = 40
        
        assert fd.name == "John"
        assert fd.age == 40

    def test_mixed_access_patterns(self):
        """Test mixing dot and bracket notation."""
        fd = FlexDict()
        fd.name = "John"
        fd["age"] = 40
        
        assert fd["name"] == "John"
        assert fd.age == 40

    def test_dict_methods(self):
        """Test that dict methods work correctly."""
        fd = FlexDict(a=1, b=2, c=3)
        
        # Test keys, values, items
        assert set(fd.keys()) == {"a", "b", "c"}
        assert set(fd.values()) == {1, 2, 3}
        assert set(fd.items()) == {("a", 1), ("b", 2), ("c", 3)}
        
        # Test get method
        assert fd.get("a") == 1
        assert fd.get("nonexistent", "default") == "default"
        
        # Test pop method
        value = fd.pop("a")
        assert value == 1
        assert "a" not in fd

    def test_len_and_bool(self):
        """Test len() and bool() operations."""
        fd = FlexDict()
        assert len(fd) == 0
        assert not fd
        
        fd.name = "John"
        assert len(fd) == 1
        assert fd

    def test_iteration(self):
        """Test iteration over FlexDict."""
        fd = FlexDict(a=1, b=2, c=3)
        keys = []
        for key in fd:
            keys.append(key)
        assert set(keys) == {"a", "b", "c"}


class TestNestedStructures:
    """Test handling of nested structures."""

    def test_nested_dict_conversion(self):
        """Test automatic conversion of nested dicts to FlexDict."""
        nested_dict = {
            "user": {
                "name": "John",
                "profile": {
                    "age": 30,
                    "city": "New York"
                }
            }
        }
        
        fd = FlexDict(nested_dict)
        assert isinstance(fd.user, FlexDict)
        assert isinstance(fd.user.profile, FlexDict)
        assert fd.user.name == "John"
        assert fd.user.profile.age == 30

    def test_assignment_of_nested_dicts(self):
        """Test assigning nested dictionaries."""
        fd = FlexDict()
        fd.config = {"database": {"host": "localhost", "port": 5432}}
        
        assert isinstance(fd.config, FlexDict)
        assert isinstance(fd.config.database, FlexDict)
        assert fd.config.database.host == "localhost"
        assert fd.config.database.port == 5432

    def test_deep_nesting(self):
        """Test very deep nesting scenarios."""
        fd = FlexDict()
        fd.a.b.c.d.e.f.g = "deep value"
        
        assert fd.a.b.c.d.e.f.g == "deep value"
        assert isinstance(fd.a.b.c.d.e.f, FlexDict)


class TestUpdateMethod:
    """Test the update method functionality."""

    def test_update_with_dict(self):
        """Test updating with a regular dictionary."""
        fd = FlexDict(a=1, b=2)
        fd.update({"b": 20, "c": 30})
        
        assert fd.a == 1
        assert fd.b == 20
        assert fd.c == 30

    def test_update_with_flexdict(self):
        """Test updating with another FlexDict."""
        fd1 = FlexDict(a=1, b=2)
        fd2 = FlexDict(b=20, c=30)
        
        fd1.update(fd2)
        assert fd1.a == 1
        assert fd1.b == 20
        assert fd1.c == 30

    def test_update_with_kwargs(self):
        """Test updating with keyword arguments."""
        fd = FlexDict(a=1)
        fd.update(b=2, c=3)
        
        assert fd.a == 1
        assert fd.b == 2
        assert fd.c == 3


class TestUtilityMethods:
    """Test utility methods."""

    def test_to_dict_conversion(self):
        """Test converting FlexDict back to regular dict."""
        fd = FlexDict()
        fd.user.name = "John"
        fd.user.age = 30
        fd.settings.theme = "dark"
        
        regular_dict = fd.to_dict()
        expected = {
            "user": {"name": "John", "age": 30},
            "settings": {"theme": "dark"}
        }
        
        assert regular_dict == expected
        assert isinstance(regular_dict, dict)
        assert not isinstance(regular_dict, FlexDict)
        assert isinstance(regular_dict["user"], dict)
        assert not isinstance(regular_dict["user"], FlexDict)

    def test_repr_method(self):
        """Test string representation."""
        fd = FlexDict()
        assert repr(fd) == "FlexDict()"
        
        fd.name = "John"
        fd.age = 30
        repr_str = repr(fd)
        assert "FlexDict" in repr_str
        assert "name" in repr_str
        assert "John" in repr_str

    def test_deepcopy(self):
        """Test deep copying functionality."""
        fd = FlexDict()
        fd.user.name = "John"
        fd.user.scores = [90, 85, 88]
        
        fd_copy = copy.deepcopy(fd)
        
        # Modify original
        fd.user.name = "Jane"
        fd.user.scores.append(92)
        
        # Copy should be unchanged
        assert fd_copy.user.name == "John"
        assert fd_copy.user.scores == [90, 85, 88]
        assert isinstance(fd_copy, FlexDict)
        assert isinstance(fd_copy.user, FlexDict)


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_attribute_error_for_dict_methods(self):
        """Test that dict methods can't be accessed via dot notation."""
        fd = FlexDict()
        
        # Accessing dict methods should work normally (not via dot notation for assignment)
        keys_method = fd.keys
        assert callable(keys_method)
        
        # But setting dict method names as attributes should raise error
        with pytest.raises(AttributeError):
            fd.keys = "something"  # Should raise AttributeError

    def test_attribute_error_for_private_attributes(self):
        """Test that private attributes raise AttributeError."""
        fd = FlexDict()
        
        with pytest.raises(AttributeError):
            _ = fd._private
        
        with pytest.raises(AttributeError):
            fd._private = "value"

    def test_deletion_of_nonexistent_attribute(self):
        """Test deleting a nonexistent attribute."""
        fd = FlexDict()
        
        with pytest.raises(AttributeError):
            del fd.nonexistent

    def test_complex_key_types(self):
        """Test handling of complex key types."""
        fd = FlexDict()
        fd[1] = "numeric key"
        fd[(1, 2)] = "tuple key"
        
        assert fd[1] == "numeric key"
        assert fd[(1, 2)] == "tuple key"


class TestWorkflowExamples:
    """Test the specific examples from the workflow."""

    def test_workflow_example_1(self):
        """Test the first workflow example."""
        # var = FlexDict() -> Empty FlexDict
        var = FlexDict()
        assert len(var) == 0
        assert isinstance(var, FlexDict)

    def test_workflow_example_2(self):
        """Test the second workflow example."""
        # sample_dict = { "varname": 40 } -> General dict in python
        # var = FlexDict(sample_dict) -> instantiation of FlexDict from a dict object
        sample_dict = {"varname": 40}
        var = FlexDict(sample_dict)
        assert var.varname == 40
        assert var["varname"] == 40

    def test_workflow_example_3(self):
        """Test the main workflow example."""
        # var = FlexDict("name": "John Doe", "age": 40, "abilities": {"english": "strong" })
        var = FlexDict(name="John Doe", age=40, abilities={"english": "strong"})
        
        # This should be equivalent to:
        var2 = FlexDict()
        var2.name = "John Doe"
        var2.age = 40
        var2.abilities.english = "strong"
        
        # Test equivalence
        assert var.name == var2.name == "John Doe"
        assert var.age == var2.age == 40
        assert var.abilities.english == var2.abilities.english == "strong"
        
        # Test that both have the same structure
        assert var.to_dict() == var2.to_dict()


if __name__ == "__main__":
    pytest.main([__file__])
