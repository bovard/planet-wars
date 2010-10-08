#!/usr/bin/env python
#

"""
// My Function: It rules
// http://www.ai-contest.com/resources.
"""


import logging
import time

from PlanetWars2 import PlanetWars2 as PlanetWars
from Planet import Planet
import Logging as L

def MainLoop(pw):
  if L.DEBUG: logging.debug('starting the turn loop cycle ('+repr(pw.MaxDistance())+' turns)')
  for i in range(pw.MaxDistance()):
    pw.CalcNeighbors(i)
    if L.DEBUG: logging.debug('turn loop '+repr(i))
    #calculate free troops
    if L.DEBUG: logging.debug('calculating free troops')
    for p in pw.Planets():
      p.CalcFreeTroops(i+1)
    if L.DEBUG: logging.debug('getting requets')

    #figure out requests
    for dist in range(1, pw.MaxDistance()+1):
      if L.DEBUG: logging.debug('dist='+repr(dist))
      for p in pw.MyPlanets(i):
        if p.GetEnemyArrival(i+1)>0 and p.GetOwner(i)==1 and p.GetFreeTroops(i+1) < 0:
          if L.INFO: logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
          if pw.CanDefend(p,i+1):
            if L.INFO: logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
            pw.CommitDefend(p,i+1)
        if (p.NearestEnemy()==i and p.NearestEnemy()==dist) or (p.FarthestEnemy()==i and p.FarthestEnemy()==dist):
          if L.DEBUG: logging.debug('reinfrocing a planet because '+repr(p.NearestEnemy())+" == "+repr(dist))
          if pw.CanReinforce(p,i+1):
            if L.DEBUG: logging.debug('Planet'+repr(p.PlanetID())+' is being reinforced on turn '+repr(i+1))
            pw.CommitReinforce(p,i+1)
    for dist in range(1, pw.MaxDistance()+1):
      for p in pw.EnemyPlanets(i):
        if (p.NearestAlly()==i and p.NearestAlly()<=dist) or (p.FarthestAlly()==i and p.FarthestAlly()==dist):
          if not(pw.CanReinforce(p,i+1)):
            pw.EnemyCommitReinforce(p,i+1)

    #calculate owner and number of ships
    if L.DEBUG: logging.debug('calculating owner and numnber of ships')
    for p in pw.Planets():
      p.CalcOwnerAndNumShips(i+1)

  if L.INFO: logging.info('i should be done')
  for p in pw.Planets():
    p.PrintSummary(1)


def AttackEnemies(pw):

  deja_attacke=[]
  if L.DEBUG: logging.debug('looking for enemies to attack')
  for i in range(1,pw.MaxDistance()):
    if L.DEBUG: logging.debug('turn '+repr(i))
    for p in pw.EnemyPlanets(i):
      if not(p.GetOwner(i-1)==0) and not(p.PlanetID() in deja_attacke):
        if pw.CanRecklessTakeOver(p,i):
          if L.INFO: logging.info('CAN TAKE OVER PLANET '+repr(p.PlanetID())+' ON TURN '+repr(i))
          pw.CommitRecklessTakeOver(p,i)
          deja_attacke.append(p.PlanetID())
          for j in range(i+1,pw.MaxDistance()):
            if p.GetEnemyArrival(j)>0 and p.GetFreeTroops(j) < 0:
              if L.INFO: logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
              if pw.CanDefend(p,j):
                if L.INFO: logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
                pw.CommitDefend(p,j)
  if L.DEBUG: logging.debug('done')

def AttackNeutrals(pw):
  deja_attacked=[]
  if (pw.GetGlobalNearestEnemy()<=pw.MaxDistance() and pw.GetGlobalFarthestEnemy()>0 and len(pw.MyPlanets())>0):
    to_attack=[]
    if L.DEBUG: logging.debug('looking for neturals to attack')
    if L.DEBUG: logging.debug('collecting targets')
    for p in pw.NeutralPlanets():
      if p.GrowthRate()>0 and p.NearestAlly()<=p.NearestEnemy():
        if L.DEBUG: logging.debug('calculating with ships '+repr(p.GetNumShips())+' growth: '+repr(p.GrowthRate())+ ' nearest: '+repr(p.NearestAlly()))
        calc = int((float(p.GetNumShips())/float(2*p.GrowthRate())))
        if L.DEBUG: logging.debug('calc = '+repr(calc))
        if L.DEBUG: logging.debug('done')
        
        if L.DEBUG: logging.debug('adding')
        to_attack.append([calc,p])
    if L.DEBUG: logging.debug('done collecting targets')

    if L.DEBUG: logging.debug('cycling through attacks!')
    while len(to_attack)>0:
      min = 999999999999999999
      target = -1
      for entry in to_attack:
        if entry[0]<min:
          min=entry[0]
          target = entry

      if L.DEBUG: logging.debug('found target')
      to_attack.remove(target)
      if L.DEBUG: logging.debug('removed target')
      p = target[1]
      if L.DEBUG: logging.debug('pulled planet '+repr(p.PlanetID())+' with '+repr(p.GetNumShips())+' and calc='+repr(min))
      if p.FarthestEnemy() > 0 and p.NearestAlly() < pw.MaxDistance and p.NearestAlly() <= p.NearestEnemy():
        if p.NearestEnemy() > pw.GetGlobalNearestEnemy() or pw.CanSafeTakeNeutral(p,p.FarthestEnemy()):
          if L.DEBUG: logging.debug('can take over!')
          done = 0
          i = 1
          if L.DEBUG: logging.debug('Longest Distance to look is: '+repr(p.FarthestAlly()))
          if p.FarthestAlly() < pw.MaxDistance():
            while i <= p.NearestAlly() and not(done) and i < pw.MaxDistance():
              if L.DEBUG: logging.debug('Starting CanTakeNeutral looking '+repr(i)+' units away')
              if p.NearestAlly(i) <= p.NearestEnemy(i) and pw.CanTakeNeutral(p,i):
                done = 1
                pw.CommitTakeNeutral(p,i)
                deja_attacked.append(p)
                for j in range(i,pw.MaxDistance()):
                  if p.GetEnemyArrival(j)>0 and p.GetFreeTroops(j) < 0:
                    if L.INFO: logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
                    if pw.CanDefend(p,j):
                      if L.INFO: logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
                      pw.CommitDefend(p,j)
              i +=1


    if L.DEBUG: logging.debug('done with cycle1')




def Reinforce(pw):
  if L.INFO: logging.info('entering reinforcement phase')
  for p in pw.MyPlanets():
    if L.INFO: logging.info('starting to reinforce from planet'+repr(p.PlanetID()))
    if L.INFO: logging.info('sending reinforcements! of '+repr(p.GetFreeTroops())+ ' or '+repr(p.GetReinforcingTroops()))
    if p.GetReinforcingTroops()>0 or p.GetForcastingTroops()>0:
      if L.INFO: logging.info('have some troops to reinforce with')
      near_enemy = p.NearestEnemy()
      if near_enemy <= pw.MaxDistance():
        start_dist = int((3*near_enemy)/4)+1
        if L.INFO: logging.info("start_dist="+repr(start_dist))
        to_send = -1
        nearest_enemy = p.NearestEnemy()
        for i in range(start_dist,0,-1):
          for o in pw.GetNeighbors(p.PlanetID(),i):
            if o.GetOwner(i)==1:
              if L.INFO: logging.info('Found Allied Planet '+repr(o.PlanetID()))
              if o.NearestEnemy(i)<nearest_enemy and not(p.PlanetID()==o.PlanetID()):
                if L.INFO: logging.info('Allied Planet '+repr(o.PlanetID())+ ' might be reinforced!')
                to_send = o.PlanetID()
                nearest_enemy = o.NearestEnemy(i)
        if to_send>=0:
          if L.INFO: logging.info('Launching reinforcements!')
          pw.AddLaunch(p.PlanetID(),to_send,p.GetReinforcingTroops()+p.GetForcastingTroops())
          #pw.CommitTroops(p,0,p.GetFreeTroops(),[p.FreeTroops()],p.ReinforcingTroops())


def LaunchAttack(pw):
  for p in pw.MyPlanets():
    if p.NearestEnemy() == pw.GetGlobalNearestEnemy():
      for o in pw.EnemyPlanets():
        if pw.Distance(p.PlanetID(),o.PlanetID())==pw.GetGlobalNearestEnemy():
          pw.AddLaunch(p.PlanetID(),o.PlanetID(),int(p.GetFreeTroops()/2+p.GetReinforcingTroops()/2))
          p.CommitTroops(0,int(p.GetFreeTroops()/2+p.GetReinforcingTroops()/2),[p.FreeTroops()],p.DefendingTroops())

def DoTurn(pw, turn):
  start_time = time.time()
  if L.INFO: logging.info('-------------------Starting the Main Loop-------------------------------')
  MainLoop(pw)
  if L.INFO: logging.info('-------------------Finished the Main Loop-------------------------------')
  if L.INFO: logging.info('-------------------Attacking Enemies------------------------------------')
  AttackEnemies(pw)
  if L.INFO: logging.info('-------------------Finished Attacking Enemies---------------------------')
  if 1:
    #if L.INFO: logging.info('-------------------Activating Neutral Hunter----------------------------')
    #to_attack = pw.RecursiveNeutralHunter(int(pw.MaxDistance()/2) )
    #if L.WARNING: logging.warning('Neutral Hunter said to attack '+repr(to_attack))
    #for entry in to_attack:
    #  if entry[0]!=-1:
    #    pw.CommitTakeNeutral(pw.GetPlanet(entry[0]), entry[1])
    #if L.WARNING: logging.warning('Attacks Launched!')
    #if L.INFO: logging.info('-------------------Leaving Neutral Hunter-------------------------------')
    
    if L.INFO: logging.info('-------------------Attacking Neutrals-----------------------------------')
    AttackNeutrals(pw)
    if L.INFO: logging.info('-------------------Finished Attacking Neutrals--------------------------')
  if L.INFO: logging.info('-------------------Reinforcing------------------------------------------')
  Reinforce(pw)
  if L.INFO: logging.info('-------------------Finished Reinforcing---------------------------------')

  ##if L.INFO: logging.info('-------------------Launching An Attack!---------------------------------')
  #LaunchAttack(pw)
  ##if L.INFO: logging.info('-------------------Finished Launching An Attack!------------------------')

  
  if L.INFO: logging.info('-------------------Launching Ships--------------------------------------')
  pw.LaunchShips()
  if L.INFO: logging.info('-------------------Finsihed Launching Ships-----------------------------')
  if L.CRITICAL: logging.critical('This turn took '+repr(time.time()-start_time))


def main():
  map_data = ''
  turn = -1
  pw = -1
  while(True):
    try:
      current_line = raw_input()
      if len(current_line) >= 2 and current_line.startswith("go"):
        turn += 1
        if turn == 0:
          pw = PlanetWars(map_data, turn)
        else:
          pw.Update(map_data, turn)
        if L.INFO: logging.info('====================================================================')
        if L.INFO: logging.info('==============Starting Turn ' + repr(turn) +'=================================')
        DoTurn(pw, turn)
        if L.INFO: logging.info('==============finished turn!========================================')
        if L.INFO: logging.info('====================================================================')
        pw.FinishTurn()
        map_data = ''
      else:
        map_data += current_line + '\n'
    except EOFError, e: break
  


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
