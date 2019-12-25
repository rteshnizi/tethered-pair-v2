# tethered-pair-v2

Work in progress.

## Running the GUI

* Without VS Code: `python main.py`
* With VS Code: `Run GUI` task

## Running Unit Tests

* Without VS Code: `python test.py`
* With VS Code: `Run Tests` task

## Dependencies

1. tkinter
	* On Ubuntu `sudo apt-get install python3-tk`
2. ~~SymPy: `pip install sympy`~~ (replaced by CGAL)
3. [CGAL python bindings](https://github.com/CGAL/cgal-swig-bindings)
	* Ubuntu:
		* Don't install boost from source. It will mess with the make process somehow.
		* [Installation instructions for Ubuntu](https://github.com/CGAL/cgal-swig-bindings/wiki/Installation)
4. [GEOS](https://trac.osgeo.org/geos/)
	* Windows
		* Use [OSGeo4W](https://trac.osgeo.org/osgeo4w/wiki/WikiStart#QuickStartforOSGeo4WUsers)
		* Add `C:\OSGeo4W64\bin` to Windows path
	* Ubuntu: I don't remember needing to do this
5. [Shapely](https://github.com/Toblerity/Shapely):
	* On Ubuntu `pip install shapely`
6. [termcolor](https://pypi.org/project/termcolor/):
	* For unit test print statements
	* `pip install termcolor`

## Recommended Tools

1. VS Code
	* This whole project was developed in VS Code so it's setup to work with it.

## TODO:

1. ~~Construct a DS to access triangles and edges and pts the way we need them in the alg (Feb 8, 2019)~~
2. Test the current impl for a case where the cable won't get more taut (Aug 6, 2019)
3. ~~We can now traverse th triangulation, maintain the funnel (Aug 6, 2019)~~
4. Change GapDetector to reduced visibility graph calculator (Aug 19, 2019)
5. ~~Add a cable entity whose shape is a line (for debugging)~~
6. ~~Add a case with initial cable config not being straight (Sep 3, 2019)~~
7. ~~Crashes on Windows (Dec 22, 2019)~~
