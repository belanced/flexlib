from __future__ import annotations

import io
import os
import stat as _stat
import glob as _glob
import pwd as _pwd
import grp as _grp
import fnmatch as _fnmatch
from urllib.parse import quote as _urlquote
from typing import Iterator, List, Optional, Union


_StrOrPath = Union[str, os.PathLike]


class FlexPath(str):
    """A POSIX-compatible pathlib-like path that subclasses ``str``.

    Supports Linux, macOS, and other UNIX-like systems.

    - Immutable: operations return new ``FlexPath`` instances.
    - Standalone: implemented using only the Python standard library (no pathlib).
    - POSIX semantics only; Windows is intentionally unsupported.
    """

    # --- construction -----------------------------------------------------
    def __new__(cls, path: _StrOrPath = "") -> "FlexPath":
        """Construct from a string or ``os.PathLike`` (UNIX semantics).

        Automatically normalizes the path (removes './' segments, collapses
        redundant separators) using ``os.path.normpath``. This does not resolve
        symlinks. The empty string is preserved as-is.
        """
        s = os.fspath(path)
        norm = "" if s == "" else os.path.normpath(s)
        return str.__new__(cls, norm)

    def __repr__(self) -> str:
        """Return a debug-friendly representation."""
        return f"FlexPath({super().__repr__()})"

    def __fspath__(self) -> str:
        """Return the filesystem representation (PEP 519)."""
        return str(self)

    # --- helpers ----------------------------------------------------------
    def _is_abs(self) -> bool:
        return str(self).startswith("/")

    def _split_parts(self) -> tuple[str, ...]:
        """Split into parts similar to PurePosixPath.parts."""
        s = str(self)
        if s == "":
            return tuple()
        if s == "/":
            return ("/",)
        comps = [c for c in s.split("/") if c != ""]
        if s.startswith("/"):
            return ("/",) + tuple(comps)
        return tuple(comps)

    def _last_component(self) -> str:
        s = str(self)
        if s == "/":
            return "/"
        s = s.rstrip("/")
        if s == "":
            return ""
        idx = s.rfind("/")
        return s[idx + 1 :] if idx >= 0 else s

    def _wrap(self, value: _StrOrPath) -> "FlexPath":
        """Internal: wrap a string/PathLike as FlexPath."""
        return FlexPath(value)

    # --- representation ---------------------------------------------------
    @property
    def parts(self) -> tuple[str, ...]:
        """Tuple of path components (root included when present)."""
        return self._split_parts()

    @property
    def anchor(self) -> str:
        """The concatenation of the drive and root (on POSIX just ``/`` or ``""``)."""
        return "/" if self._is_abs() else ""

    @property
    def root(self) -> str:
        """The root component (``/`` on absolute POSIX paths, else ``""``)."""
        return "/" if self._is_abs() else ""

    @property
    def drive(self) -> str:
        """Drive component (always ``""`` on POSIX)."""
        return ""

    @property
    def name(self) -> str:
        """Final path component (file or directory name)."""
        return self._last_component()

    @property
    def suffix(self) -> str:
        """Final component's file extension, including the leading dot."""
        n = self.name
        if not n or n == "/":
            return ""
        i = n.rfind(".")
        if i <= 0:
            return ""
        return n[i:]

    @property
    def suffixes(self) -> List[str]:
        """List of file extensions for the final component (e.g. [".tar", ".gz"])."""
        n = self.name
        if not n or n.startswith(".") and n.count(".") == 1:
            return []
        parts = n.split(".")
        if len(parts) <= 1:
            return []
        return ["." + p for p in parts[1:]]

    @property
    def stem(self) -> str:
        """Final component without its last suffix."""
        n = self.name
        if not n or n == "/":
            return n
        i = n.rfind(".")
        if i <= 0:
            return n
        return n[:i]

    @property
    def parent(self) -> "FlexPath":
        """The logical parent directory (pure operation)."""
        s = str(self)
        if s == "/":
            return self
        s = s.rstrip("/")
        if s == "":
            return self._wrap(".")
        d = os.path.dirname(s)
        return self._wrap(d if d != "" else ".")

    @property
    def parents(self) -> tuple["FlexPath", ...]:
        """Tuple of ancestors, nearest first. Differs from pathlib's view type."""
        res: list[FlexPath] = []
        p: FlexPath = self
        while True:
            par = p.parent
            if str(par) == str(p):  # reached root '/'
                break
            if str(par) == ".":
                break
            res.append(par)
            p = par
        return tuple(res)

    def with_name(self, name: str) -> "FlexPath":
        """Return a new path with the final component replaced by ``name``."""
        if "/" in name or name == "":
            raise ValueError("Invalid name")
        if str(self) in ("", "/"):
            raise ValueError("Cannot replace the name of root or empty path")
        p = self.parent
        if str(p) == ".":
            return self._wrap(name)
        return self._wrap(str(p) + "/" + name)

    def with_suffix(self, suffix: str) -> "FlexPath":
        """Return a new path with the file suffix changed to ``suffix``."""
        if suffix and not suffix.startswith("."):
            raise ValueError("Invalid suffix: must start with '.' or be empty")
        n = self.name
        if n in ("", "/"):
            raise ValueError("Path has no name")
        base = str(self)[: -len(n)] if len(n) != len(str(self)) else ""
        i = n.rfind(".")
        if i <= 0:
            new_name = n + suffix
        else:
            new_name = n[:i] + suffix
        return self._wrap(base + new_name)

    def with_stem(self, stem: str) -> "FlexPath":
        """Return a new path with the final component's stem replaced by ``stem``."""
        if "/" in stem or stem == "":
            raise ValueError("Invalid stem")
        n = self.name
        if n in ("", "/"):
            raise ValueError("Path has no name")
        base = str(self)[: -len(n)] if len(n) != len(str(self)) else ""
        suf = self.suffix
        return self._wrap(base + stem + suf)

    # --- joining / combining ---------------------------------------------
    def joinpath(self, *others: _StrOrPath) -> "FlexPath":
        """Join one or more paths to this path using POSIX semantics."""
        if not others:
            return self
        joined = os.path.join(str(self), *(os.fspath(o) for o in others))
        return self._wrap(joined)

    def __truediv__(self, other: _StrOrPath) -> "FlexPath":  # self / other
        """Implement ``/`` operator for joining with another path fragment."""
        return self.joinpath(other)

    def __rtruediv__(self, other: _StrOrPath) -> "FlexPath":  # other / self
        """Allow joining when ``other`` is left operand (e.g., ``"/tmp" / p``)."""
        return self._wrap(os.path.join(os.fspath(other), str(self)))

    # --- conversions ------------------------------------------------------
    def as_posix(self) -> str:
        """Return the POSIX string representation (slashes).

        As this is a POSIX-only class, simply normalize any backslashes to
        forward slashes and return the string.
        """
        s = str(self)
        return s.replace("\\", "/")

    def as_uri(self) -> str:
        """Return a file URI for this absolute POSIX path.

        Raises ValueError if the path is not absolute.
        """
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        # Percent-encode characters as per RFC 8089
        return "file://" + _urlquote(self.as_posix(), safe="/:")

    @classmethod
    def cwd(cls) -> "FlexPath":
        """Return the current working directory as ``FlexPath``."""
        return cls(os.getcwd())

    @classmethod
    def home(cls) -> "FlexPath":
        """Return the user's home directory as ``FlexPath`` (POSIX)."""
        return cls(os.path.expanduser("~"))

    # --- normalization ----------------------------------------------------
    def expanduser(self) -> "FlexPath":
        """Expand a leading ``~`` or ``~user`` to the user's home directory."""
        return self._wrap(os.path.expanduser(str(self)))

    def resolve(self, strict: bool = False) -> "FlexPath":
        """Resolve symlinks and ``..``/``.`` elements. If ``strict`` and target
        doesn't exist, raise ``FileNotFoundError``.
        """
        s = str(self)
        if strict and not os.path.exists(s):
            raise FileNotFoundError(s)
        return self._wrap(os.path.realpath(s))

    def absolute(self) -> "FlexPath":
        """Return an absolute path without resolving symlinks."""
        return self._wrap(os.path.abspath(str(self)))

    def is_absolute(self) -> bool:
        """Whether the path is absolute (starts with ``/`` on POSIX)."""
        return os.path.isabs(str(self))

    def relative_to(self, *other: _StrOrPath) -> "FlexPath":
        """Return the relative path to ``other`` (raises ``ValueError`` if not
        a subpath). Accepts one or more path segments like pathlib.
        """
        base = os.path.join(*(os.fspath(o) for o in other)) if other else ""
        sp = os.path.normpath(str(self))
        bp = os.path.normpath(base)
        # Both must be absolute or both relative for pathlib-like semantics
        if os.path.isabs(sp) != os.path.isabs(bp):
            raise ValueError(f"{self!s} and {bp!s} are on different anchors")
        try:
            common = os.path.commonpath([sp, bp])
        except ValueError:
            # Different drives (not possible on POSIX) or invalid
            raise ValueError(f"{self!s} is not in the subpath of {bp!s}")
        if common != bp:
            raise ValueError(f"{self!s} is not in the subpath of {bp!s}")
        rel = os.path.relpath(sp, bp)
        return self._wrap("." if rel == "." else rel)

    def is_relative_to(self, *other: _StrOrPath) -> bool:
        """Return True if this path is relative to ``other`` (Python 3.9+ like)."""
        try:
            self.relative_to(*other)
            return True
        except Exception:
            return False

    # --- filesystem checks ------------------------------------------------
    def exists(self) -> bool:
        """True if the path points to an existing filesystem entry."""
        return os.path.exists(str(self))

    def is_file(self) -> bool:
        """True if the path points to a regular file."""
        return os.path.isfile(str(self))

    def is_dir(self) -> bool:
        """True if the path points to a directory."""
        return os.path.isdir(str(self))

    def is_symlink(self) -> bool:
        """True if the path is a symbolic link."""
        return os.path.islink(str(self))

    def is_mount(self) -> bool:
        """True if the path is a mount point (POSIX heuristic via ``os.path.ismount``)."""
        return os.path.ismount(str(self))

    def is_block_device(self) -> bool:
        """True if the path is a block device (POSIX; requires existence)."""
        try:
            mode = os.lstat(str(self)).st_mode
        except FileNotFoundError:
            return False
        return _stat.S_ISBLK(mode)

    def is_char_device(self) -> bool:
        """True if the path is a character device (POSIX; requires existence)."""
        try:
            mode = os.lstat(str(self)).st_mode
        except FileNotFoundError:
            return False
        return _stat.S_ISCHR(mode)

    def is_fifo(self) -> bool:
        """True if the path is a FIFO (named pipe)."""
        try:
            mode = os.lstat(str(self)).st_mode
        except FileNotFoundError:
            return False
        return _stat.S_ISFIFO(mode)

    def is_socket(self) -> bool:
        """True if the path is a UNIX domain socket."""
        try:
            mode = os.lstat(str(self)).st_mode
        except FileNotFoundError:
            return False
        return _stat.S_ISSOCK(mode)

    # --- filesystem ops ---------------------------------------------------
    def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        """Create a directory.

        - ``mode``: permission bits (umask applies)
        - ``parents``: create missing parents
        - ``exist_ok``: ignore error if the directory already exists
        """
        if parents:
            os.makedirs(str(self), mode=mode, exist_ok=exist_ok)
        else:
            try:
                os.mkdir(str(self), mode=mode)
            except FileExistsError:
                if not exist_ok:
                    raise

    def rmdir(self) -> None:
        """Remove an empty directory."""
        os.rmdir(str(self))

    def unlink(self, missing_ok: bool = False) -> None:
        """Remove the file or symbolic link. If ``missing_ok`` is True, ignore
        missing path errors.
        """
        try:
            os.remove(str(self))
        except FileNotFoundError:
            if not missing_ok:
                raise

    def rename(self, target: _StrOrPath) -> "FlexPath":
        """Rename this path to ``target``. Returns the new path."""
        os.rename(str(self), os.fspath(target))
        return self._wrap(os.fspath(target))

    def replace(self, target: _StrOrPath) -> "FlexPath":
        """Rename, overwriting ``target`` if it exists. Returns the new path."""
        os.replace(str(self), os.fspath(target))
        return self._wrap(os.fspath(target))

    def samefile(self, other: _StrOrPath) -> bool:
        """Return True if this path and ``other`` refer to the same file."""
        return os.path.samefile(str(self), os.fspath(other))

    def readlink(self) -> "FlexPath":
        """Return the path to which the symbolic link points (not resolved)."""
        return self._wrap(os.readlink(str(self)))

    def symlink_to(self, target: _StrOrPath, target_is_directory: bool = False) -> None:
        """Create a symbolic link pointing to ``target`` named at this path.

        ``target_is_directory`` is ignored on POSIX (optional for API parity).
        """
        os.symlink(os.fspath(target), str(self))

    def link_to(self, target: _StrOrPath) -> None:
        """Create a hard link pointing to ``target`` named at this path."""
        os.link(os.fspath(target), str(self))

    def chmod(self, mode: int, *, follow_symlinks: bool = True) -> None:
        """Change permissions to ``mode``. On POSIX, ``follow_symlinks`` is honored."""
        os.chmod(str(self), mode, follow_symlinks=follow_symlinks)

    def lchmod(self, mode: int) -> None:
        """Change permissions of a symlink itself (do not follow)."""
        os.chmod(str(self), mode, follow_symlinks=False)

    def touch(self, mode: int = 0o666, exist_ok: bool = True) -> None:
        """Create the file if it doesn't exist.

        If it exists and ``exist_ok`` is False, raise ``FileExistsError``;
        otherwise update its modification time.
        """
        if self.exists():
            if not exist_ok:
                raise FileExistsError(str(self))
            os.utime(str(self), None)
            return
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        fd = os.open(str(self), flags, mode)
        os.close(fd)

    def iterdir(self) -> Iterator["FlexPath"]:
        """Iterate over directory entries (names are not sorted)."""
        if not self.is_dir():
            raise NotADirectoryError(f"Not a directory: {self}")
        for name in os.listdir(str(self)):
            yield self._wrap(os.path.join(str(self), name))

    def glob(self, pattern: str) -> Iterator["FlexPath"]:
        """Yield paths matching a glob pattern relative to this directory."""
        base = str(self)
        recursive = "**" in pattern
        paths = sorted(_glob.iglob(os.path.join(base, pattern), recursive=recursive))
        for p in paths:
            yield self._wrap(p)

    def rglob(self, pattern: str) -> Iterator["FlexPath"]:
        """Recursive glob (``**`` is implied)."""
        base = str(self)
        pat = pattern if pattern.startswith("**/") else f"**/{pattern}"
        paths = sorted(_glob.iglob(os.path.join(base, pat), recursive=True))
        for p in paths:
            yield self._wrap(p)

    def match(self, pattern: str) -> bool:
        """Match this path against a glob-style pattern (pure operation)."""
        return _fnmatch.fnmatchcase(self.as_posix(), pattern)

    # --- IO ---------------------------------------------------------------
    def open(self, mode: str = "r", buffering: int = -1, encoding: Optional[str] = None,
             errors: Optional[str] = None, newline: Optional[str] = None) -> io.TextIOBase:
        """Open the file and return a file object (like ``open()``)."""
        return open(str(self), mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    def read_text(self, encoding: str = "utf-8", errors: str = "strict") -> str:
        """Read the file as text and return its content as ``str``."""
        with open(str(self), "r", encoding=encoding, errors=errors) as f:
            return f.read()

    def write_text(self, data: str, encoding: str = "utf-8", errors: str = "strict") -> int:
        """Write ``data`` to the file as text and return the number of bytes written."""
        with open(str(self), "w", encoding=encoding, errors=errors) as f:
            return f.write(data)

    def read_bytes(self) -> bytes:
        """Read the file as bytes and return its content as ``bytes``."""
        with open(str(self), "rb") as f:
            return f.read()

    def write_bytes(self, data: bytes) -> int:
        """Write bytes to the file and return the number of bytes written."""
        with open(str(self), "wb") as f:
            return f.write(data)

    # --- metadata ---------------------------------------------------------
    def stat(self) -> os.stat_result:
        """Perform a ``stat()`` system call on this path, following symlinks."""
        return os.stat(str(self))

    def lstat(self) -> os.stat_result:
        """Like ``stat()`` but do not follow symlinks."""
        return os.lstat(str(self))

    def owner(self) -> str:
        """Return the login name of the file owner (POSIX only)."""
        return _pwd.getpwuid(self.stat().st_uid).pw_name

    def group(self) -> str:
        """Return the group name of the file owner (POSIX only)."""
        return _grp.getgrgid(self.stat().st_gid).gr_name
