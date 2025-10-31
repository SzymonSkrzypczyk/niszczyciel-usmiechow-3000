# To install make on Windows: choco install make

SCRIPT := main
EXE := main.exe
PYTHON := python
PYINSTALLER_OPTS := --onefile --noconsole
REQS := requirements.txt
VENV := .venv

.PHONY: run build clean install

define run_in_venv
	@echo Removing existing temporary virtual environment (if any)...
	if exist $(VENV) rmdir /s /q $(VENV)
	@echo Creating temporary virtual environment...
	$(PYTHON) -m venv $(VENV)
	@echo Installing dependencies...
	$(VENV)\Scripts\python.exe -m pip install --upgrade pip
	$(VENV)\Scripts\python.exe -m pip install -r $(REQS)
	@echo Running: $(1)
	$(1)
	@echo Removing temporary virtual environment...
	if exist $(VENV) rmdir /s /q $(VENV)
endef

install:
	@echo Installing dependencies in temporary venv...
	$(call run_in_venv,$(VENV)\Scripts\python.exe -c "print('Dependencies installed successfully.')")

run:
	$(call run_in_venv,$(VENV)\Scripts\python.exe $(SCRIPT).py)

build:
	$(call run_in_venv,$(VENV)\Scripts\python.exe -m PyInstaller $(PYINSTALLER_OPTS) $(SCRIPT).py)
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
	if exist main.exe del /f /q main.exe
	if exist .venv rmdir /s /q .venv
