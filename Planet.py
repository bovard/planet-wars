
import logging
import Logging as L

class Planet:
  def __init__(self, planet_id, owner, num_ships, growth_rate, x, y):
    if L.DEBUG: logging.debug('creating a planet')
    self._connectedness = 0
    self._planet_id = planet_id
    self._owner = []
    self._owner.append(owner)
    self._num_ships = []
    self._num_ships.append(num_ships)
    self._growth_rate = growth_rate
    self._x = x
    self._y = y
    self._allied_arrivals = []
    self._enemy_arrivals = []
    # free troops are those that haven't been used for anything yet
    self._free_troops = []
    # reinforcing troops are committed to respond to an enemy threat
    self._reinforcing_troops=[]
    # forcast troops are committed to respond to long-range enemy threats
    self._forcasting_troops = []
    # defending troops are committed to respond to an actualy enemy attack
    self._defending_troops=[]
    # ally reinforcing troops are troops that are currently committed on allied planets
    # that are committed to come help out your planet
    self._allied_reinforcements = []
    self._attacking_troops = []
    self._nearest_ally = []
    self._nearest_enemy = []
    self._farthest_enemy = []
    self._farthest_ally = []
    self._nearest_ally.append(100000000000)
    self._nearest_enemy.append(100000000000)
    self._farthest_enemy.append(0)
    self._farthest_ally.append(0)

    if L.DEBUG: logging.debug('done')

  def SetConnectedness(self, con):
    self._connectedness = con

  def GetConnectedness(self):
    return self._connectedness


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

  def SetAlliedArrival(self, turn, ships):
    self._allied_arrivals[turn]=ships


  def SimulateAttack(self, turn):
    if L.DEBUG: logging.debug('Simulating an attack on turn'+repr(turn))
    self.PrintSummary()
    for i in range(turn, len(self._owner)):
      self.CalcFreeTroops(i,1)
      self.CalcOwnerAndNumShips(i,1)
    if L.DEBUG: logging.debug('done!')
    self.PrintSummary()

  # this should be called before flights are processed (done)
  def Update(self):
    self._enemy_arrivals = self._enemy_arrivals[1:]
    self._enemy_arrivals.append(0)
    self._allied_arrivals = self._allied_arrivals[1:]
    self._allied_arrivals.append(0)




  # this should be called before every turn starts
  # reinforcing troops are committed to respond to an enemy threat
  # defending troops are committed to respond to an actualy enemy attack
  def ResetReinforcements(self, max):
    self._reinforcing_troops=[]
    self._defending_troops=[]
    self._allied_reinforcements=[]
    self._attacking_troops = []
    self._forcasting_troops = []
    for i in range(max+1):
      self._reinforcing_troops.append(0)
      self._defending_troops.append(0)
      self._allied_reinforcements.append(0)
      self._attacking_troops.append(0)
      self._forcasting_troops.append(0)

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
    if L.DEBUG: logging.debug('in ResetFreeTroops')
    self._free_troops = []
    if self._owner[0] == 1:
      self._free_troops.append(self._num_ships[0])
    elif self._owner[0] == 2:
      self._free_troops.append(-1*self._num_ships[0])
    else:
      self._free_troops.append(0)
    if L.DEBUG: logging.debug('done')


  def AddNearestAlly(self, near):
    self._nearest_ally.append(near)

  def AddNearestEnemy(self, near):
    self._nearest_enemy.append(near)

  def AddFarthestAlly(self, far):
    self._farthest_ally.append(far)

  def AddFarthestEnemy(self, far):
    self._farthest_enemy.append(far)



  # this needs to be called every turn sequentailly to work
  def CalcOwnerAndNumShips(self, turn, update=0):
    levels = [0, self._allied_arrivals[turn]+self._allied_reinforcements[turn], self._enemy_arrivals[turn]]
    levels[self._owner[turn-1]] += self._num_ships[turn-1]
    if not(self._owner[turn-1] == 0):
      levels[self._owner[turn-1]] += self._growth_rate
    if L.DEBUG: logging.debug('levels: '+repr(levels))
    max = -1
    for i in levels:
      if i>max:
        max = i
    if levels.count(max)>1 and max > 0:
      if not(update):
        self._owner.append(self._owner[turn-1])
        self._num_ships.append(0)
      else:
        self._owner[turn]=self._owner[turn-1]
        self._num_ships[turn]=0
    else:
      if not(update):
        self._owner.append(levels.index(max))
      else:
        self._owner[turn]=levels.index(max)
      levels[levels.index(max)]=0
      max2 = -1
      for i in levels:
        if i>max2:
          max2=i
      if not(update):
        self._num_ships.append(max-max2)
      else:
        self._num_ships[turn]= max-max2

  # this needs to be called every turn sequentially to work, call at the begginning of the turn
  def CalcFreeTroops(self, turn, update=0):
    if L.DEBUG: logging.debug('in CalcFreeTroops')
    self.PrintSummary()
    levels = [0, self._allied_arrivals[turn], self._enemy_arrivals[turn]]
    if self._owner[turn-1] != 0:
      levels[self._owner[turn-1]] += self._growth_rate
    else:
      levels[0]=self._num_ships[turn-1]
    if L.DEBUG: logging.debug('levels in CalcFreeTroops '+repr(levels))
    max1 = max(levels)
    winner = levels.index(max1)
    if levels.count(max1)>1 and max1 > 0:
      if not(update):
        self._free_troops.append(0)
      else:
        self._free_troops[turn]=0
    else:
      levels[levels.index(max1)]=0
      max2 = -1
      for i in levels:
        if i>max2:
          max2=i
      if winner==1:
        if not(update):
          self._free_troops.append(max1-max2)
        else:
          self._free_troops[turn]=max1-max2
      elif winner==2:
        if not(update):
          self._free_troops.append(max2-max1)
        else:
          self._free_troops[turn]=max2-max1
      else:
        if not(update):
          self._free_troops.append(0)
        else:
          self._free_troops[turn]=0
    if L.DEBUG: logging.debug('leaving, free troops: ' + repr(self._free_troops))


  def GetFreeTroops(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetFreeTroops ' + repr(self._free_troops)+ ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._free_troops[start_turn]
    else:
      return sum(self._free_troops[start_turn:end_turn+1])

  def GetDefendingTroops(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetDefendingTroops ' + repr(self._defending_troops)+ ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._defending_troops[start_turn]
    else:
      return sum(self._defending_troops[start_turn:end_turn+1])

  def GetReinforcingTroops(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetReinforcingTroops ' + repr(self._reinforcing_troops) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._reinforcing_troops[start_turn]
    else:
      return sum(self._reinforcing_troops[start_turn:end_turn+1])

  def GetForcastingTroops(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetForcastingTroops ' + repr(self._forcasting_troops) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._forcasting_troops[start_turn]
    else:
      return sum(self._forcasting_troops[start_turn:end_turn+1])

  def GetAlliedReinforcements(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetAlliedReinforcements ' + repr(self._allied_reinforcements) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._allied_reinforcements[start_turn]
    else:
      return sum(self._allied_reinforcements[start_turn:end_turn+1])

  def GetAttackingTroops(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetAttackingTroops ' + repr(self._allied_reinforcements) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._attacking_troops[start_turn]
    else:
      return sum(self._attacking_troops[start_turn:end_turn+1])

  def GetAllTroops(self, start_turn=0, end_turn=-1):
    if L.DEBUG: logging.debug('in GetAllTroops')
    return self.GetFreeTroops(start_turn, end_turn) + self.GetDefendingTroops(start_turn, end_turn) \
      + self.GetReinforcingTroops(start_turn, end_turn) + self.GetAttackingTroops(start_turn, end_turn) \
      + self.GetForcastingTroops(start_turn, end_turn)


  def SetFreeTroops(self, turn, troops):
    if L.DEBUG: logging.debug('in SetFreeTroops')
    if L.DEBUG: logging.debug(repr(self._free_troops))
    self._free_troops[turn]=troops
    if L.DEBUG: logging.debug(repr(self._free_troops))

  def PlanetID(self):
    return self._planet_id

  def SetOwner(self, new_owner):
    self._owner = []
    self._owner.append(new_owner)

  def GetOwner(self, turn=0):
    return self._owner[turn]

  def GetNumShips(self, turn=0):
    if L.DEBUG: logging.debug('in GetNumShips with turn='+repr(turn))
    return self._num_ships[turn]

  def FreeTroops(self):
    return self._free_troops
  
  def ReinforcingTroops(self):
    return self._reinforcing_troops

  def ForcastingTroops(self):
    return self._forcasting_troops
  
  def DefendingTroops(self):
    return self._defending_troops

  def AttackingTroops(self):
    return self._attacking_troops

  def AlliedReinforcements(self):
    return self._allied_reinforcements

  def SetNumShips(self, new_num_ships):
    if L.DEBUG: logging.debug('in SetNumShips with new_num_ships='+repr(new_num_ships))
    self._num_ships = []
    if L.DEBUG: logging.debug('adding some new ships'+repr(new_num_ships))
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

  def PrintSummary(self, info=0):
    if not(info):
      if L.DEBUG: logging.debug('________________________________________________________________')
      if L.DEBUG: logging.debug('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0])+' and regen '+repr(self._growth_rate))
      if L.DEBUG: logging.debug('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
      if L.DEBUG: logging.debug('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
      if L.DEBUG: logging.debug('Allied Arrivals - '+repr(self._allied_arrivals))
      if L.DEBUG: logging.debug('Enemy Arrivals  - '+repr(self._enemy_arrivals))
      if L.DEBUG: logging.debug('Owner List      - '+repr(self._owner))
      if L.DEBUG: logging.debug('Num Ships List  - '+repr(self._num_ships))
      if L.DEBUG: logging.debug('FreeTroops List - '+repr(self._free_troops))
      if L.DEBUG: logging.debug('Reinforcing List- '+repr(self._reinforcing_troops))
      if L.DEBUG: logging.debug('Forcasing List  - '+repr(self._forcasting_troops))
      if L.DEBUG: logging.debug('Defending List  - '+repr(self._defending_troops))
      if L.DEBUG: logging.debug('Attacking List  - '+repr(self._attacking_troops))
      if L.DEBUG: logging.debug('Allied Reinforce- '+repr(self._allied_reinforcements))
      if L.DEBUG: logging.debug('________________________________________________________________')
      return 0
    else:
      if L.INFO: logging.info('________________________________________________________________')
      if L.INFO: logging.info('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0]))
      if L.INFO: logging.info('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
      if L.INFO: logging.info('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
      if L.INFO: logging.info('Allied Arrivals - '+repr(self._allied_arrivals))
      if L.INFO: logging.info('Enemy Arrivals  - '+repr(self._enemy_arrivals))
      if L.INFO: logging.info('Owner List      - '+repr(self._owner))
      if L.INFO: logging.info('FreeTroops List - '+repr(self._free_troops))
      if L.INFO: logging.info('Reinforcing List- '+repr(self._reinforcing_troops))
      if L.INFO: logging.info('Forcasing List  - '+repr(self._forcasting_troops))
      if L.INFO: logging.info('Defending List  - '+repr(self._defending_troops))
      if L.INFO: logging.info('Attacking List  - '+repr(self._attacking_troops))
      if L.INFO: logging.info('Allied Reinforce- '+repr(self._allied_reinforcements))
      if L.INFO: logging.info('________________________________________________________________')
      return 0