#!/usr/bin/env python
#

"""
// My Function: It rules
// http://www.ai-contest.com/resources.
"""


#import #logging
import time

from PlanetWars2 import PlanetWars2 as PlanetWars
from Planet import Planet
from copy import deepcopy

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
          if pw.CanDefend(p,i+1):
            #logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
            pw.CommitDefend(p,i+1)
        if (p.NearestEnemy()==i and p.NearestEnemy()==dist) or (p.FarthestEnemy()==i and p.FarthestEnemy()==dist):
          #logging.debug('reinfrocing a planet because '+repr(p.NearestEnemy())+" == "+repr(dist))
          if pw.CanReinforce(p,i+1):
            #logging.debug('Planet'+repr(p.PlanetID())+' is being reinforced on turn '+repr(i+1))
            pw.CommitReinforce(p,i+1)
    for dist in range(1, pw.MaxDistance()+1):
      for p in pw.EnemyPlanets(i):
        if (p.NearestAlly()==i and p.NearestAlly()<=dist) or (p.FarthestAlly()==i and p.FarthestAlly()==dist):
          if not(pw.CanReinforce(p,i+1)):
            pw.EnemyCommitReinforce(p,i+1)

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
        if pw.CanRecklessTakeOver(p,i):
          #logging.info('CAN TAKE OVER PLANET '+repr(p.PlanetID())+' ON TURN '+repr(i))
          pw.CommitRecklessTakeOver(p,i)
          deja_attacke.append(p.PlanetID())
          for j in range(i+1,pw.MaxDistance()):
            if p.GetEnemyArrival(j)>0 and p.GetFreeTroops(j) < 0:
              #logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
              if pw.CanDefend(p,j):
                #logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
                pw.CommitDefend(p,j)
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
        calc = int((float(p.GetNumShips())/float(p.GrowthRate())+2*p.NearestAlly())*p.GetConnectedness())
        #logging.debug('calc = '+repr(calc))
        #logging.debug('done')
        
        #logging.debug('adding')
        to_attack.append([calc,p])
    #logging.debug('done collecting targets')

    #logging.debug('cycling through attacks!')
    while len(to_attack)>0:
      min = 999999999999999999
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
        if p.NearestEnemy() > pw.GetGlobalNearestEnemy() or pw.CanSafeTakeNeutral(p,p.FarthestEnemy()):
          #logging.debug('can take over!')
          done = 0
          i = 1
          #logging.debug('Longest Distance to look is: '+repr(p.FarthestAlly()))
          if p.FarthestAlly() < pw.MaxDistance():
            while i <= p.FarthestAlly()+1 and not(done) and i < pw.MaxDistance():
              #logging.debug('Starting CanTakeNeutral looking '+repr(i)+' units away')
              if p.NearestAlly(i) < p.NearestEnemy(i) and pw.CanTakeNeutral(p,i):
                done = 1
                pw.CommitTakeNeutral(p,i)
                deja_attacked.append(p)
                for j in range(i,pw.MaxDistance()):
                  if p.GetEnemyArrival(j)>0 and p.GetFreeTroops(j) < 0:
                    #logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
                    if pw.CanDefend(p,j):
                      #logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
                      pw.CommitDefend(p,j)
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
        calc = int((float(p.GetNumShips())/float(p.GrowthRate())+2*p.NearestAlly())*p.GetConnectedness())
        #logging.debug('calc = '+repr(calc))
        #logging.debug('done')
        #logging.debug('adding')
        to_attack.append([calc,p])
    #logging.debug('done collecting targets')

    #logging.debug('cycling through attacks!')
    while len(to_attack)>0:
      min = 99999999999999999999
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
        if  pw.CanSafeTakeNeutral(p,p.FarthestEnemy()) and p.NearestAlly() < p.NearestEnemy():
          #logging.debug('can take over!')
          done = 0
          i = 1
          #logging.debug('Longest Distance to look is: '+repr(p.FarthestAlly()))
          if p.FarthestAlly() < pw.MaxDistance():
            while i <= p.NearestAlly()+1 and not(done) and i < pw.MaxDistance():
              #logging.debug('Starting CanTakeNeutral looking '+repr(i)+' units away')
              if p.NearestAlly(i) < p.NearestEnemy(i) and pw.CanTakeNeutral(p,i):
                done = 1
                pw.CommitTakeNeutral(p,i)
                deja_attacked.append(p)
                for j in range(i,pw.MaxDistance()):
                  if p.GetEnemyArrival(j)>0 and p.GetFreeTroops(j) < 0:
                    #logging.info('defending Planet '+repr(p.PlanetID())+'on turn'+repr(i+1)+' because '+repr(p.GetEnemyArrival(i+1)) + ' > 0')
                    if pw.CanDefend(p,j):
                      #logging.info('Planet'+repr(p.PlanetID())+' is being defended on turn '+repr(i+1))
                      pw.CommitDefend(p,j)
              i +=1


#def RecursiveNeutralHunter(pw, turn, history=[], max=-9999999999999999, max_entry=[], depth=0):
#  #clone the old planets, put the old planets in the list, then set pw on the clones
#  #logging.debug('in RecursiveNeutralHunter depth = '+repr(depth))
#
#  #logging.debug('setting pw to the new planets')
#  #logging.debug('old planets')
#  pw.PrintPlanetSummary()
#  pw.SetPlanets(pw.PopPlanetList())
#  #logging.debug('new planets')
#  pw.PrintPlanetSummary()
#
#  #logging.debug('history '+repr(history))
#  if len(history)>0:
#    if history[len(history)-1][0]==-1:
#      #logging.debug('dead end, returning')
#      return
#
#  #logging.debug('finding neutrals allies can take')
#  neutrals_allies_can_take = []
#  for planet in pw.NeutralPlanets(pw.MaxDistance()-1):
#    if pw.CanSafeTakeNeutral(planet, turn):
#      for i in range(1, turn+1):
#        if pw.CanTakeNeutral(planet, i):
#          neutrals_allies_can_take.append([planet,i])
#          break
#  #logging.debug('Allies can take '+repr(len(neutrals_allies_can_take))+' planets:')
#  for entry in neutrals_allies_can_take:
#    p = entry[0]
#    #logging.debug('Planet '+repr(p.PlanetID())+ ' with '+repr(p.GetNumShips())+' ships and regen of '+repr(p.GrowthRate()))
#    p.PrintSummary()
#
#
#
#  #logging.debug('starting the loop')
#  for i in range(-1,len(neutrals_allies_can_take)):
#    #logging.debug('i='+repr(i)+' and depth = '+repr(depth))
#    entry = [-1,-1]
#    if i>=0:
#      #logging.debug('making new planets')
#      new_planets = deepcopy(pw.Planets())
#      pw.PrintPlanetSummary()
#      pw.PushPlanetList(pw.Planets)
#      pw.SetPlanets(new_planets)
#      pw.PrintPlanetSummary()
#      #logging.debug('changed to a new set of planets')
#      entry = neutrals_allies_can_take[i]
#      #logging.debug('looking at entry: '+repr(entry))
#      pw.CommitTakeNeutral(entry[0], entry[1], 0)
#      entry[0].SimulateAttack(entry[1])
#
#    #logging.debug('calculating neutrals enemies control')
#    neutrals_enemies_control = []
#    for planet in pw.NeutralPlanets():
#      if pw.CanSafeTakeNeutral(planet, turn, 1):
#        neutrals_enemies_control.append(planet)
#
#    #logging.debug('calculating netural growth rates')
#    enemy_controlled_growthrate = 0
#    for p in neutrals_enemies_control:
#      enemy_controlled_growthrate += p.GrowthRate()
#
#    #logging.debug('calcuulating my growthrate')
#    my_growthrate = 0
#    for p in pw.MyPlanets(turn):
#      my_growthrate = p.GrowthRate()
#    if entry[0]!=-1:
#      my_growthrate += entry[0].GrowthRate()
#    for thing in history:
#      if thing[0]!=-1:
#        my_growthrate += thing[0].GrowthRate()
#
#    #logging.debug('calculating score with '+repr(my_growthrate)+ ' - '+repr(enemy_controlled_growthrate))
#    score = my_growthrate - enemy_controlled_growthrate
#    #logging.debug('score='+repr(score))
#
#    if score > max or (score == max and my_growthrate > max + enemy_controlled_growthrate):
#      #logging.debug('found a new max!')
#      max = score
#      #logging.debug('score = '+repr(max))
#      max_entry = deepcopy(history)
#      max_entry.append(entry)
#      #logging.debug('max_entry = '+repr(max_entry))
#
#    if i>=0:
#      #logging.debug('recursing')
#      new_history = deepcopy(history)
#      new_history.append(entry)
#      pw.PushPlanetList(pw.Planets())
#      RecursiveNeutralHunter(pw, turn, new_history, max, max_entry, depth+1)
#
#
#      #logging.debug('going back to the old planets')
#      pw.PrintPlanetSummary()
#      pw.SetPlanets(pw.PopPlanetList())
#      pw.PrintPlanetSummary()
#      #logging.debug('now using '+repr(pw.Planets()))
#
#
#
#  #logging.debug('done')
#  return max_entry




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
          for o in pw.GetNeighbors(p.PlanetID(),i):
            if o.GetOwner(i)==1:
              #logging.info('Found Allied Planet '+repr(o.PlanetID()))
              if o.NearestEnemy(i)<nearest_enemy and not(p.PlanetID()==o.PlanetID()):
                #logging.info('Allied Planet '+repr(o.PlanetID())+ ' might be reinforced!')
                to_send = o.PlanetID()
                nearest_enemy = o.NearestEnemy(i)
        if to_send>=0:
          #logging.info('Launching reinforcements!')
          pw.AddLaunch(p.PlanetID(),to_send,p.GetFreeTroops()+int(p.GetReinforcingTroops()/2))
          pw.CommitTroops(p,0,p.GetFreeTroops(),[p.FreeTroops()],p.ReinforcingTroops())


def LaunchAttack(pw):
  for p in pw.MyPlanets():
    if p.NearestEnemy() == pw.GetGlobalNearestEnemy():
      for o in pw.EnemyPlanets():
        if pw.Distance(p.PlanetID(),o.PlanetID())==pw.GetGlobalNearestEnemy():
          pw.AddLaunch(p.PlanetID(),o.PlanetID(),int(p.GetFreeTroops()/2+p.GetReinforcingTroops()/2))
          p.CommitTroops(0,int(p.GetFreeTroops()/2+p.GetReinforcingTroops()/2),[p.FreeTroops()],p.DefendingTroops())

def DoTurn(pw, turn):
  start_time = time.time()
  #logging.info('-------------------Starting the Main Loop-------------------------------')
  MainLoop(pw)
  #logging.info('-------------------Finished the Main Loop-------------------------------')
  #logging.info('-------------------Attacking Enemies------------------------------------')
  AttackEnemies(pw)
  #logging.info('-------------------Finished Attacking Enemies---------------------------')
  if 1:
    #logging.info('-------------------Activating Neutral Hunter----------------------------')
    to_attack = pw.RecursiveNeutralHunter(int(pw.MaxDistance()/2) )
    #logging.warning('Neutral Hunter said to attack '+repr(to_attack))
    for entry in to_attack:
      if entry[0]!=-1:
        pw.CommitTakeNeutral(pw.GetPlanet(entry[0]), entry[1])
    #logging.warning('Attacks Launched!')
    #logging.info('-------------------Leaving Neutral Hunter-------------------------------')
    
    #logging.info('-------------------Attacking Neutrals-----------------------------------')
    #AttackNeutrals(pw)
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
  #logging.info('This turn took '+repr(time.time()-start_time))


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
        #logging.info('====================================================================')
        #logging.info('==============Starting Turn ' + repr(turn) +'=================================')
        DoTurn(pw, turn)
        #logging.info('==============finished turn!========================================')
        #logging.info('====================================================================')
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
