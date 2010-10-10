import random
import Logging as L
import logging as l
import copy

class Bee:
  def __init__(self, order, random=0):
    if L.DEBUG: l.debug('creating Bee')
    if (random):
      self._order = copy.copy(order)
    else:
      self._order = self.GenerateRandomOrder(order)
    self._turns = -1
    self._new_turns = self._turns
    self._new_order = self._order
    self._committed = 0
    self._selected = 0
    if L.DEBUG: l.debug('done')

  def Select(self):
    self._selected += 1

  def GetSelected(self):
    return self._selected

  def GetCommitted(self):
    return self._committed

  def GetOrder(self):
    return self._order

  def GetTurns(self):
    return self._turns

  def SetTurns(self, turns):
    self._turns=turns

  def SetNewTurns(self, new_turns):
    self._new_turns=new_turns

  def MutateOrder(self):
    self._committed = 0
    self._new_order = self.GenerateMutation(self._order)

  def CommitMutation(self):
    if self._new_turns < self._turns:
      self._oder = self._new_order
      self._turns = self._new_turns
      self._committed = 1

  @staticmethod
  def GenerateRandomOrder(planet_ids):
    to_choose = copy.copy(planet_ids)
    for i in range(len(to_choose),0, -1):
      to_choose.append(to_choose.pop(random.randrange(0,i)))
    return order

  @staticmethod
  def GenerateMutation(order):
    to_return = copy.copy(order)
    pos1 = random.rangerange(0, len(to_return))
    pos2 = random.rangerange(0, len(to_return))
    temp = to_return[pos1]
    to_return[pos1]=to_return[pos2]
    to_return[pos2]=temp
    return to_return