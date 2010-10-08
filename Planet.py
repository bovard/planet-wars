
#import #logging
from copy import deepcopy

class Planet:
  def __init__(self, planet_id, owner, num_ships, growth_rate, x, y):
    #logging.debug('creating a planet')
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

    #logging.debug('done')

#  def Copy(self):
#    #logging.debug('in Copy for planet '+repr(self._planet_id))
#    new = Planet(self._planet_id, self._owner[0], self._num_ships[0], self._growth_rate, self._x, self._y)
#    #logging.debug(repr(self._owner))
#    owner = deepcopy(self._owner)
#    #logging.debug(repr(owner))
#    num_ships = deepcopy(self._num_ships)
#    allied_arrivals = deepcopy(self._allied_arrivals)
#    #logging.debug(repr(self._free_troops))
#    free_troops = deepcopy(self._free_troops)
#    #logging.debug(repr(free_troops))
#    reinforcing_troops = deepcopy(self._reinforcing_troops)
#    defending_troops = deepcopy(self._defending_troops)
#    allied_reinforcements = deepcopy(self._allied_reinforcements)
#    attacking_troops = deepcopy(self._attacking_troops)
#    nearest_ally = deepcopy(self._nearest_ally)
#    nearest_enemy = deepcopy(self._nearest_enemy)
#    farthest_ally = deepcopy(self._farthest_ally)
#    farthest_enemy = deepcopy(self._farthest_enemy)
#    new.ReplaceArrays(owner, num_ships, allied_arrivals, deepcopy(self._free_troops), reinforcing_troops, defending_troops, allied_reinforcements, attacking_troops, nearest_ally, nearest_enemy, farthest_ally, farthest_enemy)
#    return new
#
#  def ReplaceArrays(self, owner, num_ships, allied_arrivals, free_troops, reinforcing_troops, defending_troops, allied_reinforcements, attacking_troops, nearest_ally, nearest_enemy, farthest_ally, farthest_enemy):
#    #logging.debug('Replacing Arrays')
#    self.PrintSummary()
#    self._owner = owner
#    self._num_ships = num_ships
#    self._allied_arrivals = allied_arrivals
#    #logging.debug('replacing '+repr(self._free_troops))
#    #logging.debug('with '+repr(free_troops))
#    self._enemy_arrivals = free_troops
#    self._free_troops = reinforcing_troops
#    self._reinforcing_troops= reinforcing_troops
#    self._defending_troops= defending_troops
#    self._allied_reinforcements = allied_reinforcements
#    self._attacking_troops = attacking_troops
#    self._nearest_ally = nearest_ally
#    self._nearest_enemy = nearest_enemy
#    self._farthest_enemy = farthest_enemy
#    self._farthest_ally = farthest_ally
#    self.PrintSummary()



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
    self._allied_arrivals[turn]+=ships


  def SimulateAttack(self, turn):
    #logging.debug('Simulating an attack on turn'+repr(turn))
    self.PrintSummary()
    for i in range(turn, len(self._owner)):
      self.CalcFreeTroops(i,1)
      self.CalcOwnerAndNumShips(i,1)
    #logging.debug('done!')
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
    for i in range(max+1):
      self._reinforcing_troops.append(0)
      self._defending_troops.append(0)
      self._allied_reinforcements.append(0)
      self._attacking_troops.append(0)

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
    #logging.debug('in ResetFreeTroops')
    self._free_troops = []
    if self._owner[0] == 1:
      self._free_troops.append(self._num_ships[0])
    elif self._owner[0] == 2:
      self._free_troops.append(-1*self._num_ships[0])
    else:
      self._free_troops.append(0)
    #logging.debug('done')


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
    #logging.debug('levels: '+repr(levels))
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
    levels = [0, self._allied_arrivals[turn], self._enemy_arrivals[turn]]
    if self._owner[turn-1] != 0:
      levels[self._owner[turn-1]] += self._growth_rate
    else:
      levels[0]=self._num_ships[turn-1]
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
    #logging.debug('leaving, free troops: ' + repr(self._free_troops))


  def GetFreeTroops(self, start_turn=0, end_turn=-1):
    #logging.debug('in GetFreeTroops ' + repr(self._free_troops)+ ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._free_troops[start_turn]
    else:
      #logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._free_troops[start_turn:end_turn+1])

  def GetDefendingTroops(self, start_turn=0, end_turn=-1):
    #logging.debug('in GetDefendingTroops ' + repr(self._defending_troops)+ ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._defending_troops[start_turn]
    else:
      #logging.debug('returning a range of defending troops troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._defending_troops[start_turn:end_turn+1])

  def GetReinforcingTroops(self, start_turn=0, end_turn=-1):
    #logging.debug('in GetReinforcingTroops ' + repr(self._reinforcing_troops) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._reinforcing_troops[start_turn]
    else:
      #logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._reinforcing_troops[start_turn:end_turn+1])


  def GetAlliedReinforcements(self, start_turn=0, end_turn=-1):
    #logging.debug('in GetAlliedReinforcements ' + repr(self._allied_reinforcements) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._allied_reinforcements[start_turn]
    else:
      #logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._allied_reinforcements[start_turn:end_turn+1])

  def GetAttackingTroops(self, start_turn=0, end_turn=-1):
    #logging.debug('in GetAttackingTroops ' + repr(self._allied_reinforcements) + ' turn='+repr(start_turn))
    if end_turn == -1:
      return self._attacking_troops[start_turn]
    else:
      #logging.debug('returning a range of troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._attacking_troops[start_turn:end_turn+1])

  def GetAllTroops(self, start_turn=0, end_turn=-1):
    #logging.debug('in GetAllTroops')
    return self.GetFreeTroops(start_turn, end_turn) + self.GetDefendingTroops(start_turn, end_turn) \
      + self.GetReinforcingTroops(start_turn, end_turn) + self.GetAttackingTroops(start_turn, end_turn)



  def SetFreeTroops(self, turn, troops):
    #logging.debug('in SetFreeTroops')
    #logging.debug(repr(self._free_troops))
    self._free_troops[turn]=troops
    #logging.debug(repr(self._free_troops))

  def PlanetID(self):
    return self._planet_id

  def SetOwner(self, new_owner):
    self._owner = []
    self._owner.append(new_owner)

  def GetOwner(self, turn=0):
    return self._owner[turn]

  def GetNumShips(self, turn=0):
    #logging.debug('in GetNumShips with turn='+repr(turn))
    return self._num_ships[turn]

  def FreeTroops(self):
    return self._free_troops
  
  def ReinforcingTroops(self):
    return self._reinforcing_troops
  
  def DefendingTroops(self):
    return self._defending_troops

  def AttackingTroops(self):
    return self._attacking_troops

  def AlliedReinforcements(self):
    return self._allied_reinforcements

  def SetNumShips(self, new_num_ships):
    #logging.debug('in SetNumShips with new_num_ships='+repr(new_num_ships))
    self._num_ships = []
    #logging.debug('adding some new ships'+repr(new_num_ships))
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
      #logging.debug('________________________________________________________________')
      #logging.debug('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0])+' and regen '+repr(self._growth_rate))
      #logging.debug('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
      #logging.debug('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
      #logging.debug('Owner List      - '+repr(self._owner))
      #logging.debug('Num Ships List  - '+repr(self._num_ships))
      #logging.debug('FreeTroops List - '+repr(self._free_troops))
      #logging.debug('Reinforcing List- '+repr(self._reinforcing_troops))
      #logging.debug('Defending List  - '+repr(self._defending_troops))
      #logging.debug('Attacking List  - '+repr(self._attacking_troops))
      #logging.debug('Allied Reinforce- '+repr(self._allied_reinforcements))
      #logging.debug('________________________________________________________________')
      return 0
    else:
      #logging.info('________________________________________________________________')
      #logging.info('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0]))
      #logging.info('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
      #logging.info('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
      #logging.info('Owner List      - '+repr(self._owner))
      #logging.info('FreeTroops List - '+repr(self._free_troops))
      #logging.info('Reinforcing List- '+repr(self._reinforcing_troops))
      #logging.info('Defending List  - '+repr(self._defending_troops))
      #logging.info('Attacking List  - '+repr(self._attacking_troops))
      #logging.info('Allied Reinforce- '+repr(self._allied_reinforcements))
      #logging.info('________________________________________________________________')
      return 0