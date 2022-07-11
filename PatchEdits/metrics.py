import numpy as np
import tensorflow as tf

log_2_e = 1.44269504089 # Constant to convert to binary entropies

class MetricsTracker():
	def __init__(self, top_10=False):
		self.total_tokens = 0
		self.total_samples = 0
		self.flush()
	
	def flush(self, flush_totals=False):
		if flush_totals:
			self.total_tokens = 0
			self.total_samples = 0
		self.loss = 0.0
		self.acc = 0.0
		self.pointer_acc = 0.0
		self.pointer_acc_count = 0
		self.acc_count = 0
		self.total_acc = 0.0
		self.total_acc_count = 0
	
	def add_observation(self, num_tokens, targets, predictions, pointer_locs=None, pointer_preds=None):
		padding = tf.cast(tf.clip_by_value(targets, 0, 1), "float32")
		target_tensor = tf.cast(tf.one_hot(targets, predictions.shape[-1]), "float32")
		
		# Compute overall statistics, gathering types and predictions accordingly
		self.loss += log_2_e * tf.reduce_sum(padding*tf.nn.softmax_cross_entropy_with_logits(labels=target_tensor, logits=predictions))
		self.acc += tf.reduce_sum(padding*tf.metrics.sparse_categorical_accuracy(tf.constant(targets), predictions))
		self.acc_count += tf.reduce_sum(padding).numpy()
		whole_seq_acc = tf.reduce_prod((1-padding) + padding*tf.metrics.sparse_categorical_accuracy(tf.constant(targets), predictions), -1)
		
		if pointer_locs is not None:
			pointers_acc = tf.metrics.sparse_categorical_accuracy(pointer_locs, pointer_preds)
			pointers_acc = tf.reduce_prod(pointers_acc, -1)
			self.pointer_acc += tf.reduce_sum(pointers_acc)
			self.pointer_acc_count += targets.shape[0]
			whole_seq_acc *= pointers_acc
		
		self.total_acc += tf.reduce_sum(whole_seq_acc)
		self.total_acc_count += targets.shape[0]
		
		self.total_tokens += num_tokens
		self.total_samples += len(targets)
	
	def get_stats(self):
		avg_loss = self.loss.numpy()/self.acc_count if self.acc_count > 0 else 0.0
		avg_acc = self.acc.numpy()/self.acc_count if self.acc_count > 0 else 0.0
		avg_total_acc = self.total_acc.numpy()/self.total_acc_count if self.total_acc_count > 0 else 0.0
		
		if self.pointer_acc_count > 0:
			avg_pointer_acc = self.pointer_acc.numpy() / self.pointer_acc_count
			return self.total_samples, self.total_tokens, "{0:.3f}".format(avg_loss), "{0:.2%}".format(avg_acc), "{0:.2%}".format(avg_pointer_acc), "{0:.2%}".format(avg_total_acc)
		else:
			return self.total_samples, self.total_tokens, "{0:.3f}".format(avg_loss), "{0:.2%}".format(avg_acc), "{0:.2%}".format(avg_total_acc)
