
# Multiprocessing code for qubricks
# Inspired by: http://stackoverflow.com/questions/3288595/multiprocessing-using-pool-map-on-a-function-defined-in-a-class

#WARNING: This module is currently under development.

import Queue
import multiprocessing, traceback, logging, resource
import sys, gc
import warnings
import datetime

heap = None
def set_heap(hp):
	global heap
	heap = hp

def get_heap(hp):
	global heap
	return heap

def error(msg, *args):
	return multiprocessing.get_logger().error(msg, *args)

def warn(msg, *args):
	return multiprocessing.get_logger().warn(msg, *args)

def spawn(f):
	def fun(q_in, q_out):
		warnings.simplefilter("ignore")
		initial_memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
		while True:
			i, args, kwargs = q_in.get()
			if i is None:
				break
			
			try:
				r = f(*args, **kwargs)
			except Exception as e:
				error(traceback.format_exc())
				raise e

			q_out.put((i, r))
			
			gc.collect()
			
			if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > 2*initial_memory_usage:
				warn('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
			
	return fun

def spawnonce(f):
	def fun(q_in, q_out):
		warnings.simplefilter("ignore")

		i, args, kwargs = q_in.get()
		if i is None:
			return
		
		r = None
		try:
			r = f(*args, **kwargs)
		except Exception as e:
			error(traceback.format_exc())
			raise e

		q_out.put((i, r))
			
	return fun

class AsyncParallelMap(object):

	def __init__(self, f, progress=False, nprocs=None, spawnonce=True):
		multiprocessing.log_to_stderr(logging.WARN)
		if nprocs is None:
			self.nprocs = multiprocessing.cpu_count()
		else:
			self.nprocs = multiprocessing.cpu_count() + nprocs if nprocs < 0 else nprocs
		self.proc = []
		self.progress = progress
		self.spawnonce = spawnonce
		self.f = f

	def reset(self, f, count_offset=None,count_total=None):
		self.f = f
		
		self.count_offset = count_offset
		self.count_total = count_total
		
		self.results = []
		self.start_time = None
		
		self.q_in = multiprocessing.Queue(1 if not spawnonce else self.nprocs)
		self.q_out = multiprocessing.Queue()
		
		while len(self.proc) > 0:
			self.proc.pop().terminate()
		if not self.spawnonce:
			self.proc = [multiprocessing.Process(target=spawn(self.f), args=(self.q_in, self.q_out)) for _ in range(self.nprocs)]
			for p in self.proc:
				p.daemon = True
				p.start()

	def __sweep_results(self):
		while True:
			try:
				self.results.append(self.q_out.get(timeout=0.01))
			except Queue.Empty:
				break
			except:
				break

	def __print_progress(self, count):
		
		current = len(self.results) + self.count_offset if self.count_offset is not None else 0
		total = count + self.count_offset if self.count_total is None else self.count_total
		
		progress = float(current) / total
		sys.stderr.write("\r %3d%% | %d of %d | Memory usage: %.2f MB" % (
								progress * 100,
								current, 
								total, 
								resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.)
						)
		
		if progress > 0:
			delta = datetime.datetime.now() - self.start_time
			delta = datetime.timedelta( delta.total_seconds()/24/3600 * (1-progress)/progress )
			sys.stderr.write(" | Remaining: %02dd:%02dh:%02dm:%02ds" % (
					delta.days,
					delta.seconds/3600,
					delta.seconds/60 % 60,
					delta.seconds % 60
				)
			)
		
		if current == total:
			sys.stderr.write('\n')
		
		sys.stderr.flush()


	def map(self, X, count_offset=None,count_total=None,start_time=None):
		self.reset(self.f,count_offset=count_offset,count_total=count_total)
		
		self.start_time = start_time if start_time is not None else datetime.datetime.now()
		count = len(X)
		if not self.spawnonce:
			X = X + [(None, None, None)] * self.nprocs  # add sentinels

		for i, x in enumerate(X):
			
			if self.spawnonce and len(self.results) + self.nprocs <= i:  # Wait for processes to finish before starting new ones
				self.results.append(self.q_out.get())
			self.q_in.put(x)
			if self.spawnonce:
				self.proc.append(multiprocessing.Process(target=spawnonce(self.f), args=(self.q_in, self.q_out)))
				self.proc[-1].daemon = False
				self.proc[-1].start()
				while len(self.proc) > 2*self.nprocs:
					p = self.proc.pop(0)
					if not p.is_alive():
						p.terminate()
						del p
			
			self.__sweep_results()

			gc.collect()
			if self.progress:
				self.__print_progress(count)

		self.q_in.close()
		
		while len(self.results) < len(X) - (self.nprocs if not self.spawnonce else 0):
			self.results.append(self.q_out.get())
			if self.progress:
				self.__print_progress(count)
		
		if not self.spawnonce:
			[p.terminate() if p.is_alive() else False for p in self.proc]
		
		return [(i, x) for i, x in sorted(self.results)]

