#!/usr/bin/env python3
"""Comprehensive test suite for FlexPath class."""

import unittest
import tempfile
import os
import shutil
import stat
import platform
from pathlib import Path
import sys

from flexlib.flexpath import FlexPath


class TestFlexPathPlatform(unittest.TestCase):
    """Test platform-specific behaviors."""

    def test_platform_compatibility(self):
        """Test that FlexPath works on supported platforms."""
        current_platform = platform.system()
        supported_platforms = ["Linux", "Darwin"]  # Darwin is macOS
        
        if current_platform in supported_platforms:
            # Basic functionality should work
            p = FlexPath("/tmp/test")
            self.assertTrue(p.is_absolute())
            self.assertEqual(str(p), "/tmp/test")
        else:
            # Should still work on other POSIX systems
            p = FlexPath("/tmp/test")
            self.assertEqual(str(p), "/tmp/test")

    @unittest.skipUnless(platform.system() == "Darwin", "macOS-specific test")
    def test_macos_paths(self):
        """Test macOS-specific path behaviors."""
        # Test typical macOS paths
        home = FlexPath("~/Library/Preferences")
        expanded = home.expanduser()
        self.assertTrue(str(expanded).endswith("/Library/Preferences"))
        
        # Test Applications folder
        apps = FlexPath("/Applications")
        self.assertEqual(str(apps), "/Applications")
        
        # Test Volumes (mount points on macOS)
        volumes = FlexPath("/Volumes")
        self.assertEqual(str(volumes), "/Volumes")

    @unittest.skipUnless(platform.system() == "Darwin", "macOS-specific test")
    def test_macos_home_directory(self):
        """Test macOS home directory patterns."""
        home = FlexPath.home()
        self.assertTrue(str(home).startswith("/Users/") or str(home).startswith("/var/"))
        
        # Test typical macOS user subdirectories
        desktop = home / "Desktop"
        documents = home / "Documents"
        downloads = home / "Downloads"
        
        self.assertTrue(str(desktop).endswith("/Desktop"))
        self.assertTrue(str(documents).endswith("/Documents"))
        self.assertTrue(str(downloads).endswith("/Downloads"))

    @unittest.skipUnless(platform.system() == "Linux", "Linux-specific test")
    def test_linux_paths(self):
        """Test Linux-specific path behaviors."""
        # Test typical Linux paths
        home = FlexPath.home()
        self.assertTrue(str(home).startswith("/home/") or str(home).startswith("/root"))
        
        # Test proc filesystem
        proc = FlexPath("/proc")
        self.assertEqual(str(proc), "/proc")
        
        # Test sys filesystem
        sys_path = FlexPath("/sys")
        self.assertEqual(str(sys_path), "/sys")

    def test_cross_platform_temp_directory(self):
        """Test temporary directory handling across platforms."""
        # This should work on both Linux and macOS
        temp_dir = FlexPath(tempfile.gettempdir())
        self.assertTrue(temp_dir.exists())
        self.assertTrue(temp_dir.is_dir())
        
        if platform.system() == "Darwin":
            # macOS typically uses /var/folders/... for temp
            self.assertTrue(str(temp_dir).startswith("/var/") or str(temp_dir).startswith("/tmp"))
        elif platform.system() == "Linux":
            # Linux typically uses /tmp
            self.assertTrue(str(temp_dir).startswith("/tmp") or str(temp_dir).startswith("/var/tmp"))


class TestFlexPathConstruction(unittest.TestCase):
    """Test FlexPath construction and basic operations."""

    def test_construction_from_string(self):
        """Test creating FlexPath from string."""
        p = FlexPath("/home/user")
        self.assertEqual(str(p), "/home/user")
        self.assertIsInstance(p, str)
        self.assertIsInstance(p, FlexPath)

    def test_construction_from_pathlike(self):
        """Test creating FlexPath from os.PathLike object."""
        path_obj = Path("/tmp/test")
        p = FlexPath(path_obj)
        self.assertEqual(str(p), "/tmp/test")

    def test_construction_empty(self):
        """Test creating FlexPath with empty string."""
        p = FlexPath("")
        self.assertEqual(str(p), "")

    def test_construction_normalization(self):
        """Test path normalization during construction."""
        p = FlexPath("/home//user/./docs/../files")
        self.assertEqual(str(p), "/home/user/files")

    def test_repr(self):
        """Test string representation."""
        p = FlexPath("/home/user")
        self.assertEqual(repr(p), "FlexPath('/home/user')")

    def test_fspath(self):
        """Test PEP 519 filesystem path representation."""
        p = FlexPath("/home/user")
        self.assertEqual(os.fspath(p), "/home/user")


class TestFlexPathProperties(unittest.TestCase):
    """Test FlexPath properties and path components."""

    def test_parts_absolute(self):
        """Test parts property for absolute paths."""
        p = FlexPath("/home/user/docs")
        self.assertEqual(p.parts, ("/", "home", "user", "docs"))

    def test_parts_relative(self):
        """Test parts property for relative paths."""
        p = FlexPath("user/docs")
        self.assertEqual(p.parts, ("user", "docs"))

    def test_parts_root(self):
        """Test parts property for root path."""
        p = FlexPath("/")
        self.assertEqual(p.parts, ("/",))

    def test_parts_empty(self):
        """Test parts property for empty path."""
        p = FlexPath("")
        self.assertEqual(p.parts, ())

    def test_anchor(self):
        """Test anchor property."""
        abs_path = FlexPath("/home/user")
        rel_path = FlexPath("home/user")
        self.assertEqual(abs_path.anchor, "/")
        self.assertEqual(rel_path.anchor, "")

    def test_root(self):
        """Test root property."""
        abs_path = FlexPath("/home/user")
        rel_path = FlexPath("home/user")
        self.assertEqual(abs_path.root, "/")
        self.assertEqual(rel_path.root, "")

    def test_drive(self):
        """Test drive property (always empty on POSIX)."""
        p = FlexPath("/home/user")
        self.assertEqual(p.drive, "")

    def test_name(self):
        """Test name property."""
        p = FlexPath("/home/user/file.txt")
        self.assertEqual(p.name, "file.txt")
        
        root = FlexPath("/")
        self.assertEqual(root.name, "/")

    def test_suffix(self):
        """Test suffix property."""
        p = FlexPath("/home/user/file.txt")
        self.assertEqual(p.suffix, ".txt")
        
        no_suffix = FlexPath("/home/user/file")
        self.assertEqual(no_suffix.suffix, "")

    def test_suffixes(self):
        """Test suffixes property."""
        p = FlexPath("/home/user/archive.tar.gz")
        self.assertEqual(p.suffixes, [".tar", ".gz"])
        
        single_suffix = FlexPath("/home/user/file.txt")
        self.assertEqual(single_suffix.suffixes, [".txt"])
        
        no_suffix = FlexPath("/home/user/file")
        self.assertEqual(no_suffix.suffixes, [])

    def test_stem(self):
        """Test stem property."""
        p = FlexPath("/home/user/file.txt")
        self.assertEqual(p.stem, "file")
        
        multi_suffix = FlexPath("/home/user/archive.tar.gz")
        self.assertEqual(multi_suffix.stem, "archive.tar")

    def test_parent(self):
        """Test parent property."""
        p = FlexPath("/home/user/file.txt")
        self.assertEqual(str(p.parent), "/home/user")
        
        root = FlexPath("/")
        self.assertEqual(str(root.parent), "/")
        
        rel = FlexPath("user/file.txt")
        self.assertEqual(str(rel.parent), "user")

    def test_parents(self):
        """Test parents property."""
        p = FlexPath("/home/user/docs/file.txt")
        parents = p.parents
        # FlexPath implementation includes the root "/" in parents (matches pathlib behavior)
        expected = [FlexPath("/home/user/docs"), FlexPath("/home/user"), FlexPath("/home"), FlexPath("/")]
        self.assertEqual(list(parents), expected)


class TestFlexPathManipulation(unittest.TestCase):
    """Test path manipulation methods."""

    def test_with_name(self):
        """Test with_name method."""
        p = FlexPath("/home/user/file.txt")
        new_p = p.with_name("newfile.txt")
        self.assertEqual(str(new_p), "/home/user/newfile.txt")

    def test_with_name_invalid(self):
        """Test with_name with invalid inputs."""
        p = FlexPath("/home/user/file.txt")
        with self.assertRaises(ValueError):
            p.with_name("invalid/name")
        with self.assertRaises(ValueError):
            p.with_name("")

    def test_with_suffix(self):
        """Test with_suffix method."""
        p = FlexPath("/home/user/file.txt")
        new_p = p.with_suffix(".py")
        self.assertEqual(str(new_p), "/home/user/file.py")
        
        # Remove suffix
        no_suffix = p.with_suffix("")
        self.assertEqual(str(no_suffix), "/home/user/file")

    def test_with_suffix_invalid(self):
        """Test with_suffix with invalid inputs."""
        p = FlexPath("/home/user/file.txt")
        with self.assertRaises(ValueError):
            p.with_suffix("invalid")

    def test_with_stem(self):
        """Test with_stem method."""
        p = FlexPath("/home/user/file.txt")
        new_p = p.with_stem("newfile")
        self.assertEqual(str(new_p), "/home/user/newfile.txt")

    def test_with_stem_invalid(self):
        """Test with_stem with invalid inputs."""
        p = FlexPath("/home/user/file.txt")
        with self.assertRaises(ValueError):
            p.with_stem("invalid/stem")
        with self.assertRaises(ValueError):
            p.with_stem("")


class TestFlexPathJoining(unittest.TestCase):
    """Test path joining and combining operations."""

    def test_joinpath(self):
        """Test joinpath method."""
        p = FlexPath("/home/user")
        joined = p.joinpath("docs", "file.txt")
        self.assertEqual(str(joined), "/home/user/docs/file.txt")

    def test_truediv_operator(self):
        """Test / operator for path joining."""
        p = FlexPath("/home/user")
        joined = p / "docs" / "file.txt"
        self.assertEqual(str(joined), "/home/user/docs/file.txt")

    def test_rtruediv_operator(self):
        """Test reverse / operator."""
        p = FlexPath("docs/file.txt")
        joined = "/home/user" / p
        self.assertEqual(str(joined), "/home/user/docs/file.txt")


class TestFlexPathConversions(unittest.TestCase):
    """Test path conversion methods."""

    def test_as_posix(self):
        """Test as_posix method."""
        p = FlexPath("/home\\user")  # Backslashes should be converted
        self.assertEqual(p.as_posix(), "/home/user")

    def test_as_uri(self):
        """Test as_uri method."""
        p = FlexPath("/home/user/file with spaces.txt")
        uri = p.as_uri()
        self.assertTrue(uri.startswith("file://"))
        self.assertIn("file%20with%20spaces.txt", uri)

    def test_as_uri_relative_error(self):
        """Test as_uri with relative path raises error."""
        p = FlexPath("relative/path")
        with self.assertRaises(ValueError):
            p.as_uri()

    def test_cwd(self):
        """Test cwd class method."""
        cwd = FlexPath.cwd()
        self.assertTrue(cwd.is_absolute())
        self.assertEqual(str(cwd), os.getcwd())

    def test_home(self):
        """Test home class method."""
        home = FlexPath.home()
        self.assertTrue(home.is_absolute())
        self.assertEqual(str(home), os.path.expanduser("~"))


class TestFlexPathNormalization(unittest.TestCase):
    """Test path normalization methods."""

    def test_expanduser(self):
        """Test expanduser method."""
        p = FlexPath("~/docs")
        expanded = p.expanduser()
        self.assertTrue(str(expanded).startswith("/"))

    def test_absolute(self):
        """Test absolute method."""
        p = FlexPath("relative/path")
        abs_p = p.absolute()
        self.assertTrue(abs_p.is_absolute())

    def test_is_absolute(self):
        """Test is_absolute method."""
        abs_path = FlexPath("/home/user")
        rel_path = FlexPath("home/user")
        self.assertTrue(abs_path.is_absolute())
        self.assertFalse(rel_path.is_absolute())

    def test_relative_to(self):
        """Test relative_to method."""
        p = FlexPath("/home/user/docs/file.txt")
        base = FlexPath("/home/user")
        rel = p.relative_to(base)
        self.assertEqual(str(rel), "docs/file.txt")

    def test_relative_to_error(self):
        """Test relative_to with incompatible paths."""
        p = FlexPath("/home/user/docs")
        base = FlexPath("/other/path")
        with self.assertRaises(ValueError):
            p.relative_to(base)

    def test_is_relative_to(self):
        """Test is_relative_to method."""
        p = FlexPath("/home/user/docs/file.txt")
        base = FlexPath("/home/user")
        other = FlexPath("/other/path")
        self.assertTrue(p.is_relative_to(base))
        self.assertFalse(p.is_relative_to(other))


class TestFlexPathFilesystem(unittest.TestCase):
    """Test filesystem operations with temporary files."""

    def setUp(self):
        """Set up temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = FlexPath(self.temp_dir)
        self.platform = platform.system()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mkdir(self):
        """Test mkdir method."""
        new_dir = self.temp_path / "newdir"
        new_dir.mkdir()
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())

    def test_mkdir_parents(self):
        """Test mkdir with parents=True."""
        nested_dir = self.temp_path / "parent" / "child"
        nested_dir.mkdir(parents=True)
        self.assertTrue(nested_dir.exists())
        self.assertTrue(nested_dir.is_dir())

    def test_touch(self):
        """Test touch method."""
        test_file = self.temp_path / "testfile.txt"
        test_file.touch()
        self.assertTrue(test_file.exists())
        self.assertTrue(test_file.is_file())

    def test_write_read_text(self):
        """Test writing and reading text."""
        test_file = self.temp_path / "testfile.txt"
        content = "Hello, World!"
        test_file.write_text(content)
        read_content = test_file.read_text()
        self.assertEqual(content, read_content)

    def test_write_read_bytes(self):
        """Test writing and reading bytes."""
        test_file = self.temp_path / "testfile.bin"
        content = b"Hello, World!"
        test_file.write_bytes(content)
        read_content = test_file.read_bytes()
        self.assertEqual(content, read_content)

    def test_unlink(self):
        """Test unlink method."""
        test_file = self.temp_path / "testfile.txt"
        test_file.touch()
        self.assertTrue(test_file.exists())
        test_file.unlink()
        self.assertFalse(test_file.exists())

    def test_rmdir(self):
        """Test rmdir method."""
        test_dir = self.temp_path / "testdir"
        test_dir.mkdir()
        self.assertTrue(test_dir.exists())
        test_dir.rmdir()
        self.assertFalse(test_dir.exists())

    def test_rename(self):
        """Test rename method."""
        old_file = self.temp_path / "oldfile.txt"
        new_file = self.temp_path / "newfile.txt"
        old_file.touch()
        
        result = old_file.rename(new_file)
        self.assertFalse(old_file.exists())
        self.assertTrue(new_file.exists())
        self.assertEqual(str(result), str(new_file))

    def test_iterdir(self):
        """Test iterdir method."""
        # Create test files and directories
        (self.temp_path / "file1.txt").touch()
        (self.temp_path / "file2.txt").touch()
        (self.temp_path / "subdir").mkdir()
        
        items = list(self.temp_path.iterdir())
        self.assertEqual(len(items), 3)
        names = [item.name for item in items]
        self.assertIn("file1.txt", names)
        self.assertIn("file2.txt", names)
        self.assertIn("subdir", names)

    def test_glob(self):
        """Test glob method."""
        # Create test files
        (self.temp_path / "file1.txt").touch()
        (self.temp_path / "file2.txt").touch()
        (self.temp_path / "file1.py").touch()
        
        txt_files = list(self.temp_path.glob("*.txt"))
        self.assertEqual(len(txt_files), 2)
        
        all_files = list(self.temp_path.glob("file*"))
        self.assertEqual(len(all_files), 3)

    def test_stat(self):
        """Test stat method."""
        test_file = self.temp_path / "testfile.txt"
        test_file.write_text("test content")
        
        stat_result = test_file.stat()
        self.assertTrue(stat.S_ISREG(stat_result.st_mode))
        self.assertGreater(stat_result.st_size, 0)

    def test_chmod(self):
        """Test chmod method."""
        test_file = self.temp_path / "testfile.txt"
        test_file.touch()
        
        # Change permissions
        test_file.chmod(0o644)
        stat_result = test_file.stat()
        # Check that owner has read/write permissions
        self.assertTrue(stat_result.st_mode & stat.S_IRUSR)
        self.assertTrue(stat_result.st_mode & stat.S_IWUSR)

    @unittest.skipUnless(platform.system() == "Darwin", "macOS-specific test")
    def test_macos_filesystem_operations(self):
        """Test filesystem operations specific to macOS."""
        # Test creating files in macOS-style temp directory
        test_file = self.temp_path / "macos_test.txt"
        test_file.write_text("Hello macOS!")
        content = test_file.read_text()
        self.assertEqual(content, "Hello macOS!")
        
        # Test that temp directory follows macOS patterns
        if self.platform == "Darwin":
            temp_str = str(self.temp_path)
            self.assertTrue(temp_str.startswith("/var/") or temp_str.startswith("/tmp"))

    @unittest.skipUnless(platform.system() == "Darwin", "macOS-specific test")
    def test_macos_symlinks(self):
        """Test symbolic link operations on macOS."""
        source = self.temp_path / "source.txt"
        link = self.temp_path / "link.txt"
        
        source.write_text("symlink test")
        link.symlink_to(source)
        
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.read_text(), "symlink test")
        
        # Test readlink
        target = link.readlink()
        self.assertEqual(str(target), str(source))

    @unittest.skipUnless(platform.system() == "Linux", "Linux-specific test")
    def test_linux_filesystem_operations(self):
        """Test filesystem operations specific to Linux."""
        # Test creating files in Linux-style temp directory
        test_file = self.temp_path / "linux_test.txt"
        test_file.write_text("Hello Linux!")
        content = test_file.read_text()
        self.assertEqual(content, "Hello Linux!")
        
        # Test that temp directory follows Linux patterns
        if self.platform == "Linux":
            temp_str = str(self.temp_path)
            self.assertTrue(temp_str.startswith("/tmp") or temp_str.startswith("/var/tmp"))


class TestFlexPathMatching(unittest.TestCase):
    """Test pattern matching methods."""

    def test_match(self):
        """Test match method."""
        p = FlexPath("/home/user/file.txt")
        self.assertTrue(p.match("*.txt"))
        self.assertTrue(p.match("*/file.txt"))
        self.assertFalse(p.match("*.py"))

    def test_match_case_sensitive(self):
        """Test match is case sensitive."""
        p = FlexPath("/home/user/File.TXT")
        self.assertFalse(p.match("*.txt"))
        self.assertTrue(p.match("*.TXT"))


class TestFlexPathEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_path_operations(self):
        """Test operations on empty paths."""
        p = FlexPath("")
        self.assertEqual(p.parts, ())
        self.assertEqual(p.name, "")
        self.assertEqual(p.suffix, "")
        self.assertEqual(p.stem, "")

    def test_root_path_operations(self):
        """Test operations on root path."""
        p = FlexPath("/")
        self.assertEqual(p.parts, ("/",))
        self.assertEqual(p.name, "/")
        self.assertEqual(p.suffix, "")
        self.assertEqual(p.stem, "/")
        self.assertEqual(str(p.parent), "/")

    def test_path_with_dots(self):
        """Test paths with dot components."""
        p = FlexPath("./dir/../file.txt")
        # Should be normalized during construction
        self.assertEqual(str(p), "file.txt")

    def test_multiple_slashes(self):
        """Test paths with multiple consecutive slashes."""
        p = FlexPath("/home//user///file.txt")
        # Should be normalized during construction
        self.assertEqual(str(p), "/home/user/file.txt")


if __name__ == "__main__":
    unittest.main()
