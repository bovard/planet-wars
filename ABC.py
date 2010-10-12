from Bee import Bee
import copy
import random
import logging as l
import Logging as L


class ABC:
  def __init__(self, num_planets, max_distance, planet_num_ships, planet_owner_list, growth_rates, distance_matrix, neighbors_matrix):
    if L.INFO: l.info('initializing the beehive!')
    self._bee_max = 200
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
      if L.DEBUG: l.debug('mutating and evaluating')
      max = 0
      for bee in self._bees:
        bee.MutateOrder()
        bee.SetNewTurns(self._play_through_order(bee.GetNewOrder()))
        bee.CommitMutation()
        bee_turns = bee.GetTurns()
        if bee_turns > max:
          max = bee_turns

      if L.DEBUG: l.debug('creating selection list')
      #create the bee selection list
      bee_selection = []
      for bee in self._bees:
        for i in range(max-bee.GetTurns()+1):
          bee_selection.append(bee)

      #spawn observer bees
      if L.DEBUG: l.debug('spawing observer bees')
      observer_bees = []
      for i in range(self._bee_max):
        to_copy = random.randrange(len(bee_selection))
        bee_selection[to_copy].Select()
        observer_bees.append(copy.deepcopy(bee_selection[to_copy]))

      #tell teh observerbees to get out there!
      if L.DEBUG: l.debug('sending out observer bees')
      for bee in observer_bees:
        bee.MutateOrder()
        bee.SetNewTurns(self._play_through_order(bee.GetNewOrder()))
        bee.CommitMutation()


      #remove unselected scout bees
      if L.DEBUG: l.debug('killing bees :(')
      for i in range(len(self._bees)-1, -1, -1):
        if not(self._bees[i].GetSelected()):
          del self._bees[i]


      #remove unsucessful observer bees
      for i in range(len(observer_bees)-1, -1, -1):
        if not(observer_bees[i].GetCommitted()):
          del observer_bees[i]

      if L.DEBUG: l.debug('joining lists')
      #recruit the sucesfull observers as scouts
      self._bees += observer_bees

      if L.DEBUG: l.debug('spawning new bees!')
      #spawn more scouts if necessary
      while len(self._bees)<self._bee_max:
        bee = Bee(self._neutral_ids)
        bee.SetTurns(self._play_through_order(bee.GetNewOrder()))
        self._bees.append(bee)

    #done!
    if L.DEBUG: l.debug('done! finding best order')
    #find best order
    min = 1000000000000
    min_bee = -1
    for bee in self._bees:
      if bee.GetTurns() < min:
        min = bee.GetTurns()
        min_bee = bee

    if L.CRITICAL: l.critical('best order is '+repr(min_bee.GetOrder())+' in '+repr(min)+' turns!')
    return min_bee.GetOrder()




  def _calc_neutral_ID(self):
    neutral_ids = []
    for i in range(self._num_planets):
      if self._initial_owners[i]==0:
        neutral_ids.append(i)
    return neutral_ids





  def _initialize_bees(self, list_of_possible_solutions):
    if L.DEBUG: l.debug(' in _initialize bees')
    if L.DEBUG: l.debug('creating bees from the list')
    for list in list_of_possible_solutions:
      self._bees.append(Bee(list, 1))
    if L.DEBUG: l.debug('creating other bees from '+repr(self._neutral_ids))
    while len(self._bees)<self._bee_max:
      self._bees.append(Bee(self._neutral_ids))
    for bee in self._bees:
      bee.SetTurns(self._play_through_order(bee.GetOrder()))


  def _play_through_order(self, order):
    if L.DEBUG: l.debug('in _play_through_order')
    turns = 0
    num_ships = copy.copy(self._initial_num_ships)
    owners = copy.copy(self._initial_owners)
    for id in order:
      turns += self._take_planet(id, num_ships, owners)
      owners[id]=1
      num_ships[id]=-1*turns*self._growth_rates[id]+1
      #do something
    if L.DEBUG: l.debug('leaving _play_through_order')
    return turns



  def _add_turn(self, num_ships, owners):
    for i in range(len(num_ships)):
      if owners[i]==1:
        num_ships[i] += self._growth_rates[i]


  def _take_planet(self, id, num_ships, owners):
    if L.DEBUG: l.debug('in _take_planet')
    if L.DEBUG: l.debug('with num_ships = '+repr(num_ships))
    turns = 0
    done = 0
    while not(done):
      turns += 1
      avaliable = 0
      for i in range(1, min(turns+1, self._max_distance+1)):
        for p_id in self._neighbors[id][i]:
          if num_ships[p_id]>0:
            avaliable += num_ships[p_id]

      if avaliable > num_ships[id]:
        if L.DEBUG: l.debug('should be able to capture ship this next turn')
        done = 1
        for i in range(1, min(turns+1, self._max_distance+1)):
          for p_id in self._neighbors[id][i]:
            if num_ships[p_id]>0:
              avaliable -= num_ships[p_id]
              if avaliable >= -1:
                num_ships[p_id]=0
              else:
                num_ships[p_id]=-1*(avaliable+1)
                break
      self._add_turn(num_ships, owners)
    if L.DEBUG: l.debug('Num ships changed to '+repr(num_ships))
    if L.DEBUG: l.debug('leaving _take_planet with turns='+repr(turns))
    return turns


