#!/usr/bin/env python
#

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own. Check out the tutorials and articles on the contest website at
// http://www.ai-contest.com/resources.
"""

import logging

from PlanetWars import PlanetWars

def DoTurn(pw):
  logging.debug('initializing launch queue')
  launch_queue = {}
  for p in pw.Planets():
    launch_queue[p.PlanetID()]={}
    for o in pw.Planets():
      launch_queue[p.PlanetID()][o.PlanetID()]=0
  logging.debug('initialezed launch queue!')

  logging.debug('starting the turn loop cycle ('+repr(pw.MaxDistance())+' turns)')
  for i in range(pw.MaxDistance()):
    logging.debug('turn loop '+repr(i))
    #calculate free troops
    logging.debug('calculating free troops')
    for p in pw.Planets():
      p.CalcFreeTroops(i+1)
    logging.debug('getting requets')
    #figure out requests
    attack_reinforcements = []
    for p in pw.MyPlanets(i):
      logging.debug('getting requests for planet '+repr(p.PlanetID()))
      free = p.GetFreeTroops(i+1)
      logging.debug('free='+repr(free))
      if free < 0:
        logging.info('Planet'+repr(p.PlanetID())+' made a request for '+repr(free)+' on turn '+repr(i+1))
        attack_reinforcements.append([p.PlanetID(),i+1,free])
  
    #respond to requests
    logging.debug('Responding to Attack Reinforcement Requests')
    if len(attack_reinforcements)>0:
      logging.debug('attack_reinforcments: '+repr(attack_reinforcements))
    for p in pw.Planets():
      if len(attack_reinforcements)>0:
        for request in attack_reinforcements:
          if request[0]==p.PlanetID():
            logging.info('reviewing a request')
            can_help = p.CanReinforce(request[1],request[2])
            logging.debug('result: '+repr(can_help))
            if can_help:
              logging.info('commiting reinforcements')
              p.CommitReinforce(request[1],request[2], launch_queue)
              logging.info('filling a request for reinforcement of '+repr(-1*request[2])+' troops')
              p.Reinforce(i+1,-1*request[2])
            else:
              p.Reinforce(i+1,0)
              logging.warning("couldn't fill a reinforcement request!")
      else:
        p.Reinforce(i+1,0)
        logging.debug('nothing to worry about here!')

    #calculate owner and number of ships
    if i<pw.MaxDistance()-1:
      logging.debug('calculating owner and numnber of ships')
      for p in pw.Planets():
        p.CalcOwnerAndNumShips(i+1)

  logging.debug('i should be done')

  #Look for a planet with free_troops still left on it
  # (2) Find my strongest planet.
  source = -1
  source_num_ships = 0
  my_planets = pw.MyPlanets()
  logging.debug('initializing attack turn')
  for p in my_planets:
    logging.debug('looking at a planet')
    logging.debug('planet '+repr(p.PlanetID()))
    score = p.GetFreeTroops(0)
    source = p.PlanetID()
    source_num_ships = score

    # (3) Find the weakest enemy or neutral planet.
    logging.debug('choosing target')

    dest_score = 99999999.0
    dest = -1
    dest_num_ships = 0
    dest_owner = -1
    dest_enemies = -1
    dest_growth = -1
    dest_distance = -1
    dest_allies = -1
    not_my_planets = pw.NotMyPlanets()
    enemy_fleets = pw.EnemyFleets()
    for p in not_my_planets:
      if p.GrowthRate() > 0:
        distance = pw.Distance(source, p.PlanetID())
        enemies = 0
        for f in enemy_fleets:
          if f.DestinationPlanet() == p.PlanetID():
            enemies = enemies + f.NumShips()
        my_fleets = pw.MyFleets()
        allies = 0
        for f in my_fleets:
          if f.DestinationPlanet() == p.PlanetID():
            allies += f.NumShips()
        if p.GetOwner() == 2:
          score = distance + ((p.NumShips() + enemies + distance*p.GrowthRate())/(2*p.GrowthRate()))
        if p.GetOwner() == 0:
          score = distance + ((p.NumShips() + enemies)/p.GrowthRate())
        if score < dest_score and enemies + p.NumShips() > allies:
          dest_score = score
          dest = p.PlanetID()
          dest_num_ships = p.NumShips()
          dest_owner = p.GetOwner()
          dest_enemies = enemies
          dest_growth = p.GrowthRate()
          dest_distance = distance
          dest_allies = allies

    logging.debug('done')
  # (4) Send half the ships from my strongest planet to the weakest
  # planet that I do not own.
    logging.debug('sending fleets')
    if source >= 0 and dest >= 0:
      to_send = 0
      if dest_owner == 2:
        to_send = int(dest_num_ships + dest_enemies - dest_allies + dest_distance*dest_growth) + 1
      if dest_owner == 0:
        to_send = dest_num_ships + dest_enemies - dest_allies + 1
      if source_num_ships > to_send and to_send > 0:
        launch_queue[source][dest] += to_send
    logging.info('done with turn')

  #launch troops!
  for p in pw.Planets():
    to_send = 0
    for o in pw.Planets():
      to_send = launch_queue[p.PlanetID()][o.PlanetID()]
      if to_send>0:
        logging.info('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
        logging.info('Planet'+repr(p.PlanetID())+'- regen: '+repr(p.GrowthRate()) + '- troops: '+repr(p.NumShips()))
        logging.info('Planet'+repr(o.PlanetID())+'- regen: '+repr(o.GrowthRate()) + '- troops: '+repr(o.NumShips()))
        pw.IssueOrder(p.PlanetID(),o.PlanetID(),to_send)


def main():
  map_data = ''
  turn = -1
  pw = -1
  while(True):
    current_line = raw_input()
    if len(current_line) >= 2 and current_line.startswith("go"):
      turn += 1
      if turn == 0:
        pw = PlanetWars(map_data, turn)
      else:
        pw.Update(map_data, turn)
      logging.info('==============')
      logging.info('==============Starting Turn ' + repr(turn))
      DoTurn(pw)
      logging.info('==============finished turn!')
      logging.info('==============')
      pw.FinishTurn()
      map_data = ''
    else:
      map_data += current_line + '\n'


if __name__ == '__main__':
  try:
    import psyco
    psyco.full()
  except ImportError:
    pass
  try:
    main()
  except KeyboardInterrupt:
    print 'ctrl-c, leaving ...'
