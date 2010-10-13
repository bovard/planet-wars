from PlanetWars2 import PlanetWars2
from ABC import ABC
import logging as l
import Logging as L
from copy import deepcopy


class PlanetWars3(PlanetWars2):

  '''
  Reinforce2 should send id_list troops to the planet with a reinforce need
  '''

  def Reinforce2(self):
    if L.INFO: logging.info('in pw Reinforce')
    if len(self.MyPlanets(self._max_distance-1))<=1:
      return
    if L.INFO: logging.info('getting ant_ids')
    p_ids = []
    for p in self.MyPlanets(self._max_distance):
      p_ids.append(p.PlanetID())
    for p in self.MyPlanets():
      if not(p.PlanetID() in p_ids):
        p_ids.append(p.PlanetID())
    ant_network = self._ACO.GetNetwork(p_ids)

    if L.INFO: logging.info('done, starting loop')
    for p in self.MyPlanets():
      i = 1
      while i<self.MaxDistance() and p.GetForcastDemand()<0:
        for o in self.GetNeighbors(p.PlanetID(), i):
          if o.GetOwner()==1:
            forcasting = o.GetForcastingTroops(0)
            reinforcing = o.GetReinforcingTroops(0)
            avaliable = min(o.GetForcastDemand, forcasting+reinforcing)
            if avaliable > 0:
              if L.INFO: logging.info("Seding reinforcements of "+repr(avaliable)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
              self.AddLaunch(p.PlanetID(), ant_network[p.PlanetID()][o.PlanetID()], avaliable)
              if forcasting>avaliable:
                o.SetForcastingTroops(0, forcasting-avaliable)
              else:
                o.SetForcastingTroops(0,0)
                avaliable -= forcasting
                if reinforcing > avaliable:
                  o.SetReinforcingTroops(0, reinforcing - avaliable)
                else:
                  o.SetReinforcingTroops(0, 0)
        i+=1


  '''
  CommitReinforcements steps through all the enemy planets and makes sure we have enough
  troops in the area to defend against their attacks.
  This will be done after stepping through and defending where needed
  We might come back still with a negative amount which we'll have to address in the reinforce phase.
  '''
  def CommitReinforcements(self):
    if L.DEBUG: l.debug('in CommitReinforcements (PW3)')
    #reinforce against all current enemy planets
    for p in self.EnemyPlanets():
      if p.NearestAlly() < self.MaxDistance():
        for o in self.GetNeighbors(p.PlanetID(), p.NearestAlly()):
          if o.GetOwner()==L.ALLY:
            self.AllocateAlliedTroops(o, p.NearestAlly(), p.GetNumShips(), [L.FREE_TROOPS], [L.REINFORCING_TROOPS])
            break

    #reinforce against planets that the enemy will take over in the future
    for turn in range(1, int(self.MaxDistance()/2)):
      for p in self.EnemyPlanets(turn):
        if p.GetOwner(turn-1)!=L.ENEMY and p.NearestAlly() < self.MaxDistance():
          for o in self.GetNeighbors(p.PlanetID(), p.NearestAlly()):
            if o.GetOwner()==L.ALLY:
              self.AllocateAlliedTroops(o, p.NearestAlly(), p.GetNumShips(), [L.FREE_TROOPS], [L.REINFORCING_TROOPS])
              break



  def Defend(self, planet, turn):
    if L.DEBUG: l.debug("in Defend")
    if planet.GetOwner(turn-1)==L.ALLY and planet.GetFreeTroops(turn)<0 and planet.GetEnemyArrival(turn)>0:
      if L.DEBUG: l.debug("this planet needs defending!")
      to_send = planet.GetFreeTroops(turn)
      if planet.GetSelectedTroops([L.FORCASTING_TROOPS, L.FREE_TROOPS], 0, turn-1) + self.GetSpecificPlayerTroops(planet, turn, L.ALLY, [L.FORCASTING_TROOPS, L.FREE_TROOPS]) + to_send >= 0:
            self.AllocateAlliedTroops(planet, turn, to_send, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.DEFENDING_TROOPS)
            planet.SetFreeTroops(turn, 0)
            planet.AddAlliedReinforcements(turn, -1*to_send)
    if L.DEBUG: l.debug('leaving Defend')


  def AttackNeutrals(self):
    if L.DEBUG: l.debug('in AttackNeutrals')
    done = 0
    while not(done):
      done = self.AttackANeutral()
      if L.DEBUG: l.debug('finished attacking a neutral!')
    if L.DEBUG: l.debug('leaving AttackNeutrals')

  def AttackANeutral(self):
    if L.DEBUG: l.debug('in AttackANeutral')

    #choose which neturals to consider and put them in a list
    entries = []
    for p in self.NeutralPlanets():
      if self.GetControl(p, self.MaxDistance())>0 and p.GetOwner(min(p.NearestAlly(), self.MaxDistance()))!=L.ALLY:
        entries.append([p.PlanetID(), self.GetNeutralRating(p)])

    #sort the list
    if L.DEBUG: l.debug('entries completed')
    entries.sort(L.neutral_entry_compare)
    if L.DEBUG: l.debug('sorted entries: '+repr(entries))

    #attack the first entry in the list
    #for entry in entries:
    if len(entries)>0:
      entry = entries[0]
      p = self.GetPlanet(entry[0])
      if L.DEBUG: l.debug('looking at neutral planet '+repr(entry))
      if L.DEBUG: l.debug('with num_ships='+repr(p.GetNumShips())+' and regen '+repr(p.GrowthRate()))
      for i in range(1, p.NearestEnemy()):
        to_send = -1*self.GetPlayerTroops(p, i, L.ENEMY)
        to_send -= (p.GetNumShips(i)+1)
        troops = self.GetSpecificPlayerTroops(p, i, L.ALLY, [L.FORCASTING_TROOPS, L.FREE_TROOPS])
        if L.DEBUG: l.debug('we can get '+repr(troops)+' to this planet on turn '+repr(i))
        if troops + to_send >= 0:
          if L.DEBUG: l.debug('we can take it over! allocating troops')
          self.AllocateAlliedTroops(p, i, to_send, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ATTACKING_TROOPS)
          if L.DEBUG: l.debug('we allocated attacking troops')
          return 0
      return 1
    return 1


  def BeeAttackNeutrals(self):
    entries = self.GetBeeOrder()

    for entry in entries:
      if L.CRITICAL: l.critical('looking at neutral planet '+repr(entry))
      p = self.GetPlanet(entry)
      if L.CRITICAL: l.critical('with num_ships='+repr(p.GetNumShips())+' and regen '+repr(p.GrowthRate()))
      for i in range(1, self.GetGlobalNearestEnemy()):
        if self.GetSpecificControl(p, i, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ALL_TROOPS) > 0:
          to_send = -1*self.GetPlayerTroops(p, i, L.ENEMY)
          to_send -= (p.GetNumShips(i)+1)
          if self.GetSpecificPlayerTroops(p, i, L.ALLY, [L.FORCASTING_TROOPS, L.FREE_TROOPS]) + to_send >= 0:
            self.AllocateAlliedTroops(p, i, to_send, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ATTACKING_TROOPS)
            break

  def GetBeeOrder(self):
    if L.DEBUG: l.debug('in GetBeeOrder')
    num_ships = []
    owners = []
    growth_rates = []
    for p in self.Planets():
      num_ships.append(p.GetNumShips())
      if p.NearestAlly()<=p.NearestEnemy():
        owners.append(p.GetOwner())
      else:
        owners.append(L.ENEMY)
      growth_rates.append(p.GrowthRate())

    if L.DEBUG: l.debug('creating instance')
    hive = ABC(len(self._planets), self._max_distance, num_ships, owners, growth_rates, self._distance, self._neighbors)
    if L.DEBUG: l.debug('calling GetOptimalOrder')
    order = hive.GetOptimalOrder(10)
    if L.CRITICAL: l.critical('done, order = '+repr(order))
    return order


  def GetNeutralRating(self, planet):
    if L.DEBUG: l.debug('in GetNeutralRating for planet '+repr(planet.PlanetID())+' with troops = '+repr(planet.GetNumShips()) + ' and regen '+repr(planet.GrowthRate()))
    calc = float(planet.GetNumShips())/(float(planet.GrowthRate())+.0001)+planet.NearestAlly()
    if L.DEBUG: l.debug('halfway, calc= '+repr(calc))
    calc *= planet.GetConnectedness()
    if L.DEBUG: l.debug('leaving, calc = '+repr(calc))
    calc /= (float(planet.GrowthRate())+.0001)
    return calc

  def AttackEnemies(self):
    if L.DEBUG: l.debug('in AttackEnemies')
    for p in self.Planets():
      if L.DEBUG: p.PrintSummary()
      start = -1
      end = self.MaxDistance()
      for i in range(1, self.MaxDistance()+1):
        if p.GetOwner(i)==L.ENEMY and start ==-1:
          start = i
        elif p.GetOwner(i)!=L.ENEMY and start > 0 and end ==self.MaxDistance():
          end = i
          break
      if L.DEBUG: l.debug('this planet is controlled by the enemy from turn '+repr(start)+' to turn '+repr(end))
      if start != -1:
        self.AttackEnemyPlanet(p, start, end)



  def AttackEnemyPlanet(self, planet, start_turn, end_turn):
    if L.DEBUG: l.debug('attacking enemy planet '+repr(planet.PlanetID()))
    if self.GetControl(planet, min(max(planet.FarthestAlly(), planet.FarthestEnemy()), end_turn))>0:
      for i in range(start_turn, end_turn+1):
        if self.GetSpecificControl(planet, i, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ALL_TROOPS) > 0:
          to_send = -1*self.GetPlayerTroops(planet, i, L.ENEMY)
          to_send -= (planet.GetNumShips(i)+1)
          if self.GetSpecificPlayerTroops(planet, i, L.ALLY, [L.FORCASTING_TROOPS, L.FREE_TROOPS]) + to_send > 0:
            self.AllocateAlliedTroops(planet, i, to_send, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ATTACKING_TROOPS)
          return 1
      return 0




  '''
  GetPlayerTroops returns the total number of troops a player controls that can arrive
  at target planet on turn turn
  '''
  def GetPlayerTroops(self, planet, turn, player=L.ENEMY):
    if L.DEBUG: l.debug('in GetPlayerTroops with player='+repr(player)+' and turn='+repr(turn))
    troops = 0
    for dist in range(1, turn+1):
      for p in self.GetNeighbors(planet.PlanetID(), dist):
        max = 0
        for i in range(turn-dist+1):
          if p.GetOwner(i)==player and p.GetNumShips(i) > max:
            max = p.GetNumShips(i)
        if L.DEBUG: l.debug('Planet '+repr(p.PlanetID())+' can send at most '+repr(max)+" troops ")
        troops += max
    if L.DEBUG: l.debug('Leaving GetPlayerTroops with troops='+repr(troops))
    return troops

  '''
  GetSpecificPlayerTroops returns the total number of troops a player controls that can arrive
  at target planet on turn turn from the given list of list ids
  '''
  def GetSpecificPlayerTroops(self, planet, turn, player=L.ENEMY, list_of_list_ids=L.ALL):
    if L.DEBUG: l.debug('in GetPlayerSpecificTroops with player='+repr(player)+' and turn='+repr(turn))
    troops = 0
    for dist in range(1, turn+1):
      for p in self.GetNeighbors(planet.PlanetID(), dist):
        to_send = 0
        if p.GetOwner(turn-dist)==player:
          to_send = p.GetSelectedTroops(list_of_list_ids, 0, turn-dist)
        if L.DEBUG: l.debug('Planet '+repr(p.PlanetID())+' can send at most '+repr(to_send)+" troops ")
        troops += to_send
    if L.DEBUG: l.debug('Leaving GetSpecificPlayerTroops with troops='+repr(troops))
    return troops



  '''
  GetControl should return the 'Control' or the result if all planets in range would launch
  all availiable troops at planet to get there at turn
  '''
  def GetControl(self, planet, turn, player = L.ALLY):
    if L.DEBUG: l.debug('in GetControl')
    if L.DEBUG: l.debug('calculating Control for Planet '+repr(planet.PlanetID())+' on turn '+repr(turn))
    control = 0
    if planet.GetOwner(turn)!= player:
      control -= 1
      control -= planet.GetNumShips(turn)
      if L.DEBUG: l.debug('not controlled by player! controol is '+repr(control))
    else:
      control += planet.GetNumShips(turn)
      if L.DEBUG: l.debug('controlled by player! controol is '+repr(control))
    for i in range(1, turn+1):
      if planet.GetOwner(turn)==L.NEUTRAL and control > 0:
        control += planet.GrowthRate()
        if L.DEBUG: l.debug('player is in control of planet, adding regen, control is '+repr(control))
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if p.GetOwner(turn-i)==player:
          control += p.GetNumShips(turn-i)
          if L.DEBUG: l.debug('player planet detected, adding ships, control is '+repr(control))
        elif p.GetOwner(turn-i)!=player and p.GetOwner(turn-i)!=L.NEUTRAL:
          control -= p.GetNumShips(turn-i)
          if L.DEBUG: l.debug('enemy player planet detected, subtracing ships, control is '+repr(control))
    if L.DEBUG: l.debug('leaving GetControl with control = '+repr(control))
    return control


  '''
  Same as above but instead of selectioning all troops, Speicific control allows you to
  speicify which ships should be counted in the calculation
  '''
  def GetSpecificControl(self, planet, turn, ally_planet_lists_ids, enemy_planet_lists_id):
    if L.DEBUG: l.debug('in GetSpecificControl')
    control = 0
    if planet.GetOwner(turn)!=L.ALLY:
      if L.DEBUG: l.debug('Planet is not allied controlled, subtacting from control')
      control -= 1
      control -= planet.GetNumShips(turn)
      if L.DEBUG: l.debug('Control is now '+repr(control))
    else:
      control += planet.GetNumShips(turn)
      if L.DEBUG: l.debug('Allied planet, control is '+repr(control))
    if L.DEBUG: l.debug("Searching through neighbors")
    for i in range(1, turn+1):
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if p.GetOwner(turn-i)==L.ALLY:
          if L.DEBUG: l.debug('Allied neighbor deteched')
          control += p.GetSelectedTroops(ally_planet_lists_ids, 0, turn-i)
          if L.DEBUG: l.debug("control is now "+repr(control))
        elif p.GetOwner(turn-i)==L.ENEMY:
          if L.DEBUG: l.debug("Enemy neighbor detected")
          control += p.GetSelectedTroops(enemy_planet_lists_id, 0, turn-i)
          if L.DEBUG: l.debug('Control is now '+repr(control))
    if L.DEBUG: l.debug('leaving GetSpecificControl with control = '+repr(control))
    return control

  '''
  Once you have determined the amount of troops needed in a location, use AllocateTroops
  to get them there, it'll move necessary troops from source_lists to dest_list and put the
  total moved in target_list for the planet being allocated troops and add the the launch queue

  The theory should be allocate troops from planets in descending order sorting by nearest_enemy

  NOTE: ships should be the negative amount of ships needed

  This should only be called for allied allocations!
  '''
  def AllocateAlliedTroops(self, planet, turn, ships, source_lists_ids, dest_list_id, target_list_id = L.ALLIED_REINFORCEMENTS):
    if L.DEBUG: l.debug('in AllocateTroops with turn='+repr(turn)+' and ships='+repr(ships))
    if L.DEBUG: planet.PrintSummary()
    to_commit = ships

    #looking for allied planets in range of the target with max(nearest enemey)
    for dist in range(min(self.GetGlobalFarthestEnemy()+1,self.MaxDistance()),0,-1):
      if L.DEBUG: l.debug('in AllocateAlliedTroops looking for planets with nearest enemy of '+repr(dist))
      for p in self.Planets():
        distance = self.Distance(planet.PlanetID(), p.PlanetID())
        if L.DEBUG: l.debug('Looking at planet '+repr(p.PlanetID())+' '+repr(distance)+ ' units away with near='+repr(p.NearestEnemy()))
        if distance <= turn and p.NearestEnemy()== dist and (p.GetOwner(distance) == L.ALLY or (p.GetOwner(distance) == -1 and p.GetOwner(distance-1) == L.ALLY)):
          #the planet fits the criteria, start committing troops
          if L.DEBUG: l.debug('Found a candidate planet!')
          if L.DEBUG: p.PrintSummary()
          i = turn-distance
          if L.DEBUG: l.debug('i='+repr(i)+' with turn='+repr(turn)+" and dist="+repr(dist))
          while ships<0 and i>=0:
            if p.GetOwner(i)==L.ALLY:
              committed = self.CommitTroops2(p, i, ships, source_lists_ids, dest_list_id)
              if L.DEBUG: l.debug('Committed '+repr(committed)+' troops from the planet')
              if committed > 0:
                ships += committed
                if L.DEBUG: l.debug('Only '+repr(ships)+' left!')
                if i==0 and p.PlanetID()!=planet.PlanetID() and self.Distance(p.PlanetID(), planet.PlanetID())==turn:
                  if L.INFO: l.info('Seing '+repr(committed)+' troops from Planet '+repr(p.PlanetID())+' to Planet '+repr(planet.PlanetID()))
                  self.AddLaunch(p.PlanetID(), planet.PlanetID(), committed)
              elif committed < 0:
                if L.ERROR: l.error('Tried to commit a negative amount of troops from a supposedly allied owned planet!')
            i-=1
          if L.DEBUG: l.debug('Done with planet')
          if L.DEBUG: p.PrintSummary()
    if L.DEBUG: planet.PrintSummary()
    if ships >= 0:
      planet.SetSpecificTroops(target_list_id, turn, -1*to_commit + ships)
      if L.DEBUG: l.debug('leaving AllocateTroops with ships='+repr(ships)+ '(sucess)!')
      return ships
    else:
      planet.SetSpecificTroops(target_list_id, turn, -1*to_commit - ships)
      if L.ERROR: l.error('leaving AllocateTroops with ships='+repr(ships)+ '(FAILURE)!')
      return ships





  '''
  CommitTroops2 should be called when moving troops around between the possible troops queues,
  free, reinforcing, defending, a list of the source lists is taken in source_lists_ids and
  the seul destination list is taken as dest_list_id


  NOTE: This should only be called on allied planets! (but should be safe for others)
  '''
  def CommitTroops2(self, planet, turn, ships, source_lists_ids, dest_list_id, target = -1):
    if L.DEBUG: l.debug('in CommitTroops2 with turn='+repr(turn) + ' ships='+repr(ships))
    if L.DEBUG: planet.PrintSummary()

    list_source = []
    for id in source_lists_ids:
      list_source.append(planet.GetList(id))
      
    dest = planet.GetList(dest_list_id)

    #make sure there are some troops to reinforce with
    availiable=0
    for list in list_source:
      availiable += list[turn]

    if availiable!=0 and ships!=0:
      if L.DEBUG: l.debug('there are '+repr(availiable)+' ships availiable')
      left = ships + availiable
      if left * ships > 0:
        if L.DEBUG: l.debug('commiting all avaliable ships')
        #if ships left is the same sign, we have to commit everyone
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            committed += list[turn]
            list[turn]=0
        dest[turn]+=committed
        if L.DEBUG: l.debug('leaving CommitTroops2 after committing '+repr(committed) +' troops!')
        if L.DEBUG: planet.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
      else:
        #we are only going to have to commit a few
        if L.DEBUG: l.debug('only committing a few troops')
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            if abs(committed + list[turn]) >= abs(ships):
              from_list = ships + committed
              if L.DEBUG: l.debug('need to get '+repr(-1*from_list)+' from the current list '+repr(list))
              list[turn] += from_list
              dest[turn] += -1*ships
              if L.DEBUG: l.debug('leaving CommitTroops2 after committing '+repr(-1*ships) +' troops!')
              if L.DEBUG: planet.PrintSummary()
              if target!=-1:
                target[turn]=committed
              return -1*ships
            committed += list[turn]
            list[turn]=0
        if L.WARNING: l.warning('L.ERROR in the logic of CommitTroops2')
        dest[turn]+=committed
        if L.DEBUG: l.debug('leaving CommitTroops2 after committing '+repr(committed) +' troops!')
        if L.DEBUG: planet.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
    else:
      if L.DEBUG: l.debug('there were no troops here or no troops were requested')
      if L.DEBUG: l.debug('leaving CommitTroops2')
      return 0