__author__ = 'raoulfriedrich'

class Node(object):
    #neighbours =
    weight = 0
    importance = 0

    title = ""

    def __init__(self, weight, importance, title):
        self.weight = weight
        self.importance = importance
        self.title = title