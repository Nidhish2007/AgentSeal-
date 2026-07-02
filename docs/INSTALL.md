# Installation

## Fast Install

```powershell
python -m pip install --force-reinstall "https://github.com/Nidhish2007/AgentSeal-Benchmark-Forensics/releases/download/v5.0.0-beta.2/agentseal-5.0.0-1beta2fix4-py3-none-any.whl"
agentseal
```

If `agentseal` is not found:

```powershell
python -m agentseal
```

Wheel SHA256:

```text
c9ff9d6ecf99bb18fd4a16725e08f70962ad00bf9f7a2154bda686ed648fbf79
```

## Reproduce the Public Example

Inside the terminal UI:

```text
/pro 10     Quick SWE-bench Pro sample
/pro        Bundled SWE-bench Pro public audit
/open       Open the latest report
```

GitHub/HuggingFace tokens are optional. Local CodeSeal/Bloom checks can run without tokens when benchmark rows are already local. Tokens improve public evidence search and gated dataset loading.

## Local Wheel File

If you downloaded the wheel manually:

```powershell
cd "$env:USERPROFILE\Downloads"
python -m pip install --upgrade pip
python -m pip install --force-reinstall ".\agentseal-5.0.0-1beta2fix4-py3-none-any.whl"
python -m agentseal
```

## From source

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e .[dev]
python scripts/smoke_test.py
```

The source tree does not include large beta artifacts. Install the release wheel for the full offline artifact set.
