#######################################
#        Windows environment          #
#######################################

## Create a virtual environment and install dependencies
win-install:
	python -m venv .wvenv
	.\.wvenv\Scripts\python.exe -m pip install --upgrade pip
	.\.wvenv\Scripts\python.exe -m pip install -r .\requirements.txt
	"$(get-location)" > .\.wvenv\Lib\site-packages\obugs.pth

## Run the development files
win-run:
	.\.wvenv\Scripts\python.exe .\main.py

## Remove development environment
win-clean:
	rm -r .\.wvenv\

# Generate database migrations
win-gen-migrations:
	.\.wvenv\Scripts\alembic.exe revision --autogenerate

#######################################
#          Unix environment           #
#######################################

## Create a virtual environment and install dependencies
unix-install:
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip
	.venv/bin/pip3 install -r requirements.txt
	$(foreach dir, $(wildcard .venv/lib/*), echo $(shell pwd) > $(dir)/site-packages/obugs.pth &&) echo

## Run the development files
unix-run:
	.venv/bin/python3 ./main.py

## Remove development environment
unix-clean:
	rm -rf .venv
