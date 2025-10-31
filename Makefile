# To install make on Windows: choco install make

SCRIPT := main
EXE := main.exe
PYTHON := python
PIP := $(PYTHON) -m pip
PYINSTALLER_OPTS := --onefile --noconsole
REQS := requirements.txt

# Force Windows CMD shell
SHELL := cmd.exe

.PHONY: run build clean install

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQS)

run: install
	$(PYTHON) $(SCRIPT).py

build: install
	@echo Building executable...
	pyinstaller $(PYINSTALLER_OPTS) $(SCRIPT).py
	@echo Moving executable to parent directory...
	if exist dist\$(EXE) (move /Y dist\$(EXE) .)
	@echo Cleaning up build artifacts...
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist $(SCRIPT).spec del /f /q $(SCRIPT).spec
	@echo Executable ready: $(EXE)

clean:
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist __pycache__ rmdir /s /q __pycache__
	if exist $(SCRIPT).spec del /f /q $(SCRIPT).spec
