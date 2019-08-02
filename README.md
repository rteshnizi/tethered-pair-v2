# tethered-pair-v2

## Dependencies

1. tkinter
	* On Ubuntu `sudo apt-get install python3-tk`
1. ~~SymPy: `pip install sympy`~~
2. [CGAL python bindings](https://github.com/CGAL/cgal-swig-bindings)
	* Ubuntu:
		* Don't install boost from source. It will mess with the make process somehow.
		* [Installation instructions for Ubuntu](https://github.com/CGAL/cgal-swig-bindings/wiki/Installation)

## Recommended Tools

1. `PyLint` for linting
	* on Ubuntu `sudo apt install pylint`
2. `AutoPep8` for formatting\
	* on Ubuntu `sudo apt install python-autopep8`

## TODO:

1. Construct a DS to access triangles and edges and pts the way we need them in the alg (02/08)
2. Add a cable entity whose shape is a line (for debugging)
