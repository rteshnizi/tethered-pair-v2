# tethered-pair-v2

## Dependencies

1. tkinter
	* On Ubuntu `sudo apt-get install python3-tk`
1. ~~SymPy: `pip install sympy`~~
2. [CGAL python bindings](https://github.com/CGAL/cgal-swig-bindings)
	* Ubuntu:
		* Don't install boost from source. It will mess with the make process somehow.
		* [Installation instructions for Ubuntu](https://github.com/CGAL/cgal-swig-bindings/wiki/Installation)
3. [Shapely](https://github.com/Toblerity/Shapely):
	* On Ubuntu `pip install shapely`

## Recommended Tools

1. `PyLint` for linting
	* on Ubuntu `sudo apt install pylint`
2. `AutoPep8` for formatting
	* on Ubuntu `sudo apt install python-autopep8`

## TODO:

1. ~~Construct a DS to access triangles and edges and pts the way we need them in the alg (Feb 8)~~
2. Test the current impl for a case where the cable won't get more taut (Aug 6)
3. ~~We can now traverse th triangulation, maintain the funnel (Aug 6)~~
4. Change GapDetector to reduced visibility graph calculator (Aug 19)
5. ~~Add a cable entity whose shape is a line (for debugging)~~
6. Add a case with initial cable config not being straight (Sep 3)
