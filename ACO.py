import logging
import random


class ACO:
  def __init__(self, distances, neighbors, planet_ids):
    self._random_factor = 1
    self._decay_rate = .5
    self._num_runs = 50
    self._distances = distances
    self._neighbors = neighbors
    self._planet_ids = planet_ids
    self._ants = []
    self._pheremone_matrix = self._create_pheremone_matrix()

  '''
  Creates a pheremone matrix that covers all of the planets
  '''
  def _create_pheremone_matrix(self):
    logging.debug('creating the pheremone matrix')
    matrix = {}
    for p_id in self._planet_ids:
      matrix[p_id]={}
      for o_id in self._planet_ids:
        matrix[p_id][o_id]=0
    return matrix
    logging.debug('done')

  '''
  Initializes ants going in-between only the given planet_ids
  '''
  def _initialize_ants(self, planet_ids):
    logging.debug('creating ants')
    self._ants = []
    for p_id in planet_ids:
      matrix[p_id]={}
      for o_id in planet_ids:
        new_ant = Ant(p_id, o_id)
        self._ants.append(new_ant)
    logging.debug('done')


  '''
  _move should be called to move all ants that aren't finished one planet
  They will only consider going to planets that they haven't visited that are closer
  than the destination planet and that are in planet_ids

  '''
  def _move(self, planet_ids):
    done = 1
    logging.debug('starting a move action')
    for ant in self._ants:
      logging.debug('getting an ant')
      if not(ant.IsDone()):
        done = 0
        logging.debug('ant not at destination, continueing')
        move_options = []
        current_p_id = ant.GetCurrentPlanet()
        end_p_id = ant.GetEndPlant()
        history = ant.GetHistory()
        max_distance = self._distances[current_p_id][end_p_id]

        #Find all possible moves
        logging.debug('finding possible moves')
        for i in range(1, max_distance+1):
          for p in self._neighbors[current_p_id][i]:
            if not(p in history) and p in planet_ids:
              move_options.append([current_p_id,p])

        logging.debug('adding up total scent')
        #Figure out the total pheremon, add self._random_factor to each
        total = 0
        for entry in move_options:
          total += self._random_factor + self._pheremone_matrix[entry[0]][entry[1]]

        logging.debug('selecting path')
        #randomly select path to take
        to_send = random.random()*total

        logging.debug('finding selection')
        #find which path was chosen
        total = 0
        for entry in move_options:
          total += self._random_factor + self._pheremone_matrix[entry[0]][entry[1]]
          if total >= to_send:
            ant.MoveToPlanet(entry[1], self._distances[entry[0]][entry[1]])
            break

    return done


  def _update_paths(self, ant_network, score_network):
    for ant in self._ants:
      result = ant.GetResult()
      if result[0] < score_network[p.GetStartPlanet()][p.GetEndPlant()]:
        ant_network[p.GetStartPlanet()][p.GetEndPlant()] = result[1:3]

  def _add_pheremone(self, ant_network):
    for i in len(ant_network):
      for j in len(ant_network):
        path = ant_network[i][j][1]
        for k in len(path-1):
          self._pheremone_matrix[k][k+1]+=1




  def _decay_pheremone(self):
    for i in len(self._pheremone_matrix):
      for j in len(self._pheremone_matrix):
        self._pheremone_matrix[i][j] *= self._decay_rate


  '''
  The ant network had entries like [distance, path], we need to just have the next
  planet in the path, so path[1]
  '''
  def _trim_network(self, ant_network):
    for i in len(ant_network):
      for j in len(ant_network):
        ant_network[i][j]=ant_network[i][j][1][1]

  '''
  GetNetwork will return a matrix from the given planets with the next planet in line for each entry
  '''
  def GetNetwork(self, planet_ids):
    ant_network = {}
    score_network = {}
    for p in planet_ids:
      ant_network[p] = {}
      score_network[p] = {}
      for o in planet_ids:
        ant_network[p][o] = -1
        score_network[p][o] = 999999999999

    for i in range(self._num_runs):
      self._initialize_ants(planet_ids)

      done = 0
      while not(done):
        self._move(planet_ids)

      self._update_paths(ant_network, score_network)

      self._decay_pheremone()

      self._add_pheremone(ant_network)

    self._trim_network(ant_network)

    return ant_network


