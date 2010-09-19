#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout

import logging
LOG_FILENAME = 'PlanetWars.log'
#Formatting doesn't appaer to work... it takes the thing way too long
FORMAT = "%(user)-8s:%(levelname)-8s:%(message)s"
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,filemode='w')
pw_logger = logging.getLogger('PlanetWars')

class Fleet:
  def __init__(self, owner, num_ships, source_planet, destination_planet, \
   total_trip_length, turns_remaining):
    pw_logger.debug('initializing a fleet')
    self._owner = owner
    self._num_ships = num_ships
    self._source_planet = source_planet
    self._destination_planet = destination_planet
    self._total_trip_length = total_trip_length
    self._turns_remaining = turns_remaining
    pw_logger.debug('fleet initialization successfull!')

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
    pw_logger.debug('initializing a planet')
    self._planet_id = planet_id
    self._owner = owner
    self._num_ships = num_ships
    self._growth_rate = growth_rate
    self._x = x
    self._y = y
    pw_logger.debug('initializing successful!')

  def PlanetID(self):
    return self._planet_id

  def Owner(self, new_owner=None):
    if new_owner == None:
      return self._owner
    self._owner = new_owner

  def NumShips(self, new_num_ships=None):
    pw_logger.debug('setting numships for planet ' + str(self._planet_id))
    if new_num_ships == None:
      return self._num_ships
    self._num_ships = new_num_ships
    pw_logger.debug('done')

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
  def __init__(self, gameState):
    pw_logger.info('initializing planet wars')
    self._planets = []
    self._fleets = []
    self._distances = {}
    self._max_distance = -1
    self.ParseGameState(gameState)
    self.PopulateDistances()
    pw_logger.info('initialization of planet wars completed!')

  def PopulateDistances(self):
    pw_logger.info('populating distances')
    #collects all the planet ids
    planet_ids = []
    for p in self._planets:
        planet_ids.append(p.PlanetID())
    self._distances = dict.fromkeys(planet_ids)

    pw_logger.debug('dictionary creation complete!')
    #calculates and stores all the planet distances
    numPlanets = len(planet_ids)
    for i in planet_ids:
        self._distances[i] = dict.fromkeys(planet_ids,0)
    for i in range(0,numPlanets):
        for j in range(i+1,numPlanets):
            pw_logger.debug('calculating a distance')
            distance = self.CalcDistance(self._planets[i].PlanetID(), self._planets[j].PlanetID())
            pw_logger.debug('distance is ' + str(distance))
            self._distances[i][j]=distance
            self._distances[j][i]=distance
            pw_logger.debug('done assigning distances')
            if distance > self._max_distance:
                self._max_distance = distance
    pw_logger.info('max distance is '+ str(self._max_distance))
    pw_logger.debug('distances are: '+ str(self._distances))
    pw_logger.info('populated distances!')


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
    pw_logger.debug('getting a list of my planets')
    r = []
    for p in self._planets:
      if p.Owner() != 1:
        continue
      r.append(p)
    pw_logger.debug('done')
    return r

  def NeutralPlanets(self):
    pw_logger.debug('getting a list of neutral planets')
    r = []
    for p in self._planets:
      if p.Owner() != 0:
        continue
      r.append(p)
    pw_logger.debug('done')
    return r

  def EnemyPlanets(self):
    pw_logger.debug('getting a list of enemy planets')
    r = []
    for p in self._planets:
      if p.Owner() <= 1:
        continue
      r.append(p)
    pw_logger.debug('done')
    return r

  def NotMyPlanets(self):
    pw_logger.debug('getting a list of not my planets')
    r = []
    for p in self._planets:
      if p.Owner() == 1:
        continue
      r.append(p)
    pw_logger.debug('done')
    return r

  def Fleets(self):
    return self._fleets

  def MyFleets(self):
    pw_logger.debug('getting a list of my fleets!')
    r = []
    for f in self._fleets:
      if f.Owner() != 1:
        continue
      r.append(f)
    pw_logger.debug('done!')
    return r

  def EnemyFleets(self):
    pw_logger.debug('getting a list of enemy fleets')
    r = []
    for f in self._fleets:
      if f.Owner() <= 1:
        continue
      r.append(f)
    pw_logger.debug('done!')
    return r

  def ToString(self):
    pw_logger.debug('writing game state')
    s = ''
    for p in self._planets:
      s += "P %f %f %d %d %d\n" % \
       (p.X(), p.Y(), p.Owner(), p.NumShips(), p.GrowthRate())
    for f in self._fleets:
      s += "F %d %d %d %d %d %d\n" % \
       (f.Owner(), f.NumShips(), f.SourcePlanet(), f.DestinationPlanet(), \
        f.TotalTripLength(), f.TurnsRemaining())
    pw_logger.debug('done!')
    return s

  def Distance(self,source_planet, destination_planet):
    return self._distances[source_planet][destination_planet]

  def CalcDistance(self, source_planet, destination_planet):
    pw_logger.debug('starting to calculate a distance....')
    source = self._planets[source_planet]
    destination = self._planets[destination_planet]
    dx = source.X() - destination.X()
    dy = source.Y() - destination.Y()
    pw_logger.debug('done!')
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

  def ParseGameState(self, s):
    pw_logger.info('starting to parse game state!')
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
        if len(tokens) != 6:
          return 0
        p = Planet(planet_id, # The ID of this planet
                   int(tokens[3]), # Owner
                   int(tokens[4]), # Num ships
                   int(tokens[5]), # Growth rate
                   float(tokens[1]), # X
                   float(tokens[2])) # Y
        planet_id += 1
        self._planets.append(p)
      elif tokens[0] == "F":
        if len(tokens) != 7:
          return 0
        f = Fleet(int(tokens[1]), # Owner
                  int(tokens[2]), # Num ships
                  int(tokens[3]), # Source
                  int(tokens[4]), # Destination
                  int(tokens[5]), # Total trip length
                  int(tokens[6])) # Turns remaining
        self._fleets.append(f)
      else:
        return 0
    pw_logger.info('done parsing!')
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
