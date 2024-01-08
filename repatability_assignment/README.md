# Setting-up project environment

1. Install Python and its package manager pip

	> On Arch Linux use `pacman -S python python-pip`

2. Download the "right" wheel file from [here](https://github.com/davidebreso/pynusmv/releases/tag/v1.0rc8-2023)

	> We'll call this file `WHEEL.whl`

3. Run `python -m venv ./venv` to create a Python virtual environment inside the project directory

	> In this way you can perform a local installation of `pynusmv`

4. Run  `./venv/bin/pip install WHEEL.whl`

	> If you get some error messages simply choose another wheel file

5. Install *Microsoft Visual Studio Code* and its *Pyhton* extension (**OPTIONAL**)

# Running code

1. Use `./venv/bin/python react_mc.py MODEL.smv`
