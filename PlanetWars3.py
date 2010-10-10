from PlanetWars2 import PlanetWars2
import logging as l
import Logging as L
from copy import deepcopy


class PlanetWars3(PlanetWars2):

  


  def AttackNeutrals(self):
    if L.DEBUG: l.debug('in AttackNeutrals')
    entries = []
    for p in self.NeutralPlanets():
      if self.GetControl(p, self.MaxDistance())>0:
        entries.append([p.PlanetID(), self.GetNeutralRating(p)])

    if L.DEBUG: l.debug('entries completed')
    entries.sort(L.neutral_entry_compare)
    if L.DEBUG: l.debug('sorted entries: '+repr(entries))

    for entry in entries:
      p = self.GetPlanet(entry[0])
      for i in range(1, self.GetGlobalNearestEnemy()):
        if self.GetSpecificControl(p, i, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ALL_TROOPS) > 0:
          to_send = -1*self.GetPlayerTroops(p, i, L.ENEMY)
          to_send -= (p.GetNumShips(i)+1)
          if self.GetSpecificPlayerTroops(p, i, L.ALLY, [L.FORCASTING_TROOPS, L.FREE_TROOPS]) + to_send >= 0:
            self.AllocateAlliedTroops(p, i, to_send, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ATTACKING_TROOPS)
            break




  def GetNeutralRating(self, planet):
    calc = float(planet.GetNumShips())/planet.GrowthRate()+planet.NearestAlly()
    calc *= (1.5-planet.GetConnectedness())
    return calc

  def AttackEnemies(self):
    for p in self.Planets():
      start = -1
      end = -1
      for i in range(1, self.MaxDistance()+1):
        if p.GetOwner(i)==L.ENEMY and start ==-1:
          start = i
        elif p.GetOwner(i)!=L.ENEMY and start > 0 and end ==-1:
          end = i
      self.AttackEnemyPlanet(p, start, end)



  def AttackEnemyPlanet(self, planet, start_turn, end_turn):
    if self.GetControl(planet, end_turn)>0:
      for i in range(start_turn, end_turn+1):
        if self.GetSpecificControl(planet, i, [L.FORCASTING_TROOPS, L.FREE_TROOPS], L.ALL_TROOPS) > 0:
          to_send = -1*self.GetPlayerTroops(planet, i, L.ENEMY)
          to_send -= (planet.GetNumShips(i)+1)
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
  def GetControl(self, planet, turn):
    if L.DEBUG: l.debug('in GetControl')
    control = 0
    if planet.GetOwner(turn)!=L.ALLY:
      control -= 1
      control -= planet.GetNumShips(turn)
    else:
      control += planet.GetNumShips(turn)
    for i in range(1, turn+1):
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if p.GetOwner(turn-i)==L.ALLY:
          control += p.GetNumShips(turn-i)
        elif p.GetOwner(turn-i)==L.ENEMY:
          control -= p.GetNumShips(turn-i)
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
  def AllocateAlliedTroops(self, planet, turn, ships, source_lists_ids, dest_list_id, target_list_id=-1):
    if L.DEBUG: l.debug('in AllocateTroops with turn='+repr(turn)+' and ships='+repr(ships))
    if L.DEBUG: planet.PrintSummary()

    #looking for allied planets in range of the target with max(nearest enemey)
    for dist in range(self.GetGlobalFarthestEnemy(),0,-1):
      for p in self.Planets():
        distance = self.Distance(planet.PlanetID(), p.PlanetID())
        if distance <= turn and p.NearestEnemy()== dist and p.GetOwner(distance) == L.ALLY:
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
                
                if i==0 and p.PlanetID()!=planet.PlanetID() and self.Distance(p.PlanetID(), planet.PlanetID())==turn:
                  if L.INFO: l.info('Seing '+repr(committed)+' troops from Planet '+repr(p.PlanetID())+' to Planet '+repr(planet.PlanetID()))
                  self.AddLaunch(p.PlanetID(), planet.PlanetID(), committed)
              elif committed < 0:
                if L.ERROR: l.error('Tried to commit a negative amount of troops from a supposedly allied owned planet!')
            i-=1
          if L.DEBUG: l.debug('Done with planet')
          if L.DEBUG: p.PrintSummary()
    if L.DEBUG: l.debug('leaving AllocateTroops!')
    if L.DEBUG: planet.PrintSummary()





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