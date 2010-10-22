#!/usr/bin/env python
#

from math import ceil, sqrt
from sys import stdout
from Fleet import Fleet
from Planet import Planet
from ACO import ACO


import logging
import Logging as L




class PlanetWars:
  def __init__(self, gameState, turn):
    self._nearest_enemy=9999999
    self._farthest_enemy=-1
    if L.INFO: logging.info('Initializing Planet Wars')
    if L.INFO: logging.info('Turn number '+repr(turn))
    self._planets = []
    self._fleets = []
    self._planet_ids = []
    self._max_regen = -1
    self.ParseGameState(gameState)
    self._distance = {}
    self._neighbors = {}
    if L.INFO: logging.info('initializing distance')
    self._max_distance = self.InitDistance()
    self._max_regen = self.InitMaxRegen()
    self.InitConnectedness()
    self.NormalizeConnectedness()
    self.ResetFreeTroops(self._max_distance)
    self.InitOwnerAndNumShips(self._max_distance)
    if L.INFO: logging.info('done with distances')
    if L.INFO: logging.info('initialiaing and calculatings neighbors')
    self.InitNeighbors()
    self.InitNeighborRegenWeights()
    if L.INFO: logging.info('initializing arrivals')
    self.InitArrivals()
    if L.INFO: logging.info('done with arrivals')
    if L.INFO: logging.info('adding new fleets')
    self.AddNewFlights()
    if L.INFO: logging.info('done with new flights')
    if L.INFO: logging.info('setting reinforcements')
    self.ResetReinforcements()
    if L.INFO: logging.info('done setting reinforcements')
    if L.INFO: logging.info('setting nearest/farthest neighbors')
    self.ResetNeighbors()
    if L.INFO: logging.info('done setting neighbors')
    if L.INFO: logging.info('setting launch queue')
    self._launch_queue = -1
    self.InitializeLaunchQueue()
    if L.DEBUG: logging.debug(repr(self._launch_queue))
    if L.INFO: logging.info('done setting launch queue')
    if L.INFO: logging.info('initilizing planet_list_list')
    self._planet_list_list = []
    if L.INFO: logging.info('done')
    if L.INFO: logging.info('initializing ACO')
    self._ACO = ACO(self._distance, self._neighbors, self._planet_ids)
    if L.INFO: logging.info('done with initialization')

  def InitOwnerAndNumShips(self, max):
    for p in self.Planets():
      p.SetOwner(p.GetOwner(0), max)
      p.SetNumShips(p.GetNumShips(0), max)



  def ResetFreeTroops(self, max):
    for p in self.Planets():
      p.ResetFreeTroops(max)

  #called after CalCOwnerAndNumShips
  def _calc_neighbors(self, planet, turn, max):
    near_enemy =999999999999
    near_ally =99999999999
    far_enemy =0
    far_ally =0
    for i in range(1,max+1):
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if p.GetOwner(turn)==2:
          if i < near_enemy: near_enemy=i
          if i > far_enemy: far_enemy=i
        elif p.GetOwner(turn)==1:
          if i < near_ally: near_ally=i
          if i > far_ally: far_ally=i
    planet.AddNearestAlly(near_ally)
    planet.AddNearestEnemy(near_enemy)
    planet.AddFarthestAlly(far_ally)
    planet.AddFarthestEnemy(far_enemy)


  def PushPlanetList(self, list_of_planets):
    self._planet_list_list.append(list_of_planets)
    
  def PopPlanetList(self):
    return self._planet_list_list.pop()


  '''
  GetSafeTabeableNeutrals searches though all the neutrals for the that are takable.
  If test_for_enemy is not given or is 0, this will search with allies as the taker,
  if test_for_enemy!=0 it will search as the enemy as the taker.
  '''
  def GetSafeTakeableNeutrals(self, turn, test_for_enemy=0):
    can_take = []
    for p in self.NeutralPlanets():
      if p.CanSafeTakeNeutral(turn, test_for_enemy):
        can_take.append(p)
    return can_take

  def CopyPlanets(self):
    new_planets = []
    for p in self._planets:
      new_planets.append(p.Copy())
    return new_planets

  def PrintPlanetSummary(self):
    if L.DEBUG: logging.debug('Printing Planet Summary!')
    for p in self._planets:
      p.PrintSummary()
    if L.DEBUG: logging.debug('DONE')


  def SetPlanets(self, list_of_planets):
    self._planets = list_of_planets

  '''
  InitConnectedness should initialize the connectedness scores of all the planets
  It must be called after initialize distance
  '''
  def InitConnectedness(self):
    if L.DEBUG: logging.debug('in InitConnectedness')
    for p in self.Planets():
      con = 0
      for o in self.Planets():
        con += (self.Distance(p.PlanetID(), o.PlanetID())**2)
      if L.DEBUG: logging.debug('setting connectedness for planet '+repr(p.PlanetID())+ ' to '+repr(con))
      p.SetConnectedness(con)

  def NormalizeConnectedness(self):
    max = 0
    for p in self.Planets():
      if p.GetConnectedness() > max:
        max = p.GetConnectedness()
    for p in self.Planets():
      p.SetConnectedness(float(p.GetConnectedness())/max)

  def InitNeighborRegenWeights(self):
    if L.DEBUG: logging.debug('in InitNeighborRegenWeights')
    max = -1
    for p in self.Planets():
      weight = 0
      divisor = 1
      for i in range(1, self.MaxDistance()):
        divisor *= 2
        for o in self.GetNeighbors(p.PlanetID(), i):
          weight += (float(o.GrowthRate())/divisor)
      p.SetNeighborWeight(weight)
      if weight > max:
        max = weight

    if L.DEBUG: logging.debug('normalizing neighbor regen weight with max='+repr(max))
    for p in self.Planets():
      p.SetNeighborWeight((p.GetNeighborWeight()/max))


  def InitializeLaunchQueue(self):
    if L.DEBUG: logging.debug('initializing launch queue')
    self._launch_queue = {}
    for p in self.Planets():
      self._launch_queue[p.PlanetID()]={}
      for o in self.Planets():
        self._launch_queue[p.PlanetID()][o.PlanetID()]=0
    if L.DEBUG: logging.debug('initialezed launch queue!')

    

  def MaxRegen(self):
    return self._max_regen

  def GetLaunch(self, p_id_source, p_id_dest):
    return self._launch_queue[p_id_source][p_id_dest]

  def AddLaunch(self, p_id_source, p_id_dest, ships):
    if int(ships)>0:
      self._launch_queue[p_id_source][p_id_dest]+=int(ships)
    else:
      if L.WARNING: logging.warning('Tried to send a non-positive amount of troops!')
      return -1

  def LaunchShips(self):
    #launch troops!
    if L.DEBUG: logging.debug('lauching ships!')
    if L.DEBUG: logging.debug(repr(self._launch_queue))
    for p in self.MyPlanets():
      to_send = 0
      for o in self.Planets():
        to_send = self._launch_queue[p.PlanetID()][o.PlanetID()]
        if to_send>0:
          if L.INFO: logging.info('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
          if L.INFO: logging.info('Planet'+repr(p.PlanetID())+'- regen: '+repr(p.GrowthRate()) + '- troops: '+repr(p.GetNumShips()))
          if L.INFO: logging.info('Planet'+repr(o.PlanetID())+'- regen: '+repr(o.GrowthRate()) + '- troops: '+repr(o.GetNumShips()))
          if L.INFO: logging.info('balls?')
          availiable = p.GetNumShips()
          if availiable >= to_send:
            p.ReduceNumShips(0, to_send)
            self.IssueOrder(p.PlanetID(),o.PlanetID(),to_send)
          elif availiable > 0:
            if L.ERROR: logging.error('BAD TROOP TRANSPORT')
            if L.ERROR: logging.error('Tried to send '+repr(to_send)+' but had '+repr(availiable))
            p.ReduceNumShips(0, availiable)
            self.IssueOrder(p.PlanetID(),o.PlanetID(),availiable)
          else:
            if L.ERROR: logging.error('somehow we have a negative amount on one of the planets.... oops?')
            if L.ERROR: logging.error('BAD TROOP TRANSPORT')
            continue
        elif to_send<0:
          if L.ERROR: logging.error('NEGATIVE AMOUNT TO SEND')
          if L.ERROR: logging.error('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
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


  def GetPlayerRegen(self, turn=0,  player = L.ALLY):
    regen = 0
    for p in self.GetPlayerPlanets(player, turn):
      regen += p.GrowthRate()
    return regen

  def GetPlayerPlanets(self, player = L.ALLY, turn=0):
    planets = []
    for p in self._planets:
      if p.GetOwner[turn]==player:
        planets.append(p)
    return planets

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
      self._calc_neighbors(p, turn, self._max_distance)
      if p.GetOwner(turn)==1:
        if p.NearestEnemy(0)<self._nearest_enemy:
          self._nearest_enemy=p.NearestEnemy(0)
        if p.FarthestEnemy(0)>self._farthest_enemy:
          self._farthest_enemy=p.FarthestEnemy(0)

  def GetNeighbors(self, p_id, dist):
    ids = self._neighbors[p_id][dist]
    to_return = []
    for id in ids:
      to_return.append(self.GetPlanet(id))
    return to_return


  def MaxDistance(self):
    return self._max_distance

  def InitNeighbors(self):
    if L.DEBUG: logging.debug('initializing arrays')
    #create the arrays
    for p in self._planets:
      self._neighbors[p.PlanetID()]={}
    if L.DEBUG: logging.debug('done '+repr(self._neighbors))

    if L.DEBUG: logging.debug('done, populating arrays')
    #populate the arrays
    for p1 in self._planets:
      for i in range(1,self.MaxDistance()+1):
        self._neighbors[p1.PlanetID()][i]=[]
      for p2 in self._planets:
        distance = self.Distance(p1.PlanetID(),p2.PlanetID())
        if distance>0:
          self._neighbors[p1.PlanetID()][distance].append(p2.PlanetID())
    if L.DEBUG: logging.debug('done')

  def InitArrivals(self):
    if L.DEBUG: logging.debug('initializing arrays')
    for p in self._planets:
      p.InitArrivals(self._max_distance)
    if L.DEBUG: logging.debug('done')


  def AddNewFlights(self):
    if L.DEBUG: logging.debug('in AddNewFlights')
    for f in self._fleets:
      if L.DEBUG: logging.debug('testing for new flights')
      if L.DEBUG: logging.debug(repr(f.TurnsRemaining()+1)+'=?'+repr(f.TotalTripLength()))
      if f.TurnsRemaining()+1==f.TotalTripLength():
        if L.DEBUG: logging.debug('testing for owner')
        if f.Owner() ==1:
          if L.DEBUG: logging.debug('my fleet')
          self.GetPlanet(f.DestinationPlanet()).AddAlliedArrival(f.TurnsRemaining(), f.NumShips())
        elif f.Owner() ==2:
          if L.DEBUG: logging.debug('enemy fleet')
          self.GetPlanet(f.DestinationPlanet()).AddEnemyArrival(f.TurnsRemaining(), f.NumShips())
    if L.DEBUG: logging.debug('leaving AddNewFlights')

  def Update(self, gameState, turn):
    if L.INFO: logging.info('Updating map information for turn '+repr(turn))
    if L.DEBUG: logging.debug('updating old flight information')
    to_remove = []
    for f in self._fleets:
      if L.DEBUG: logging.debug('updating a flight')
      in_flight = f.Update()
      if L.DEBUG: logging.debug(repr(in_flight) + ' turns left for this flight')
      if not(in_flight):
        to_remove.append(f)
      if L.DEBUG: logging.debug('updated a flight!')
    for f in to_remove:
      self._fleets.remove(f)
      if L.DEBUG: logging.debug('removed flight ' + repr(f))
    if L.DEBUG: logging.debug('updated!')
    if L.DEBUG: logging.debug('updating the arrival queues')
    for p in self._planets:
      p.Update()
    if L.DEBUG: logging.debug('done')
    self.ParseGameState(gameState, 1)
    if L.DEBUG: logging.debug('there are ' + repr(len(self._planets)) + ' and ' + repr(len(self._fleets)) + ' fleets')
    if L.DEBUG: logging.debug('adding new flights')
    self.AddNewFlights()
    if L.DEBUG: logging.debug('done')
    if L.INFO: logging.info('setting reinforcements')
    self.ResetReinforcements()
    self.ResetFreeTroops(self._max_distance)
    if L.INFO: logging.info('done setting reinforcements')
    if L.INFO: logging.info('resetting nearest/farthest neighbors')
    self.ResetNeighbors()
    if L.INFO: logging.info('done resetting neighbors')
    if L.INFO: logging.info('setting launch queue')
    self._launch_queue = []
    self.InitializeLaunchQueue()
    if L.INFO: logging.info('done setting launch queue')
    if L.INFO: logging.info('sucessfully updated!')


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
    for i in range(0,len(self._planets)):
      p_id = self._planets[i].PlanetID()
      for j in range(i, len(self._planets)):
        o_id = self._planets[j].PlanetID()
        if i==j and p_id==o_id:
          self._distance[p_id][o_id]=0
        else:
          self._distance[o_id][p_id] = self._distance[p_id][o_id]
    if L.DEBUG: logging.debug('done. max is '+repr(max))
    return max

  def Distance(self, source, dest):
    return self._distance[source][dest]


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
    if L.INFO: logging.info("%d %d %d\n" % (source_planet, destination_planet, num_ships))
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
        if L.DEBUG: logging.debug('planet token')
        if len(tokens) != 6:
          return 0
        if(update):
          if L.DEBUG: logging.debug('updating planet '+repr(planet_id))
          p = self.GetPlanet(planet_id)
          if L.DEBUG: logging.debug('pulled the planet')
          p.SetOwner(int(tokens[3]), self._max_distance)
          p.SetNumShips(int(tokens[4]), self._max_distance)
          if L.DEBUG: logging.debug('done')
        else:
          self._planet_ids.append(planet_id)
          if int(tokens[5])>self._max_regen:
            self._max_regen = int(tokens[5])
          p = Planet(planet_id, # The ID of this planet
                   int(tokens[3]), # Owner
                   int(tokens[4]), # Num ships
                   int(tokens[5]), # Growth rate
                   float(tokens[1]), # X
                   float(tokens[2])) # Y
          self._planets.append(p)
        planet_id += 1

      elif tokens[0] == "F":
        if L.DEBUG: logging.debug('flight token')
        flights += 1
        if len(tokens) != 7:
          return 0
        else:
          if L.DEBUG: logging.debug('testing to add a valid flight')
          if L.DEBUG: logging.debug('update='+repr(update))
          if L.DEBUG: logging.debug(tokens[6] + '+1=?' + tokens[5])
          if not(update) or int(tokens[6])+1==int(tokens[5]):
            if L.DEBUG: logging.debug('adding a flight')
            f = Fleet(int(tokens[1]), # Owner
                  int(tokens[2]), # Num ships
                  int(tokens[3]), # Source
                  int(tokens[4]), # Destination
                  int(tokens[5]), # Total trip length
                  int(tokens[6])) # Turns remaining
            self._fleets.append(f)
            if L.DEBUG: logging.debug('done')
      else:
        return 0
    if not(flights==len(self._fleets)):
      if L.ERROR: logging.error("FLIGHT MISMANAGEDMENT!")
      if L.ERROR: logging.error('processed: '+repr(flights)+' but only have '+repr(len(self._fleets)))
      return -1
    return 1

  def FinishTurn(self):
    stdout.write("go\n")
    stdout.flush()
    