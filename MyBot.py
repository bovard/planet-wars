#!/usr/bin/env python
#

"""
// My Function: It rules
// http://www.ai-contest.com/resources.
"""

#import #logging

from PlanetWars import PlanetWars
from Planet2 import Planet2 as Planet


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
    for dist in range(1, pw.MaxDistance()+1):
      #logging.debug('dist='+repr(dist))
      for p in pw.MyPlanets(i):
        if p.GetEnemyArrival(i+1)>0 and p.GetOwner(i)==1 and p.GetFreeTroops(i+1) < 0:
          #logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
          if p.CanDefend(i+1):
            #logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
            p.CommitDefend(i+1)
        if (p.NearestEnemy()==i and p.NearestEnemy()==dist) or (p.FarthestEnemy()==i and p.FarthestEnemy()==dist):
          #logging.debug('reinfrocing a planet because '+repr(p.NearestEnemy())+" == "+repr(dist))
          if p.CanReinforce(i+1):
            #logging.debug('Planet'+repr(p.PlanetID())+' is being reinforced on turn '+repr(i+1))
            p.CommitReinforce(i+1)
    for dist in range(1, pw.MaxDistance()+1):
      for p in pw.EnemyPlanets(i):
        if (p.NearestAlly()==i and p.NearestAlly()<=dist) or (p.FarthestAlly()==i and p.FarthestAlly()==dist):
          if not(p.CanReinforce(i+1)):
            p.EnemyCommitReinforce(i+1)

    #calculate owner and number of ships
    #logging.debug('calculating owner and numnber of ships')
    for p in pw.Planets():
      p.CalcOwnerAndNumShips(i+1)

  #logging.info('i should be done')
  for p in pw.Planets():
    p.PrintSummary(1)


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
  if (pw.GetGlobalNearestEnemy()<=pw.MaxDistance() and pw.GetGlobalFarthestEnemy()>0 and len(pw.MyPlanets())>0):
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
      if p.FarthestEnemy() > 0 and p.NearestAlly() < pw.MaxDistance:
        if p.NearestEnemy() > pw.GetGlobalNearestEnemy() or p.CanSafeTakeNeutral(p.FarthestEnemy()):
          #logging.debug('can take over!')
          done = 0
          i = 1
          #logging.debug('Longest Distance to look is: '+repr(p.FarthestAlly()))
          while i <= p.FarthestAlly()+1 and not(done):
            #logging.debug('Starting CanTakeNeutral looking '+repr(i)+' units away')
            if p.NearestAlly(i) < p.NearestEnemy(i) and p.CanTakeNeutral(i):
              done = 1
              p.CommitTakeNeutral(i)
              deja_attacked.append(p)
              for j in range(i,pw.MaxDistance()):
                if p.GetFreeTroops(j)<0:
                    if p.CanDefend(j):
                      p.CommitDefend(j)
            i +=1


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
      if p.FarthestEnemy() > 0 and p.NearestAlly() < pw.MaxDistance:
        if  p.CanSafeTakeNeutral(p.FarthestEnemy()) and p.NearestAlly() < p.NearestEnemy():
          #logging.debug('can take over!')
          done = 0
          i = 1
          #logging.debug('Longest Distance to look is: '+repr(p.FarthestAlly()))
          while i <= p.NearestAlly()+1 and not(done):
            #logging.debug('Starting CanTakeNeutral looking '+repr(i)+' units away')
            if p.NearestAlly(i) < p.NearestEnemy(i) and p.CanTakeNeutral(i) and p.CanSafeTakeNeutral(p.FarthestEnemy(i)):
              done = 1
              p.CommitTakeNeutral(i)
              deja_attacked.append(p)
              for j in range(i,pw.MaxDistance()):
                if p.GetFreeTroops(j)<0:
                    if p.CanDefend(j):
                      p.CommitDefend(j)
            i +=1


'''
    #logging.debug('done with cycle2')
    #logging.debug('cycle 3')
    to_attack=[]
    #logging.debug('looking for neturals to attack')
    #logging.debug('collecting targets')
    for p in pw.NeutralPlanets():
      if p.GrowthRate()>0 and not(p in deja_attacked):
        #logging.debug('calculating')
        #logging.debug('calculating with ships '+repr(p.GetNumShips())+' growth: '+repr(p.GrowthRate())+ ' nearest: '+repr(p.NearestAlly()))
        calc = p.GetNumShips()/p.GrowthRate()
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
      if p.FarthestEnemy() > 0 and p.NearestAlly() < pw.MaxDistance:
        if p.NearestAlly()*2 < p.NearestEnemy() and target[0]<pw.GetGlobalNearestEnemy():
          #logging.debug('can take over!')
          done = 0
          i = 1
          #logging.debug('Longest Distance to look is: '+repr(p.FarthestAlly()))
          while i <= p.NearestAlly()+1 and not(done):
            #logging.debug('Starting CanTakeNeutral looking '+repr(i)+' units away')
            if p.CanRecklessTakeOver(i):
              done = 1
              p.CommitRecklessTakeOver(i)
              deja_attacked.append(p)
              for j in range(i,pw.MaxDistance()):
                if p.GetFreeTroops(j)<0:
                    if p.CanDefend(j):
                      p.CommitDefend(j)
            i +=1
'''



def Reinforce(pw):
  #logging.info('entering reinforcement phase')
  for p in pw.MyPlanets():
    #logging.info('starting to reinforce from planet'+repr(p.PlanetID()))
    #logging.info('sending reinforcements! of '+repr(p.GetFreeTroops())+ ' or '+repr(p.GetReinforcingTroops()))
    if p.GetFreeTroops()>0 or p.GetReinforcingTroops()>0:
      #logging.info('have some troops to reinforce with')
      near_enemy = p.NearestEnemy()
      if near_enemy <= pw.MaxDistance():
        start_dist = int((3*near_enemy)/4)+1
        #logging.info("start_dist="+repr(start_dist))
        to_send = -1
        nearest_enemy = p.NearestEnemy()
        for i in range(start_dist,0,-1):
          for o in p.GetNeighbors(i):
            if o.GetOwner(i)==1:
              #logging.info('Found Allied Planet '+repr(o.PlanetID()))
              if o.NearestEnemy(i)<nearest_enemy and not(p.PlanetID()==o.PlanetID()):
                #logging.info('Allied Planet '+repr(o.PlanetID())+ ' might be reinforced!')
                to_send = o.PlanetID()
                nearest_enemy = o.NearestEnemy(i)
        if to_send>=0:
          #logging.info('Launching reinforcements!')
          pw.AddLaunch(p.PlanetID(),to_send,p.GetFreeTroops()+int(p.GetReinforcingTroops()/2))
          p.CommitTroops(0,p.GetFreeTroops(),[p.FreeTroops()],p.ReinforcingTroops())


def LaunchAttack(pw):
  for p in pw.MyPlanets():
    if p.NearestEnemy() == pw.GetGlobalNearestEnemy():
      for o in pw.EnemyPlanets():
        if pw.Distance(p.PlanetID(),o.PlanetID())==pw.GetGlobalNearestEnemy():
          pw.AddLaunch(p.PlanetID(),o.PlanetID(),int(p.GetFreeTroops()/2+p.GetReinforcingTroops()/2))
          p.CommitTroops(0,int(p.GetFreeTroops()/2+p.GetReinforcingTroops()/2),[p.FreeTroops()],p.DefendingTroops())

def DoTurn(pw, turn):
  #logging.info('-------------------Starting the Main Loop-------------------------------')
  MainLoop(pw)
  #logging.info('-------------------Finished the Main Loop-------------------------------')
  #logging.info('-------------------Attacking Enemies------------------------------------')
  AttackEnemies(pw)
  #logging.info('-------------------Finished Attacking Enemies---------------------------')
  if pw.GetRegenBalance() <= 0:
    #logging.info('-------------------Attacking Neutrals-----------------------------------')
    AttackNeutrals(pw)
    #logging.info('-------------------Finished Attacking Neutrals--------------------------')
  #logging.info('-------------------Reinforcing------------------------------------------')
  Reinforce(pw)
  #logging.info('-------------------Finished Reinforcing---------------------------------')

  ###logging.info('-------------------Launching An Attack!---------------------------------')
  #LaunchAttack(pw)
  ###logging.info('-------------------Finished Launching An Attack!------------------------')

  
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
