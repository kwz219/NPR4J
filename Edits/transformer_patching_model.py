import math

import numpy as np
import tensorflow as tf

from transformer import Transformer

class TransformerPatchingModel(tf.keras.Model):
	def __init__(self, model_config, vocab_dim, is_pointer=False):
		super(TransformerPatchingModel, self).__init__()
		self.vocab_dim = vocab_dim
		self.is_pointer = is_pointer
		self.transformer_enc = Transformer(model_config, vocab_dim)
		self.transformer_dec = Transformer(model_config, vocab_dim, shared_embedding=self.transformer_enc.embed, bias_dim=4)
		if self.is_pointer:
			self.pointer_pred = tf.keras.layers.Dense(2)
	
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None), dtype=tf.int32), tf.TensorSpec(shape=(None, None), dtype=tf.int32), tf.TensorSpec(shape=(None, None), dtype=tf.int32), tf.TensorSpec(shape=(None, None), dtype=tf.int32), tf.TensorSpec(shape=None, dtype=tf.bool)])
	def call(self, pre_indices, pre_locs, post_indices, pointer_locs, training=True):
		batch_dim = tf.shape(pre_indices)[0]
		pre_len = tf.shape(pre_indices)[-1]
		post_len = tf.shape(post_indices)[-1]

		enc_mask = tf.cast(tf.clip_by_value(pre_indices, 0, 1), 'float32')
		enc_mask = tf.reshape(enc_mask, [batch_dim, 1, 1, pre_len])
		enc_state = self.transformer_enc((pre_indices,), (enc_mask,), training)
		
		post_mask = tf.cast(tf.clip_by_value(post_indices, 0, 1), 'float32')
		post_mask = tf.reshape(post_mask, [batch_dim, 1, post_len, 1])
		post_seq_mask = self.transformer_dec.get_sequence_mask(post_len)
		post_seq_mask = tf.reshape(post_seq_mask, [1, 1, post_len, post_len])
		post_enc_mask = enc_mask * post_mask
		
		start_end_mask = tf.cast(tf.sequence_mask(pre_locs[:, 1], pre_len), 'int32')
		start_end_mask -= tf.cast(tf.sequence_mask(pre_locs[:, 0]-1, pre_len), 'int32')

		in_biases = tf.tile(tf.expand_dims(start_end_mask, 1), [1, post_len, 1])
		in_biases = tf.cast(tf.where(tf.greater(in_biases, 0)), 'int32')
		in_biases = tf.pad(in_biases, [[0, 0], [0, 1]])
		
		# If predicting edits, update input biases to specifically identify the start and end (edit) pointers
		if tf.shape(pointer_locs)[0] > 0:
			loc_bias = tf.stack([tf.range(batch_dim), pointer_locs[:, 0]], axis=1)
			loc_bias = tf.scatter_nd(loc_bias, tf.ones(batch_dim), tf.shape(start_end_mask))
			loc_bias = tf.tile(tf.expand_dims(loc_bias, 1), [1, post_len, 1])
			loc_bias = tf.cast(tf.where(tf.greater(loc_bias, 0)), 'int32')
			loc_bias = tf.concat([loc_bias, tf.fill((tf.shape(loc_bias)[0], 1), 2, 'int32')], axis=1)
			
			rem_bias = tf.stack([tf.range(batch_dim), pointer_locs[:, 1]], axis=1)
			rem_bias = tf.scatter_nd(rem_bias, tf.ones(batch_dim), tf.shape(start_end_mask))
			rem_bias = tf.tile(tf.expand_dims(rem_bias, 1), [1, post_len, 1])
			rem_bias = tf.cast(tf.where(tf.greater(rem_bias, 0)), 'int32')
			rem_bias = tf.concat([rem_bias, tf.fill((tf.shape(rem_bias)[0], 1), 3, 'int32')], axis=1)
			
			in_biases = tf.concat([in_biases, loc_bias, rem_bias], axis=0)
		
		dec_state = self.transformer_dec((post_indices, enc_state), (post_seq_mask, post_enc_mask), training, in_biases)
		preds = self.transformer_dec.predict(dec_state)
		if self.is_pointer:
			pointer_preds = self.pointer_pred(enc_state)
			pointer_preds += (1.0 - tf.expand_dims(tf.cast(start_end_mask, 'float32'), -1)) * tf.float32.min
			pointer_preds = tf.transpose(pointer_preds, [0, 2, 1])
			return preds, pointer_preds
		else:
			return preds
	
	# Beam searches patches given a bug
	def predict(self, vocabulary, pre_indices, pre_locs, beam_size, max_expansions):
		batch_dim = int(tf.shape(pre_indices)[0].numpy())
		pre_len = tf.shape(pre_indices)[-1]
		
		start_end_mask = tf.cast(tf.sequence_mask(pre_locs[:, 1], pre_len), 'int32')
		start_end_mask -= tf.cast(tf.sequence_mask(pre_locs[:, 0]-1, pre_len), 'int32')

		# Pre-compute encoder states for all buggy lines
		pre_mask = tf.cast(tf.clip_by_value(pre_indices, 0, 1), "float32")
		pre_mask = tf.reshape(pre_mask, [batch_dim, 1, 1, pre_len])
		pre_states = self.transformer_enc((pre_indices,), (pre_mask,), training=False)
		
		if self.is_pointer:
			pointer_preds = self.pointer_pred(pre_states)
			pointer_preds += (1.0 - tf.expand_dims(tf.cast(start_end_mask, 'float32'), -1)) * tf.float32.min
			pointer_preds = tf.transpose(pointer_preds, [0, 2, 1])
		
		pre_states = tf.split(pre_states, batch_dim)
		pre_mask = tf.split(pre_mask, batch_dim)
		start_end_mask = tf.expand_dims(start_end_mask, 1)
		start_end_mask = tf.split(start_end_mask, batch_dim)
		
		if self.is_pointer:
			per_side = math.ceil(math.sqrt(beam_size))
			probs, ixes = tf.math.top_k(tf.nn.softmax(pointer_preds), k=per_side)
			probs = tf.transpose(probs, [0, 2, 1]).numpy()
			ixes = tf.transpose(ixes, [0, 2, 1]).numpy()
			results = {}
			for ix in range(batch_dim):
				results[ix] = []
				for i in range(per_side):
					for j in range(per_side):
						pointers = [ixes[ix][i][0], ixes[ix][j][1]]
						entropy = -math.log2(probs[ix][i][0] * probs[ix][j][1] + 1e-7)
						sample = (entropy, False, pointers, [vocabulary.w2i["<s>"]])
						results[ix].append(sample)
						if len(results[ix]) == beam_size: break
					if len(results[ix]) == beam_size: break
		else:
			results = {ix: [(0.0, False, [], [vocabulary.w2i["<s>"]])] for ix in range(batch_dim)} # source_ix: (entropy, is_completed, indices)
		
		for step in range(max_expansions):
			# Extract sequences to complete (those that aren't done yet)
			to_process = {ix: [r for r in res if not r[1]] for ix, res in results.items()}
			to_process = {ix: res for ix, res in to_process.items() if len(res) > 0}
			if len(to_process) == 0: break
			
			in_states = tf.concat([tf.tile(pre_states[ix], [len(to_proc), 1, 1]) for ix, to_proc in to_process.items()], axis=0)
			in_masks = tf.concat([tf.tile(pre_mask[ix], [len(to_proc), 1, 1, 1]) for ix, to_proc in to_process.items()], axis=0)
			in_start_end_mask = tf.concat([tf.tile(start_end_mask[ix], [len(to_proc), 1, 1]) for ix, to_proc in to_process.items()], axis=0)
			if self.is_pointer:
				in_pointer_locs = tf.stack([t[2] for to_proc in to_process.values() for t in to_proc], axis=0)
				batch_indices = tf.range(sum(len(to_proc) for to_proc in to_process.values()))
			
			# Flatten input for easy access
			to_process = [(ix, *r) for ix, res in to_process.items() for r in res]
			post_indices = tf.constant([inp[-1] for inp in to_process])
			
			# Run decoding transformer
			post_masks = tf.ones_like(post_indices, dtype='float32')
			post_masks = tf.expand_dims(tf.expand_dims(post_masks, 1), 1)
			in_biases = tf.tile(in_start_end_mask, [1, step + 1, 1])
			in_biases = tf.cast(tf.where(tf.greater(in_biases, 0)), 'int32')
			in_biases = tf.pad(in_biases, [[0, 0], [0, 1]])
			if self.is_pointer:
				in_start_end_mask = tf.squeeze(in_start_end_mask, 1)
				loc_bias = tf.stack([batch_indices, in_pointer_locs[:, 0]], axis=1)
				loc_bias = tf.scatter_nd(loc_bias, tf.ones(tf.shape(loc_bias)[0]), tf.shape(in_start_end_mask))
				loc_bias = tf.tile(tf.expand_dims(loc_bias, 1), [1, step + 1, 1])
				loc_bias = tf.cast(tf.where(tf.greater(loc_bias, 0)), 'int32')
				loc_bias = tf.concat([loc_bias, tf.fill((tf.shape(loc_bias)[0], 1), 2, 'int32')], axis=1)
				
				rem_bias = tf.stack([batch_indices, in_pointer_locs[:, 1]], axis=1)
				rem_bias = tf.scatter_nd(rem_bias, tf.ones(tf.shape(rem_bias)[0]), tf.shape(in_start_end_mask))
				rem_bias = tf.tile(tf.expand_dims(rem_bias, 1), [1, step + 1, 1])
				rem_bias = tf.cast(tf.where(tf.greater(rem_bias, 0)), 'int32')
				rem_bias = tf.concat([rem_bias, tf.fill((tf.shape(rem_bias)[0], 1), 3, 'int32')], axis=1)
				
				in_biases = tf.concat([in_biases, loc_bias, rem_bias], axis=0)
			
			post_states = self.transformer_dec((post_indices, in_states), (post_masks, in_masks,), False, in_biases)
			post_states = post_states[:, -1:] # We are only interested in the last value
			preds = self.transformer_dec.predict(post_states)
			preds = tf.squeeze(preds, 1)
			
			# Get top-k predictions for each bug-fix
			probs, ixes = tf.math.top_k(tf.nn.softmax(preds), k=max(25, beam_size))
			new_results = {}
			probs = probs.numpy()
			ixes = ixes.numpy()
			new_results = {}
			for seq_ix in range(len(probs)):
				old_patch = to_process[seq_ix]
				index = old_patch[0]
				res = results[index]
				del res[res.index(old_patch[1:])]
				if index not in new_results:
					new_results[index] = []
				for pred_ix in range(beam_size):
					prob = probs[seq_ix][pred_ix]
					pred = ixes[seq_ix][pred_ix]
					ent = -math.log2(prob + 1e-7)
					is_done = vocabulary.i2w[pred] == "</s>"
					new_results[index].append((old_patch[1] + ent, is_done, old_patch[3], list(old_patch[4])+[pred]))
			for seq_ix in results.keys():
				if seq_ix not in new_results:
					continue
				results[seq_ix].extend(new_results[seq_ix])
				results[seq_ix] = sorted(results[seq_ix], key=lambda res: res[0])[:beam_size]
		
		# Clean up results before returning.
		for ix in results.keys():
			results[ix] = [(res[0], res[2], res[-1][1:]) for res in results[ix]]
			results[ix] = sorted(results[ix], key=lambda res: res[0])
			results[ix] = results[ix][:beam_size]
		results = [results[ix] for ix in sorted(results.keys())]
		return results