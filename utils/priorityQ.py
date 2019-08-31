"""
A wrapper for heapq to enable arbitrary objects in the data array
See https://stackoverflow.com/a/8875823/750567
"""
import heapq

class PriorityQ(object):
	def __init__(self, key, initial=None):
		"""
		initial: The initial data array

		key: a function to return the key (or the cost) associated with the given item
		"""
		self.key = key
		if initial:
			self._data = [self._createTuple(item) for item in initial]
			heapq.heapify(self._data)
		else:
			self._data = []

	def __repr__(self):
		return 'Q(count = %d)' % len(self._data)

	def _createTuple(self, item):
		"""
		Remarks
		===
		* The first element of the tuple is the cost associated with the item.
		* The second is just a sequence id in order to avoid comparison between items if the keys happen to be equal
		* The third is the item itself
		"""
		return (self.key(item), len(self._data), item)

	def enqueue(self, item):
		heapq.heappush(self._data, self._createTuple(item))

	def dequeue(self):
		# Return the last item of the tuple
		return heapq.heappop(self._data)[-1]

	def isEmpty(self):
		return len(self._data) == 0
