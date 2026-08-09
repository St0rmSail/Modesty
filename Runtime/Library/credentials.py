"""Current-user encrypted storage for Grand Library credentials on Windows."""

import base64
import ctypes
from ctypes import wintypes
from pathlib import Path
import sys


class CredentialError(RuntimeError):
    """A credential could not be stored or recovered safely."""


class _DataBlob(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_byte))]


def _blob(value: bytes) -> tuple[_DataBlob, object]:
    buffer = ctypes.create_string_buffer(value)
    return _DataBlob(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))), buffer


def _windows_dpapi():
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = (
        ctypes.POINTER(_DataBlob),
        wintypes.LPCWSTR,
        ctypes.POINTER(_DataBlob),
        wintypes.LPVOID,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(_DataBlob),
    )
    crypt32.CryptProtectData.restype = wintypes.BOOL
    crypt32.CryptUnprotectData.argtypes = (
        ctypes.POINTER(_DataBlob),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(_DataBlob),
        wintypes.LPVOID,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(_DataBlob),
    )
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = (wintypes.HLOCAL,)
    kernel32.LocalFree.restype = wintypes.HLOCAL
    return crypt32, kernel32


def protect_for_current_user(value: bytes) -> bytes:
    """Encrypt bytes with Windows DPAPI, bound to the signed-in user account."""
    if sys.platform != "win32":
        raise CredentialError("Secure credential storage is available only on Windows.")
    source, source_buffer = _blob(value)
    entropy, entropy_buffer = _blob(b"Modesty Grand Library credential v1")
    protected = _DataBlob()
    crypt32, kernel32 = _windows_dpapi()
    if not crypt32.CryptProtectData(
        ctypes.byref(source),
        "Modesty Grand Library",
        ctypes.byref(entropy),
        None,
        None,
        0x1,
        ctypes.byref(protected),
    ):
        raise CredentialError("Windows could not encrypt the credential.")
    try:
        return ctypes.string_at(protected.data, protected.size)
    finally:
        kernel32.LocalFree(protected.data)
        del source_buffer, entropy_buffer


def unprotect_for_current_user(value: bytes) -> bytes:
    """Decrypt bytes previously protected for the current Windows user."""
    if sys.platform != "win32":
        raise CredentialError("Secure credential storage is available only on Windows.")
    source, source_buffer = _blob(value)
    entropy, entropy_buffer = _blob(b"Modesty Grand Library credential v1")
    clear = _DataBlob()
    crypt32, kernel32 = _windows_dpapi()
    if not crypt32.CryptUnprotectData(
        ctypes.byref(source),
        None,
        ctypes.byref(entropy),
        None,
        None,
        0x1,
        ctypes.byref(clear),
    ):
        raise CredentialError(
            "Windows could not decrypt the credential for this user account."
        )
    try:
        return ctypes.string_at(clear.data, clear.size)
    finally:
        kernel32.LocalFree(clear.data)
        del source_buffer, entropy_buffer


class CredentialStore:
    """Persist a single DPAPI-protected secret without exposing its clear text."""

    HEADER = b"MODESTY-DPAPI-1\n"

    def __init__(
        self,
        path: Path,
        protect=protect_for_current_user,
        unprotect=unprotect_for_current_user,
    ):
        self.path = Path(path)
        self._protect = protect
        self._unprotect = unprotect

    @property
    def exists(self) -> bool:
        return self.path.is_file()

    def store(self, secret: str):
        value = secret.strip()
        if not value or "\n" in value or "\r" in value:
            raise CredentialError("The API key must be one non-empty line.")
        if len(value) > 1024:
            raise CredentialError("The API key is unexpectedly large and was not stored.")
        protected = self._protect(value.encode("utf-8"))
        document = self.HEADER + base64.b64encode(protected) + b"\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_bytes(document)
        temporary.replace(self.path)

    def load(self) -> str:
        try:
            document = self.path.read_bytes()
        except FileNotFoundError as error:
            raise CredentialError("No Smithsonian API key is stored.") from error
        if not document.startswith(self.HEADER):
            raise CredentialError("The stored credential has an unknown format.")
        try:
            protected = base64.b64decode(
                document[len(self.HEADER):].strip(), validate=True
            )
            return self._unprotect(protected).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise CredentialError("The stored credential is damaged.") from error

    def remove(self) -> bool:
        try:
            self.path.unlink()
        except FileNotFoundError:
            return False
        return True
