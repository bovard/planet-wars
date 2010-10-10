
import copy
import random
import logging as l
import Logging as L


class ABC:
  def __init__(self, num_planets, max_distance, planet_num_ships, planet_owner_list, growth_rates, distance_matrix, neighbors_matrix):
    if L.INFO: l.info('initializing the beehive!')
    self._bee_max = 20
    self._max_distance = max_distance
    self._num_planets = num_planets
    self._initial_num_ships = planet_num_ships
    self._initial_owners = planet_owner_list
    self._growth_rates = growth_rates
    self._distances = distance_matrix
    self._neighbors = neighbors_matrix
    self._neutral_ids = self._calc_neutral_ID()
    self._bees = []
    if L.INFO: l.info('done initializing')

  def Update(self, planet_num_ships, planet_owner_list):
    if L.INFO: l.info('updating BeeHive')
    self._initial_num_ships = planet_num_ships
    self._initial_owners = planet_owner_list
    self._neutral_ids = self._calc_neutral_ID()
    if L.INFO: l.info('done updating')

  def GetOptimalOrder(self, turns, list_of_possible_solutions=[]):
    if L.DEBUG: l.debug('in GetOptimalOrder')
    self._initialize_bees(list_of_possible_solutions)
    for i in range(turns):
      if L.DEBUG: l.debug('bee turn = '+repr(i))

      #mutate the orders from the last generation and play through each, committed if warrented
      #and get the min
      max = 0
      for bee in self._bees:
        bee.MutateOrder()
        bee.SetNewTurns(self._play_through_order(bee.GetNewOrder()))
        bee.CommitMutation()
        bee_turns = bee.GetTurns()
        if bee_turns > min:
          max = bee_turns

      #create the bee selection list
      bee_selection = []
      for bee in self._bees:
        for i in range(max-bee.GetTurns()+1):
          bee_selection.append(bee)

      #spawn observer bees
      observer_bees = []
      for i in range(self._bee_max):
        to_copy = random.randrage(len(bee_selection))
        bee_selection[to_copy].Select()
        observer_bees.append(copy.deepcopy(bee_selection[to_copy]))

      #remove unselected scout bees
      to_kill = []
      for bee in self._bees:
        if not(bee.GetSelected()):
          to_kill.append(bee)
      for bee in to_kill:
        self._bees.pop(bee)

      #remove unsucessful observer bees
      to_kill = []
      for bee in observer_bees:
        if not(bee.GetCommitted()):
          to_kill.append(bee)
      for bee in to_kill:
        observer_bees.pop(bee)

      #recruit the sucesfull observers as scouts
      self._bees += observer_bees

      #spawn more scouts if necessary
      while len(self._bees)<self._bee_max:
        self._bees.append(Bee(self._neutral_ids))

    #done!
    #find best order
    min = 1000000000000
    min_bee = -1
    for bee in self._bees:
      if bee.GetTurns() < min:
        min = bee.GetTurns()
        min_bee = bee

    return min_bee.GetOrder()




  def _calc_neutral_ID(self):
    neutral_ids = []
    for i in range(self._num_planets):
      if self._initial_owners[i]==0:
        neutral_ids.append(i)





  def _initialize_bees(self, list_of_possible_solutions):
    for list in list_of_possible_solutions:
      self._bees.append(Bee(list, 1))
    while len(self._bees)<self._bee_max:
      self._bees.append(Bee(self._neutral_ids))
    for bee in self._bees:
      bee.SetTurns(self._play_through_order(bee.GetOrder()))


  def _play_through_order(self, order):
    #TODO: implement this
    turn = 0
    num_ships = copy.copy(self._initial_num_ships)
    owners = copy.copy(self._initial_owners)
    for id in order:
      turns += self._take_planet(id, num_ships, owners)
      #do something
      return turn



  def _add_turn(self, num_ships, owners):
    for i in range(len(num_ships)):
      if owners[i]==1:
        num_ships[i] += self._growth_rates[i]


  def _take_planet(self, id, num_ships, owners):
    turns = 0
    done = 0
    while not(done):
      turn += 1
      avaliable = 0
      for i in range(1, min(turns+1, self._max_distance+1)):
        for p_id in self._neighbors[id][i]:
          avaliable += num_ships[p_id]

      if avaliable > num_ships[id]:
        done = 1
        for i in range(1, min(turns+1, self._max_distance+1)):
          for p_id in self._neighbors[id][i]:
            avaliable -= num_ships[p_id]
            if avaliable >= -1:
              num_ships[p_id]=0
            else:
              num_ships[p_id]=-1*(avaliable+1)
              break
      self._add_turn(num_ships, owners)
    return turns


