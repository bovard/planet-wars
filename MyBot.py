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


from PlanetWars import PlanetWars
import logging
mb_logger = logging.getLogger('MyBot')

def DoTurn(pw):
  mb_logger.info('starting your turn!')

  # (1) If we currently have a fleet in flight, just do nothing.
  mb_logger.info('checking currently fleet flights')
  if len(pw.MyFleets()) >= len(pw.MyPlanets()):
    return
  # (2) Find my strongest planet.
  mb_logger.info('finding strongest source planet')
  source = -1
  source_score = -999999.0
  source_num_ships = 0
  my_planets = pw.MyPlanets()
  for p in my_planets:
    score = float(p.NumShips())
    if score > source_score:
      source_score = score
      source = p.PlanetID()
      source_num_ships = p.NumShips()


  # (3) Find the weakest enemy or neutral planet.
  mb_logger.info('finding weaking target planet')
  dest = -1
  dest_score = 999999.0
  dest_ships = 0
  dest_growth = 0
  not_my_planets = pw.NotMyPlanets()
  my_fleets = pw.MyFleets()
  my_fleet_dest = []
  for f in my_fleets:
      my_fleet_dest.append(f.DestinationPlanet())
  for p in not_my_planets:
    score = p.NumShips()/p.GrowthRate()
    if score < dest_score and not(p.PlanetID() in my_fleet_dest):
      dest_score = score
      dest = p.PlanetID()
      dest_ships = p.NumShips()
      dest_growth = p.GrowthRate()

  # (4) Send half the ships from my strongest planet to the weakest
  # planet that I do not own.
  mb_logger.info('sending ships...')
  if source >= 0 and dest >= 0:
    distance = pw.Distance(source, dest)
    if dest_ships + (distance+1)*dest_growth +1 > source_num_ships:
        num_ships = source_num_ships
    else:
        num_ships = dest_ships + (distance+1)*dest_growth+1
    pw.IssueOrder(source, dest, num_ships)

  mb_logger.info('turn done!')


def main():
  map_data = ''
  while(True):
    current_line = raw_input()
    if len(current_line) >= 2 and current_line.startswith("go"):
      pw = PlanetWars(map_data)
      DoTurn(pw)
      mb_logger.warning('starting your turn!')
      pw.FinishTurn()
      mb_logger.warning('finished your turn!')
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
