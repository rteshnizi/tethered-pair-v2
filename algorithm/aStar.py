from algorithm.node import Node
from model.model_service import Model
from utils.priorityQ import PriorityQ

model = Model()

def aStar():
	q = PriorityQ(key=Node.pQGetCost) # The Priority Queue container
	root = Node(cable=model.cable)
	q.enqueue(root)
	while (not q.isEmpty()):
		n = q.dequeue()
		if (_isAtDestination(n)):
			return # For now terminate at first solution


def _isAtDestination(n):
	return n.cable[0].name == model.robots[0].destination.name and n.cable[-1].name == model.robots[1].destination.name
