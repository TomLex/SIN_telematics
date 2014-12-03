import os
from datetime import datetime
import argparse

__author__ = "Tomas Varga"
__editor__ = "Barbora Netkova"


class LaneType1():
	# two lanes - left and straight_right
	# l  = left
	# rs = right straight

	def __init__(self):
		self.gen_cars_l = 0
		self.queue_l = []
		self.queue_lengths_l = []

		self.gen_cars_sr = 0
		self.queue_sr = []
		self.queue_lengths_sr = []

	def queue(self, direction=None):
		if direction == "left":
			self.gen_cars_l += 1
			self.queue_l.append(self.gen_cars_l)
			self.queue_lengths_l.append(len(self.queue_l))
		elif direction == "straight_right":
			self.gen_cars_sr += 1
			self.queue_sr.append(self.gen_cars_sr)
			self.queue_lengths_sr.append(len(self.queue_sr))

	def dequeue(self, direction=None):
		if direction == "left":
			self.queue_l.pop()
		elif direction == "straight_right":
			self.queue_sr.pop()

	def __get_average_queue_length(self, queue):
		try:
			return sum(queue) / float(len(queue))
		except:
			return 0

	def stats(self):
		print "=================================================================="
		print "STATS FOR {0}:".format(self.name.upper())
		print "------------------"
		print "Generated cars left            :", self.gen_cars_l
		print "Length of queue to left        :", len(self.queue_l)
		print "Average length of queue to left:", self.__get_average_queue_length(self.queue_lengths_l)
		print
		print "Generated cars straight and right            :", self.gen_cars_sr 
		print "Length of queue to straight and right        :", len(self.queue_sr)
		print "Average length of queue to straight and right:", self.__get_average_queue_length(self.queue_lengths_sr)
		print "=================================================================="


class LaneType2():
	# one lane - left_straight_right

	def __init__(self):
		self.gen_cars = 0
		self.queue = []
		self.queue_lengths = []

	def queue(self):
		self.gen_cars += 1
		self.queue.append(self.gen_cars)
		self.queue_lengths.append(len(self.queue))

	def dequeue(self):
		self.queue.pop()
	

class Obilnak(LaneType1):
	def __init__(self):
		LaneType1.__init__(self)
		self.name = "obilnak"


class Mendlak(LaneType1):
	def __init__(self):
		LaneType1.__init__(self)
		self.name = "mendlak"


class Konecnak(LaneType1):
	def __init__(self):
		LaneType1.__init__(self)
		self.name = "konecnak"


class Kravak(LaneType2):
	def __init__(self):
		LaneType2.__init__(self)
		self.name = "kravak"


class TelematicsStats():
	
	def __init__(self, stats_file):
		self.home = os.path.expanduser('~')
		self.default_stats_file = os.path.join(self.home, "renewlogs/telematics.log")
		self.lanes = ["ME", "OB", "KO", "KR"]
		self.important_labels = self.lanes + ["SearchQueue"]
		self.direction_mapping = {
			"<"  :"left",
			"^>" :"right_straight",
			"<^>":"all"
		}

		if stats_file:
			self.stats_file = stats_file
		else:
			self.stats_file = self.default_stats_file
		self.stats_lines = []

		self.time = 0.0
		self.obilnak = Obilnak()
		self.mendlak = Mendlak()
		self.konecnak = Konecnak()
		self.kravak = Kravak()
		self.lane_mapping = {
			"OB" : self.obilnak,
			"KO" : self.konecnak,
			"ME" : self.mendlak,
			"KR" : self.kravak
		}

		self.__parse_input()


	def __parse_input(self):
		with open(self.stats_file, 'r+') as f:
			for line in f.readlines():
				(label, _, message) = line.split(' ',2)
				if any([label.startswith(important_label) for important_label in self.important_labels]):
					self.stats_lines.append(line)


	def __get_data(self, line):
		lane_info = line.split()[0].split('_')
		state_info = line.split()[2]
		data = {
			"lane"     : self.lane_mapping[lane_info[0]],
			"process"  : lane_info[1],
			"direction": self.direction_mapping[lane_info[2]],
		}

		if "Removing" in state_info:
			data['state'] = "removing"
		elif "Putting" in state_info:
			data['state'] = "putting"
		return data


	def run(self):
		for line in self.stats_lines[:5]:
			# advancing time
			if line.startswith("SearchQueue"):
				self.time += line.split()[-1]
			# process obilnak
			elif any([line.startswith(lane) for lane in self.lanes]):
				try:
					data = self.__get_data(line)
				except:
					continue
				if data['process'] == "waiting" and data['state'] == "putting":
					data['lane'].queue(direction=data['direction'])
				elif data['process'] == "waiting" and data['state'] == "removing":
					data['lane'].dequeue(direction=data['direction'])

		self.obilnak.stats()		
		self.konecnak.stats()			

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', type=str)
	stats_file = parser.parse_args().input

	stats = TelematicsStats(stats_file)
	stats.run()