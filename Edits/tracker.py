import os
import time

import tensorflow as tf

class Tracker(object):
	def __init__(self, model, model_path='models', log_path='log.txt', suffix=None):
		self.log_path = log_path
		self.model_path = model_path
		if suffix is not None:
			if self.log_path.endswith(".txt"):
				self.log_path = self.log_path[:-4] + "-" + suffix + ".txt"
			else:
				self.log_path += "-" + suffix
			self.model_path += "-" + suffix
		self.ckpt = tf.train.Checkpoint(model=model, step=tf.Variable(0), samples=tf.Variable(0), time=tf.Variable(0.0))
		self.manager = tf.train.CheckpointManager(self.ckpt, self.model_path, max_to_keep=None)
		
		self.log = []
		if os.path.exists(self.log_path):
			with open(self.log_path) as f:
				for l in f:
					l = l.rstrip().split(': ')
					scores = [float(v.replace('%', ''))/100 if '%' in v else v for v in l[1].split(',')]
					self.log.append((l[0], scores))
	
	def restore(self, best_only=False):
		if self.manager.checkpoints:
			if best_only:
				best = max(enumerate(self.log), key=lambda e: e[1][1][0])[0] # e[1][1] just selects the list of accuracies; the final index controls the specific value used.
				print("Restoring top checkpoint:", best + 1)
				status = self.ckpt.restore(self.manager.checkpoints[best])
			else:
				status = self.ckpt.restore(self.manager.latest_checkpoint)
			status.assert_existing_objects_matched()
			status.assert_consumed()		
		self.time = time.time()
	
	def update(self, model, scores):
		self.ckpt.step.assign_add(1)
		self.ckpt.time.assign_add(time.time() - self.time)
		self.time = time.time()
		
		s = self.ckpt.step.numpy()
		c = self.ckpt.samples.numpy()
		t = self.ckpt.time.numpy()
		self.log.append(((s, t), scores))
		with open(self.log_path, 'a') as f:
			f.write(str(s))
			f.write(', ')
			f.write(str(c))
			f.write(', ')
			f.write('{0:.3f}'.format(t))
			f.write(': ')
			f.write(', '.join([s if isinstance(s, str) else '{0:.2%}'.format(s) for s in scores]))
			f.write('\n')
		self.manager.save()


	def save(self):
		self.manager.save()