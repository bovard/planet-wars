#!/usr/bin/env python
#

"""
// My Function: It rules
// http://www.ai-contest.com/resources.
"""

#import #logging

from PlanetWars import PlanetWars


def MainLoop(pw):
  #logging.debug('starting the turn loop cycle ('+repr(pw.MaxDistance())+' turns)')
  for i in range(pw.MaxDistance()):
    pw.CalcNeighbors(i)
    #logging.debug('turn loop '+repr(i))
    #calculate free troops
    #logging.debug('calculating free troops')
    for p in pw.Planets():
      p.CalcFreeTroops(i+1)
    #logging.debug('getting requets')
    #figure out requests
    for dist in range(1, pw.MaxDistance()):
      for p in pw.MyPlanets(i):
        if p.NearestEnemy(i)==dist or p.GetFreeTroops(i+1)<0:
          #logging.debug('reinfrocing a planet')
          if p.CanReinforce(i+1):
            #logging.info('Planet'+repr(p.PlanetID())+' is being reinforced on turn '+repr(i+1))
            p.CommitReinforce(i+1)

    #calculate owner and number of ships
    if i<pw.MaxDistance()-1:
      #logging.debug('calculating owner and numnber of ships')
      for p in pw.Planets():
        p.CalcOwnerAndNumShips(i+1)

  #logging.debug('i should be done')

def AttackEnemies(pw):

  deja_attacke=[]
  #logging.debug('looking for enemies to attack')
  for i in range(1,pw.MaxDistance()):
    #logging.debug('turn '+repr(i))
    for p in pw.EnemyPlanets(i):
      if not(p.GetOwner(i-1)==0) and not(p.PlanetID() in deja_attacke):
        if p.CanRecklessTakeOver(i):
          #logging.info('CAN TAKE OVER PLANET '+repr(p.PlanetID())+' ON TURN '+repr(i))
          p.CommitRecklessTakeOver(i)
          deja_attacke.append(p.PlanetID())
          for j in range(i+1,pw.MaxDistance()):
            troops = p.GetEnemyArrival(j)+p.GetAlliedArrival(j)
            if troops < 0:
              if p.CanReinforce(j):
                p.CommitReinforce(j)
  #logging.debug('done')

def AttackNeutrals(pw):
  deja_attacked=[]
  if (pw.GetGlobalNearestEnemy()<=pw.MaxDistance()):
    to_attack=[]
    #logging.debug('looking for neturals to attack')
    #logging.debug('collecting targets')
    for p in pw.NeutralPlanets():
      if p.GrowthRate()>0:
        #logging.debug('calculating with ships '+repr(p.GetNumShips())+' growth: '+repr(p.GrowthRate())+ ' nearest: '+repr(p.NearestAlly()))
        calc = float(p.GetNumShips())/float(p.GrowthRate())+p.NearestAlly()
        #logging.debug('calc = '+repr(calc))
        #logging.debug('done')
        if calc <=pw.GetGlobalNearestEnemy():
          #logging.debug('adding')
          to_attack.append([calc,p])
    #logging.debug('done collecting targets')

    #logging.debug('cycling through attacks!')
    while len(to_attack)>0:
      min = 99999
      target = -1
      for entry in to_attack:
        if entry[0]<min:
          min=entry[0]
          target = entry

      #logging.debug('found target')
      to_attack.remove(target)
      #logging.debug('removed target')
      p = target[1]
      #logging.debug('pulled planet '+repr(p.PlanetID())+' with '+repr(p.GetNumShips())+' and calc='+repr(min))
      if p.CanSafeTakeOver(p.FarthestEnemy()):
        #logging.debug('can take over!')
        done = 0
        i = 1
        while i < p.FarthestAlly() and not(done):
          i +=1
          if p.CanSafeTakeOver(i):
            done = 1
            p.CommitSafeTakeOver(i)
            deja_attacked.append(p)
            for j in range(i,pw.MaxDistance()):
                    if p.CanReinforce(j):
                      p.CommitReinforce(j)


    #logging.debug('done with cycle1')
    #logging.debug('cycle 2!')
    to_attack=[]
    #logging.debug('looking for neturals to attack')
    #logging.debug('collecting targets')
    for p in pw.NeutralPlanets():
      if p.GrowthRate()>0 and not(p in deja_attacked):
        #logging.debug('calculating')
        #logging.debug('calculating with ships '+repr(p.GetNumShips())+' growth: '+repr(p.GrowthRate())+ ' nearest: '+repr(p.NearestAlly()))
        calc = p.GetNumShips()/p.GrowthRate()+p.NearestAlly()
        #logging.debug('calc = '+repr(calc))
        #logging.debug('done')
        #logging.debug('adding')
        to_attack.append([calc,p])
    #logging.debug('done collecting targets')

    #logging.debug('cycling through attacks!')
    while len(to_attack)>0:
      min = 99999
      target = -1
      for entry in to_attack:
        if entry[0]<min:
          min=entry[0]
          target = entry

      #logging.debug('found target')
      to_attack.remove(target)
      #logging.debug('removed target')
      p = target[1]
      #logging.debug('pulled planet '+repr(p))
      if p.CanSafeTakeOver(p.FarthestEnemy()):
        #logging.debug('can take over!')
        done = 0
        i = 1
        while i < p.NearestAlly() and not(done):
          i +=1
          if p.CanSafeTakeOver(i):
            done = 1
            p.CommitSafeTakeOver(i)
            deja_attacked.append(p)
            for j in range(i,pw.MaxDistance()):
                    if p.CanReinforce(j):
                      p.CommitReinforce(j)



def Reinforce(pw):
  #logging.info('entering reinforcement phase')
  for p in pw.MyPlanets():
    #logging.debug('starting to reinforce planet'+repr(p.PlanetID()))
    #logging.debug('sending reinforcements! of '+repr(p.GetFreeTroops()))
    if p.GetFreeTroops()>0:
      near_enemy = p.NearestEnemy()
      if near_enemy <= pw.MaxDistance():
        start_dist = int((3*near_enemy)/4)+1
        #logging.debug("start_dist="+repr(start_dist))
        to_send = -1
        nearest_enemy = p.NearestEnemy()
        for i in range(start_dist,0,-1):
          #logging.debug('here, i='+repr(i))
          for o in p.GetNeighbors(i):
            #logging.debug('here2')
            if o.GetOwner(i)==1:
              #logging.debug('here3')
              if o.NearestEnemy(i)<nearest_enemy and not(p.PlanetID()==o.PlanetID()):
                #logging.debug('here4')
                to_send = o.PlanetID()
                nearest_enemy = o.NearestEnemy(i)
        if to_send>=0:
          pw.AddLaunch(p.PlanetID(),to_send,p.GetFreeTroops())
          p.CommitFreeTroops(0,p.GetFreeTroops())


def LaunchAttack(pw):
  target = -1
  nearest = 9999999
  for p in pw.EnemyPlanets():
    if p.NearestAlly()<nearest:
      target = p
      nearest = p.NearestAlly()
  if not(target==-1):
    #logging.info('targetting planet '+repr(target.PlanetID())+' with defenses '+repr(target.GetNumShips()))
    for o in pw.MyPlanets():
      pw.AddLaunch(o.PlanetID(),target.PlanetID(),o.GetFreeTroops(0))

def DoTurn(pw, turn):
  #logging.info('-------------------Starting the Main Loop-------------------------------')
  MainLoop(pw)
  #logging.info('-------------------Finished the Main Loop-------------------------------')
  #logging.info('-------------------Attacking Enemies------------------------------------')
  AttackEnemies(pw)
  #logging.info('-------------------Finished Attacking Enemies---------------------------')

  #logging.info('-------------------Attacking Neutrals-----------------------------------')
  AttackNeutrals(pw)
  #logging.info('-------------------Finished Attacking Neutrals--------------------------')
  #logging.info('-------------------Reinforcing------------------------------------------')
  Reinforce(pw)
  #logging.info('-------------------Finished Reinforcing---------------------------------')

#  #logging.info('-------------------Launching An Attack!---------------------------------')
#  LaunchAttack(pw)
#  #logging.info('-------------------Finished Launching An Attack!------------------------')

  
  #logging.info('-------------------Launching Ships--------------------------------------')
  pw.LaunchShips()
  #logging.info('-------------------Finsihed Launching Ships-----------------------------')


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
      #logging.info('====================================================================')
      #logging.info('==============Starting Turn ' + repr(turn) +'=================================')
      DoTurn(pw, turn)
      #logging.info('==============finished turn!========================================')
      #logging.info('====================================================================')
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
