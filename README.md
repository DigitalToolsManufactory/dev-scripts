# dev-scripts

## Prerequisites

* `git`
* `python` (`>= 3.9`)

## Getting Started

To get started using `dev-scripts`, follow these instructions:

1. Clone the repository

```commandline
git clone https://github.com/DigitalToolsManufactory/dev-scripts.git
cd dev-scripts
```

2. Setup your [Python `venv`](https://docs.python.org/3/library/venv.html)

```commandline
python -m venv .venv
```

3. Activate the newly created `venv`

<details>
<summary>Windows (Powershell)</summary>

```commandline
./.venv/Scripts/activate.ps1
```

</details>

4. Install the required [pip](https://pip.pypa.io/en/stable/) packages

```commandline
pip install -r requirements.txt
```

5. Run the bootstrap script

```commandline
python bootstrap.py
```