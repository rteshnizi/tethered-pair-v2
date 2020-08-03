import datetime
import logging
import os
import sys

class Logger(object):
	_privateLogger = None
	logFileName = ""
	def __init__(self):
		if not Logger._privateLogger:
			Logger.logFileName = "%s.log" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
			Logger.logFileName = os.path.join(os.path.dirname(__file__), "..", "logs", Logger.logFileName)
			Logger.logFileName = os.path.abspath(Logger.logFileName)
			# set up logging to file - see previous section for more details
			logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename=Logger.logFileName, filemode="a")
			# define a Handler which writes INFO messages or higher to the sys.stderr
			console = logging.StreamHandler()
			console.setLevel(logging.DEBUG)
			# set a format which is simpler for console use
			formatter = logging.Formatter('%(message)s')
			# tell the handler to use this format
			console.setFormatter(formatter)
			# add the handler to the root logger
			Logger._privateLogger = logging.getLogger()
			Logger._privateLogger.addHandler(console)

	def log(self, msg, level=logging.DEBUG):
		if level == logging.DEBUG:
			self._privateLogger.debug(msg)
		elif level == logging.INFO:
			self._privateLogger.info(msg)
		elif level == logging.WARNING:
			self._privateLogger.warning(msg)
		elif level == logging.ERROR:
			self._privateLogger.error(msg)
		elif level == logging.FATAL:
			self._privateLogger.fatal(msg)
		else:
			self._privateLogger.debug(msg)
