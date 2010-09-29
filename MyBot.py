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
    pw.CalcNeighbors(i)
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

  logging.debug('creating attack options queue')
  attack_options = {}
  for p in pw.Planets():
    attack_options[p.PlanetID()]={}
    for i in range(pw.MaxDistance()+1):
      attack_options[p.PlanetID()][i]=0
  logging.debug('done')



  deja_attacke=[]
  logging.debug('looking for enemies to attack')
  for i in range(1,pw.MaxDistance()):
    logging.debug('turn '+repr(i))
    for p in pw.EnemyPlanets(i):
      if not(p.GetOwner(i-1)==0) and not(p.PlanetID() in deja_attacke):
        if p.CanTakeOver(i):
          p.CommitReinforce(i, p.GetFreeTroops(0,i)-1, launch_queue)
          attack_options[p.PlanetID()][i]=p.GetFreeTroops(0,i)-1
          logging.info('launched an attack!')
          logging.info('sending '+repr(p.GetFreeTroops(0,i)-1)+' troops to '+repr(p.PlanetID()))
          deja_attacke.append(p.PlanetID())
          for j in range(i+1,pw.MaxDistance()):
            troops = p.GetEnemyArrival(j)+p.GetAlliedArrival(j)
            if troops < 0:
              if p.CanReinforce(j, troops):
                p.CommitReinforce(i, troops, launch_queue)

        else:
          logging.debug("counldn't attack!")
  logging.debug('done')

#  logging.debug('holding back reinforcements')
#  for p in pw.MyPlanets():
#    i = p.CanDefend(pw.MaxDistance())
#    free = p.GetFreeTroops(0)
#    if i>0:
#      p.CommitFreeTroops(0, free-i)
#    elif i<0:
#      p.CommitFreeTroops(0, free)

  deja_attacke=[]
  logging.debug('looking for neutrals to attack')
  for i in range(1,pw.MaxDistance()):
    logging.debug('turn '+repr(i))
    for p in pw.NeutralPlanets(i):
      logging.debug('Looking at neutral planet with id='+repr(p.PlanetID()))
      if not(p in deja_attacke) and p.NearestAlly(i) < p.NearestEnemy(i) and not(p.GrowthRate()==0):
        logging.debug('first condition met')
        if (p.GetNumShips(i)/p.GrowthRate()+p.NearestAlly(i)) < p.NearestEnemy(i) and p.NearestEnemy(i)<=pw.MaxDistance():
          logging.debug('second condition met')
          if p.CanTakeOver(i):
            logging.debug('third condition met! attack!')
            logging.debug('this neutral planet has '+repr(p.GetNumShips(i))+' troops on it!')
            p.CommitReinforce(i, p.GetFreeTroops(0,i)-1-p.GetNumShips(i), launch_queue)
            logging.info('launched an attack!')
            logging.info('sending '+repr(p.GetFreeTroops(0,i)-1)+' troops to '+repr(p.PlanetID()))
            deja_attacke.append(p)

  logging.debug('done')

  logging.info('entering reinforcement phase')
  for p in pw.MyPlanets():
    logging.info('STARTING A PLANET ============='+repr(p.PlanetID()))
    if p.GetFreeTroops()>0:
      near_enemy = p.NearestEnemy()
      if near_enemy <= pw.MaxDistance():
        start_dist = int(near_enemy/2)+1
        logging.info("start_dist="+repr(start_dist))
        for i in range(start_dist,0,-1):
          logging.info('here, i='+repr(i))
          for o in o.GetNeighbors(i):
            logging.info('here2')
            if o.GetOwner(i)==1:
              logging.info('here3')
              if o.NearestEnemy(i)<=p.NearestEnemy(i) and not(p.PlanetID()==o.PlanetID()):
                logging.info('here4')
                launch_queue[p.PlanetID()][o.PlanetID()]+=p.GetFreeTroops()
                p.CommitFreeTroops(0,p.GetFreeTroops())
                logging.info('here5')

  #launch troops!
  for p in pw.MyPlanets():
    to_send = 0
    for o in pw.Planets():
      to_send = launch_queue[p.PlanetID()][o.PlanetID()]
      if to_send>0:
        logging.info('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
        logging.info('Planet'+repr(p.PlanetID())+'- regen: '+repr(p.GrowthRate()) + '- troops: '+repr(p.GetNumShips()))
        logging.info('Planet'+repr(o.PlanetID())+'- regen: '+repr(o.GrowthRate()) + '- troops: '+repr(o.GetNumShips()))
        logging.info('balls?')
        pw.IssueOrder(p.PlanetID(),o.PlanetID(),to_send)
      elif to_send<0:
        logging.critical('NEGATIVE AMOUNT TO SEND')
        logging.critical('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))


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
