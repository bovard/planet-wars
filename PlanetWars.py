#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout
from Fleet import Fleet
from Planet2 import Planet2 as Planet

#import #logging
#LOG_FILENAME = 'War.log'
#logging.basicConfig(filename=LOG_FILENAME,level=#logging.DEBUG, filemode='w')







class PlanetWars:
  def __init__(self, gameState, turn):
    self._nearest_enemy=9999999
    self._farthest_enemy=-1
    #logging.info('Initializing Planet Wars')
    #logging.info('Turn number '+repr(turn))
    self._planets = []
    self._fleets = []
    self.ParseGameState(gameState)
    self._distance = {}
    #logging.info('initializing distance')
    self._max_distance = self.InitDistance()
    self._max_regen = self.InitMaxRegen()
    #logging.info('done with distances')
    #logging.info('initialiaing and calculatings neighbors')
    self.InitNeighbors()
    #logging.info('initializing arrivals')
    self.InitArrivals()
    #logging.info('done with arrivals')
    #logging.info('adding new fleets')
    self.AddNewFlights()
    #logging.info('done with new flights')
    #logging.info('setting reinforcements')
    self.ResetReinforcements()
    #logging.info('done setting reinforcements')
    #logging.info('setting nearest/farthest neighbors')
    self.ResetNeighbors()
    #logging.info('done setting neighbors')
    #logging.info('setting launch queue')
    self._launch_queue = self.InitializeLaunchQueue()
    #logging.info('done setting launch queue')
    #logging.info('done with initialization')


  def InitializeLaunchQueue(self):
    #logging.debug('initializing launch queue')
    launch_queue = {}
    for p in self.Planets():
      launch_queue[p.PlanetID()]={}
      for o in self.Planets():
        launch_queue[p.PlanetID()][o.PlanetID()]=0
    #logging.debug('initialezed launch queue!')
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
      #logging.warning('Tried to send a non-positive amount of troops!')
      return -1

  def LaunchShips(self):
    #launch troops!
    for p in self.MyPlanets():
      to_send = 0
      for o in self.Planets():
        to_send = self._launch_queue[p.PlanetID()][o.PlanetID()]
        if to_send>0:
          #logging.info('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
          #logging.info('Planet'+repr(p.PlanetID())+'- regen: '+repr(p.GrowthRate()) + '- troops: '+repr(p.GetNumShips()))
          #logging.info('Planet'+repr(o.PlanetID())+'- regen: '+repr(o.GrowthRate()) + '- troops: '+repr(o.GetNumShips()))
          #logging.info('balls?')
          availiable = p.GetNumShips()
          if availiable >= to_send:
            p.SetNumShips(availiable-to_send)
            self.IssueOrder(p.PlanetID(),o.PlanetID(),to_send)
          elif availiable > 0:
            #logging.critical('BAD TROOP TRANSPORT')
            #logging.critical('Tried to send '+repr(to_send)+' but had '+repr(availiable))
            p.SetNumShips(0)
            self.IssueOrder(p.PlanetID(),o.PlanetID(),availiable)
          else:
            #logging.critical('somehow we have a negative amount on one of the planets.... oops?')
            #logging.critical('BAD TROOP TRANSPORT')
            continue
        elif to_send<0:
          #logging.critical('NEGATIVE AMOUNT TO SEND')
          #logging.critical('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
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
    #logging.debug('initializing arrays')
    #create the arrays
    for p in self._planets:
      p.CreateNeighbor(self._max_distance)
    #logging.debug('done, populating arrays')
    #populate the arrays
    for p1 in self._planets:
      for p2 in self._planets:
        distance = self.Distance(p1.PlanetID(),p2.PlanetID())
        if distance>0:
          p1.AddNeighbor(distance, p2)
    #logging.debug('done')

  def InitArrivals(self):
    #logging.debug('initializing arrays')
    for p in self._planets:
      p.InitArrivals(self._max_distance)
    #logging.debug('done')


  def AddNewFlights(self):
    #logging.debug('in AddNewFlights')
    for f in self._fleets:
      #logging.debug('testing for new flights')
      #logging.debug(repr(f.TurnsRemaining()+1)+'=?'+repr(f.TotalTripLength()))
      if f.TurnsRemaining()+1==f.TotalTripLength():
        #logging.debug('testing for owner')
        if f.Owner() ==1:
          #logging.debug('my fleet')
          self.GetPlanet(f.DestinationPlanet()).AddAlliedArrival(f.TurnsRemaining(), f.NumShips())
        elif f.Owner() ==2:
          #logging.debug('enemy fleet')
          self.GetPlanet(f.DestinationPlanet()).AddEnemyArrival(f.TurnsRemaining(), f.NumShips())
    #logging.debug('leaving AddNewFlights')

  def Update(self, gameState, turn):
    #logging.info('Updating map information for turn '+repr(turn))
    #logging.debug('updating old flight information')
    to_remove = []
    for f in self._fleets:
      #logging.debug('updating a flight')
      in_flight = f.Update()
      #logging.debug(repr(in_flight) + ' turns left for this flight')
      if not(in_flight):
        to_remove.append(f)
      #logging.debug('updated a flight!')
    for f in to_remove:
      self._fleets.remove(f)
      #logging.debug('removed flight ' + repr(f))
    #logging.debug('updated!')
    #logging.debug('updating the arrival queues')
    for p in self._planets:
      p.Update()
    #logging.debug('done')
    self.ParseGameState(gameState, 1)
    #logging.debug('there are ' + repr(len(self._planets)) + ' and ' + repr(len(self._fleets)) + ' fleets')
    #logging.debug('adding new flights')
    self.AddNewFlights()
    #logging.debug('done')
    #logging.info('setting reinforcements')
    self.ResetReinforcements()
    #logging.info('done setting reinforcements')
    #logging.info('resetting nearest/farthest neighbors')
    self.ResetNeighbors()
    #logging.info('done resetting neighbors')
    #logging.info('setting launch queue')
    self._launch_queue = self.InitializeLaunchQueue()
    #logging.info('done setting launch queue')
    #logging.info('sucessfully updated!')


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
    #logging.debug('done. max is '+repr(max))
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
    #logging.info("%d %d %d\n" % (source_planet, destination_planet, num_ships))
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
        #logging.debug('planet token')
        if len(tokens) != 6:
          return 0
        if(update):
          #logging.debug('updating planet '+repr(planet_id))
          p = self.GetPlanet(planet_id)
          #logging.debug('pulled the planet')
          p.SetOwner(int(tokens[3]))
          p.SetNumShips(int(tokens[4]))
          p.ResetFreeTroops()
          #logging.debug('done')
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
        #logging.debug('flight token')
        flights += 1
        if len(tokens) != 7:
          return 0
        else:
          #logging.debug('testing to add a valid flight')
          #logging.debug('update='+repr(update))
          #logging.debug(tokens[6] + '+1=?' + tokens[5])
          if not(update) or int(tokens[6])+1==int(tokens[5]):
            #logging.debug('adding a flight')
            f = Fleet(int(tokens[1]), # Owner
                  int(tokens[2]), # Num ships
                  int(tokens[3]), # Source
                  int(tokens[4]), # Destination
                  int(tokens[5]), # Total trip length
                  int(tokens[6])) # Turns remaining
            self._fleets.append(f)
            #logging.debug('done')
      else:
        return 0
    if not(flights==len(self._fleets)):
      #logging.critical("FLIGHT MISMANAGEDMENT!")
      #logging.critical('processed: '+repr(flights)+' but only have '+repr(len(self._fleets)))
      return -1
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
    