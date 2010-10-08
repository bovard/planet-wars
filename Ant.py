class Ant:
  def __init__(self, start_p_id, end_p_id):
    self._start_p_id = start_p_id
    self._current_p_id = start_p_id
    self._hitory = []
    self._score = 0
    self._distance_travelled = 0
    self._end_p_id = end_p_id

  def MoveToPlanet(self, dest_id, distance):
    self._history.append(self._current_p_id)
    self._distance_travelled += distance
    self._score += distance**2
    self._current_p_id = dest_id
    if dest_id == self._end_p_id:
      return self._score
    return 0

  def GetCurrentPlanet(self):
    return self._current_p_id

  def GetStartPlanet(self):
    return self._start_p_id

  def GetEndPlant(self):
    return self._end_p_id

  def GetHistory(self):
    return self._history

  def IsDone(self):
    return self._current_p_id == self._end_p_id

  def GetResult(self):
    return [self._score, self._distance_travelled, self._hitory]