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
    to_aid = []
    for p in pw.MyPlanets(i):
      logging.debug('getting requests for planet '+repr(p.PlanetID()))
      free = p.GetFreeTroops(i+1)
      logging.debug('free='+repr(free))
      if free < 0:
        logging.info('Planet'+repr(p.PlanetID())+' made a request for '+repr(free)+' on turn '+repr(i+1))
        to_aid.append(p.PlanetID())
  
    #respond to requests
      #if distance = i+1, add committed troops to send queue

    for p in pw.Planets():
      p.Reinforce(0)
    #calculate owner and number of ships
    if i<pw.MaxDistance()-1:
      logging.debug('calculating owner and numnber of ships')
      for p in pw.Planets():
        p.CalcOwnerAndNumShips(i)

  logging.debug('i should be done')

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
      logging.info('==============Starting Turn ' + repr(pw))
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
