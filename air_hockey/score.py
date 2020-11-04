import numpy as np


class Score(object):

    def __init__(self, dim):
        self._score = {'top': 0, 'bottom': 0}
        self.dim = dim

    def get_top(self):
        return self._score['top']

    def get_bottom(self):
        return self._score['bottom']

    def add_bottom(self):
        self._score["bottom"] += 1

    def add_top(self):
        self._score["top"] += 1


    def update(self, puck):
        x, y = puck.position

        scored = None
        score_flag = 0
        
        if y < self.dim.top_goal:
            #self._score['bottom'] += 1
            scored = 'bottom'
            score_flag = 1
        elif y > self.dim.bottom_goal:
            #self._score['top'] += 1
            scored = 'top'
            score_flag = -1
        if not (self.dim.rink_left < x < self.dim.rink_right):
            scored = 'out_of_bounds'

        return scored, score_flag

    def __repr__(self):
        return str(self._score)

    def reset(self):
        self._score['top']    = 0
        self._score['bottom'] = 0