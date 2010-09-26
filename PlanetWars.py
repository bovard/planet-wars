#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout

import logging
LOG_FILENAME = 'War.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, filemode='w')


class Fleet:
  def __init__(self, owner, num_ships, source_planet, destination_planet, total_trip_length, turns_remaining):
    self._owner = owner
    self._num_ships = num_ships
    self._source_planet = source_planet
    self._destination_planet = destination_planet
    self._total_trip_length = total_trip_length
    self._turns_remaining = turns_remaining

  def Update(self):
    self._turns_remaining -= 1
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
    self._free_troops = []
    self._allied_reinforcements=[]

  # needs to be called once at the beginning of the game (done)
  def InitArrivals(self, max):
    for i in range(max+1):
      self._allied_arrivals.append(0)
      self._enemy_arrivals.append(0)


  # this should be called before flights are processed (done)
  def Update(self):
    logging.debug('in Planet.Update() for planet ' + repr(self._planet_id))
    self._enemy_arrivals = self._enemy_arrivals[1:]
    self._enemy_arrivals.append(0)
    self._allied_arrivals = self._allied_arrivals[1:]
    self._allied_arrivals.append(0)
    logging.debug('done')

  # this should be called after troop levels are set (even when creating a planet!)(done)
  def ResetFreeTroops(self):
    self._allied_reinforcements=[]
    self._allied_reinforcements.append(0)
    self._free_troops = []
    if self._owner == 1:
      self._free_troops.append(self._num_ships)
    elif self._owner == 2:
      self._free_troops.append(-1*self._num_ships)

  # this needs to be called every turn sequentailly to work
  def CalcOwnerAndNumShips(self, turn):
    levels = [0, self._enemy_arrivals[turn], self._allied_arrivals[turn]+self._allied_reinforcements[turn]]
    levels[self._owner[turn-1]] += self._num_ships[turn-1]
    if not(owner[turn-1] == 0):
      levels[self._owner[turn-1]] += self._growth_rate
    max = -1
    for i in levels:
      if i>max:
        max = i
    if count(max)>1:
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
  def SetFreeTroops(self, turn):
    levels = [0, self._enemy_arrivals[turn], self._allied_arrivals[turn]]
    if not(owner[turn-1] == 0):
      levels[self._owner[turn-1]] += self._growth_rate
    max = -1
    for i in levels:
      if i>max:
        max = i
    owner = levels.index(max)
    if count(max)>1:
       self._free_troops.append(0)
    else:
      levels[levels.index(max)]=0
      max2 = -1
      for i in levels:
        if i>max2:
          max2=i
      if owner==1:
        self._num_ships.append(max-max2)
      elif owner==2:
        self._num_ships.append(max2-max)
      else:
        self._num_ships.append(0)


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

  def Owner(self, new_owner=None):
    if new_owner == None:
      return self._owner[0]
    self._owner = []
    self._owner.append(new_owner)

  def NumShips(self, new_num_ships=None):
    if new_num_ships == None:
      return self._num_ships[0]
    self._num_ships = []
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
    logging.info('done with initialization')
    self.InitArrivals()


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

  def Update(self, gameState, turn):
    logging.info('Updating map information for turn '+repr(turn))
    logging.debug('updating old flight information')
    for f in self._fleets:
      in_flight = f.Update()
      logging.debug(repr(in_flight) + ' turns left for this flight')
      if not(in_flight):
        self._fleets.remove(f)
        logging.debug('removed flight ' + repr(f))
      logging.debug('updated a flight!')
    logging.debug('updated!')
    logging.debug('updating the arrival queues')
    for p in self._planets:
      p.Update()
    logging.debug('done')
    self.ParseGameState(gameState, 1)
    logging.info('there are ' + repr(len(self._planets)) + ' and ' + repr(len(self._fleets)) + ' fleets')
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

  def MyPlanets(self):
    r = []
    for p in self._planets:
      if p.Owner() != 1:
        continue
      r.append(p)
    return r

  def NeutralPlanets(self):
    r = []
    for p in self._planets:
      if p.Owner() != 0:
        continue
      r.append(p)
    return r

  def EnemyPlanets(self):
    r = []
    for p in self._planets:
      if p.Owner() <= 1:
        continue
      r.append(p)
    return r

  def NotMyPlanets(self):
    r = []
    for p in self._planets:
      if p.Owner() == 1:
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
       (p.X(), p.Y(), p.Owner(), p.NumShips(), p.GrowthRate())
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
    stdout.write("%d %d %d\n" % \
     (source_planet, destination_planet, num_ships))
    stdout.flush()

  def IsAlive(self, player_id):
    for p in self._planets:
      if p.Owner() == player_id:
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
          p.Owner(int(tokens[3]))
          p.NumShips(int(tokens[4]))
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
        if len(tokens) != 7:
          return 0
        else:
          logging.debug('testing to add a valid flight')
          logging.debug('update='+repr(update))
          logging.debug(repr(int(tokens[6])+1) + '=' + repr(tokens[5]))
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
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
