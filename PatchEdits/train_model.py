import math
import yaml
import argparse
import numpy
import tensorflow as tf

from PatchEdits.data_reader import DataReader
from PatchEdits.metrics import MetricsTracker
from PatchEdits.tracker import Tracker
from PatchEdits.transformer_patching_model import TransformerPatchingModel

config = yaml.safe_load(open("config.yml"))

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def main():
	# Extract arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("data", help="File with pre-processed data (optional)")
	ap.add_argument("vocabulary", help="Vocabulary file (optional)")
	ap.add_argument("-s", "--suffix", help="Model and log-file suffix")
	args = ap.parse_args()
	print("Using configuration:", config)

	gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
	for gpu in gpus:
		tf.config.experimental.set_memory_growth(gpu, True)
	
	data = DataReader(config["data"], args.data, args.vocabulary)
	model = TransformerPatchingModel(config["transformer"], data.vocabulary.vocab_dim, is_pointer=config["data"]["edits"])
	train(model, data, suffix=args.suffix)

def train(model, data, suffix=None):
	optimizer = tf.optimizers.Adam(config["training"]["lr"])
	tracker = Tracker(model, suffix=suffix)
	model(tf.zeros((1, 2), 'int32'), tf.zeros((1, 2), 'int32'), tf.zeros((1, 2), 'int32'), tf.zeros((0, 0), 'int32'), True)
	tracker.restore()
	
	total_batches = 0
	current_epoch = tracker.ckpt.step.numpy()

	for epoch in range(current_epoch, config["training"]["num_epochs"]):
		print("Epoch:", epoch + 1)
		mbs = 0
		words = 0
		metrics = MetricsTracker()
		# Batcher returns a square index array and a binary mask indicating which words are padding (0) and real (1)
		for batch in data.batcher(mode="train"):
			mbs += 1
			total_batches += 1
			
			if config["data"]["edits"]:
				pre, pre_locs, post, pointer_locs = batch
			else:
				pre, pre_locs, post = batch
				pointer_locs = tf.zeros((0, 0), 'int32')
			samples = int(tf.reduce_sum(1 - tf.clip_by_value(pre, 0, 1)).numpy() + tf.reduce_sum(1 - tf.clip_by_value(post[:, 1:], 0, 1)).numpy())
			words += samples
			
			# Compute loss in scope of gradient-tape (can also use implicit gradients)
			with tf.GradientTape(watch_accessed_variables=False) as tape:
				tape.watch(model.trainable_variables)

				preds = model(pre, pre_locs, post[:, :-1], pointer_locs, training=True)
				if config["data"]["edits"]:
					preds, pointer_preds = preds
					loss = masked_ce_loss(post[:, 1:], preds, pointer_locs, pointer_preds)
					if numpy.any(numpy.isnan(loss)):
						print('bugs:', metrics.get_stats()[0])
						exit()
				else:
					loss = masked_ce_loss(post[:, 1:], preds)
			
			# Collect gradients, clip and apply
			grads = tape.gradient(loss, model.trainable_variables)
			grads, _ = tf.clip_by_global_norm(grads, 0.25)
			optimizer.apply_gradients(zip(grads, model.trainable_variables))
			
			# Update average loss and print if applicable
			if config["data"]["edits"]:
				metrics.add_observation(samples, post[:, 1:], preds, pointer_locs, pointer_preds)
			else:
				metrics.add_observation(samples, post[:, 1:], preds)
			if mbs % config["training"]["print_freq"] == 0:
				if config["data"]["edits"]:
					print("MB: {0}, bugs: {1}, tokens: {2}, entropy: {3}, acc: {4}, pointer acc: {5}, full seq acc: {6}".format(mbs, *metrics.get_stats()))
				else:
					print("MB: {0}, bugs: {1}, tokens: {2}, entropy: {3}, acc: {4}, full seq acc: {5}".format(mbs, *metrics.get_stats()))
				metrics.flush()
				if mbs % (5*config["training"]["print_freq"]) == 0:
					if config["data"]["edits"]:
						analyze_sample(data, pre, pre_locs, post, preds, pointer_locs, pointer_preds)
					else:
						analyze_sample(data, pre, pre_locs, post, preds)

		if metrics.total_acc_count > 0:
			if config["data"]["edits"]:
				print("MB: {0}, bugs: {1}, tokens: {2}, entropy: {3}, acc: {4}, pointer acc: {5}, full seq acc: {6}".format(mbs, *metrics.get_stats()))
			else:
				print("MB: {0}, bugs: {1}, tokens: {2}, entropy: {3}, acc: {4}, full seq acc: {5}".format(mbs, *metrics.get_stats()))

		tracker.save()
		# stats, top_k_accs = eval(model, data)
		# if config["data"]["edits"]:
		# 	bugs, tokens, entropy, accs, pointer_accs, full_accs = stats
		# 	print("Validation: bugs: {0}, tokens: {1}, entropy: {2}, accuracy: {3}, pointer acc: {4}, full seq accuracy: {5}".format(bugs, tokens, entropy, accs, pointer_accs, full_accs))
		# 	tracker.update(model, [full_accs, pointer_accs, *top_k_accs])
		# else:
		# 	bugs, tokens, entropy, accs, full_accs = stats
		# 	print("Validation: bugs: {0}, tokens: {1}, entropy: {2}, accuracy: {3}, full seq accuracy: {4}".format(bugs, tokens, entropy, accs, full_accs))
		# 	tracker.update(model, [full_accs, *top_k_accs])

def eval(model, data, validate=True):
	mbs = 0
	metrics = MetricsTracker()
	top_k_accs = [0.0]*config["data"]["beam_size"]
	for batch in data.batcher(mode="valid" if validate else "test"):
		if config["data"]["edits"]:
			pre, pre_locs, post, pointer_locs = batch
		else:
			pre, pre_locs, post = batch
			pointer_locs = tf.zeros((0, 0), 'int32')
		mbs += 1
		samples = int(tf.reduce_sum(1 - tf.clip_by_value(pre, 0, 1)).numpy() + tf.reduce_sum(1 - tf.clip_by_value(post[:, 1:], 0, 1)).numpy())
		preds = model(pre, pre_locs, post[:, :-1], pointer_locs, training=False)
		if config["data"]["edits"]:
			preds, pointer_preds = preds
		beams = model.predict(data.vocabulary, pre, pre_locs, config["data"]["beam_size"], config["data"]["max_bug_length"])
		targets = post[:, 1:].numpy().tolist()
		targets = [[t for t in tgt if t > 0] for tgt in targets]
		for ix, beam in enumerate(beams):
			for rank, (prob, locs, pred) in enumerate(beam):
				if pred[:len(targets[ix])] == targets[ix] and (not locs or locs == pointer_locs[ix].numpy().tolist()):
					top_k_accs[rank] += 1
					break
		if config["data"]["edits"]:
			metrics.add_observation(samples, post[:, 1:], preds, pointer_locs, pointer_preds)
		else:
			metrics.add_observation(samples, post[:, 1:], preds)
		if mbs % ((1 if validate else 5)*config["training"]["print_freq"]) == 0:
			if config["data"]["edits"]:
				analyze_sample(data, pre, pre_locs, post, preds, pointer_locs, pointer_preds)
			else:
				analyze_sample(data, pre, pre_locs, post, preds)
	for k in range(len(top_k_accs)):
		top_k_accs[k] /= metrics.total_samples
	print("Top K accuracies: {0}".format(", ".join(["{0}: {1:.2%}".format(ix + 1, acc) for ix, acc in enumerate(top_k_accs)])))
	return metrics.get_stats(), top_k_accs

# Prints a bug/repair pair with the (teacher-forced) generated fix for reference
def analyze_sample(data, pre, pre_locs, post, preds, pointer_locs=None, pointer_preds=None):
	offsets = [int(l) for l in pre_locs[0].numpy()]
	if pointer_locs is not None:
		pointer_locs = pointer_locs[0].numpy()
		max_pointers = tf.argmax(pointer_preds[0], -1).numpy()
		max_pointers[0] -= offsets[0]
		max_pointers[1] -= offsets[0]
		pointer_locs[0] -= offsets[0]
		pointer_locs[1] -= offsets[0]
		buggy_tokens = []
		for pos, ix in enumerate(pre[0, offsets[0]:offsets[1]].numpy()):
			if data.vocabulary.i2w[ix] == "<pad>": continue
			if pos == max_pointers[0]: buggy_tokens.append('>')
			if pos == pointer_locs[0]: buggy_tokens.append('^')
			buggy_tokens.append(data.vocabulary.i2w[ix])
			if pos == max_pointers[1]: buggy_tokens.append('<')
			if pos == pointer_locs[1]: buggy_tokens.append('$')
		buggy_tokens = data.vocabulary.undo_bpe(buggy_tokens)
	else:
		buggy_tokens = data.vocabulary.undo_bpe([data.vocabulary.i2w[ix] for ix in pre[0, offsets[0]:offsets[1]].numpy() if data.vocabulary.i2w[ix] != "<pad>"])
	real_fix_tokens = data.vocabulary.undo_bpe([data.vocabulary.i2w[ix] for ix in post[0, 1:].numpy() if data.vocabulary.i2w[ix] != "<pad>"])
	model_fix_tokens = data.vocabulary.undo_bpe([data.vocabulary.i2w[ix] for ix in tf.argmax(preds[0], -1).numpy()])[:len(real_fix_tokens)]
	print("Sample:", " ".join(buggy_tokens))
	print("  -->  ", " ".join(model_fix_tokens))
	print("Actual:", " ".join(real_fix_tokens))

# Compute cross-entropy loss, making sure not to include "masked" padding tokens
def masked_ce_loss(post_indices, preds, pointer_locs=None, pointer_preds=None):
	post_masks = tf.cast(tf.clip_by_value(post_indices, 0, 1), "float32")

	#print('Postmask:', post_masks)
	samples = tf.reduce_sum(post_masks)


	loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=post_indices, logits=preds)
	losstemp = loss
	loss *= post_masks
	#print('loss_sum:', tf.reduce_sum(loss))
	if numpy.any(numpy.isnan(tf.reduce_sum(loss))):
		print('loss', loss)
		print('losstemp', losstemp)
		print('postmasks', post_masks)

		print('post:', post_indices)
		print('preds:', preds)
		#exit()
	loss = tf.reduce_sum(loss) / samples
	if pointer_locs is not None:
		pointer_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=pointer_locs, logits=pointer_preds)
		if numpy.any(numpy.isnan(pointer_loss)):
			print("pointer_loss: ", pointer_loss)
			print("pointer_locs: ", pointer_locs)
			print("pointer_preds: ", pointer_preds)
		pointer_loss = tf.reduce_sum(pointer_loss, -1)
		pointer_loss = tf.reduce_mean(pointer_loss)
		loss += pointer_loss
	return loss


if __name__ == '__main__':
	main()
