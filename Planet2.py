from Planet import Planet

import logging

class Planet2(Planet):

  def PrintSummary(self):
    logging.debug('________________________________________________________________')
    logging.debug('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0]))
    logging.debug('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
    logging.debug('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
    logging.debug('Owner List      - '+repr(self._owner))
    logging.debug('FreeTroops List - '+repr(self._free_troops))
    logging.debug('Reinforcing List- '+repr(self._reinforcing_troops))
    logging.debug('Defending List  - '+repr(self._defending_troops))
    logging.debug('________________________________________________________________')
    return 0



  '''
  CommitTroops should be called when moving troops around between the possible troops queues,
  free, reinforcing, defending, a list of the source lists is taken in list_source and
  the seul destination list is taken as dest

  The target should be the allied_reinforcement_troops list from the planet calling
  CommitTroops

  NOTE: This should only be called on allied planets! (but should be safe for others)
  '''
  def CommitTroops(self, turn, ships, list_source, dest, target=-1):
    logging.debug('in CommitTroops with turn='+repr(turn) + ' ships='+repr(ships))
    self.PrintSummary()

    #make sure there are some troops to reinforce with
    availiable=0
    for list in list_source:
      availiable += list[turn]

    if availiable!=0:
      logging.debug('there are '+repr(availiable)+' ships availiable')
      left = ships + availiable
      if left * ships > 0:
        logging.debug('commiting all avaliable ships')
        #if ships left is the same sign, we have to commit everyone
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            committed += list[turn]
            list[turn]=0
        dest[turn]+=committed
        logging.debug('leaving CommitTroops after committing '+repr(committed) +' troops!')
        self.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
      else:
        #we are only going to have to commit a few
        logging.debug('only committing a few troops')
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            if abs(committed + list[turn]) >= ships:
              from_list = ships + committed
              list[turn] += from_list
              dest[turn] += -1*ships
              logging.debug('leaving CommitTroops after committing '+repr(-1*ships) +' troops!')
              self.PrintSummary()
              if target!=-1:
                target[turn]=committed
              return -1*ships
            committed += list[turn]
            list[turn]=0
        logging.warning('ERROR in the logic of CommitTroops')
        dest[turn]+=committed
        logging.debug('leaving CommitTroops after committing '+repr(committed) +' troops!')
        self.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
    else:
      logging.debug('there were no troops here to commit in the given input lists')
      logging.debug('leaving CommitTroops')
      return 0

  '''
  CanDefend should be called to see if an allied planet at turn-1 can be defended from an
  enemy fleet arriving at turn
  '''
  def CanDefend(self, turn):
    logging.debug('in CanDefend')
    self.PrintSummary()
    ships = self.GetAllTroops(turn)

    #check oneself first
    logging.debug('looking for reinforcements from home planet')
    logging.debug('Current balance of '+repr(ships)+' when trying to defend')
    ships += self.GetAllTroops(0,turn-1)
    logging.debug('Current balance of '+repr(ships)+' when trying to defend')

    #check levels on nearby planets for help
    logging.debug('looking at nearby planets for troops')
    for i in range(1,turn+1):
      logging.debug('looking '+repr(i)+' units away')
      for p in self._neighbors[i]:
        ships += p.GetFreeTroops(0,turn-i) + p.GetReinforcingTroops(0, turn-i)
        logging.debug('Current balance of '+repr(ships)+' when trying to defend')
    if ships >= 0:
      logging.debug('one can defend (leaving CanDefend)')
      return 1
    logging.debug('one cannot defend! (leaving CanDefend)')
    return 0


  '''
  CommitDefend should be called after CanDefend returns a true result
  '''
  def CommitDefend(self, turn):
    ships = self.GetAllTroops(turn)
    logging.debug('in CommitDefend')
    self.PrintSummary()
    logging.debug('there are '+repr(ships)+' left!')
    if def_ships>0:
      ships += self.GetReinforcingTroops(0, turn-1)
    #add any enemies that are too close to the planet to the reinforce request

    r_ally=0
    r_enemy=1
    done = 0
    while (r_ally<=turn or r_enemy<=turn) and not(done):
      logging.debug('top of main loop')
      done = 1
      while ships<0 and r_ally<=turn:
        logging.debug('top of allied loop with r_ally='+repr(r_ally))
        if r_ally==0:
          #check oneself first
          if self._owner[turn-1]==1:
            logging.debug('looking for reinforcements from home planet')
            for i in range(turn-1,-1,-1):
              ships += self.CommitTroops(i, ships, [self._free_troops, self._reinforcing_troops], self._defending_troops, self._allied_reinforcements)
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
                logging.debug('committing free troops')
                enforcements = p.CommitTroops(j, ships, [p.FreeTroops(), p.ReinforcingTroops()], p.DefendingTroops(), self._allied_reinforcements)
                ships += enforcements
                logging.debug('there are '+repr(ships)+' left!')

                #launch defending troops in necessary
                if r_ally==turn and j==0 and enforcements>0:
                  logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(r_ally))
                  self._launch_queue[p.PlanetID()][self._planet_id]+=enforcements

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
      self._free_troops[turn]=ships
      logging.debug('sucess! leaving CommitDefend')
      self.PrintSummary()
      return 1
    self._free_troops[turn]=ships
    logging.debug('failed! CommitDefend')
    self.PrintSummary()
    return 0


  '''
  CanReinforce should be called on a planet on turn t, if there exists an enemy planet
  p such that distance(self,p)==t
  '''
  def CanReinforce(self, turn):
    logging.debug('in CanReinforce')
    self.PrintSummary()
    ships = self.GetFreeTroops(turn)

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
    self.PrintSummary()
    logging.debug('there are '+repr(ships)+' left!')
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
        if r_ally==0:
          #check oneself first
          if self._owner[turn-1]==1:
            logging.debug('looking for reinforcements from home planet')
            for i in range(turn,-1,-1):
              ships += self.CommitTroops(i, ships, [self._free_troops, self._reinforcing_troops], self._reinforcing_troops)
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
                logging.debug('committing free troops')
                enforcements = p.CommitTroops(j, ships, [p.FreeTroops(), p.ReinforcingTroops()], p.ReinforcingTroops())
                ships += enforcements
                logging.debug('there are '+repr(ships)+' left!')

                #do we really want to launch these????
                if r_ally==turn and j==0 and enforcements>0:
                  logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(r_ally))
                  self._launch_queue[p.PlanetID()][self._planet_id]+=enforcements

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
      self._free_troops[turn]=ships
      logging.debug('sucess! leaving commitreinforce')
      self.PrintSummary()
      return 1
    self._free_troops[turn]=ships
    logging.debug('failed! CommitReinforce')
    self.PrintSummary()
    return 0



  """
  CanSafeTakeNeutral is a function that should be used when taking over neutral planets, and
  calculates to see if one could take over the planet in a global context. It should count
  up all the Free and Reinforcing Troops and come up with the result.

  This would be called to check out the neutral if closest enemy < the nearest allies closest enemy
  """

  def CanSafeTakeNeutral(self, turn):

    logging.debug('in CanSafeTakeNeutral')
    if self._owner[turn]==0:

      ships = -1
      ships -= self._num_ships[turn]
      logging.debug('there are '+repr(ships)+' left!')

      logging.debug('checking home planet')
      free = self.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        logging.debug('large enemy force detected, changing number of ships')
        ships = free
        logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        logging.debug('there are '+repr(ships)+' left!')

      #check levels on nearby planets for help
      logging.debug('looking for reinforcements from nearby planets')
      for i in range(1,turn+1):
        logging.debug('looking '+repr(i)+' units away')
        if ships>0:
          ships+=self.GrowthRate()
        for p in self._neighbors[i]:
          ships += p.GetFreeTroops(0,turn-i) + p.GetReinforcingTroops(0, turn-i)
          logging.debug('only '+repr(ships)+' left!')

      if ships >= 0:
        logging.debug('one can TAKEOVER (leaving CanSafeTakeNeutral)')
        return 1
      logging.debug('one cannot take over! (leaving CanSafeTakeNeutral)')
      return 0
    else:
      logging.debug('tried to call CanSafeTakeNeutral on a non-neutral planet!')
      return 0


  '''
  CanTakeNeutral checks to see if there are enough ships around to take over only using
  free troops
  This will also count any enemies in the area toward the total number of ships to send
  Should be called on neutrals with nearest_enemy > clostest_ally.nearest_enemey
  '''
  def CanTakeNeutral(self, turn):
    logging.debug('in CanTakeNeutral')
    if self._owner[turn]==0:
      ships = -1

      ships -= self._num_ships[turn]
      logging.debug('there are '+repr(ships)+' left!')

      logging.debug('checking home planet')
      free = self.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        logging.debug('large enemy force detected, changing number of ships')
        ships = free
        logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        logging.debug('there are '+repr(ships)+' left!')

      #check levels on nearby planets for help
      logging.debug('looking for reinforcements from nearby planets')
      for i in range(1,turn+1):
        logging.debug('looking '+repr(i)+' units away')
        if ships>0:
          ships+=self.GrowthRate()
        for p in self._neighbors[i]:
          ships += p.GetFreeTroops(0,turn-i)
          logging.debug('only '+repr(ships)+' left!')

      if ships >= 0:
        logging.debug('one can TAKEOVER (leaving CanTakeNeutral)')
        return 1
      logging.debug('one cannot take over! (leaving CanTakeNeutral)')
      return 0
    else:
      logging.warning('CanTakeNeutral called on a non-neutral planet!')
      return 0

  '''
  CommitTakeNeutral is a function that will be used to attack any neutral planets. It
  should only be using Free Troops for this attack
  '''

  def CommitTakeNeutral(self, turn):
    if self._owner[turn]==0:
      ships = -1*(self._num_ships[turn]+1)
      logging.debug('in CommitTakeNeutral')
      logging.debug('there are '+repr(ships)+' left!')

      logging.debug('checking home planet')
      free = self.GetFreeTroops(turn)
      if free < 0 and abs(free) > abs(ships):
        logging.debug('large enemy force detected, changing number of ships')
        ships = free
        logging.debug('there are '+repr(ships)+' left!')
      elif free > 0:
        logging.debug('allied for detected, reducing number to take-over with')
        ships += free
        logging.debug('there are '+repr(ships)+' left!')

      #check allies for help
      for i in range(1,turn+1):
        if ships>0:
          ships+=self.GrowthRate()
        for p in self._neighbors[i]:
          for j in range(turn,i-1,-1):
            k = turn-j
            if p.GetOwner(k)==1:
              logging.debug('found allied planet '+repr(p.PlanetID()))
              reinforcement = p.CommitTroops(k, ships, [p.FreeTroops(), p.ReinforcingTroops()], p.ReinforcingTroops(), self._allied_reinforcements)
              ships += reinforcement
              logging.debug('there are '+repr(ships)+' left!')
              if i==turn and k==0 and reinforcement>0:
                logging.info('attacking!!!')
                logging.info('sending '+repr(reinforcement)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(i))
                self._launch_queue[p.PlanetID()][self._planet_id]+=reinforcement
            elif p.GetOwner(k)==2:
              logging.debug('found enemy planet '+repr(p.PlanetID()))
              ships += p.GetFreeTroops(k)
              logging.debug('there are '+repr(ships)+' left!')
      if ships >= 0:
        logging.debug('sucess! leaving CommitTakeNeutral')
        logging.debug(repr(self._free_troops))
        return 1
      logging.debug('failed! CommitTakeNeutral')
      return 0
    else:
      logging.warning('tried to take over an allied planet!')
      return 0

  def CanRecklessTakeOver(self, turn):
    logging.debug('in CanRecklessTakeOVer')
    ships = -1

    if self._owner[turn]==0:
      ships -= self._num_ships[turn]

    #check oneself first
    ships += self.GetFreeTroops(0,turn)
    if ships >= 0:
      logging.debug('leaving CanRecklessTakeOver (sucess! one CAN takeover)')
      return 1

    #check levels on nearby planets for help
    for i in range(1,turn+1):
      logging.debug('range of '+repr(i))
      for p in self._neighbors[i]:
        logging.debug('looking at planet '+repr(p.PlanetID())+' with troops= '+repr(p.GetNumShips()))
        ships += p.GetFreeTroops(0,turn-i) +p.GetReinforcingTroops(0, turn-i)
        if ships >= 0:
          logging.debug('leaving CanRecklessTakeOver (sucess! one CAN takeover)')
          return 1
    logging.debug('leaving CanRecklessTakeOver (cannot take over!)')
    return 0

  def CommitRecklessTakeOver(self, turn):
    logging.debug('in CommitRecklessTakeOver')
    ships = -1
    logging.debug('only '+repr(ships)+' left!')

    if not(self._owner[turn]==1):
      ships -= self._num_ships[turn]
    logging.debug('only '+repr(ships)+' left!')

    logging.debug('Enemy presence: '+repr(ships))

    #check allies for help
    logging.debug('looking at nearby planets')
    for i in range(1,turn+1):
      logging.debug('range of '+repr(i))
      for p in self._neighbors[i]:
        logging.debug('looking at planet '+repr(p.PlanetID())+' with troops= '+repr(p.GetNumShips()))
        for j in range(turn,i-1,-1):
          k = turn-j
          reinforcement = p.CommitTroops(k, ships, [p.FreeTroops(), p.ReinforcingTroops()], p.ReinforcingTroops(), self._allied_reinforcements)
          logging.debug('pulled '+repr(reinforcement)+' troops from the planet for turn '+repr(k))
          ships += reinforcement
          logging.debug('only '+repr(ships)+' left!')
          if i==turn and k==0 and reinforcement>0:
            logging.debug('sending '+repr(reinforcement)+' to Planet '+repr(self._planet_id))
            self._launch_queue[p.PlanetID()][self._planet_id]+=reinforcement
          if ships >= 0:
            self._free_troops[turn]=ships
            logging.debug('leaving CommitRecklessTakeOver (sucess!)')
            return 1
    self._free_troops[turn]=ships
    logging.debug('leaving CommitRecklessTakeOver (failure!)')
    return 0

