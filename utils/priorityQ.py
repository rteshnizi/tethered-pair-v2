"""
A wrapper for heapq to enable arbitrary objects in the data array
See https://stackoverflow.com/a/8875823/750567
"""
import heapq

class PriorityQ(object):
	def __init__(self, initial=None, key=lambda x:x):
		"""
		initial: The initial data array

		key: a function to return the key (or the cost) associated with the given item
		"""
		self.key = key
		if initial:
			self._data = [(key(item), item) for item in initial]
			heapq.heapify(self._data)
		else:
			self._data = []

	def enqueue(self, item):
		heapq.heappush(self._data, (self.key(item), item))

	def dequeue(self):
		return heapq.heappop(self._data)[1]

	def isEmpty(self):
		return len(self._data) == 0
