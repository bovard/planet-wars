from PlanetWars import PlanetWars



class PlanetWars2(PlanetWars):


  #called after CalCOwnerAndNumShips
  def _calc_neighbors(self, planet, turn, max):
    near_enemy =999999999999
    near_ally =99999999999
    far_enemy =0
    far_ally =0
    for i in range(1,max+1):
      for p in self._neighbors[planet.PlanetID()][i]:
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


  '''
  CanDefend should be called to see if an allied planet at turn-1 can be defended from an
  enemy fleet arriving at turn
  '''
  def CanDefend(self, planet, turn):
    #logging.debug('in CanDefend')
    planet.PrintSummary()
    ships = 0

    #check oneself first
    #logging.debug('looking for reinforcements from home planet')
    #logging.debug('Current balance of '+repr(ships)+' when trying to defend')
    ships += planet.GetAllTroops(0,turn)
    #logging.debug('Current balance of '+repr(ships)+' when trying to defend')

    #check levels on nearby planets for help
    #logging.debug('looking at nearby planets for troops')
    for i in range(1,turn+1):
      #logging.debug('looking '+repr(i)+' units away')
      for p in self._neighbors[planet.PlanetID()][i]:
        ships += p.GetFreeTroops(0,turn-i) + p.GetReinforcingTroops(0, turn-i)
        #logging.debug('Current balance of '+repr(ships)+' when trying to defend')
    if ships >= 0:
      #logging.debug('one can defend (leaving CanDefend)')
      return 1
    #logging.debug('one cannot defend! (leaving CanDefend)')
    return 0


  '''
  CommitDefend should be called after CanDefend returns a true result
  '''
  def CommitDefend(self, planet, turn):
    ships = planet.GetAllTroops(turn)
    #logging.debug('in CommitDefend')
    planet.PrintSummary()
    #logging.debug('there are '+repr(ships)+' left!')
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=0
    r_enemy=1
    done = 0
    while (r_ally<=turn or r_enemy<=turn) and not(done):
      #logging.debug('top of main loop')
      done = 1
      while ships<0 and r_ally<=turn:
        #logging.debug('top of allied loop with r_ally='+repr(r_ally))
        if r_ally==0:
          #check oneself first
          if planet.GetOwner(turn-1)==1:
            #logging.debug('looking for reinforcements from home planet')
            for i in range(turn-1,-1,-1):
              ships += planet.CommitTroops(i, ships, [planet.ReinforcingTroops(), planet.FreeTroops()], planet.DefendingTroops())
              #logging.debug('there are '+repr(ships)+' left!')
          if ships<0:
            #logging.debug('increasing allied radius')
            r_ally+=1
        else:
          #check allies for help
          #logging.debug('checking allies for help')
          for p in self._neighbors[planet.PlanetID()][r_ally]:
            if p.GetOwner(r_ally-1)==1:
              j=turn-r_ally
              while ships<0 and j>=0:
                #logging.debug('searching through planets j='+repr(j))
                #logging.debug('committing free troops')
                enforcements = p.CommitTroops(j, ships, [p.ReinforcingTroops(), p.FreeTroops()], p.DefendingTroops(), planet._allied_reinforcements)
                ships += enforcements
                #logging.debug('there are '+repr(ships)+' left!')

                #launch defending troops in necessary
                if r_ally==turn and j==0 and enforcements>0:
                  #logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(planet.PlanetID())+' a distance of '+repr(r_ally))
                  self.AddLaunch(p.PlanetID(),planet.PlanetID(),enforcements)

                j-=1
          #logging.debug('increasing allied radius')
          r_ally+=1

      while ships>=0 and r_enemy<=turn:
        done = 0
        #logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        for p in self._neighbors[planet.PlanetID()][r_enemy]:
          if p.GetOwner(r_enemy-1)==2:
            ships += p.GetAllTroops(0, turn-r_enemy)
            #logging.debug('there are '+repr(ships)+' left!')
        #logging.debug('botton of enemy loop!')
        #logging.debug('increasing enemy radius')
        r_enemy+=1
    if ships >= 0:
      planet.SetFreeTroops(turn,ships)
      #logging.debug('sucess! leaving CommitDefend')
      planet.PrintSummary()
      return 1
    planet.SetFreeTroops(turn,ships)
    #logging.debug('failed! CommitDefend')
    planet.PrintSummary()
    return 0


  '''
  CanReinforce should be called on a planet on turn t, if there exists an enemy planet
  p such that distance(self,p)==t
  '''
  def CanReinforce(self, planet, turn):
    #logging.debug('in CanReinforce')
    planet.PrintSummary()
    ships = 0

    #check oneself first
    #logging.debug('looking for reinforcements from home planet')
    #logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    ships += planet.GetAllTroops(0,turn)
    #logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    #check levels on nearby planets for help
    #logging.debug('looking at nearby planets for free troops')
    for i in range(1,turn+1):
      #logging.debug('looking '+repr(i)+' units away')
      for p in self._neighbors[planet.PlanetID()][i]:
        ships += p.GetAllTroops(0,turn-i)
        #logging.debug('Current balance of '+repr(ships)+' when trying to reinforce')
    if ships >= 0:
      #logging.debug('one can reinfroce (leaving CanReinforce)')
      return 1
    #logging.debug('one cannot reinforce! (leaving CanReinforce)')
    return 0

  def CommitReinforce(self, planet, turn):
    ships = planet.GetAllTroops(turn)
    #logging.debug('in CommitReinforce')
    planet.PrintSummary()
    #logging.debug('there are '+repr(ships)+' left!')
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=0
    r_enemy=1
    done = 0
    while (r_ally<=turn or r_enemy<=turn) and not(done):
      #logging.debug('top of main loop')
      done = 1
      while ships<0 and r_ally<=turn:
        #logging.debug('top of allied loop with r_ally='+repr(r_ally))
        if r_ally==0:
          #check oneself first
          if planet.GetOwner(turn-1)==1:
            #logging.debug('looking for reinforcements from home planet')
            for i in range(turn,-1,-1):
              ships += planet.CommitTroops(i, ships, [planet.ReinforcingTroops(), planet.FreeTroops()], planet.ReinforcingTroops())
              #logging.debug('there are '+repr(ships)+' left!')
          if ships<0:
            #logging.debug('increasing allied radius')
            r_ally+=1
        else:
          #check allies for help
          #logging.debug('checking allies for help')
          for p in self._neighbors[planet.PlanetID()][r_ally]:
            if p.GetOwner(r_ally-1)==1:
              j=turn-r_ally
              while ships<0 and j>=0:
                #logging.debug('searching through planets j='+repr(j))
                #logging.debug('committing free troops')
                enforcements = p.CommitTroops(j, ships, [p.ReinforcingTroops(), p.FreeTroops()], p.ReinforcingTroops())
                ships += enforcements
                #logging.debug('there are '+repr(ships)+' left!')

#                #do we really want to launch these????
#                if r_ally==turn and j==0 and enforcements>0:
#                  #logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(r_ally))
#                  self._launch_queue[p.PlanetID()][self._planet_id]+=enforcements

                j-=1
          #logging.debug('increasing allied radius')
          r_ally+=1

      while ships>=0 and r_enemy<=turn:
        done = 0
        #logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        for p in self._neighbors[planet.PlanetID()][r_enemy]:
          if p.GetOwner(r_enemy-1)==2:
            ships += p.GetAllTroops(0, turn-r_enemy)
            #logging.debug('there are '+repr(ships)+' left!')
        #logging.debug('botton of enemy loop!')
        #logging.debug('increasing enemy radius')
        r_enemy+=1
    if ships >= 0:
      planet.SetFreeTroops(turn,ships)
      #logging.debug('sucess! leaving commitreinforce')
      planet.PrintSummary()
      return 1
    planet.SetFreeTroops(turn,ships)
    #logging.debug('failed! CommitReinforce')
    planet.PrintSummary()
    return 0

  def EnemyCommitReinforce(self, planet, turn):
    ships = planet.GetAllTroops(turn)
    #logging.debug('in EnemyCommitReinforce')
    planet.PrintSummary()
    #logging.debug('there are '+repr(ships)+' left!')

    r_enemy=0
    r_ally=1
    done = ships+1
    while (r_ally<=turn or r_enemy<=turn) and done!=ships:
      #logging.debug('top of main loop')
      done = ships
      while ships>0 and r_enemy<=turn:
        #logging.debug('top of enemy loop with r_enemy='+repr(r_enemy))
        if r_enemy==0:
          #check oneself first
          if planet.GetOwner(turn-1)==2:
            #logging.debug('looking for reinforcements from home planet')
            for i in range(turn,-1,-1):
              ships += planet.CommitTroops(i, ships, [planet.ReinforcingTroops(), planet.FreeTroops()], planet.ReinforcingTroops())
              #logging.debug('there are '+repr(ships)+' left!')
          if ships<0 or ships==done:
            #logging.debug('increasing enemy radius')
            r_enemy+=1
        else:
          #check allies for help
          #logging.debug('checking enemies for help')
          for p in self._neighbors[planet.PlanetID()][r_enemy]:
            if p.GetOwner(r_enemy-1)==2:
              j=turn-r_enemy
              while ships>0 and j>=0:
                #logging.debug('searching through planets j='+repr(j))
                #logging.debug('committing free troops')
                enforcements = p.CommitTroops(j, ships, [p.ReinforcingTroops(), p.FreeTroops()], p.ReinforcingTroops())
                ships += enforcements
                #logging.debug('there are '+repr(ships)+' left!')
                j-=1
          #logging.debug('increasing enemy radius')
          r_enemy+=1

      while ships<=0 and r_ally<=turn:
        #logging.debug('top of ally loop with r_ally='+repr(r_ally))
        for p in self._neighbors[planet.PlanetID()][r_ally]:
          if p.GetOwner(r_ally-1)==1:
            ships += p.GetAllTroops(0, turn-r_ally)
            #logging.debug('there are '+repr(ships)+' left!')
        #logging.debug('botton of ally loop!')
        #logging.debug('increasing ally radius')
        r_ally+=1
    if ships < 0:
      planet.SetFreeTroops(turn,ships)
      #logging.debug('sucess! leaving EnemyCommitReinforce')
      planet.PrintSummary()
      return 1
    planet.SetFreeTroops(turn,ships)
    #logging.debug('failed! EnemyCommitReinforce')
    planet.PrintSummary()
    return 0


  """
  CanSafeTakeNeutral is a function that should be used when taking over neutral planets, and
  calculates to see if one could take over the planet in a global context. It should count
  up all the Free and Reinforcing Troops and come up with the result.

  This would be called to check out the neutral if closest enemy < the nearest allies closest enemy
  """

  def CanSafeTakeNeutral(self, planet, turn, test_for_enemy=0):

    #logging.debug('in CanSafeTakeNeutral')
    if planet.GetOwner(turn)==0:

      if not(test_for_enemy):
        #logging.debug('checking to see if the allies can take this neutral planet')
        ships = -1
        ships -= planet.GetNumShips(turn)
        #logging.debug('there are '+repr(ships)+' left!')
      else:
        #logging.debug('checking to see if the enemies can take this neutral planet')
        ships = 1
        ships += planet.GetNumShips(turn)
        #logging.debug('there are '+repr(ships)+' left!')

      #logging.debug('checking home planet')
      free = planet.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        #logging.debug('large enemy force detected, changing number of ships')
        if not(test_for_enemy):
          ships = free
        else:
          ships += free
        #logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        #logging.debug('allied for detected, reducing number to take-over with')
        if not(test_for_enemy):
          ships += free
        else:
          ships = free
        #logging.debug('there are '+repr(ships)+' left!')

      #check levels on nearby planets for help
      #logging.debug('looking for reinforcements from nearby planets')
      for i in range(1,turn+1):
        #logging.debug('looking '+repr(i)+' units away')
        if not(test_for_enemy):
          if ships>0:
            ships+=planet.GrowthRate()
        else:
          if ships<0:
            ships-=planet.GrowthRate()
        for p in self._neighbors[planet.PlanetID()][i]:
          ships += p.GetFreeTroops(0,turn-i)
          #logging.debug('only '+repr(ships)+' left!')

      if not(test_for_enemy):
        if ships >= 0:
          #logging.debug('allies can TAKEOVER (leaving CanSafeTakeNeutral)')
          return 1
        #logging.debug('allies cannot take over! (leaving CanSafeTakeNeutral)')
        return 0
      else:
        if ships <= 0:
          #logging.debug('enemies can TAKEOVER (leaving CanSafeTakeNeutral)')
          return 1
        #logging.debug('enemies cannot take over! (leaving CanSafeTakeNeutral)')
        return 0
    else:
      #logging.debug('tried to call CanSafeTakeNeutral on a non-neutral planet!')
      return 0


  '''
  CanTakeNeutral checks to see if there are enough ships around to take over only using
  free troops
  This will also count any enemies in the area toward the total number of ships to send
  Should be called on neutrals with nearest_enemy > clostest_ally.nearest_enemey
  '''
  def CanTakeNeutral(self, planet, turn):
    #logging.debug('in CanTakeNeutral')
    if planet.GetOwner(turn)==0:
      ships = -1

      ships -= planet.GetNumShips(turn)
      #logging.debug('there are '+repr(ships)+' left!')

      #logging.debug('checking home planet')
      free = planet.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        #logging.debug('large enemy force detected, changing number of ships')
        ships = free
        #logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        #logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        #logging.debug('there are '+repr(ships)+' left!')

      #check levels on nearby planets for help
      #logging.debug('looking for reinforcements from nearby planets')
      for i in range(1,turn+1):
        #logging.debug('looking '+repr(i)+' units away')
        if ships>0:
          ships+=planet.GrowthRate()
        for p in self._neighbors[planet.PlanetID()][i]:
          ships += p.GetFreeTroops(0,turn-i)
          #logging.debug('only '+repr(ships)+' left!')

      if ships >= 0:
        #logging.debug('one can TAKEOVER (leaving CanTakeNeutral)')
        return 1
      #logging.debug('one cannot take over! (leaving CanTakeNeutral)')
      return 0
    else:
      #logging.warning('CanTakeNeutral called on a non-neutral planet!')
      return 0

  '''
  CommitTakeNeutral is a function that will be used to attack any neutral planets. It
  should only be using Free Troops for this attack
  '''

  def CommitTakeNeutral(self, planet, turn):
    if planet.GetOwner(turn)==0:
      ships = -1*(planet.GetNumShips(turn)+1)
      #logging.debug('in CommitTakeNeutral')
      #logging.debug('there are '+repr(ships)+' left!')

      #logging.debug('checking home planet')
      free = planet.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        #logging.debug('large enemy force detected, changing number of ships')
        ships = free
        #logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        #logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        #logging.debug('there are '+repr(ships)+' left!')

      #check allies for help
      for i in range(1,turn+1):
        if ships>0:
          ships+=planet.GrowthRate()
        for p in self._neighbors[planet.PlanetID()][i]:
          for j in range(turn,i-1,-1):
            k = turn-j
            if p.GetOwner(k)==1:
              #logging.debug('found allied planet '+repr(p.PlanetID()))
              reinforcement = p.CommitTroops(k, ships, [p.FreeTroops()], p.AttackingTroops(), planet.AlliedReinforcements())
              ships += reinforcement
              #logging.debug('there are '+repr(ships)+' left!')
              if i==turn and k==0 and reinforcement>0:
                #logging.info('attacking!!!')
                #logging.info('sending '+repr(reinforcement)+' from '+repr(p.PlanetID())+' to '+repr(planet.PlanetID())+' a distance of '+repr(i))
                self.AddLaunch(p.PlanetID(),planet.PlanetID(),reinforcement)
            elif p.GetOwner(k)==2:
              #logging.debug('found enemy planet '+repr(p.PlanetID()))
              ships += p.GetAllTroops(k)
              #logging.debug('there are '+repr(ships)+' left!')
      if ships >= 0:
        #logging.debug('sucess! leaving CommitTakeNeutral')
        #logging.debug(repr(planet.FreeTroops()))
        return 1
      #logging.debug('failed! CommitTakeNeutral')
      return 0
    else:
      #logging.warning('tried to take over an allied planet!')
      return 0

  def CanRecklessTakeOver(self, planet, turn):
    #logging.debug('in CanRecklessTakeOVer')
    ships = -1

    if planet.GetOwner(turn)==0:
      ships -= planet._num_ships[turn]

    #check oneself first
    ships += planet.GetFreeTroops(0,turn) +planet.GetReinforcingTroops(0, turn)
    if ships >= 0:
      #logging.debug('leaving CanRecklessTakeOver (sucess! one CAN takeover)')
      return 1

    #check levels on nearby planets for help
    for i in range(1,turn+1):
      #logging.debug('range of '+repr(i))
      for p in self._neighbors[planet.PlanetID()][i]:
        #logging.debug('looking at planet '+repr(p.PlanetID())+' with troops= '+repr(p.GetNumShips()))
        ships += p.GetFreeTroops(0,turn-i) +p.GetReinforcingTroops(0, turn-i)
        if ships >= 0:
          #logging.debug('leaving CanRecklessTakeOver (sucess! one CAN takeover)')
          return 1
    #logging.debug('leaving CanRecklessTakeOver (cannot take over!)')
    return 0

  def CommitRecklessTakeOver(self, planet, turn):
    #logging.debug('in CommitRecklessTakeOver')
    ships = -1
    #logging.debug('only '+repr(ships)+' left!')

    if not(planet.GetOwner(turn)==1):
      ships -= planet.GetNumShip(turn)
    #logging.debug('only '+repr(ships)+' left!')

    #logging.debug('Enemy presence: '+repr(ships))

    #check allies for help
    #logging.debug('looking at nearby planets')
    for i in range(1,turn+1):
      #logging.debug('range of '+repr(i))
      for p in self._neighbors[planet.PlanetID()][i]:
        #logging.debug('looking at planet '+repr(p.PlanetID())+' with troops= '+repr(p.GetNumShips()))
        for j in range(turn,i-1,-1):
          k = turn-j
          reinforcement = p.CommitTroops(k, ships, [p.ReinforcingTroops(), p.FreeTroops()], p.AttackingTroops(), planet.AlliedReinforcements())
          #logging.debug('pulled '+repr(reinforcement)+' troops from the planet for turn '+repr(k))
          ships += reinforcement
          #logging.debug('only '+repr(ships)+' left!')
          if i==turn and k==0 and reinforcement>0:
            #logging.debug('sending '+repr(reinforcement)+' to Planet '+repr(planet.PlanetID()))
            self.AddLaunch(p.PlanetID(),planet.PlanetID(),reinforcement)
          if ships >= 0:
            planet.SetFreeTroops(turn,ships)
            #logging.debug('leaving CommitRecklessTakeOver (sucess!)')
            return 1
    planet.SetFreeTroops(turn,ships)
    #logging.debug('leaving CommitRecklessTakeOver (failure!)')
    return 0


