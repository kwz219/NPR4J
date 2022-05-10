import math
import yaml
import argparse

import numpy as np
import tensorflow as tf

from data_reader import DataReader
from metrics import MetricsTracker
from tracker import Tracker
from transformer_patching_model import TransformerPatchingModel

config = yaml.safe_load(open("config.yml"))

def main():
	# Extract arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("data", help="Data file containing bugs")
	ap.add_argument("vocabulary", help="Vocabulary file")
	ap.add_argument("-s", "--suffix", help="Model and log-file suffix")
	args = ap.parse_args()
	
	data = DataReader(config["data"], data_file=args.data, vocab_path=args.vocabulary)
	model = TransformerPatchingModel(config["transformer"], data.vocabulary.vocab_dim, is_pointer=config["data"]["edits"])
	
	# Restore model after a simple init
	tracker = Tracker(model, suffix=args.suffix)
	model(tf.zeros((1, 2), 'int32'), tf.zeros((1, 2), 'int32'), tf.zeros((1, 2), 'int32'), tf.zeros((0, 0), 'int32'), True)
	tracker.restore(best_only=False)

	print("Start predicting")
	with open("results" + ("" if args.suffix is None else "-" + args.suffix) + ".txt", "w") as f_out:
		idx=0
		for batch in data.batcher(mode="test", optimize_packing=False):
			if idx < 62:
				print(idx,len(batch))
				idx+=1
				continue
			pre, pre_locs = batch[:2]

			preds = model.predict(data.vocabulary, pre, pre_locs, config["data"]["beam_size"], config["data"]["max_bug_length"])
			print(idx,"predict finished")
			
			write_completions(f_out, data.vocabulary, pre.numpy(), pre_locs.numpy(), preds)
			print(idx, "write finished")

def write_completions(f_out, vocabulary, bugs, bug_locs, completions, pointer_locs=None):
	for bug_ix, comp_list in enumerate(completions):
		f_out.write('\n')
		if not comp_list:
			f_out.write('\n')
			continue
		bug_subtokens = [vocabulary.i2w[ix] for ix in bugs[bug_ix]]
		if '<pad>' in bug_subtokens:
			bug_subtokens = bug_subtokens[:bug_subtokens.index('<pad>')]
		if config["data"]["add_context"]:
			bug_subtokens = bug_subtokens[bug_locs[bug_ix][0]:bug_locs[bug_ix][1]]
		bug = vocabulary.undo_bpe(bug_subtokens)
		bug = "\t".join(bug)
		f_out.write(bug)
		f_out.write('\n')
		fix_probs = [math.exp(-p) for p, _, _ in comp_list]
		fix_probs_total = sum(fix_probs)
		fix_probs = [p/fix_probs_total for p in fix_probs]
		for ix, (_, pointer_locs, bug_fix) in enumerate(comp_list):
			fix_prob = fix_probs[ix]
			fix_ent = -math.log2(fix_prob + 1e-9)
			fix_subtokens = [vocabulary.i2w[b] for b in bug_fix]
			if '</s>' in fix_subtokens:
				fix_subtokens = fix_subtokens[:fix_subtokens.index('</s>')]
			if pointer_locs:
				pointer_locs[0] -= bug_locs[bug_ix][0]
				pointer_locs[1] -= bug_locs[bug_ix][0]
				bug_fix = bug_subtokens[:pointer_locs[0]]
				bug_fix += fix_subtokens
				if pointer_locs[1] > 0 or pointer_locs[0] == 0:
					bug_fix += bug_subtokens[pointer_locs[1] + 1:]
				else:
					bug_fix += bug_subtokens[pointer_locs[0]:]
			else:
				bug_fix = fix_subtokens
			bug_fix = "\t".join(vocabulary.undo_bpe(bug_fix))
			f_out.write('{0:.2%}'.format(fix_prob))
			f_out.write(': ')
			f_out.write(bug_fix)
			f_out.write('\n')
			if ix == 0:
				print("{0:.3f}/{1:.2%}, {2}  -->  {3}".format(fix_ent, fix_prob, " ".join(bug.split("\t")), " ".join(bug_fix.split("\t"))))


if __name__ == '__main__':
	main()
