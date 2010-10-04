import logging

class Planet:
  def __init__(self, planet_id, owner, num_ships, growth_rate, x, y):
    logging.debug('creating a planet')
    self._planet_id = planet_id
    self._owner = []
    self._owner.append(owner)
    self._num_ships = []
    self._num_ships.append(num_ships)
    self._growth_rate = growth_rate
    self._x = x
    self._y = y
    self._neighbors = {}
    self._allied_arrivals = []
    self._enemy_arrivals = []
    # free troops are those that haven't been used for anything yet
    self._free_troops = []
    # reinforcing troops are committed to respond to an enemy threat
    self._reinforcing_troops=[]
    # defending troops are committed to respond to an actualy enemy attack
    self._defending_troops=[]
    # ally reinforcing troops are troops that are currently committed on allied planets
    # that are committed to come help out your planet
    self._allied_reinforcements = []
    self._nearest_ally = []
    self._nearest_enemy = []
    self._farthest_enemy = []
    self._farthest_ally = []
    self._nearest_ally.append(100000000000)
    self._nearest_enemy.append(100000000000)
    self._farthest_enemy.append(0)
    self._farthest_ally.append(0)
    self._launch_queue = -1
    logging.debug('done')




  def SetLaunchQueue(self, launch_queue):
    self._launch_queue = launch_queue

  # needs to be called once at the beginning of the game (done)

  def InitArrivals(self, max):
    for i in range(max+1):
      self._allied_arrivals.append(0)
      self._enemy_arrivals.append(0)

  def AddEnemyArrival(self, turn, ships):
    self._enemy_arrivals[turn] += ships

  def AddAlliedArrival(self, turn, ships):
    self._allied_arrivals[turn] += ships

  def GetEnemyArrival(self, turn):
    return self._enemy_arrivals[turn]

  def GetAlliedArrival(self, turn):
    return self._allied_arrivals[turn]

  # this should be called before flights are processed (done)
  def Update(self):
    self._enemy_arrivals = self._enemy_arrivals[1:]
    self._enemy_arrivals.append(0)
    self._allied_arrivals = self._allied_arrivals[1:]
    self._allied_arrivals.append(0)


  def IsOutsideAlliedCloud(self, max):
    logging.debug('in IsOnTheFront')
    is_outside = 1
    for i in range(0, self._nearest_enemy[0]):
      for p in self._neighbors[i]:
        if p.NearestEnemy()<self._nearest_enemy[0]:
          is_outside = 0

    return is_outside



  # this should be called before every turn starts
  # reinforcing troops are committed to respond to an enemy threat
  # defending troops are committed to respond to an actualy enemy attack
  def ResetReinforcements(self, max):
    self._reinforcing_troops=[]
    self._defending_troops=[]
    self._allied_reinforcements=[]
    for i in range(max+1):
      self._reinforcing_troops.append(0)
      self._defending_troops.append(0)
      self._allied_reinforcements.append(0)

  def ResetNeighbors(self):
    self._nearest_ally = []
    self._nearest_enemy = []
    self._farthest_enemy = []
    self._farthest_ally = []

  def NearestAlly(self, turn=0):
    return self._nearest_ally[turn]

  def NearestEnemy(self, turn=0):
    return self._nearest_enemy[turn]

  def FarthestEnemy(self, turn=0):
    return self._farthest_enemy[turn]

  def FarthestAlly(self, turn=0):
    return self._farthest_ally[turn]

  # this should be called after troop levels are set (even when creating a planet!)(done)
  def ResetFreeTroops(self):
    logging.debug('in ResetFreeTroops')
    self._free_troops = []
    if self._owner[0] == 1:
      self._free_troops.append(self._num_ships[0])
    elif self._owner[0] == 2:
      self._free_troops.append(-1*self._num_ships[0])
    else:
      self._free_troops.append(0)
    logging.debug('done')

  #called after CalCOwnerAndNumShips
  def CalcNeighbors(self, turn, max):
    logging.debug('Enterning CalcNeighbors')
    near_enemy =999999999999
    near_ally =99999999999
    far_enemy =0
    far_ally =0
    for i in range(1,max+1):
      for p in self._neighbors[i]:
        if p.GetOwner(turn)==2:
          if i < near_enemy: near_enemy=i
          if i > far_enemy: far_enemy=i
        elif p.GetOwner(turn)==1:
          if i < near_ally: near_ally=i
          if i > far_ally: far_ally=i
    self._nearest_ally.append(near_ally)
    self._nearest_enemy.append(near_enemy)
    self._farthest_ally.append(far_ally)
    self._farthest_enemy.append(far_enemy)
    logging.debug('done')


  # this needs to be called every turn sequentailly to work
  def CalcOwnerAndNumShips(self, turn):
    logging.debug('in CalcOwnerAndNumShips')
    levels = [0, self._allied_arrivals[turn]+self._reinforcing_troops[turn], self._enemy_arrivals[turn]]
    levels[self._owner[turn-1]] += self._num_ships[turn-1]
    if not(self._owner[turn-1] == 0):
      levels[self._owner[turn-1]] += self._growth_rate
    logging.debug('levels: '+repr(levels))
    max = -1
    logging.debug('finding max')
    for i in levels:
      if i>max:
        max = i
    if levels.count(max)>1 and max > 0:
      logging.debug('there is a tie')
      self._owner.append(self._owner[turn-1])
      self._num_ships.append(0)
    else:
      self._owner.append(levels.index(max))
      levels[levels.index(max)]=0
      max2 = -1
      for i in levels:
        if i>max2:
          max2=i
      self._num_ships.append(max-max2)


  # this needs to be called every turn sequentially to work, call at the begginning of the turn
  def CalcFreeTroops(self, turn):
    logging.debug('in CalcFreeTroops')
    levels = [0, self._allied_arrivals[turn], self._enemy_arrivals[turn]]
    if not(self._owner[turn-1] == 0):
      levels[self._owner[turn-1]] += self._growth_rate
    else:
      levels[0]=self._num_ships[turn-1]
    max = -1
    for i in levels:
      if i>max:
        max = i
    winner = levels.index(max)
    if levels.count(max)>1 and max > 0:
       self._free_troops.append(0)
       logging.debug('calced 0 free troops (tie)')
    else:
      levels[levels.index(max)]=0
      max2 = -1
      for i in levels:
        if i>max2:
          max2=i
      if winner==1:
        self._free_troops.append(max-max2)
        logging.debug('calced + free troops')
      elif winner==2:
        self._free_troops.append(max2-max)
        logging.debug('calced - free troops')
      else:
        self._free_troops.append(0)
        logging.debug('calced 0 free troops (neutral)')
    logging.debug('leaving, free troops: ' + repr(self._free_troops))


  def GetFreeTroops(self, start_turn=0, end_turn=-1):
    logging.debug('in GetFreeTroops ' + repr(self._free_troops)+ ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._free_troops[start_turn]
    else:
      logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._free_troops[start_turn:end_turn+1])

  def GetDefendingTroops(self, start_turn=0, end_turn=-1):
    logging.debug('in GetDefendingTroops ' + repr(self._defending_troops)+ ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._defending_troops[start_turn]
    else:
      logging.debug('returning a range of defending troops troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._defending_troops[start_turn:end_turn+1])

  def GetReinforcingTroops(self, start_turn=0, end_turn=-1):
    logging.debug('in GetReinforcingTroops ' + repr(self._reinforcing_troops) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._reinforcing_troops[start_turn]
    else:
      logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._reinforcing_troops[start_turn:end_turn+1])


  def GetAlliedReinforcements(self, start_turn=0, end_turn=-1):
    logging.debug('in GetAlliedReinforcements ' + repr(self._allied_reinforcements) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._allied_reinforcements[start_turn]
    else:
      logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._allied_reinforcements[start_turn:end_turn+1])

  def GetAllTroops(self, start_turn=0, end_turn=-1):
    logging.debug('in GetAllTroops')
    return self.GetFreeTroops(start_turn, end_turn) + self.GetDefendingTroops(start_turn, end_turn) \
    + self.GetReinforcingTroops(start_turn, end_turn) + self.GetAlliedReinforcements(start_turn, end_turn)





  #called once at the beggining of the game (done)
  def CreateNeighbor(self, max):
    for i in range(1,max+1):
      self._neighbors[i]=[]

  def AddNeighbor(self, distance, p):
    self._neighbors[distance].append(p)

  def GetNeighbors(self, distance):
    return self._neighbors[distance]

  def PlanetID(self):
    return self._planet_id

  def SetOwner(self, new_owner):
    self._owner = []
    self._owner.append(new_owner)

  def GetOwner(self, turn=0):
    return self._owner[turn]

  def GetNumShips(self, turn=0):
    logging.debug('in GetNumShips with turn='+repr(turn))
    return self._num_ships[turn]

  def FreeTroops(self):
    return self._free_troops
  
  def ReinforcingTroops(self):
    return self._reinforcing_troops
  
  def DefendingTroops(self):
    return self._defending_troops

  def SetNumShips(self, new_num_ships):
    logging.debug('in SetNumShips with new_num_ships='+repr(new_num_ships))
    self._num_ships = []
    logging.debug('adding some new ships'+repr(new_num_ships))
    self._num_ships.append(new_num_ships)

  def GrowthRate(self):
    return self._growth_rate

  def X(self):
    return self._x

  def Y(self):
    return self._y

  def AddShips(self, amount):
    self._num_ships += amount

  def RemoveShips(self, amount):
    self._num_ships -= amount

