from PlanetWars import PlanetWars
from copy import deepcopy
import logging
import Logging as L
from copy import deepcopy


class PlanetWars2(PlanetWars):

  def Reinforce(self):
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





  def GetControl(self, planet, turn):
    control = 0
    if planet.GetOwner(turn)!=2:
      control -= 1
      control -= planet.GetNumShips(turn)
    for i in range(1, turn):
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if planet.GetOwner(turn-i)==1:
          control += planet.GetNumShips(turn-i)
        elif planet.GetOwner(turn-i)==2:
          control += planet.GetNumShips(turn-i)
    return control


  '''
  CanDefend should be called to see if an allied planet at turn-1 can be defended from an
  enemy fleet arriving at turn
  '''
  def CanDefend(self, planet, turn):
    if L.DEBUG: logging.debug('in CanDefend')
    if L.DEBUG: planet.PrintSummary()
    ships = 0

    #check oneself first
    if L.DEBUG: logging.debug('looking for reinforcements from home planet')
    if L.DEBUG: logging.debug('Current balance of '+repr(ships)+' when trying to defend')
    ships += planet.GetAllTroops(0,turn)
    if L.DEBUG: logging.debug('Current balance of '+repr(ships)+' when trying to defend')

    #check levels on nearby planets for help
    if L.DEBUG: logging.debug('looking at nearby planets for troops')
    for i in range(1,turn+1):
      if L.DEBUG: logging.debug('looking '+repr(i)+' units away')
      for p in self.GetNeighbors(planet.PlanetID(), i):
        ships += p.GetFreeTroops(0,turn-i) + p.GetReinforcingTroops(0, turn-i)
        if L.DEBUG: logging.debug('Current balance of '+repr(ships)+' when trying to defend')
    if ships >= 0:
      if L.DEBUG: logging.debug('one can defend (leaving CanDefend)')
      return 1
    if L.DEBUG: logging.debug('one cannot defend! (leaving CanDefend)')
    return 0


  '''
  CommitDefend should be called after CanDefend returns a true result
  '''
  def CommitSafeTakeOver(self, planet, turn):
    ships = -1-planet.GetNumShips(turn)
    if L.DEBUG: logging.debug('in CommitSafeTakeOver')
    if L.DEBUG: planet.PrintSummary()
    if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=1
    r_enemy=1
    done = ships+1
    while (r_ally<=turn or r_enemy<=turn) and done!=ships:
      if L.DEBUG: logging.debug('top of main loop')
      done = ships
      while ships<0 and r_ally<=turn:
        if L.DEBUG: logging.debug('top of allied loop with r_ally='+repr(r_ally))
          #check allies for help
        if L.DEBUG: logging.debug('checking allies for help')
        for p in self.GetNeighbors(planet.PlanetID(), r_ally):
          if p.GetOwner(r_ally-1)==1:
            j=turn-r_ally
            while ships<0 and j>=0:
              if L.DEBUG: logging.debug('searching through planets j='+repr(j))
              if L.DEBUG: logging.debug('committing free troops')
              enforcements = self.CommitTroops(p, j, ships, [p.ForcastingTroops(), p.FreeTroops()], p.AttackingTroops())
              ships += enforcements
              if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

              #launch defending troops in necessary
              if r_ally==turn and j==0 and enforcements>0:
                if L.INFO: logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(planet.PlanetID())+' a distance of '+repr(r_ally))
                self.AddLaunch(p.PlanetID(),planet.PlanetID(),enforcements)

              j-=1
        if L.DEBUG: logging.debug('increasing allied radius')
        r_ally+=1

      while ships>=0 and r_enemy<=turn:
        if L.DEBUG: logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        for p in self.GetNeighbors(planet.PlanetID(), r_enemy):
          if p.GetOwner(r_enemy-1)==2:
            ships += p.GetAllTroops(0, turn-r_enemy)
            if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
        if L.DEBUG: logging.debug('botton of enemy loop!')
        if L.DEBUG: logging.debug('increasing enemy radius')
        r_enemy+=1
    if ships >= 0:
      planet.SetFreeTroops(turn,ships)
      if L.DEBUG: logging.debug('sucess! leaving CommitSafeTakeOver')
      if L.DEBUG: planet.PrintSummary()
      return 1
    planet.SetFreeTroops(turn,ships)
    if L.DEBUG: logging.debug('failed! CommitCommitSafeTakeOver')
    if L.DEBUG: planet.PrintSummary()
    return 0


  '''
  CommitDefend should be called after CanDefend returns a true result
  '''
  def CommitDefend(self, planet, turn):
    ships = planet.GetAllTroops(turn)
    if L.DEBUG: logging.debug('in CommitDefend')
    if L.DEBUG: planet.PrintSummary()
    if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=0
    r_enemy=1
    done = ships+1
    while (r_ally<=turn or r_enemy<=turn) and done!=ships:
      if L.DEBUG: logging.debug('top of main loop')
      done = ships
      while ships<0 and r_ally<=turn:
        if L.DEBUG: logging.debug('top of allied loop with r_ally='+repr(r_ally))
        if r_ally==0:
          #check oneself first
          if planet.GetOwner(turn-1)==1:
            if L.DEBUG: logging.debug('looking for reinforcements from home planet')
            for i in range(turn-1,-1,-1):
              ships += self.CommitTroops(planet, i, ships, [planet.ForcastingTroops(), planet.ReinforcingTroops(), planet.FreeTroops()], planet.DefendingTroops())
              if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
          if ships<0 or done==ships:
            if L.DEBUG: logging.debug('increasing allied radius')
            r_ally+=1
        else:
          #check allies for help
          if L.DEBUG: logging.debug('checking allies for help')
          for p in self.GetNeighbors(planet.PlanetID(), r_ally):
            if p.GetOwner(r_ally-1)==1:
              j=turn-r_ally
              while ships<0 and j>=0:
                if L.DEBUG: logging.debug('searching through planets j='+repr(j))
                if L.DEBUG: logging.debug('committing free troops')
                enforcements = self.CommitTroops(p, j, ships, [p.ForcastingTroops(), p.FreeTroops()], p.DefendingTroops())
                ships += enforcements
                if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

                #launch defending troops in necessary
                if r_ally==turn and j==0 and enforcements>0:
                  if L.INFO: logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(planet.PlanetID())+' a distance of '+repr(r_ally))
                  self.AddLaunch(p.PlanetID(),planet.PlanetID(),enforcements)

                j-=1
          if L.DEBUG: logging.debug('increasing allied radius')
          r_ally+=1

      while ships>=0 and r_enemy<=turn:
        if L.DEBUG: logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        for p in self.GetNeighbors(planet.PlanetID(), r_enemy):
          if p.GetOwner(r_enemy-1)==2:
            ships += p.GetAllTroops(0, turn-r_enemy)
            if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
        if L.DEBUG: logging.debug('botton of enemy loop!')
        if L.DEBUG: logging.debug('increasing enemy radius')
        r_enemy+=1
    if ships >= 0:
      planet.SetFreeTroops(turn,ships)
      if L.DEBUG: logging.debug('sucess! leaving CommitDefend')
      if L.DEBUG: planet.PrintSummary()
      return 1
    planet.SetFreeTroops(turn,ships)
    if L.DEBUG: logging.debug('failed! CommitDefend')
    if L.DEBUG: planet.PrintSummary()
    return 0


  '''
  CanReinforce should be called on a planet on turn t, if there exists an enemy planet
  p such that distance(self,p)==t
  '''
  def CanReinforce(self, planet, turn):
    if L.DEBUG: logging.debug('in CanReinforce')
    if L.DEBUG: planet.PrintSummary()
    ships = 0

    #check oneself first
    if L.DEBUG: logging.debug('looking for reinforcements from home planet')
    if L.DEBUG: logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    ships += planet.GetAllTroops(0,turn)
    if L.DEBUG: logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    #check levels on nearby planets for help
    if L.DEBUG: logging.debug('looking at nearby planets for free troops')
    for i in range(1,turn+1):
      if L.DEBUG: logging.debug('looking '+repr(i)+' units away')
      for p in self.GetNeighbors(planet.PlanetID(), i):
        ships += p.GetAllTroops(0,turn-i)
        if L.DEBUG: logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    if ships >= 0:
      if L.DEBUG: logging.debug('one can reinfroce (leaving CanReinforce)')
      return 1
    if L.DEBUG: logging.debug('one cannot reinforce! (leaving CanReinforce)')
    return 0

  def CommitReinforce(self, planet, turn, forcasting=0):
    ships = planet.GetAllTroops(turn)
    if L.DEBUG: logging.debug('in CommitReinforce')
    if L.DEBUG: planet.PrintSummary()
    if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=0
    r_enemy=1
    done = ships+1
    while (r_ally<=turn or r_enemy<=turn) and done!=ships:
      if L.DEBUG: logging.debug('top of main loop')
      done = ships
      while ships<0 and r_ally<=turn:
        if L.DEBUG: logging.debug('top of allied loop with r_ally='+repr(r_ally))
        if r_ally==0:
          #check oneself first
          if planet.GetOwner(turn-1)==1:
            if L.DEBUG: logging.debug('looking for reinforcements from home planet')
            for i in range(turn,-1,-1):
              if not(forcasting):
                ships += self.CommitTroops(planet, i, ships, [planet.ReinforcingTroops(), planet.FreeTroops()], planet.ReinforcingTroops())
              else:
                ships += self.CommitTroops(planet, i, ships, [planet.ForcastingTroops(), deepcopy(planet.ReinforcingTroops()), planet.FreeTroops()], planet.ForcastingTroops())
                planet.PullOutReinforcing()
              if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
          if ships<0 or done==ships:
            if L.DEBUG: logging.debug('increasing allied radius')
            r_ally+=1
        else:
          #check allies for help
          if L.DEBUG: logging.debug('checking allies for help')
          for p in self.GetNeighbors(planet.PlanetID(),r_ally):
            if p.GetOwner(r_ally-1)==1:
              j=turn-r_ally
              while ships<0 and j>=0:
                if L.DEBUG: logging.debug('searching through planets j='+repr(j))
                if L.DEBUG: logging.debug('committing free troops')
                if not(forcasting):
                  enforcements = self.CommitTroops(p, j, ships, [p.ReinforcingTroops(), p.FreeTroops()], p.ReinforcingTroops())
                else:
                  enforcements = self.CommitTroops(p, j, ships, [p.ForcastingTroops(), deepcopy(p.ReinforcingTroops()), p.FreeTroops()], p.ForcastingTroops())
                  p.PullOutReinforcing()
                ships += enforcements
                if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

#                #do we really want to launch these????
                if not(forcasting):
                  if r_ally==turn and j==0 and enforcements>0:
                    if L.INFO: logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(planet.PlanetID())+' a distance of '+repr(r_ally))
                    self._launch_queue[p.PlanetID()][planet.PlanetID()]+=enforcements



                j-=1
          if L.DEBUG: logging.debug('increasing allied radius')
          r_ally+=1

      while ships>=0 and r_enemy<=turn:
        if L.DEBUG: logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        for p in self.GetNeighbors(planet.PlanetID(),r_enemy):
          if p.GetOwner(r_enemy-1)==2:
            ships += p.GetAllTroops(0, turn-r_enemy)
            if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
        if L.DEBUG: logging.debug('botton of enemy loop!')
        if L.DEBUG: logging.debug('increasing enemy radius')
        r_enemy+=1
    if ships >= 0:
      if not(forcasting):
        planet.SetFreeTroops(turn,ships)
      else:
        planet.SetForcastDemand(ships)
      if L.DEBUG: logging.debug('sucess! leaving commitreinforce')
      if L.DEBUG: planet.PrintSummary()
      return 1
    if not(forcasting):
      planet.SetFreeTroops(turn,ships)
    else:
      planet.SetForcastDemand(ships)
    if L.DEBUG: logging.debug('failed! CommitReinforce')
    if L.DEBUG: planet.PrintSummary()
    return 0

  def EnemyCommitReinforce(self, planet, turn):
    ships = planet.GetAllTroops(turn)
    if L.DEBUG: logging.debug('in EnemyCommitReinforce')
    if L.DEBUG: planet.PrintSummary()
    if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

    r_enemy=0
    r_ally=1
    done = ships+1
    while (r_ally<=turn or r_enemy<=turn) and done!=ships:
      if L.DEBUG: logging.debug('top of main loop')
      done = ships
      while ships>0 and r_enemy<=turn:
        if L.DEBUG: logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        if r_enemy==0:
          #check oneself first
          if planet.GetOwner(turn-1)==2:
            if L.DEBUG: logging.debug('looking for reinforcements from home planet')
            for i in range(turn,-1,-1):
              ships += self.CommitTroops(planet, i, ships, [planet.ForcastingTroops(), planet.FreeTroops()], planet.ForcastingTroops())
              if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
          if ships<0 or ships==done:
            if L.DEBUG: logging.debug('increasing enemy radius')
            r_enemy+=1
        else:
          #check allies for help
          if L.DEBUG: logging.debug('checking enemies for help')
          for p in self.GetNeighbors(planet.PlanetID(),r_enemy):
            if p.GetOwner(r_enemy-1)==2:
              j=turn-r_enemy
              while ships>0 and j>=0:
                if L.DEBUG: logging.debug('searching through planets j='+repr(j))
                if L.DEBUG: logging.debug('committing free troops')
                enforcements = self.CommitTroops(p, j, ships, [p.ForcastingTroops(), p.FreeTroops()], p.ForcastingTroops())
                ships += enforcements
                if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
                j-=1
          if L.DEBUG: logging.debug('increasing enemy radius')
          r_enemy+=1

      while ships<=0 and r_ally<=turn:
        if L.DEBUG: logging.debug('top of ally loop with r_ally='+repr(r_ally))
        for p in self.GetNeighbors(planet.PlanetID(),r_ally):
          if p.GetOwner(r_ally-1)==1:
            ships += p.GetAllTroops(0, turn-r_ally)
            if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
        if L.DEBUG: logging.debug('botton of ally loop!')
        if L.DEBUG: logging.debug('increasing ally radius')
        r_ally+=1
    if ships < 0:
      planet.SetFreeTroops(turn,ships)
      if L.DEBUG: logging.debug('sucess! leaving EnemyCommitReinforce')
      if L.DEBUG: planet.PrintSummary()
      return 1
    planet.SetFreeTroops(turn,ships)
    if L.DEBUG: logging.debug('failed! EnemyCommitReinforce')
    if L.DEBUG: planet.PrintSummary()
    return 0


  """
  CanSafeTakeNeutral is a function that should be used when taking over neutral planets, and
  calculates to see if one could take over the planet in a global context. It should count
  up all the Free and Reinforcing Troops and come up with the result.

  This would be called to check out the neutral if closest enemy < the nearest allies closest enemy
  """

  def CanSafeTakeNeutral(self, planet, turn, test_for_enemy=0):

    if L.DEBUG: logging.debug('in CanSafeTakeNeutral')
    if planet.GetOwner(turn)==0:

      if not(test_for_enemy):
        if L.DEBUG: logging.debug('checking to see if the allies can take this neutral planet')
        ships = -1
        ships -= planet.GetNumShips(turn)
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
      else:
        if L.DEBUG: logging.debug('checking to see if the enemies can take this neutral planet')
        ships = 1
        ships += planet.GetNumShips(turn)
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

      if L.DEBUG: logging.debug('checking home planet')
      free = planet.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        if L.DEBUG: logging.debug('large enemy force detected, changing number of ships')
        if not(test_for_enemy):
          ships = free
        else:
          ships += free
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        if L.DEBUG: logging.debug('allied for detected, reducing number to take-over with')
        if not(test_for_enemy):
          ships += free
        else:
          ships = free
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

      #check levels on nearby planets for help
      if L.DEBUG: logging.debug('looking for reinforcements from nearby planets')
      for i in range(1,turn+1):
        if L.DEBUG: logging.debug('looking '+repr(i)+' units away')
        if not(test_for_enemy):
          if ships>0:
            ships+=planet.GrowthRate()
        else:
          if ships<0:
            ships-=planet.GrowthRate()
        for p in self.GetNeighbors(planet.PlanetID(), i):
          if p.GetOwner(turn-i)==1:
            ships += p.GetFreeTroops(0,turn-i)
          else:
            ships += p.GetFreeTroops(0,turn-i) + p.GetForcastingTroops(0, turn-i)
          if L.DEBUG: logging.debug('only '+repr(ships)+' left!')

      if not(test_for_enemy):
        if ships >= 0:
          if L.DEBUG: logging.debug('allies can TAKEOVER (leaving CanSafeTakeNeutral)')
          return 1
        if L.DEBUG: logging.debug('allies cannot take over! (leaving CanSafeTakeNeutral)')
        return 0
      else:
        if ships <= 0:
          if L.DEBUG: logging.debug('enemies can TAKEOVER (leaving CanSafeTakeNeutral)')
          return 1
        if L.DEBUG: logging.debug('enemies cannot take over! (leaving CanSafeTakeNeutral)')
        return 0
    else:
      if L.DEBUG: logging.debug('tried to call CanSafeTakeNeutral on a non-neutral planet!')
      return 0


  '''
  CanTakeNeutral checks to see if there are enough ships around to take over only using
  free troops
  This will also count any enemies in the area toward the total number of ships to send
  Should be called on neutrals with nearest_enemy > clostest_ally.nearest_enemey
  '''
  def CanTakeNeutral(self, planet, turn):
    if L.DEBUG: logging.debug('in CanTakeNeutral')
    if planet.GetOwner(turn)==0:
      ships = -1

      ships -= planet.GetNumShips(turn)
      if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

      if L.DEBUG: logging.debug('checking home planet')
      free = planet.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        if L.DEBUG: logging.debug('large enemy force detected, changing number of ships')
        ships = free
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        if L.DEBUG: logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

      #check levels on nearby planets for help
      if L.DEBUG: logging.debug('looking for reinforcements from nearby planets')
      for i in range(1,turn+1):
        if L.DEBUG: logging.debug('looking '+repr(i)+' units away')
        if ships>0:
          ships+=planet.GrowthRate()
        for p in self.GetNeighbors(planet.PlanetID(), i):
          ships += p.GetFreeTroops(0,turn-i)
          if L.DEBUG: logging.debug('only '+repr(ships)+' left!')

      if ships >= 0:
        if L.DEBUG: logging.debug('one can TAKEOVER (leaving CanTakeNeutral)')
        return 1
      if L.DEBUG: logging.debug('one cannot take over! (leaving CanTakeNeutral)')
      return 0
    else:
      if L.WARNING: logging.warning('CanTakeNeutral called on a non-neutral planet!')
      return 0

  '''
  CommitTakeNeutral is a function that will be used to attack any neutral planets. It
  should only be using Free Troops for this attack
  '''

  def CommitTakeNeutral(self, planet, turn, really=1):
    if planet.GetOwner(turn)==0:
      ships = -1*(planet.GetNumShips(turn)+1)
      if L.DEBUG: logging.debug('in CommitTakeNeutral')
      if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

      if L.DEBUG: logging.debug('checking home planet')
      free = planet.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        if L.DEBUG: logging.debug('large enemy force detected, changing number of ships')
        ships = free
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        if L.DEBUG: logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')

      #check allies for help
      for i in range(1,turn+1):
        if ships>0:
          ships+=planet.GrowthRate()
        for p in self.GetNeighbors(planet.PlanetID(), i):
          for j in range(turn,i-1,-1):
            k = turn-j
            if p.GetOwner(k)==1:
              if L.DEBUG: logging.debug('found allied planet '+repr(p.PlanetID()))
              reinforcement = self.CommitTroops(p, k, ships, [p.FreeTroops()], p.AttackingTroops())
              ships += reinforcement
              if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
              if i==turn and k==0 and reinforcement>0 and really:
                if L.INFO: logging.info('attacking!!!')
                if L.INFO: logging.info('sending '+repr(reinforcement)+' from '+repr(p.PlanetID())+' to '+repr(planet.PlanetID())+' a distance of '+repr(i))
                self.AddLaunch(p.PlanetID(),planet.PlanetID(),reinforcement)
            elif p.GetOwner(k)==2:
              if L.DEBUG: logging.debug('found enemy planet '+repr(p.PlanetID()))
              ships += p.GetAllTroops(k)
              if L.DEBUG: logging.debug('there are '+repr(ships)+' left!')
      if ships >= 0:
        if L.DEBUG: logging.debug('sucess! leaving CommitTakeNeutral')
        planet.SetFreeTroops(turn, planet.GetNumShips(turn)+1)
        if L.DEBUG: logging.debug(repr(planet.FreeTroops()))
        return 1
      if L.DEBUG: logging.debug('failed! CommitTakeNeutral')
      return 0
    else:
      if L.WARNING: logging.warning('tried to take over an allied planet!')
      return 0

  def CanRecklessTakeOver(self, planet, turn):
    if L.DEBUG: logging.debug('in CanRecklessTakeOVer')
    ships = -1

    if planet.GetOwner(turn)==0:
      ships -= planet._num_ships[turn]

    #check oneself first
    ships += planet.GetFreeTroops(0,turn) +planet.GetForcastingTroops(0, turn)

    #check levels on nearby planets for help
    for i in range(1,turn+1):
      if L.DEBUG: logging.debug('range of '+repr(i))
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if L.DEBUG: logging.debug('looking at planet '+repr(p.PlanetID())+' with troops= '+repr(p.GetNumShips()))
        ships += p.GetFreeTroops(0,turn-i) +p.GetForcastingTroops(0, turn-i)
    if ships >= 0:
      if L.DEBUG: logging.debug('leaving CanRecklessTakeOver (sucess! one CAN takeover)')
      return 1
    if L.DEBUG: logging.debug('leaving CanRecklessTakeOver (cannot take over!)')
    return 0

  def CommitRecklessTakeOver(self, planet, turn):
    if L.DEBUG: logging.debug('in CommitRecklessTakeOver')
    ships = -1
    if L.DEBUG: logging.debug('only '+repr(ships)+' left!')

    if not(planet.GetOwner(turn)==1):
      ships -= planet.GetNumShips(turn)
    if L.DEBUG: logging.debug('only '+repr(ships)+' left!')

    if L.DEBUG: logging.debug('Enemy presence: '+repr(ships))

    #check allies for help
    if L.DEBUG: logging.debug('looking at nearby planets')
    for i in range(1,turn+1):
      if L.DEBUG: logging.debug('range of '+repr(i))
      for p in self.GetNeighbors(planet.PlanetID(), i):
        if L.DEBUG: logging.debug('looking at planet '+repr(p.PlanetID())+' with troops= '+repr(p.GetNumShips()))
        for j in range(turn,i-1,-1):
          k = turn-j
          reinforcement = self.CommitTroops(p, k, ships, [p.FreeTroops(), p.ForcastingTroops()], p.AttackingTroops(), planet.AlliedReinforcements())
          if L.DEBUG: logging.debug('pulled '+repr(reinforcement)+' troops from the planet for turn '+repr(k))
          ships += reinforcement
          if L.DEBUG: logging.debug('only '+repr(ships)+' left!')
          if i==turn and k==0 and reinforcement>0:
            if L.DEBUG: logging.debug('sending '+repr(reinforcement)+' to Planet '+repr(planet.PlanetID()))
            self.AddLaunch(p.PlanetID(),planet.PlanetID(),reinforcement)
    if ships >= 0:
      planet.SetFreeTroops(turn,ships)
      if L.DEBUG: logging.debug('leaving CommitRecklessTakeOver (sucess!)')
      return 1
    planet.SetFreeTroops(turn,ships)
    if L.DEBUG: logging.debug('leaving CommitRecklessTakeOver (failure!)')
    return 0




  '''
  CommitTroops should be called when moving troops around between the possible troops queues,
  free, reinforcing, defending, a list of the source lists is taken in list_source and
  the seul destination list is taken as dest

  The target should be the allied_reinforcement_troops list from the planet calling
  CommitTroops

  NOTE: This should only be called on allied planets! (but should be safe for others)
  '''
  def CommitTroops(self, planet, turn, ships, list_source, dest, target=-1):
    if L.DEBUG: logging.debug('in CommitTroops with turn='+repr(turn) + ' ships='+repr(ships))
    if L.DEBUG: planet.PrintSummary()

    #make sure there are some troops to reinforce with
    availiable=0
    for list in list_source:
      availiable += list[turn]

    if availiable!=0 and ships!=0:
      if L.DEBUG: logging.debug('there are '+repr(availiable)+' ships availiable')
      left = ships + availiable
      if left * ships > 0:
        if L.DEBUG: logging.debug('commiting all avaliable ships')
        #if ships left is the same sign, we have to commit everyone
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            committed += list[turn]
            list[turn]=0
        dest[turn]+=committed
        if L.DEBUG: logging.debug('leaving CommitTroops after committing '+repr(committed) +' troops!')
        if L.DEBUG: planet.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
      else:
        #we are only going to have to commit a few
        if L.DEBUG: logging.debug('only committing a few troops')
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            if abs(committed + list[turn]) >= abs(ships):
              from_list = ships + committed
              if L.DEBUG: logging.debug('need to get '+repr(-1*from_list)+' from the current list '+repr(list))
              list[turn] += from_list
              dest[turn] += -1*ships
              if L.DEBUG: logging.debug('leaving CommitTroops after committing '+repr(-1*ships) +' troops!')
              if L.DEBUG: planet.PrintSummary()
              if target!=-1:
                target[turn]=committed
              return -1*ships
            committed += list[turn]
            list[turn]=0
        if L.WARNING: logging.warning('L.ERROR in the logic of CommitTroops')
        dest[turn]+=committed
        if L.DEBUG: logging.debug('leaving CommitTroops after committing '+repr(committed) +' troops!')
        if L.DEBUG: planet.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
    else:
      if L.DEBUG: logging.debug('there were no troops here or no troops were requested')
      if L.DEBUG: logging.debug('leaving CommitTroops')
      return 0




  def RecursiveNeutralHunter(self, turn, history=[], max=-9999999999999999, max_entry=[], depth=0):
    #clone the old planets, put the old planets in the list, then set pw on the clones
    if L.DEBUG: logging.debug('in RecursiveNeutralHunter depth = '+repr(depth))
    if L.DEBUG: logging.debug('there are '+repr(len(self._planet_list_list))+' set(s) in the queue')
    for list in self._planet_list_list:
      if L.DEBUG: logging.debug(repr(list))
      for p in list:
        p.PrintSummary()
#    if L.DEBUG: logging.debug('setting pw to the new planets')
#    if L.DEBUG: logging.debug('old planets')
#    self.PrintPlanetSummary()
#    self.SetPlanets(self.PopPlanetList())
#    if L.DEBUG: logging.debug('new planets')
#    self.PrintPlanetSummary()
#    if L.DEBUG: logging.debug('there are '+repr(len(self._planet_list_list))+' set(s) in the queue')

    if L.DEBUG: logging.debug('history '+repr(history))
    if len(history)>0:
      if history[len(history)-1][0]==-1:
        if L.DEBUG: logging.debug('dead end, returning')
        return

    if L.DEBUG: logging.debug('finding neutrals allies can take')
    neutrals_allies_can_take = []
    for planet in self.NeutralPlanets(self.MaxDistance()-1):
      if self.CanSafeTakeNeutral(planet, turn):
        for i in range(1, turn+1):
          if self.CanTakeNeutral(planet, i):
            neutrals_allies_can_take.append([planet.PlanetID(),i])
            break
    if L.DEBUG: logging.debug('Allies can take '+repr(len(neutrals_allies_can_take))+' planets:')
    for entry in neutrals_allies_can_take:
      p_id = entry[0]
      p = self.GetPlanet(p_id)
      if L.DEBUG: logging.debug('Planet '+repr(p.PlanetID())+ ' with '+repr(p.GetNumShips())+' ships and regen of '+repr(p.GrowthRate()))
      p.PrintSummary()



    if L.DEBUG: logging.debug('starting the loop')
    for i in range(-1,len(neutrals_allies_can_take)):
      if L.DEBUG: logging.debug('i='+repr(i)+' and depth = '+repr(depth))
      entry = [-1,-1]
      if i>=0:
        if L.DEBUG: logging.debug('making new planets')

        new_planets = []
        for o in self._planets:
          new_planets.append(deepcopy(o))
        if L.DEBUG: logging.debug('Planets are: ')
        if L.DEBUG: logging.debug(repr(self._planets))
        self._planet_list_list.append(self._planets)
        self._planets = new_planets
        if L.DEBUG: logging.debug('Planets now are: ')
        if L.DEBUG: logging.debug(repr(self._planets))
        if L.DEBUG: logging.debug('and list is: ')
        if L.DEBUG: logging.debug(repr(self._planet_list_list))
        if L.DEBUG: logging.debug('changed to a new set of planets')
        entry = neutrals_allies_can_take[i]
        if L.DEBUG: logging.debug('looking at entry: '+repr(entry))
        self.CommitTakeNeutral(self.GetPlanet(entry[0]), entry[1], 0)
        self.GetPlanet(entry[0]).SimulateAttack(entry[1])

      if L.DEBUG: logging.debug('calculating neutrals enemies control')
      neutrals_enemies_control = []
      for planet in self.NeutralPlanets():
        if self.CanSafeTakeNeutral(planet, turn, 1):
          neutrals_enemies_control.append(planet)

      if L.DEBUG: logging.debug('calculating netural growth rates')
      enemy_controlled_growthrate = 0
      for pl in neutrals_enemies_control:
        enemy_controlled_growthrate += pl.GrowthRate()

      if L.DEBUG: logging.debug('calcuulating my growthrate')
      my_growthrate = 0
      for pla in self.MyPlanets(turn):
        my_growthrate = pla.GrowthRate()
      if entry[0]!=-1:
        my_growthrate += self.GetPlanet(entry[0]).GrowthRate()
      for thing in history:
        if thing[0]!=-1:
          my_growthrate += self.GetPlanet(thing[0]).GrowthRate()

      if L.DEBUG: logging.debug('calculating score with '+repr(my_growthrate)+ ' - '+repr(enemy_controlled_growthrate))
      score = my_growthrate - enemy_controlled_growthrate
      if L.DEBUG: logging.debug('score='+repr(score))

      if score > max or (score == max and my_growthrate > max + enemy_controlled_growthrate):
        if L.DEBUG: logging.debug('found a new max!')
        max = score
        if L.DEBUG: logging.debug('score = '+repr(max))
        max_entry = deepcopy(history)
        max_entry.append(entry)
        if L.DEBUG: logging.debug('max_entry = '+repr(max_entry))

      if i>=0:
        if L.DEBUG: logging.debug('recursing')
        new_history = deepcopy(history)
        new_history.append(entry)
#        self.PushPlanetList(self._planets)
        self.RecursiveNeutralHunter( turn, new_history, max, max_entry, depth+1)


        if L.DEBUG: logging.debug('going back to the old planets')
        self.PrintPlanetSummary()
        self._planets = self._planet_list_list.pop()
        self.PrintPlanetSummary()
        if L.DEBUG: logging.debug('now using '+repr(self.Planets()))



    if L.DEBUG: logging.debug('done')
    return max_entry
