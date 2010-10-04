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

  #commits free troops for turn=turn
  #ships = # enemy ships to commit against
  # this should be called when defending against an incoming fleet
  # this should only be called from the CommitReinforce method
  # we know this is an allied planet!
  def CommitDefendingTroops(self, turn, ships):
    logging.debug('in CommitDefendingTroops with turn='+repr(turn) + ' ships='+repr(ships))
    logging.debug('With FreeTroops       '+ repr(self._free_troops))
    logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
    logging.debug('and DefendingTroops   '+ repr(self._defending_troops))

    #need to make sure there are some troops to reinforce with
    avaliable = self._free_troops[turn]+self._reinforcing_troops[turn]
    if not(avaliable==0):
      left = ships + avaliable
      # if we have to commit all the troops:
      # Note: we'll only be
      if left * ships > 0:
        ships_committed = self._free_troops[turn] + self._reinforcing_troops[turn]
        if ships_committed > 0:
          self._free_troops[turn] =0
          self._reinforcing_troops[turn] =0
          logging.debug('committing free troops to defence')
        logging.debug('leaving CommitDefendingTroops')
        logging.debug('With FreeTroops       '+ repr(self._free_troops))
        logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
        logging.debug('and DefendingTroops   '+ repr(self._defending_troops))
        return ships_committed
      # we only have to commit some of the troops!
      else:
        logging.debug('commiting defenders')
        # we're going to have to commit a few free troops
        # we need to check how many more we have to commit than the current defenders
        left= ships + self._reinforcing_troops[turn]
        if left <= 0:
          # we need to commit left free ships to defense!
          self._free_troops[turn] += left
          self._reinforcing_troops[turn] = 0
          logging.debug('leaving CommitDefendingTroops after commiting '+repr(left)+' free troops to defesne')
          logging.debug('With FreeTroops       '+ repr(self._free_troops))
          logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
          logging.debug('and DefendingTroops   '+ repr(self._defending_troops))
          return -1*ships
        else:
          # don't have to commit any free troops to defense!
          self._reinforcing_troops[turn] += ships
          logging.debug("didn't have to commit anything and leaving CommitDefendingTroops")
          logging.debug('With FreeTroops       '+ repr(self._free_troops))
          logging.debug('and ReinforcingTroops '+ repr(self._reinforcing_troops))
          logging.debug('and DefendingTroops   '+ repr(self._defending_troops))
          return -1*ships
    else:
      logging.debug('leaving CommitTroops (there was nothing to reinforce with!)')
      return 0


  #commits free troops for turn=turn
  #ships = # ships needed (negative)
  #this should be called when looking for ships to attack with
  def CommitFreeTroops(self, turn, ships):
    logging.debug('in CommitFreeTroops with turn='+repr(turn) + ' ships='+repr(ships))
    logging.debug('and with free troops = '+ repr(self._free_troops))
    #check to make sure there are some free troops to use
    if not(self._free_troops[turn]==0):
      left = ships + self._free_troops[turn]
      # if we have to commit all the troops:
      if left * ships > 0:
        ships_committed = self._free_troops[turn]
        if ships_committed > 0:
          self._free_troops[turn] -= ships_committed
        logging.debug('leaving CommitTroops')
        return ships_committed
      # we only have to commit some of the troops!
      else:
        # we're going to have to commit a few free troops
        self._free_troops[turn] += ships
        logging.debug('leaving CommitTroops')
        return -1*ships
    else:
      logging.debug('leaving CommitFreeTroops (no free troops to commit here!)')
      return 0

  #commits free troops for turn=turn
  #ships = # enemy ships to commit against
  #this should be called when looking for ships to attack with
  def CommitFreeAndReinforcingTroops(self, turn, ships):
    logging.debug('in CommitFreeAndReinforcingTroops with turn='+repr(turn) + ' ships='+repr(ships))
    logging.debug('and with free troops = '+ repr(self._free_troops))
    logging.debug('with reinforcing troo= '+ repr(self._reinforcing_troops))
    #check to make sure there are some free troops to use
    if not(self._free_troops[turn]+self._reinforcing_troops[turn]==0):
      left = ships + self._free_troops[turn] + self._reinforcing_troops[turn]
      # if we have to commit all the troops:
      if left * ships > 0:
        ships_committed = self._free_troops[turn] + self._reinforcing_troops[turn]
        if ships_committed > 0:
          self._free_troops[turn] = 0
          self._reinforcing_troops[turn] = 0
          self._reinforcing_troops[turn]= ships_committed
        logging.debug('leaving CommitFreeAndReinforcingTroops')
        return self._reinforcing_troops[turn]
      # we only have to commit some of the troops!
      else:
        # we're going to have to commit a few free troops
        if self._free_troops[turn] + ships > 0:
          self._free_troops[turn] += ships
          self._reinforcing_troops[turn] += -1*ships
        else:
          self._reinforcing_troops[turn] += self._free_troops[turn]
          self._free_troops[turn] = 0
        logging.debug('leaving CommitFreeAndReinforcingTroops')
        return -1*ships
    else:
      logging.debug('leaving CommitFreeTroops (no free troops to commit here!)')
      return 0
    return 0

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
    def_ships = ships
    if def_ships>0:
      ships += self.GetReinforcingTroops(0, turn-1)
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
        if not(r_enemy_last_seen==r_enemy):
          for i in range(r_enemy_last_seen,r_enemy):
            for p in self._neighbors[i]:
              if def_ships >= 0:
                ships += p.GetReinforcingTroops(0, turn-i)
          done = 0

          r_enemy_last_seen=r_enemy
        elif r_ally==0:
          #check oneself first
          if self._owner[turn-1]==1:
            logging.debug('looking for reinforcements from home planet')
            for i in range(turn-1,-1,-1):
              if def_ships >= 0:
                ships += self.CommitFreeTroops(i, ships)
              else:
                enforcements = self.CommitDefendingTroops(i, ships)
                ships += enforcements
                def_ships += enforcements
                self._defending_troops[i]+=enforcements
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
                if def_ships >= 0:
                  logging.debug('committing free troops')
                  enforcements = self.CommitFreeTroops(j, ships)
                  ships += enforcements
                  logging.debug('there are '+repr(ships)+' left!')
                else:
                  logging.debug('committing defending troops with j='+repr(j)+' and ships='+repr(ships))
                  enforcements = self.CommitDefendingTroops(j, ships)
                  ships += enforcements
                  def_ships += enforcements
                  self._defending_troops[j]+=enforcements
                  logging.debug('there are '+repr(ships)+' left!')
                #only launch ships if we are defening against an attack... ?
                if r_ally==turn and j==0 and enforcements>0:
                  logging.info('sending '+repr(enforcements)+' from '+repr(p.PlanetID())+' to '+repr(self._planet_id)+' a distance of '+repr(i))
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
              reinforcement = p.CommitFreeTroops(k, ships)
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
          reinforcement = p.CommitFreeAndReinforcingTroops(k, ships)
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

