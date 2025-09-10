from pygame.time import get_ticks

class Timer:
	def __init__(self, duration, func = None, repeat = False):
		self.duration = duration
		self.func = func
		self.start_time = 0
		self.active = False
		self.repeat = repeat

	def activate(self):
		self.active = True
		self.start_time = get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0
		if self.repeat:
			self.activate()

	def update(self):
		current_time = get_ticks()
		if current_time - self.start_time >= self.duration:
			if self.func and self.start_time != 0:
				self.func()
			self.deactivate()

	def time_left(self):
		if not self.active:
			return 0
		current_time = get_ticks()
		elapsed = current_time - self.start_time
		remaining = self.duration - elapsed
		return remaining
"""
	def time_taken(self):
		current_time = get_ticks()
		return (current_time - self.start_time)

	def time_left(self):
		current_time = get_ticks()
		elapsed = current_time - self.start_time
		remaining = self.duration - elapsed
		return max(remaining,0)
"""

