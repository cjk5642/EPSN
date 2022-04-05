class SportNotAllowedError(Exception):
  def __init__(self, sport: str):
    self.sport = sport
    self.message = f"{self.sport} is not allowed"
    super().__init__(self.message)