# Candidate Image Security Scan

## Scope and result

- Candidate: `communication-bridge-ai:security-20261101-r4`
- Image ID: `sha256:0b226630db5e840b4b77cf6909aaeb52e433d97d5411f1f41be13d67b1542441`
- Scanner: Trivy 0.76.1
- Image OS: Debian 13.7
- Scan time: 2026-11-01 12:58 UTC
- Trivy vulnerability database updated: 2026-11-01 07:08 UTC
- Findings: 235 OS-package matches (1 critical, 55 high, 76 medium, 99 low, 4 unknown); 0 Python-package findings.

The scanner's package-level matches include duplicates where a CVE affects multiple installed packages. The critical/high findings comprise 18 distinct CVEs and 56 CVE/package pairs. Trivy did not report a fixed version for any critical/high finding. The complete scan output contains the remaining severity levels and all package-level details.

## Critical and high findings

| Severity | Vulnerability | Affected package(s) and installed version(s) | Fixed version |
|---|---|---|---|
| Critical | CVE-2026-6653 (libxml2 use-after-free / denial of service) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2025-69720 (ncurses buffer overflow) | `libncursesw6`, `libtinfo6`, `ncurses-base`, `ncurses-bin` 6.5+20250216-2 | Not listed |
| High | CVE-2026-16742 (systemd-homed local privilege escalation) | `libsystemd0`, `libudev1` 257.13-1~deb13u1 | Not listed |
| High | CVE-2026-54369 (ACL symlink traversal) | `libacl1` 2.3.2-2+b1 | Not listed |
| High | CVE-2026-74860 (libxml2 double-free / use-after-free) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-76642 (util-linux mount-helper issue) | `bsdutils`, `libblkid1`, `liblastlog2-2`, `libmount1`, `libsmartcols1`, `libuuid1`, `mount`, `util-linux` 2.41.5-0+deb13u1; `login` 1:4.16.0-2+really2.41.5-0+deb13u1 | Not listed |
| High | CVE-2026-78408 (util-linux nsenter cgroup authority) | Same util-linux package set and versions as CVE-2026-76642 | Not listed |
| High | CVE-2026-78409 (util-linux mount subdirectory path traversal) | Same util-linux package set and versions as CVE-2026-76642 | Not listed |
| High | CVE-2026-78410 (util-linux restricted bind-mount issue) | Same util-linux package set and versions as CVE-2026-76642 | Not listed |
| High | CVE-2026-86138 (libxml2 heap buffer overflow) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-86139 (libxml2 integer overflow) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-86140 (libxml2 stack buffer overflow) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-86142 (libxml2 XPointer heap buffer overflow) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-86143 (libxml2 write-callback integer overflow) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-86144 (libxml2 parsing flags issue) | `libxml2` 2.12.7+dfsg+really2.9.14-2.1+deb13u3 | Not listed |
| High | CVE-2026-88806 (libX11 heap buffer overflow) | `libx11-6`, `libx11-data`, `libx11-xcb1` 2:1.8.12-1 | Not listed |
| High | CVE-2026-88807 (libXrender heap overflow) | `libxrender1` 1:0.9.12-1 | Not listed |
| High | CVE-2026-9538 (perl-Archive-Tar denial of service) | `perl-base` 5.40.1-6+deb13u1 | Not listed |

## Assessment and remediation

The Python dependency set is pinned in `requirements.lock`; `pip-audit` reports no known Python advisories, and Trivy reports no Python-package findings. The runtime image also removes `pip`, setuptools, and wheel after installation.

The remaining findings are Debian OS-package matches from the pinned Python slim base and runtime libraries. OpenCV/MediaPipe runtime requirements include graphics libraries; other listed packages are part of the Debian base or dependency closure. The findings were not suppressed. The scan lists no fixed versions, and the available Debian package candidates checked during assessment did not provide fixes for the affected installed versions. Arbitrarily removing runtime libraries or changing distributions without a rebuilt and tested candidate would risk breaking real landmark inference.

**Status: unresolved, deployment blocked.** These scanner matches do not by themselves prove that a vulnerable code path is reachable in this application. However, the critical/high OS findings remain installed and must be treated as residual risk. Recheck Debian security updates, rebuild from a patched supported base/package set, rerun Trivy, and rerun candidate tests before reconsidering deployment.

The Python base image is digest-pinned and the model download is SHA-256 verified. Python package versions are locked but not hash-pinned, and Debian packages are installed from live repositories rather than a dated repository snapshot; therefore, the build is not fully reproducible at the artifact level.

## MediaPipe / protobuf compatibility

The prior direct pins were MediaPipe 0.10.21 and protobuf 4.25.9. That MediaPipe release constrained protobuf below version 5, conflicting with the protobuf security fix requiring protobuf 5.29.6 or later. Upgrading MediaPipe also removed the legacy `mp.solutions` API used by the existing implementation.

The candidate uses MediaPipe 0.10.35 with protobuf 5.29.6 and the MediaPipe Tasks Hand Landmarker API. The official model asset is checksum-pinned. The candidate successfully initialized MediaPipe Tasks in Linux and retained the application’s existing heuristic gesture labels; it does not claim validated ASL or SASL translation.

## Validation and deployment status

- Python tests: 62 passed.
- Frontend tests: 34 passed. No `package.json` or frontend production-build script is present.
- Ruff, Python compilation, `pip check`, and `git diff --check`: passed.
- `pip-audit -r requirements.lock`: no known vulnerabilities.
- Candidate image build: passed; image size approximately 311 MB.
- Isolated candidate health, authentication, sessions, text/emoji workflows, protected routes, MediaPipe initialization, invalid-frame handling, and SQLite integrity checks: passed.
- Host webcam: opened and processed 20 frames, but detected no hands or gestures. Actual gesture recognition is therefore unverified.
- Production: unchanged. The existing container remains healthy on its prior image, and its persistent volume was not modified.

No production database backup was made because deployment was not authorized or recommended. The production database schema has not been validated by restoring a fresh production backup into the candidate. A production environment-file compatibility check and that restore test remain required deployment gates.
