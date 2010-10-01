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
    for dist in range(1, pw.MaxDistance()):
      for p in pw.MyPlanets(i):
        if p.NearestEnemy(i)==dist:
          logging.debug('reinfrocing a planet')
          if p.CanReinforce(i+1):
            logging.info('Planet'+repr(p.PlanetID())+' is being reinforced on turn '+repr(i+1))
            p.CommitReinforce(i+1, launch_queue)

    #calculate owner and number of ships
    if i<pw.MaxDistance()-1:
      logging.debug('calculating owner and numnber of ships')
      for p in pw.Planets():
        p.CalcOwnerAndNumShips(i+1)

  logging.debug('i should be done')

def HoldNecessary(pw):
  logging.debug('holding back reinforcements')
  for p in pw.MyPlanets():
    logging.debug('starting a planet')
    if p.NearestEnemy(0)<=pw.MaxDistance() and p.NearestEnemy(0)==pw.GetGlobalNearestEnemy():
      logging.debug('hold conditions met')
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
          p.CommitTakeOver(i, launch_queue)
          attack_options[p.PlanetID()][i]=p.GetFreeTroops(0,i)-1
          logging.info('launched an attack!')
          logging.info('sending '+repr(p.GetFreeTroops(0,i)-1)+' troops to '+repr(p.PlanetID()))
          deja_attacke.append(p.PlanetID())
          for j in range(i+1,pw.MaxDistance()):
            troops = p.GetEnemyArrival(j)+p.GetAlliedArrival(j)
            if troops < 0:
              if p.CanReinforce(j):
                p.CommitReinforce(i, launch_queue)
  logging.debug('done')

def AttackNeutrals(pw, launch_queue):
  deja_attacked=[]
  if (pw.GetGlobalNearestEnemy()<=pw.MaxDistance()):
    to_attack=[]
    logging.debug('looking for neturals to attack')
    logging.debug('collecting targets')
    for p in pw.NeutralPlanets():
      if p.GrowthRate()>0:
        logging.debug('calculating')
        calc = (p.GetNumShips()/p.GrowthRate()+p.NearestAlly())
        logging.debug('done')
        if calc <=pw.GetGlobalNearestEnemy():
          logging.debug('adding')
          to_attack.append([calc,p])
    logging.debug('done collecting targets')

    logging.debug('cycling through attacks!')
    while len(to_attack)>0:
      min = 99999
      target = -1
      for entry in to_attack:
        if entry[0]<min:
          entry[0]==min
          target = entry

      logging.debug('found target')
      to_attack.remove(target)
      logging.debug('removed target')
      p = target[1]
      logging.debug('pulled planet '+repr(p.PlanetID())+' with '+repr(p.GetNumShips())+' and calc='+repr(min))
      if p.CanTakeOver(p.FarthestEnemy()):
        logging.debug('can take over!')
        done = 0
        i = 1
        while i < p.FarthestAlly() and not(done):
          i +=1
          if p.CanTakeOver(i):
            done = 1
            p.CommitTakeOver(i, launch_queue)
            deja_attacked.append(p)
            for j in range(i,pw.MaxDistance()):
                    if p.CanReinforce(j):
                      p.CommitReinforce(j, launch_queue)


#    logging.debug('done with cycle1')
#    logging.debug('cycle 2!')
#    to_attack=[]
#    logging.debug('looking for neturals to attack')
#    logging.debug('collecting targets')
#    for p in pw.NeutralPlanets():
#      if p.GrowthRate()>0 and not(p in deja_attacked):
#        logging.debug('calculating')
#        calc = p.GetNumShips()/(p.GetNumShips()/p.GrowthRate()+p.NearestAlly())
#        logging.debug('done')
#        logging.debug('adding')
#        to_attack.append([calc,p])
#    logging.debug('done collecting targets')
#
#    logging.debug('cycling through attacks!')
#    while len(to_attack)>0:
#      min = 99999
#      target = -1
#      for entry in to_attack:
#        if entry[0]<min:
#          entry[0]==min
#          target = entry
#
#      logging.debug('found target')
#      to_attack.remove(target)
#      logging.debug('removed target')
#      p = target[1]
#      logging.debug('pulled planet '+repr(p))
#      if p.CanTakeOver(p.FarthestEnemy()):
#        logging.debug('can take over!')
#        done = 0
#        i = 1
#        while i < pw.MaxDistance and not(done):
#          i +=1
#          if p.CanTakeOver(i):
#            done = 1
#            p.CommitTakeOver(i, launch_queue)
#            deja_attacked.append(p)
#            for j in range(i,pw.MaxDistance()):
#                    if p.CanReinforce(j):
#                      p.CommitReinforce(j, launch_queue)



#    logging.debug('looking for neutrals to attack')
#    for i in range(1,pw.MaxDistance()):
#      logging.debug('Looking for turn='+repr(i))
#      if pw.GetRegenBalance(i) < 30:
#        for p in pw.NeutralPlanets(i):
#          if i <= p.FarthestAlly(i) and i>= p.NearestAlly(i):
#            if p.GrowthRate()>0 and p.NearestAlly(i) <= p.NearestEnemy(i):
#              calc = p.GetNumShips()/p.GrowthRate()+p.NearestAlly()
#              logging.debug('The calculations is: '+repr(calc)+' and GlobalEnemey='+repr(pw.GetGlobalNearestEnemy()))
#              if calc <= pw.GetGlobalNearestEnemy():
#                logging.debug('A good candidate for takeover has been found!')
#                if p.CanTakeOver(min(p.FarthestEnemy(i),pw.MaxDistance())):
#                  logging.debug('It can be taken over, lauching attack!')
#                  deja_attacked.append(p)
#                  p.CommitTakeOver(i, launch_queue)
#                  for j in range(i,pw.MaxDistance()):
#                    if p.CanReinforce(j):
#                      p.CommitReinforce(j, launch_queue)
#
#    logging.debug('looking for neutrals to attack (cycle 2)')
#    for k in range(pw.MaxRegen(),0,-1):
#      for i in range(1,pw.MaxDistance()):
#        logging.debug('Looking for turn='+repr(i))
#        if pw.GetRegenBalance(i) <= 0:
#          for p in pw.NeutralPlanets(i):
#            if i <= p.FarthestAlly(i) and i>= p.NearestAlly(i) and not(p in deja_attacked):
#              if p.GrowthRate()>0 and p.NearestAlly(i) <= p.NearestEnemy(i):
#                if p.GrowthRate()==k:
#                  logging.debug('A good candidate for takeover has been found!')
#                  if p.CanTakeOver(pw.MaxDistance()):
#                    logging.debug('It can be taken over, lauching attack!')
#                    deja_attacked.append(p)
#                    p.CommitTakeOver(i, launch_queue)
#                    for j in range(i,pw.MaxDistance()):
#                      if p.CanReinforce(j):
#                        p.CommitReinforce(j, launch_queue)


def Reinfroce(pw, launch_queue):
  logging.info('entering reinforcement phase')
  for p in pw.MyPlanets():
    logging.debug('starting to reinforce planet'+repr(p.PlanetID()))
    logging.debug('sending reinforcements! of '+repr(p.GetFreeTroops()))
    if p.GetFreeTroops()>0:
      near_enemy = p.NearestEnemy()
      if near_enemy <= pw.MaxDistance():
        start_dist = int((3*near_enemy)/4)+1
        logging.debug("start_dist="+repr(start_dist))
        to_send = -1
        nearest_enemy = p.NearestEnemy()
        for i in range(start_dist,0,-1):
          logging.debug('here, i='+repr(i))
          for o in p.GetNeighbors(i):
            logging.debug('here2')
            if o.GetOwner(i)==1:
              logging.debug('here3')
              if o.NearestEnemy(i)<nearest_enemy and not(p.PlanetID()==o.PlanetID()):
                logging.debug('here4')
                to_send = o.PlanetID()
                nearest_enemy = o.NearestEnemy(i)
        if to_send>=0:
          launch_queue[p.PlanetID()][to_send]+=p.GetFreeTroops()
          p.CommitFreeTroops(0,p.GetFreeTroops())

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
        availiable = p.GetNumShips()
        if availiable > to_send:
          p.SetNumShips(availiable-to_send)
          pw.IssueOrder(p.PlanetID(),o.PlanetID(),to_send)
        elif availiable > 0:
          logging.critical('BAD TROOP TRANSPORT')
          p.SetNumShips(0)
          pw.IssueOrder(p.PlanetID(),o.PlanetID(),availiable)
        else:
          logging.critical('BAD TROOP TRANSPORT')
          continue
      elif to_send<0:
        logging.critical('NEGATIVE AMOUNT TO SEND')
        logging.critical('Sending a fleet of ' + repr(to_send)+' from '+repr(p.PlanetID())+' to '+repr(o.PlanetID()))
        continue

def LaunchAttack(pw, launch_queue):
  target = -1
  nearest = 9999999
  for p in pw.EnemyPlanets():
    if p.NearestAlly()<nearest:
      target = p
      nearest = p.NearestAlly()
  if not(target==-1):
    logging.info('targetting planet '+repr(target.PlanetID())+' with defenses '+repr(target.GetNumShips()))
    for o in pw.MyPlanets():
      launch_queue[o.PlanetID()][target.PlanetID()]=o.GetFreeTroops(0)

def DoTurn(pw, turn):
  logging.info('-------------------Initializing the Launch Queue------------------------')
  launch_queue=InitializeLaunchQueue(pw)
  logging.info('-------------------Finished Initilizing the Launch Queue----------------')
  logging.info('-------------------Starting the Main Loop-------------------------------')
  MainLoop(pw, launch_queue)
  logging.info('-------------------Finished the Main Loop-------------------------------')
  #logging.info('-------------------Starting Hold Orders on Necessary Troops-------------')
  #HoldNecessary(pw)
  #logging.info('-------------------Finished Hold Orders---------------------------------')
  logging.info('-------------------Attacking Enemies------------------------------------')
  AttackEnemies(pw, launch_queue)
  logging.info('-------------------Finished Attacking Enemies---------------------------')
  if turn<10 or turn%2==1:
    logging.info('-------------------Attacking Neutrals-----------------------------------')
    AttackNeutrals(pw, launch_queue)
    logging.info('-------------------Finished Attacking Neutrals--------------------------')
    logging.info('-------------------Reinforcing------------------------------------------')
    Reinfroce(pw, launch_queue)
    logging.info('-------------------Finished Reinforcing---------------------------------')
  else:
    logging.info('-------------------Launching An Attack!---------------------------------')
    LaunchAttack(pw, launch_queue)
    logging.info('-------------------Finished Launching An Attack!------------------------')

  
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
      logging.info('====================================================================')
      logging.info('==============Starting Turn ' + repr(turn) +'=================================')
      DoTurn(pw, turn)
      logging.info('==============finished turn!========================================')
      logging.info('====================================================================')
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
