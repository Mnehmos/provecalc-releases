# ProveCalc Releases

Download the latest ProveCalc desktop app from the
[Releases](https://github.com/Mnehmos/provecalc-releases/releases/latest) page.
Purchase a license at [provecalc.com](https://provecalc.com).

## Which file do I need?

| Platform | Download |
|----------|----------|
| Windows 10/11 (64-bit) | `ProveCalc_<version>_x64-setup.exe` (recommended) or `ProveCalc_<version>_x64_en-US.msi` |
| macOS, Apple Silicon (M1 and later) | `ProveCalc_<version>_aarch64.dmg` |
| macOS, Intel | `ProveCalc_<version>_x64.dmg` |
| Linux | `ProveCalc_<version>_amd64.AppImage`, `.deb` (Debian/Ubuntu), or `.rpm` (Fedora/RHEL) |

Files named `ProveCalc_<platform>...`, `.sig`, and `latest.json` are used by
the in-app updater; you do not need to download them.

## First launch

Installers are not yet signed with a publisher certificate, so the
operating system asks for confirmation the first time:

- **Windows:** if SmartScreen shows "Windows protected your PC", choose
  **More info** → **Run anyway**.
- **macOS:** if the app "cannot be opened", open **System Settings** →
  **Privacy & Security** and choose **Open Anyway** for ProveCalc.
- **Linux (AppImage):** mark the file as executable
  (`chmod +x ProveCalc_*.AppImage`) before running it.

Newer releases also publish `ProveCalc_<version>_SHA256SUMS.txt`, an SPDX
SBOM, and build provenance so downloads can be verified.

## Activating

Enter the license key from your purchase email in **Settings** → **License**.
The key is also available at [provecalc.com/success](https://provecalc.com/success)
while signed in.
