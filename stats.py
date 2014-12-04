import os
from datetime import datetime
import argparse
from pprint import pprint as pp

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
		self.times_spent_in_queue_l = []

		self.gen_cars_sr = 0
		self.queue_sr = []
		self.queue_lengths_sr = []
		self.times_spent_in_queue_rs = []
		

	def enqueue(self, direction, time):
		if direction == "left":
			self.gen_cars_l += 1
			self.queue_l.append((self.gen_cars_l, time))
			self.queue_lengths_l.append(len(self.queue_l))
		elif direction == "straight_right":
			self.gen_cars_sr += 1
			self.queue_sr.append((self.gen_cars_sr, time))
			self.queue_lengths_sr.append(len(self.queue_sr))


	def dequeue(self, direction, time):
		if direction == "left":
			index, time_of_input = self.queue_l.pop(0)
			self.times_spent_in_queue_l.append(time-time_of_input)
		elif direction == "straight_right":
			index, time_of_input = self.queue_sr.pop(0)
			self.times_spent_in_queue_rs.append(time-time_of_input)


	def __get_average_queue_value(self, queue):
		try:
			return sum(queue) / float(len(queue))
		except:
			return 0


	def stats(self):
		print "=================================================================="
		print "| STATS FOR {0} LANE:".format(self.name.upper())
		print "| ------------------------"
		print "| Generated cars left            :", self.gen_cars_l
		print "| Average length of queue to left:", self.__get_average_queue_value(self.queue_lengths_l)
		print "| Actual length of queue to left :", len(self.queue_l)
		print "| Average time of waiting to left: {0} seconds".format(round(self.__get_average_queue_value(self.times_spent_in_queue_l),2))
		print "| "
		print "| Generated cars straight and right            :", self.gen_cars_sr 
		print "| Average length of queue to straight and right:", self.__get_average_queue_value(self.queue_lengths_sr)
		print "| Actual length of queue to straight and right :", len(self.queue_sr)
		print "| Average time of waiting to straight and right: {0} seconds".format(round(self.__get_average_queue_value(self.times_spent_in_queue_rs),2))
		print



class LaneType2():
	# one lane - left_straight_right

	def __init__(self):
		self.gen_cars = 0
		self.queue = []
		self.queue_lengths = []

		self.times_spent_in_queue = []


	def enqueue(self, direction, time):
		self.gen_cars += 1
		self.queue.append((self.gen_cars, time))
		self.queue_lengths.append(len(self.queue))


	def dequeue(self, direction, time):
		index, time_of_input = self.queue.pop(0)
		self.times_spent_in_queue.append(time-time_of_input)


	def __get_average_queue_value(self, queue):
		try:
			return sum(queue) / float(len(queue))
		except:
			print "exception"
			return 0


	def stats(self):
		print "=================================================================="
		print "| STATS FOR {0} LANE:".format(self.name.upper())
		print "| ------------------------"
		print "| Generated cars         :", self.gen_cars
		print "| Average length of queue:", self.__get_average_queue_value(self.queue_lengths)
		print "| Actual length of queue :", len(self.queue)
		print "| "
		print "| Average time of waiting: {0} seconds".format(round(self.__get_average_queue_value(self.times_spent_in_queue),2))
		print 
	

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


class Tram():
	def __init__(self):
		self.name = "tram"
		self.gen_trams = 0
		self.queue = []

		self.times_spent_in_queue = []


	def enqueue(self, time):
		self.gen_trams += 1
		self.queue.append((self.gen_trams, time))


	def dequeue(self, time):
		index, time_of_input = self.queue.pop(0)
		self.times_spent_in_queue.append(time-time_of_input)


	def __get_average_queue_value(self, queue):
		try:
			return sum(queue) / float(len(queue))
		except:
			print 0


	def stats(self):
		print "=================================================================="
		print "| STATS FOR TRAM:"
		print "| -------------------"
		print "| Generated trams        :", self.gen_trams
		print "| Average time of waiting: {0} seconds".format(round(self.__get_average_queue_value(self.times_spent_in_queue),2))
		print


class TelematicsStats():
	
	def __init__(self, stats_file):
		self.home = os.path.expanduser('~')
		self.default_stats_file = os.path.join(self.home, "renewlogs/telematics.log")
		self.lanes = ["ME", "OB", "KO", "KR"]
		self.important_labels = self.lanes + ["SearchQueue", "tram", "telematics"]
		self.direction_mapping = {
			"<"  :"left",
			"^>" :"straight_right",
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
		self.tram = Tram()

		self.__parse_input()


	def __parse_input(self):
		with open(self.stats_file, 'r+') as f:
			for line in f.readlines():
				(label, _, message) = line.split(' ',2)
				if any([label.startswith(important_label) for important_label in self.important_labels]):
					self.stats_lines.append(line)
		# get the last simulation
		for index, line in enumerate(self.stats_lines):
			if "New net instance telematics" in line:
				last_simulation_start = index
		self.stats_lines = self.stats_lines[last_simulation_start:]



	def __get_data_lane(self, line):
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
		else:
			data = None

		return data


	def __get_data_tram(self, line):
		process = line.split()[0].split('_')[-1]
		state_info = line.split()[2]
		data = {
			"process": process,
		}

		if "Removing" in state_info:
			data['state'] = "removing"
		elif "Putting" in state_info:
			data['state'] = "putting"
		else:
			data = None

		return data


	def get_stats(self):
		self.obilnak.stats()		
		self.konecnak.stats()	
		self.kravak.stats()
		self.mendlak.stats()
		self.tram.stats()


	def run(self):
		for line in self.stats_lines:
			# advancing time
			if line.startswith("SearchQueue"):
				self.time = float(line.split()[-1])
			# process lanes
			elif any([line.startswith(lane) for lane in self.lanes]):
				try:
					data = self.__get_data_lane(line)
					if not data:
						continue
				except:
					continue
				if data['process'] == "waiting" and data['state'] == "putting":
					data['lane'].enqueue(data['direction'], self.time)
				elif data['process'] == "waiting" and data['state'] == "removing":
					data['lane'].dequeue(data['direction'], self.time)
			# process tram
			elif line.startswith("tram"):
				try:
					data = self.__get_data_tram(line)
					if not data:
						continue
				except:
					continue
				if data['process'] == "waiting" and data['state'] == "putting":
					self.tram.enqueue(self.time)
				elif data['process'] == "waiting" and data['state'] == "removing":
					self.tram.dequeue(self.time)

		# print all gathered stats			
		self.get_stats()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--input', type=str)
	stats_file = parser.parse_args().input

	stats = TelematicsStats(stats_file)
	stats.run()