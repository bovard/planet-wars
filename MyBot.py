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

  # (2) Find my strongest planet.
  source = -1
  source_score = -999999.0
  source_num_ships = 0
  my_planets = pw.MyPlanets()
  logging.info('initializing')
  for p in my_planets:
    score = p.NumShips()
    logging.info('checking enemy fleets')
    enemy_fleets = pw.EnemyFleets()
    logging.info('grabbed enemy fleets')
    for f in enemy_fleets:
      logging.info('enumerating...')
      if f.DestinationPlanet() == p.PlanetID():
        logging.info('changing scrore')
        score -= f.NumShips()
    logging.info('done')
    source_score = score
    source = p.PlanetID()
    source_num_ships = score

    # (3) Find the weakest enemy or neutral planet.
    logging.info('choosing target')
    
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
        if p.Owner() == 2:
          score = distance + ((p.NumShips() + enemies + distance*p.GrowthRate())/(2*p.GrowthRate()))
        if p.Owner() == 0:
          score = distance + ((p.NumShips() + enemies)/p.GrowthRate())
        if score < dest_score and enemies + p.NumShips() > allies:
          dest_score = score
          dest = p.PlanetID()
          dest_num_ships = p.NumShips()
          dest_owner = p.Owner()
          dest_enemies = enemies
          dest_growth = p.GrowthRate()
          dest_distance = distance
          dest_allies = allies

    logging.info('done')
  # (4) Send half the ships from my strongest planet to the weakest
  # planet that I do not own.
    logging.info('sending fleets')
    if source >= 0 and dest >= 0:
      to_send = 0
      if dest_owner == 2:
        to_send = int(dest_num_ships + dest_enemies - dest_allies + dest_distance*dest_growth) + 1
      if dest_owner == 0:
        to_send = dest_num_ships + dest_enemies - dest_allies + 1
      if source_num_ships > to_send and to_send > 0:
        pw.IssueOrder(source, dest, to_send)
    logging.info('done')


def main():
  map_data = ''
  while(True):
    current_line = raw_input()
    if len(current_line) >= 2 and current_line.startswith("go"):
      pw = PlanetWars(map_data)
      DoTurn(pw)
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
