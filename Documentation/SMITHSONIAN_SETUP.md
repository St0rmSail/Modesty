# Smithsonian Access Setup

**Scope:** Build 0.12.0 credential setup and recovery

This step stores the Smithsonian Open Access API key securely and makes one harmless authenticated validation request. It does not open the Grand Library, execute a research loan, retrieve expedition material, or write anything to the Bookshelf.

## Safety boundary

- Never paste the API key into Modesty's chat panel, a Codex task, a configuration file, or a command argument.
- The setup prompt hides keyboard input.
- Windows DPAPI encrypts the key for the currently signed-in Windows user.
- The encrypted blob is stored at `Data/Secrets/smithsonian_api_key.dpapi`; the entire directory is excluded from Git.
- The key is sent only to `https://api.si.edu` as required by the official API.
- Validation calls only the Open Access `stats` endpoint and saves none of its response content.
- The audit records the provider, endpoint, outcome, and an HTTP status on rejection. It never records the key, request URL, or response body.

## Live test

After pulling the Step Two commit into `E:\Modesty`, open PowerShell there and run:

```powershell
.\.venv\Scripts\python.exe -m Runtime.Library.smithsonian store
```

Paste or type the API key at the hidden prompt and press Enter. Nothing will appear while it is entered. Then confirm that an encrypted credential exists without displaying it:

```powershell
.\.venv\Scripts\python.exe -m Runtime.Library.smithsonian status
```

Make the one allowed validation request:

```powershell
.\.venv\Scripts\python.exe -m Runtime.Library.smithsonian validate
```

Success must read:

```text
Smithsonian authentication validated. No expedition material was retrieved or filed.
```

Do not repeat the request unnecessarily. This validation and the first bounded expedition have been demonstrated. The accepted expedition retrieved the Smithsonian Open Access record for ENIAC Accumulator #2; use this procedure again only after credential removal, loss, or migration to a rebuilt Windows installation.

To revoke Modesty's local copy later:

```powershell
.\.venv\Scripts\python.exe -m Runtime.Library.smithsonian remove
```
