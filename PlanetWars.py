#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout

import logging
LOG_FILENAME = 'War.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.CRITICAL, filemode='w')


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
    logging.debug('owner is now '+repr(self._owner))
    self._num_ships = []
    self._num_ships.append(num_ships)
    logging.debug('num ships is now '+repr(self._num_ships))
    self._growth_rate = growth_rate
    self._x = x
    self._y = y
    self._neighbors = {}
    self._allied_arrivals = []
    self._enemy_arrivals = []
    self._free_troops = []
    self._allied_reinforcements=[]
    self._nearest_ally = []
    self._nearest_enemy = []
    self._farthest_enemy = []
    self._farthest_ally = []
    self._nearest_ally.append(100000000000)
    self._nearest_enemy.append(100000000000)
    self._farthest_enemy.append(0)
    self._farthest_ally.append(0)


  # needs to be called once at the beginning of the game (done)
  def InitArrivals(self, max):
    for i in range(max+1):
      self._allied_arrivals.append(0)
      self._enemy_arrivals.append(0)

  def AddEnemyArrival(self, turn, ships):
    self._enemy_arrivals[turn] += ships
  
  def AddAlliedArrival(self, turn, ships):
    self._allied_arrivals[turn] += ships

  # this should be called before flights are processed (done)
  def Update(self):
    logging.debug('in Planet.Update() for planet ' + repr(self._planet_id))
    self._enemy_arrivals = self._enemy_arrivals[1:]
    self._enemy_arrivals.append(0)
    self._allied_arrivals = self._allied_arrivals[1:]
    self._allied_arrivals.append(0)
    logging.debug('done')

  # this should be called before every turn starts
  def ResetReinforcements(self, max):
    self._allied_reinforcements=[]
    for i in range(max+1):
      self._allied_reinforcements.append(0)

  def ResetNeighbors(self):
    self._nearest_ally = []
    self._nearest_enemy = []
    self._farthest_enemy = []
    self._farthest_ally = []

  def NearestAlly(self, turn=0):
    logging.debug('returning nearest ally for turn '+repr(turn))
    logging.debug(repr(self._nearest_ally[turn]))
    return self._nearest_ally[turn]

  def NearestEnemy(self, turn=0):
    logging.debug('returning nearest enemy for turn '+repr(turn))
    logging.debug(repr(self._nearest_enemy[turn]))
    return self._nearest_enemy[turn]

  def FarthestEnemy(self, turn=0):
    logging.debug('returning farthest enemy for turn '+repr(turn))
    logging.debug(repr(self._farthest_enemy[turn]))
    return self._farthest_enemy[turn]

  def FarthestAlly(self, turn=0):
    logging.debug('returning farthest ally for turn '+repr(turn))
    logging.debug(repr(self._farthest_ally[turn]))
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
    logging.debug('free troops are: ' + repr(self._free_troops))

  def Reinforce(self, turn, ships):
    logging.debug('entering Reinforce')
    self._allied_reinforcements[turn]+=ships
    logging.debug('leaving reinforce')

  #called after CalCOwnerAndNumShips
  def CalcNeighbors(self, turn, max):
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
    logging.debug('calculated nearest: '+repr(near_ally)+','+repr(far_ally))
    logging.debug('and farthest '+repr(far_ally)+','+repr(far_enemy)+' for turn '+repr(turn))
    self._nearest_ally.append(near_ally)
    self._nearest_enemy.append(near_enemy)
    self._farthest_ally.append(far_ally)
    self._farthest_enemy.append(far_enemy)


  # this needs to be called every turn sequentailly to work
  def CalcOwnerAndNumShips(self, turn):
    logging.debug('in CalcOwnerAndNumShips')
    levels = [0, self._allied_arrivals[turn]+self._allied_reinforcements[turn], self._enemy_arrivals[turn]]
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
      logging.info('there is a tie')
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
    logging.debug('Ownership - '+repr(self._owner))


  # this needs to be called every turn sequentially to work, call at the begginning of the turn
  def CalcFreeTroops(self, turn):
    logging.debug('in CalcFreeTroops')
    logging.debug('enemy_arrivals: '+repr(self._enemy_arrivals))
    logging.debug('allied arrivals: '+repr(self._allied_arrivals))
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
        logging.debug('I won!'+repr(max)+ ' '+repr(max2))
        self._free_troops.append(max-max2)
        logging.debug('calced + free troops')
      elif winner==2:
        logging.debug('I lost!'+repr(max)+ ' '+repr(max2))
        self._free_troops.append(max2-max)
        logging.debug('calced - free troops')
      else:
        self._free_troops.append(0)
        logging.debug('calced 0 free troops (neutral)')
    logging.debug('leaving, free troops: ' + repr(self._free_troops))

  def CanDefend(self, max):
    min = -99999999999999999
    for i in range(max):
      sum = self.GetFreeTroops(0, i)
      for j in range(1,i+1):
        for p in self._neighbors[j]:
          sum += p.GetFreeTroops(0, i-j)
      if sum<min:
        min = sum
    return min




  def GetFreeTroops(self, start_turn, end_turn=-1):
    logging.debug('in GetFreeTroops' + repr(self._free_troops)+ ' turn='+repr(start_turn))
    logging.debug(repr(self._free_troops[start_turn])+' '+repr(self._allied_reinforcements[start_turn]))
    if end_turn == -1:
      logging.debug('return a single turn of free troops')
      return self._free_troops[start_turn]+self._allied_reinforcements[start_turn]
    else:
      logging.debug('returning a range of free troops ['+repr(start_turn)+','+repr(end_turn)+']')
      return sum(self._free_troops[start_turn:end_turn+1])+sum(self._allied_reinforcements[start_turn:end_turn+1])


  def CommitFreeTroops(self, turn, ships):
    logging.debug('in CommitFreeTroops'+ repr(self._free_troops)+ ' turn='+repr(turn))
    if not(self._free_troops[turn]==0):
      left = ships + self._free_troops[turn]
      if left * ships > 0:
        ships_committed = self._free_troops[turn]
        self._free_troops[turn] -= ships_committed
        logging.debug('committed '+repr(ships_committed))
        return ships_committed
      else:
        self._free_troops[turn] += ships
        return -1*ships
    else:
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
    logging.debug('self._num_ships is '+repr(self._num_ships) + 'turn = '+repr(turn))
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

  def CanReinforce(self, turn, ship_request):
    ships = ship_request
    logging.debug('in CanReinforce')

    #check oneself first
    logging.debug('looking for reinforcements from home planet')
    logging.debug('there are '+repr(ships)+' left!')
    ships += self.GetFreeTroops(0,turn-1)
    logging.debug('only '+repr(ships)+' left!')
    if ships >= 0:
      logging.debug('one can reinfroce (leaving CanReinforce)')
      return 1
    #check levels on nearby planets for help
    logging.debug('looking for reinforcements from allied planets')
    for i in range(1,turn+1):
      logging.debug('looking '+repr(i)+' units away')
      for p in self._neighbors[i]:
        ships += p.GetFreeTroops(0,turn-i)
        if ships >= 0:
          logging.debug('one can reinfroce (leaving CanReinforce)')
          return 1
    logging.debug('one cannot reinforce! (leaving CanReinforce)')
    return 0

  def CanTakeOver(self, turn):
    ships = -1
    logging.debug('in CanTakeOver')

    if self._owner[turn]==0:
      ships -= self._num_ships[turn]

    #check oneself first
    logging.debug('looking for reinforcements from home planet')
    logging.debug('there are '+repr(ships)+' left!')
    ships += self.GetFreeTroops(0,turn)
    logging.debug('only '+repr(ships)+' left!')
    if ships >= 0:
      logging.debug('one can takeover (leaving CanTakeOver)')
      return 1

    #check levels on nearby planets for help
    logging.debug('looking for reinforcements from nearby planets')
    for i in range(1,turn+1):
      logging.debug('looking '+repr(i)+' units away')
      for p in self._neighbors[i]:
        ships += p.GetFreeTroops(0,turn-i)
        logging.debug('only '+repr(ships)+' left!')
        if ships >= 0:
          logging.debug('one can TAKEOVER (leaving CanTakeOver)')
          return 1
    logging.debug('one cannot take over! (leaving CanTakeOver)')
    return 0


  def CommitReinforce(self, turn, ship_request, launch_queue):
    ships = ship_request
    logging.debug('in CommitReinforce')
    #check oneself first
    if self._owner[turn-1]==1:
      logging.debug('looking for reinforcements from home planet')
      for i in range(turn-1,-1,-1):
        ships += self.CommitFreeTroops(i, ships)
        if ships >= 0:
          self._free_troops[turn]=ships
          logging.debug('sucess! leaving commitreinforce')
          logging.debug('free troops are: '+repr(self._free_troops))
          return 1
    #check allies for help
    for i in range(1,turn+1):
      for p in self._neighbors[i]:
        for j in range(turn,i-1,-1):
          k = turn-j
          reinforcement = p.CommitFreeTroops(k, ships)
          if reinforcement > 0:
            logging.info('have some reinforcements to send! dist='+repr(i)+' turn='+repr(turn)+' k='+repr(k))
            ships += reinforcement
            if i==turn and k==0:
              logging.info('sending '+repr(reinforcement)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(i))
              launch_queue[p.PlanetID()][self._planet_id]+=reinforcement
            if ships >= 0:
              logging.debug('sucess! leaving commitreinforce')
              self._free_troops[turn]=ships
              logging.debug(repr(self._free_troops))
              return 1
    self._free_troops[turn]=ships
    logging.debug('failed! CommitReinforce')
    return 0


class PlanetWars:
  def __init__(self, gameState, turn):
    logging.info('Initializing Planet Wars')
    logging.info('Turn number '+repr(turn))
    self._planets = []
    self._fleets = []
    self.ParseGameState(gameState)
    self._distance = {}
    logging.info('initializing distance')
    self._max_distance = self.InitDistance()
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
    logging.info('done with initialization')

  def ResetReinforcements(self):
    for p in self._planets:
      p.ResetReinforcements(self._max_distance)

  def ResetNeighbors(self):
    for p in self._planets:
      p.ResetNeighbors()

  def CalcNeighbors(self, turn):
    for p in self._planets:
      p.CalcNeighbors(turn, self._max_distance)

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
    logging.info("%d %d %d\n" % \
     (source_planet, destination_planet, num_ships))
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
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
