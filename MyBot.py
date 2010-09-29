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

def InitializeLaunchQueue(pw):
  logging.debug('initializing launch queue')
  launch_queue = {}
  for p in pw.Planets():
    launch_queue[p.PlanetID()]={}
    for o in pw.Planets():
      launch_queue[p.PlanetID()][o.PlanetID()]=0
  logging.debug('initialezed launch queue!')
  return launch_queue


def MainLoop(pw, launch_queue):
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

def HoldNecessary(pw):
  logging.debug('holding back reinforcements')
  for p in pw.MyPlanets():
    if p.NearestEnemy(0)<=pw.MaxDistance():
      extra = p.CanDefend(p.NearestEnemy(0))
      free = p.GetFreeTroops(0)
      logging.info('planet '+repr(p.PlanetID())+' with extra='+repr(extra)+' and free='+repr(free))
      if extra>0 and free>extra:
        logging.info('CanDefend committing a few troops')
        i =p.CommitFreeTroops(0, extra-free)
        logging.info('committed '+repr(i)+' troops')
      elif free>0 and not(free==extra):
        logging.info('CanDefend committing all the troops')
        p.CommitFreeTroops(0, -free)

def AttackEnemies(pw, launch_queue):
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

def AttackNeutrals(pw, launch_queue):

  deja_attacke=[]
  logging.debug('looking for neutrals to attack')
  for j in range(11):
    for i in range(1,pw.MaxDistance()):
      if pw.GetRegenBalance(i) < 30:
        if pw.Planets()[0].NearestEnemy(i)<=pw.MaxDistance():
          for p in pw.NeutralPlanets(i):
            if p.GrowthRate()>0:
              calc = p.GrowthRate()/p.GetNumShips()
              if calc < j and calc >= j-1:
                logging.debug('Looking at neutral planet with id='+repr(p.PlanetID()))
                if not(p in deja_attacke) and p.NearestAlly(i) <= p.NearestEnemy(i):
                  logging.debug('first condition met')
                  #if (p.GetNumShips(i)/p.GrowthRate()+p.NearestAlly(i)) < p.NearestEnemy(i):
                  #  logging.debug('second condition met')
                  if p.CanTakeOver(i):
                    logging.debug('third condition met! attack!')
                    logging.debug('this neutral planet has '+repr(p.GetNumShips(i))+' troops on it!')
                    p.CommitReinforce(i, p.GetFreeTroops(0,i)-1-p.GetNumShips(i), launch_queue)
                    logging.info('launched an attack!')
                    logging.info('sending '+repr(p.GetFreeTroops(0,i)-1)+' troops to '+repr(p.PlanetID()))
                    deja_attacke.append(p)
                    for k in range(i,pw.MaxDistance()):
                      troops = p.GetEnemyArrival(k)+p.GetAlliedArrival(k)
                      if troops < 0:
                        if p.CanReinforce(k, troops):
                          p.CommitReinforce(k, troops, launch_queue)

  logging.debug('done')

def Reinfroce(pw, launch_queue):
  logging.info('entering reinforcement phase')
  for p in pw.MyPlanets():
    logging.debug('starting to reinforce planet'+repr(p.PlanetID()))
    if p.GetFreeTroops()>0:
      near_enemy = p.NearestEnemy()
      if near_enemy <= pw.MaxDistance():
        start_dist = int(near_enemy/2)+1
        logging.debug("start_dist="+repr(start_dist))
        for i in range(start_dist,0,-1):
          logging.debug('here, i='+repr(i))
          for o in p.GetNeighbors(i):
            logging.debug('here2')
            if o.GetOwner(i)==1:
              logging.debug('here3')
              if o.NearestEnemy(i)<=p.NearestEnemy(i) and not(p.PlanetID()==o.PlanetID()):
                logging.debug('here4')
                launch_queue[p.PlanetID()][o.PlanetID()]+=p.GetFreeTroops()
                p.CommitFreeTroops(0,p.GetFreeTroops())
                logging.debug('here5')

def LaunchShips(pw, launch_queue):
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

def DoTurn(pw):
  logging.info('-------------------Initializing the Launch Queue------------------------')
  launch_queue=InitializeLaunchQueue(pw)
  logging.info('-------------------Finished Initilizing the Launch Queue----------------')
  logging.info('-------------------Starting the Main Loop-------------------------------')
  MainLoop(pw, launch_queue)
  logging.info('-------------------Finished the Main Loop-------------------------------')
  logging.info('-------------------Starting Hold Orders on Necessary Troops-------------')
  HoldNecessary(pw)
  logging.info('-------------------Finished Hold Orders---------------------------------')
  logging.info('-------------------Attacking Enemies------------------------------------')
  AttackEnemies(pw, launch_queue)
  logging.info('-------------------Finished Attacking Enemies---------------------------')
  logging.info('-------------------Attacking Neutrals-----------------------------------')
  AttackNeutrals(pw, launch_queue)
  logging.info('-------------------Finished Attacking Neutrals--------------------------')
  logging.info('-------------------Reinforcing------------------------------------------')
  Reinfroce(pw, launch_queue)
  logging.info('-------------------Finished Reinforcing---------------------------------')
  logging.info('-------------------Launching Ships--------------------------------------')
  LaunchShips(pw, launch_queue)
  logging.info('-------------------Finsihed Launching Ships-----------------------------')


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
