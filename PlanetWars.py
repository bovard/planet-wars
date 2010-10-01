#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout

import logging
LOG_FILENAME = 'War.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.WARNING, filemode='w')


class Fleet:
  def __init__(self, owner, num_ships, source_planet, destination_planet, total_trip_length, turns_remaining):
    self._owner = owner
    self._num_ships = num_ships
    self._source_planet = source_planet
    self._destination_planet = destination_planet
    self._total_trip_length = total_trip_length
    self._turns_remaining = turns_remaining

  def Update(self):
    logging.debug('in update')
    self._turns_remaining -= 1
    logging.debug('done')
    return self._turns_remaining

  def Owner(self):
    return self._owner

  def NumShips(self):
    return self._num_ships

  def SourcePlanet(self):
    return self._source_planet

  def DestinationPlanet(self):
    return self._destination_planet

  def TotalTripLength(self):
    return self._total_trip_length

  def TurnsRemaining(self):
    return self._turns_remaining


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

  # this should be called before every turn starts
  # reinforcing troops are committed to respond to an enemy threat
  # defending troops are committed to respond to an actualy enemy attack
  def ResetReinforcements(self, max):
    self._reinforcing_troops=[]
    self._defending_troops=[]
    for i in range(max+1):
      self._reinforcing_troops.append(0)
      self._defending_troops.append(0)

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
      logging.debug('returning a range of free troops ['+repr(start_turn)+','+repr(end_turn)+']')
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
      logging.debug('returning a range of free troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._reinforcing_troops[start_turn:end_turn+1])

  def GetAllTroops(self, start_turn=0, end_turn=-1):
    logging.debug('in GetAllTroops')
    return self.GetFreeTroops(start_turn, end_turn) + self.GetDefendingTroops(start_turn, end_turn) + self.GetReinforcingTroops(start_turn, end_turn)


  #commits free troops for turn=turn
  #ships = # enemy ships to commit against
  # this should be called when defending against an incoming fleet
  # this should only be called from the CommitReinforce method
  # we know this is an allied planet!
  def CommitDefendingTroops(self, turn, ships):
    logging.debug('in CommitDefendingTroops with turn='+repr(turn) + ' ships='+repr(ships))
    logging.debug('With FreeTroops       '+ repr(self._free_troops))
    logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
    logging.debug('and DefendingTroops   '+ repr(self._defending_troops))

    #need to make sure there are some troops to reinforce with
    avaliable = self._free_troops[turn]+self._reinforcing_troops[turn]
    if not(avaliable==0):
      left = ships + avaliable
      # if we have to commit all the troops:
      # Note: we'll only be
      if left * ships > 0:
        ships_committed = self._free_troops[turn] + self._reinforcing_troops[turn]
        if ships_committed > 0:
          self._free_troops[turn] =0
          self._reinforcing_troops[turn] =0
          logging.debug('committing free troops to defence')
        logging.debug('leaving CommitDefendingTroops')
        logging.debug('With FreeTroops       '+ repr(self._free_troops))
        logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
        logging.debug('and DefendingTroops   '+ repr(self._defending_troops))
        return ships_committed
      # we only have to commit some of the troops!
      else:
        logging.debug('commiting defenders')
        # we're going to have to commit a few free troops
        # we need to check how many more we have to commit than the current defenders
        left= ships + self._reinforcing_troops[turn]
        if left <= 0:
          # we need to commit left free ships to defense!
          self._free_troops[turn] += left
          self._reinforcing_troops[turn] = 0
          logging.debug('leaving CommitDefendingTroops after commiting '+repr(left)+' free troops to defesne')
          logging.debug('With FreeTroops       '+ repr(self._free_troops))
          logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
          logging.debug('and DefendingTroops   '+ repr(self._defending_troops))
          return -1*ships
        else:
          # don't have to commit any free troops to defense!
          self._reinforcing_troops[turn] += ships
          logging.debug("didn't have to commit anything and leaving CommitDefendingTroops")
          logging.debug('With FreeTroops       '+ repr(self._free_troops))
          logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
          logging.debug('and DefendingTroops   '+ repr(self._defending_troops))
          return -1*ships
    else:
      logging.debug('leaving CommitTroops (there was nothing to reinforce with!)')
      return 0


  #commits free troops for turn=turn
  #ships = # enemy ships to commit against
  #this should be called when looking for ships to attack with
  def CommitFreeTroops(self, turn, ships):
    logging.debug('in CommitFreeTroops with turn='+repr(turn) + ' ships='+repr(ships))
    logging.debug('and with free troops = '+ repr(self._free_troops))
    #check to make sure there are some free troops to use
    if not(self._free_troops[turn]==0):
      left = ships + self._free_troops[turn]
      # if we have to commit all the troops:
      if left * ships > 0:
        ships_committed = self._free_troops[turn]
        if ships_committed > 0:
          self._free_troops[turn] -= ships_committed
          self._reinforcing_troops[turn]= ships_committed
        logging.debug('leaving CommitTroops')
        return self._reinforcing_troops[turn]
      # we only have to commit some of the troops!
      else:
        # we're going to have to commit a few free troops
        self._free_troops[turn] += ships
        self._reinforcing_troops[turn] += -1*ships
        logging.debug('leaving CommitTroops')
        return -1*ships
    else:
      logging.debug('leaving CommitFreeTroops (no free troops to commit here!)')
      return 0



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

  def CanReinforce(self, turn):
    logging.debug('in CanReinforce')
    ships = self.GetDefendingTroops(turn)

    #check oneself first
    logging.debug('looking for reinforcements from home planet')
    logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    ships += self.GetAllTroops(0,turn-1)
    logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    #check levels on nearby planets for help
    logging.debug('looking at nearby planets for free troops')
    for i in range(1,turn+1):
      logging.debug('looking '+repr(i)+' units away')
      for p in self._neighbors[i]:
        ships += p.GetAllTroops(0,turn-i)
        logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    if ships >= 0:
      logging.debug('one can reinfroce (leaving CanReinforce)')
      return 1
    logging.debug('one cannot reinforce! (leaving CanReinforce)')
    return 0

  def CommitReinforce(self, turn):
    ships = self.GetAllTroops(turn)
    logging.debug('in CommitReinforce')
    logging.debug('there are '+repr(ships)+' left!')
    def_ships = ships
    if def_ships>0:
      ships += self.GetReinforcingTroops(0, turn-1)
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=0
    r_enemy=1
    r_enemy_last_seen=r_enemy
    done = 0
    while (r_ally<=turn or r_enemy<=turn) and not(done):
      logging.debug('top of main loop')
      done = 1
      while ships<0 and r_ally<=turn:
        logging.debug('top of allied loop with r_ally='+repr(r_ally))
        if not(r_enemy_last_seen==r_enemy):
          for i in range(r_enemy_last_seen,r_enemy):
            for p in self._neighbors[i]:
              if def_ships >= 0:
                ships += p.GetReinforcingTroops(0, turn-i)
          done = 0

          r_enemy_last_seen=r_enemy
        elif r_ally==0:
          #check oneself first
          if self._owner[turn-1]==1:
            logging.debug('looking for reinforcements from home planet')
            for i in range(turn,-1,-1):
              if def_ships >= 0:
                ships += self.CommitFreeTroops(i, ships)
              else:
                enforcements = self.CommitDefendingTroops(i, ships)
                ships += enforcements
                def_ships += enforcements
                self._defending_troops[i]+=enforcements
              logging.debug('there are '+repr(ships)+' left!')
          if ships<0:
            logging.debug('increasing allied radius')
            r_ally+=1
        else:
          #check allies for help
          logging.debug('checking allies for help')
          for p in self._neighbors[r_ally]:
            if p.GetOwner(r_ally-1)==1:
              j=turn-r_ally
              while ships<0 and j>=0:
                logging.info('searching through planets j='+repr(j))
                if def_ships >= 0:
                  enforcements = self.CommitFreeTroops(i, ships)
                  ships += enforcements
                else:
                  enforcements = self.CommitDefendingTroops(i, ships)
                  ships += enforcements
                  def_ships += enforcements
                  self._defending_troops[i]+=enforcements

                #only launch ships if we are defening against an attack... ?
                if r_ally==turn and j==0 and enforcements>0:
                  logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(i))
                  self._launch_queue[p.PlanetID()][self._planet_id]+=enforcements
                logging.debug('there are '+repr(ships)+' left!')
                j-=1
          logging.debug('increasing allied radius')
          r_ally+=1

      while ships>=0 and r_enemy<=turn:
        done = 0
        logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        for p in self._neighbors[r_enemy]:
          if p.GetOwner(r_enemy-1)==2:
            ships += p.GetFreeTroops(0, turn-r_enemy)
            logging.debug('there are '+repr(ships)+' left!')
        logging.debug('botton of enemy loop!')
        logging.debug('increasing enemy radius')
        r_enemy+=1
    if ships >= 0:
      logging.debug('sucess! leaving commitreinforce')
      logging.debug(repr(self._free_troops))
      logging.debug(repr(self._reinforcing_troops))
      return 1
    logging.debug('failed! CommitReinforce')
    return 0

  def CanTakeOver(self, turn):
    ships = -1
    logging.debug('in CanTakeOver')

    if self._owner[turn-1]==0:
      ships -= self._num_ships[turn-1]

    #check oneself first
    logging.debug('looking for reinforcements from home planet')
    logging.debug('there are '+repr(ships)+' left!')
    ships += self.GetFreeTroops(0,turn)
    logging.debug('only '+repr(ships)+' left!')

    #check levels on nearby planets for help
    logging.debug('looking for reinforcements from nearby planets')
    for i in range(1,turn+1):
      logging.debug('looking '+repr(i)+' units away')
      if ships>0:
        ships+=self.GrowthRate()
      for p in self._neighbors[i]:
        ships += p.GetFreeTroops(0,turn-i)
        if not(self._owner[turn-1]==0):
          ships += p.GetReinforcingTroops(1, turn-i)
        logging.debug('only '+repr(ships)+' left!')

    if ships >= 0:
      logging.debug('one can TAKEOVER (leaving CanTakeOver)')
      return 1
    logging.debug('one cannot take over! (leaving CanTakeOver)')
    return 0

  def CommitTakeOver(self, turn):
    if not(self._owner[turn]==1):
      ships = -1*(self._num_ships[turn]+1)
      logging.debug('in CommitTakeOver')
      logging.debug('there are '+repr(ships)+' left!')

      #check allies for help
      for i in range(1,turn+1):
        if ships>0:
          ships+=self.GrowthRate()
        for p in self._neighbors[i]:
          for j in range(turn,i-1,-1):
            k = turn-j
            reinforcement = p.CommitFreeTroops(k, ships)
            ships += reinforcement
            logging.debug('there are '+repr(ships)+' left!')
            if k==0 and reinforcement>0:
              logging.info('attacking!!!')
              logging.info('sending '+repr(reinforcement)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(i))
              self._launch_queue[p.PlanetID()][self._planet_id]+=reinforcement
            if ships >= 0:
              logging.debug('sucess! leaving CommitTakeOver')
              logging.debug(repr(self._free_troops))
              return 1
      logging.debug('failed! CommitTakeOver')
      return 0
    else:
      logging.warning('tried to take over an allied planet!')
      return 0



class PlanetWars:
  def __init__(self, gameState, turn):
    self._nearest_enemy=9999999
    self._farthest_enemy=-1
    logging.info('Initializing Planet Wars')
    logging.info('Turn number '+repr(turn))
    self._planets = []
    self._fleets = []
    self.ParseGameState(gameState)
    self._distance = {}
    logging.info('initializing distance')
    self._max_distance = self.InitDistance()
    self._max_regen = self.InitMaxRegen()
    logging.info('done with distances')
    logging.info('initialiaing and calculatings neighbors')
    self.InitNeighbors()
    logging.info('initializing arrivals')
    self.InitArrivals()
    logging.info('done with arrivals')
    logging.info('adding new fleets')
    self.AddNewFlights()
    logging.info('done with new flights')
    logging.info('setting reinforcements')
    self.ResetReinforcements()
    logging.info('done setting reinforcements')
    logging.info('setting nearest/farthest neighbors')
    self.ResetNeighbors()
    logging.info('done setting neighbors')
    logging.info('setting launch queue')
    self._launch_queue = self.InitializeLaunchQueue()
    logging.info('done setting launch queue')
    logging.info('done with initialization')


  def InitializeLaunchQueue(self):
    logging.debug('initializing launch queue')
    launch_queue = {}
    for p in self.Planets():
      launch_queue[p.PlanetID()]={}
      for o in self.Planets():
        launch_queue[p.PlanetID()][o.PlanetID()]=0
    logging.debug('initialezed launch queue!')
    for p in self.Planets():
      p.SetLaunchQueue(launch_queue)
    return launch_queue

  def MaxRegen(self):
    return self._max_regen

  def GetLaunch(self, p_id_source, p_id_dest):
    return self._launch_queue[p_id_source][p_id_dest]

  def AddLaunch(self, p_id_source, p_id_dest, ships):
    if ships>0:
      self._launch_queue[p_id_source][p_id_dest]+=ships
    else:
      logging.warning('Tried to send a non-positive amount of troops!')
      return -1

  def LaunchShips(self):
    #launch troops!
    for p in self.MyPlanets():
      to_send = 0
      for o in self.Planets():
        to_send = self._launch_queue[p.PlanetID()][o.PlanetID()]
        if to_send>0:
          logging.info('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
          logging.info('Planet'+repr(p.PlanetID())+'- regen: '+repr(p.GrowthRate()) + '- troops: '+repr(p.GetNumShips()))
          logging.info('Planet'+repr(o.PlanetID())+'- regen: '+repr(o.GrowthRate()) + '- troops: '+repr(o.GetNumShips()))
          logging.info('balls?')
          availiable = p.GetNumShips()
          if availiable >= to_send:
            p.SetNumShips(availiable-to_send)
            self.IssueOrder(p.PlanetID(),o.PlanetID(),to_send)
          elif availiable > 0:
            logging.critical('BAD TROOP TRANSPORT')
            logging.critical('Tried to send '+repr(to_send)+' but had '+repr(availiable))
            p.SetNumShips(0)
            self.IssueOrder(p.PlanetID(),o.PlanetID(),availiable)
          else:
            logging.critical('somehow we have a negative amount on one of the planets.... oops?')
            logging.critical('BAD TROOP TRANSPORT')
            continue
        elif to_send<0:
          logging.critical('NEGATIVE AMOUNT TO SEND')
          logging.critical('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
          continue

  def InitMaxRegen(self):
    max = -1
    for p in self._planets:
      if p.GrowthRate()>max:
        max = p.GrowthRate()
    return max

  def GetGlobalAlliedFreeTroopLevels(self, turn=0):
    sum = 0
    for p in self.MyPlanets(turn):
      sum += p.GetFreeTroops(0,turn)
    return sum

  def GetTroopBalance(self, turn=0):
    diff = 0
    for p in self.EnemyPlanets(turn):
      diff -= p.GetNumShips(turn)
    for p in self.MyPlanets(turn):
      diff += p.GetNumShips(turn)
    return diff

  def GetRegenBalance(self, turn=0):
    diff = 0
    for p in self.EnemyPlanets(turn):
      diff -= p.GrowthRate()
    for p in self.MyPlanets(turn):
      diff += p.GrowthRate()
    return diff

  def ResetReinforcements(self):
    for p in self._planets:
      p.ResetReinforcements(self._max_distance)

  def ResetNeighbors(self):
    for p in self._planets:
      p.ResetNeighbors()

  def GetGlobalNearestEnemy(self):
    return self._nearest_enemy

  def GetGlobalFarthestEnemy(self):
    return self._farthest_enemy

  def CalcNeighbors(self, turn):
    self._nearest_enemy=9999999
    self._farthest_enemy=-1
    for p in self._planets:
      p.CalcNeighbors(turn, self._max_distance)
      if p.GetOwner(turn)==1 or p.GetOwner(turn)==2:
        if p.NearestEnemy(0)<self._nearest_enemy:
          self._nearest_enemy=p.NearestEnemy(0)
        if p.FarthestEnemy(0)>self._farthest_enemy:
          self._farthest_enemy=p.FarthestEnemy(0)

  def MaxDistance(self):
    return self._max_distance

  def InitNeighbors(self):
    logging.debug('initializing arrays')
    #create the arrays
    for p in self._planets:
      p.CreateNeighbor(self._max_distance)
    logging.debug('done, populating arrays')
    #populate the arrays
    for p1 in self._planets:
      for p2 in self._planets:
        distance = self.Distance(p1.PlanetID(),p2.PlanetID())
        if distance>0:
          p1.AddNeighbor(distance, p2)
    logging.debug('done')

  def InitArrivals(self):
    logging.debug('initializing arrays')
    for p in self._planets:
      p.InitArrivals(self._max_distance)
    logging.debug('done')


  def AddNewFlights(self):
    logging.debug('in AddNewFlights')
    for f in self._fleets:
      logging.debug('testing for new flights')
      logging.debug(repr(f.TurnsRemaining()+1)+'=?'+repr(f.TotalTripLength()))
      if f.TurnsRemaining()+1==f.TotalTripLength():
        logging.debug('testing for owner')
        if f.Owner() ==1:
          logging.debug('my fleet')
          self.GetPlanet(f.DestinationPlanet()).AddAlliedArrival(f.TurnsRemaining(), f.NumShips())
        elif f.Owner() ==2:
          logging.debug('enemy fleet')
          self.GetPlanet(f.DestinationPlanet()).AddEnemyArrival(f.TurnsRemaining(), f.NumShips())
    logging.debug('leaving AddNewFlights')

  def Update(self, gameState, turn):
    logging.info('Updating map information for turn '+repr(turn))
    logging.debug('updating old flight information')
    to_remove = []
    for f in self._fleets:
      logging.debug('updating a flight')
      in_flight = f.Update()
      logging.debug(repr(in_flight) + ' turns left for this flight')
      if not(in_flight):
        to_remove.append(f)
      logging.debug('updated a flight!')
    for f in to_remove:
      self._fleets.remove(f)
      logging.debug('removed flight ' + repr(f))
    logging.debug('updated!')
    logging.debug('updating the arrival queues')
    for p in self._planets:
      p.Update()
    logging.debug('done')
    self.ParseGameState(gameState, 1)
    logging.debug('there are ' + repr(len(self._planets)) + ' and ' + repr(len(self._fleets)) + ' fleets')
    logging.debug('adding new flights')
    self.AddNewFlights()
    logging.debug('done')
    logging.info('setting reinforcements')
    self.ResetReinforcements()
    logging.info('done setting reinforcements')
    logging.info('resetting nearest/farthest neighbors')
    self.ResetNeighbors()
    logging.info('done resetting neighbors')
    logging.info('setting launch queue')
    self._launch_queue = self.InitializeLaunchQueue()
    logging.info('done setting launch queue')
    logging.info('sucessfully updated!')


  def InitDistance(self):
    max = 0
    for i in range(0,len(self._planets)):
      p_id = self._planets[i].PlanetID()
      self._distance[p_id]={}
      for j in range(i+1,len(self._planets)):
        o_id = self._planets[j].PlanetID()
        distance = self.CalcDistance(p_id,o_id)
        self._distance[p_id][o_id]=distance
        if distance > max:
          max = distance
    logging.debug('done. max is '+repr(max))
    return max

  def Distance(self, source, dest):
    if source < dest:
      return self._distance[source][dest]
    elif source == dest:
      return 0
    else:
      return self._distance[dest][source]

  def NumPlanets(self):
    return len(self._planets)

  def GetPlanet(self, planet_id):
    return self._planets[planet_id]

  def NumFleets(self):
    return len(self._fleets)

  def GetFleet(self, fleet_id):
    return self._fleets[fleet_id]

  def Planets(self):
    return self._planets

  def MyPlanets(self, turn=0):
    r = []
    for p in self._planets:
      if p.GetOwner(turn) != 1:
        continue
      r.append(p)
    return r

  def NeutralPlanets(self, turn=0):
    r = []
    for p in self._planets:
      if p.GetOwner(turn) != 0:
        continue
      r.append(p)
    return r

  def EnemyPlanets(self, turn =0):
    r = []
    for p in self._planets:
      if p.GetOwner(turn) <= 1:
        continue
      r.append(p)
    return r

  def NotMyPlanets(self, turn=0):
    r = []
    for p in self._planets:
      if p.GetOwner(turn) == 1:
        continue
      r.append(p)
    return r

  def Fleets(self):
    return self._fleets

  def MyFleets(self):
    r = []
    for f in self._fleets:
      if f.Owner() != 1:
        continue
      r.append(f)
    return r

  def EnemyFleets(self):
    r = []
    for f in self._fleets:
      if f.Owner() <= 1:
        continue
      r.append(f)
    return r

  def ToString(self):
    s = ''
    for p in self._planets:
      s += "P %f %f %d %d %d\n" % \
       (p.X(), p.Y(), p.GetOwner(), p.GetNumShips(), p.GrowthRate())
    for f in self._fleets:
      s += "F %d %d %d %d %d %d\n" % \
       (f.Owner(), f.NumShips(), f.SourcePlanet(), f.DestinationPlanet(), \
        f.TotalTripLength(), f.TurnsRemaining())
    return s

  def CalcDistance(self, source_planet, destination_planet):
    source = self._planets[source_planet]
    destination = self._planets[destination_planet]
    dx = source.X() - destination.X()
    dy = source.Y() - destination.Y()
    return int(ceil(sqrt(dx * dx + dy * dy)))

  def IssueOrder(self, source_planet, destination_planet, num_ships):
    logging.info("%d %d %d\n" % (source_planet, destination_planet, num_ships))
    stdout.write("%d %d %d\n" % \
     (source_planet, destination_planet, num_ships))
    stdout.flush()

  def IsAlive(self, player_id):
    for p in self._planets:
      if p.GetOwner() == player_id:
        return True
    for f in self._fleets:
      if f.Owner() == player_id:
        return True
    return False

  def ParseGameState(self, s, update=0):
    if not(update):
      self._planets = []
      self._fleets = []
    lines = s.split("\n")
    planet_id = 0
    flights = 0
    for line in lines:
      line = line.split("#")[0] # remove comments
      tokens = line.split(" ")
      if len(tokens) == 1:
        continue
      if tokens[0] == "P":
        logging.debug('planet token')
        if len(tokens) != 6:
          return 0
        if(update):
          logging.debug('updating planet '+repr(planet_id))
          p = self.GetPlanet(planet_id)
          logging.debug('pulled the planet')
          p.SetOwner(int(tokens[3]))
          p.SetNumShips(int(tokens[4]))
          p.ResetFreeTroops()
          logging.debug('done')
        else:
          p = Planet(planet_id, # The ID of this planet
                   int(tokens[3]), # Owner
                   int(tokens[4]), # Num ships
                   int(tokens[5]), # Growth rate
                   float(tokens[1]), # X
                   float(tokens[2])) # Y
          self._planets.append(p)
          p.ResetFreeTroops()
        planet_id += 1

      elif tokens[0] == "F":
        logging.debug('flight token')
        flights += 1
        if len(tokens) != 7:
          return 0
        else:
          logging.debug('testing to add a valid flight')
          logging.debug('update='+repr(update))
          logging.debug(tokens[6] + '+1=?' + tokens[5])
          if not(update) or int(tokens[6])+1==int(tokens[5]):
            logging.debug('adding a flight')
            f = Fleet(int(tokens[1]), # Owner
                  int(tokens[2]), # Num ships
                  int(tokens[3]), # Source
                  int(tokens[4]), # Destination
                  int(tokens[5]), # Total trip length
                  int(tokens[6])) # Turns remaining
            self._fleets.append(f)
            logging.debug('done')
      else:
        return 0
    if not(flights==len(self._fleets)):
      logging.critical("FLIGHT MISMANAGEDMENT!")
      logging.critical('processed: '+repr(flights)+' but only have '+repr(len(self._fleets)))
      return -1
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
    