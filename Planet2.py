from Planet import Planet

#import #logging

class Planet2(Planet):

  def PrintSummary(self, info=0):
    if not(info):
      #logging.debug('________________________________________________________________')
      #logging.debug('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0]))
      #logging.debug('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
      #logging.debug('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
      #logging.debug('Owner List      - '+repr(self._owner))
      #logging.debug('FreeTroops List - '+repr(self._free_troops))
      #logging.debug('Reinforcing List- '+repr(self._reinforcing_troops))
      #logging.debug('Defending List  - '+repr(self._defending_troops))
      #logging.debug('Attacking List  - '+repr(self._attacking_troops))
      #logging.debug('Allied Reinforce- '+repr(self._allied_reinforcements))
      #logging.debug('________________________________________________________________')
      return 0
    else:
      #logging.info('________________________________________________________________')
      #logging.info('Planet '+repr(self._planet_id)+' with '+repr(self._num_ships[0]))
      #logging.info('With nearest '+repr(self._nearest_ally[0])+','+repr(self._nearest_enemy[0]))
      #logging.info('and furthest '+repr(self._farthest_ally[0])+','+repr(self._farthest_enemy[0]))
      #logging.info('Owner List      - '+repr(self._owner))
      #logging.info('FreeTroops List - '+repr(self._free_troops))
      #logging.info('Reinforcing List- '+repr(self._reinforcing_troops))
      #logging.info('Defending List  - '+repr(self._defending_troops))
      #logging.info('Attacking List  - '+repr(self._attacking_troops))
      #logging.info('Allied Reinforce- '+repr(self._allied_reinforcements))
      #logging.info('________________________________________________________________')
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
    #logging.debug('in CommitTroops with turn='+repr(turn) + ' ships='+repr(ships))
    self.PrintSummary()

    #make sure there are some troops to reinforce with
    availiable=0
    for list in list_source:
      availiable += list[turn]

    if availiable!=0 and ships!=0:
      #logging.debug('there are '+repr(availiable)+' ships availiable')
      left = ships + availiable
      if left * ships > 0:
        #logging.debug('commiting all avaliable ships')
        #if ships left is the same sign, we have to commit everyone
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            committed += list[turn]
            list[turn]=0
        dest[turn]+=committed
        #logging.debug('leaving CommitTroops after committing '+repr(committed) +' troops!')
        self.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
      else:
        #we are only going to have to commit a few
        #logging.debug('only committing a few troops')
        committed = 0
        for list in list_source:
          #if ships aren't of the same player, commit them
          if list[turn]*ships<0:
            if abs(committed + list[turn]) >= abs(ships):
              from_list = ships + committed
              #logging.debug('need to get '+repr(-1*from_list)+' from the current list '+repr(list))
              list[turn] += from_list
              dest[turn] += -1*ships
              #logging.debug('leaving CommitTroops after committing '+repr(-1*ships) +' troops!')
              self.PrintSummary()
              if target!=-1:
                target[turn]=committed
              return -1*ships
            committed += list[turn]
            list[turn]=0
        #logging.warning('ERROR in the logic of CommitTroops')
        dest[turn]+=committed
        #logging.debug('leaving CommitTroops after committing '+repr(committed) +' troops!')
        self.PrintSummary()
        if target!=-1:
          target[turn]=committed
        return committed
    else:
      #logging.debug('there were no troops here or no troops were requested')
      #logging.debug('leaving CommitTroops')
      return 0

