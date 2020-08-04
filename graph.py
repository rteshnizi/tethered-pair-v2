import os
import sys
import pandas as pd
import plotly.express as px

def main(file):
	df = pd.read_csv(os.path.abspath(file))

	fig = px.line(df, x="CABLE-LENGTH", y=["GENERATED", "EXPANDED"], title="Expanded vs. Generated")
	fig.show()

	# fig = px.line(df, x="CABLE-LENGTH", y="TIME", title="Computation Time")
	# fig.show()

	fig = px.line(df, x="CABLE-LENGTH", y=["PATH-A-L", "PATH-B-L"], title="Active Constraint")
	fig.show()

	fig = px.line(df, x="CABLE-LENGTH", y=["CABLE-LENGTH", "CABLE-L"], title="Active Constraint")
	fig.show()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		raise RuntimeError("Input relative file path.")
	main(sys.argv[1])
