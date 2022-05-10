import os
import random
random.seed(41)

import tensorflow as tf

from vocabulary import VocabularyBuilder

class DataReader(object):
	
	def __init__(self, data_config, data_file, vocab_path):
		self.config = data_config
		self.add_context = data_config["add_context"]
		self.train_data, self.valid_data, self.test_data = self.load_processed_data(data_file)
		
		self.vocabulary = VocabularyBuilder(vocab_path=vocab_path)
		print("Finished loading data, sizes :")
		print("Vocabulary: %d" % self.vocabulary.vocab_dim)
		print("Lines: %d" % len(self.test_data))
		print("Words: %d" % sum([len([w for w in l1 if w != '\n']) + len([w for w in l2 if w != '\n']) for l1, _, l2 in self.test_data]))
	
	def load_processed_data(self, data_file):
		data = {}
		with open(data_file, "r", encoding="utf-8") as f:
			ix = 0
			for l in f:
				if len(l.strip()) == 0: continue
				try:
					ix += 1
					p = l.rstrip().split("###")
					p = [piece.strip() for piece in p]
					key = p[0]
					inds = [int(ix) for ix in p[2].split()]
					bug = p[1].split()[inds[0]:inds[1]]
					patch = p[3].split()[1:-1]
					pre, post = (p[1].split(), p[3].split())
					pre_locs = [int(i) for i in p[2].split()]
					if key not in data: data[key] = []
					if not self.add_context:
						pre = pre[pre_locs[0]:pre_locs[1]+1]
						pre_locs = [0, pre_locs[1] - pre_locs[0]]
					data[key].append((pre, pre_locs, post))
				except Exception:
					pass
		return self.split_data(data, os.path.dirname(os.path.realpath(data_file)))
	
	def split_data(self, data, data_dir):
		all_keys = list(data.keys())
		valid_keys = []
		test_keys = []
		with open(os.path.join(data_dir, "heldout_keys.txt")) as f:
			for l in f:
				if l.rstrip() not in data:
					continue
				valid_keys.append(l.rstrip())
		with open(os.path.join(data_dir, "test_keys.txt")) as f:
			for l in f:
				if l.rstrip() not in data:
					continue
				test_keys.append(l.rstrip())
		train_keys = [k for k in all_keys if k not in valid_keys and k not in test_keys]
		return [e for key in train_keys for e in data[key]], \
				[e for key in valid_keys for e in data[key]], \
				[e for key in test_keys for e in data[key]]
	
	def batcher(self, mode="train", optimize_packing=True):
		if self.config["edits"]:
			ot = (tf.int32, tf.int32, tf.int32, tf.int32)
		else:
			ot = (tf.int32, tf.int32, tf.int32)
		ds = tf.data.Dataset.from_generator(self.batch_generator, output_types=ot, args=(mode, optimize_packing))
		ds = ds.prefetch(1)
		return ds

	def batch_generator(self, mode="train", optimize_packing=True):
		if isinstance(mode, bytes): mode = mode.decode('utf-8')
		if mode == "train":
			batch_data = self.train_data
			#batch_data.reverse()
			#random.shuffle(batch_data)
		elif mode == "test":
			batch_data = self.test_data
		else:
			batch_data = self.valid_data

		def sample_len(sample):
			return len(sample[0]) + len(sample[2])
		
		def find_simple_diff(pre_tokens, post_tokens):
			adds = []
			prefix = 0
			#print("pr and suf length",len(pre_tokens),len(post_tokens))
			while pre_tokens[:prefix + 1] == post_tokens[:prefix + 1]:
				prefix += 1
				if prefix>len(pre_tokens):
					break
			#print("prefix finished")
			# Make sure the prefix pointer doesn't point past the end of the line if only tokens were added
			if prefix == len(pre_tokens):
				prefix = max(prefix-1, 0)
			suffix = 0
			while pre_tokens[-suffix - 1:] == post_tokens[-suffix - 1:]:
				suffix += 1
				if suffix > len(pre_tokens):
					break
			#print("suffix finished")
			# This can happen if e.g. the inserted/deleted repeat the last prefix token(s);
			# in that case, arbitraly assume that the prefix is unchanged and the suffix should be inserted/deleted.
			if len(pre_tokens) - suffix < prefix:
				suffix = len(pre_tokens) - prefix
			if len(post_tokens) - suffix < prefix:
				suffix = len(post_tokens) - prefix
			
			pre_diff = pre_tokens[prefix:len(pre_tokens) - suffix]
			post_diff = post_tokens[prefix:len(post_tokens) - suffix]
			if post_diff:
				adds = post_diff
			if pre_diff:
				del_end = prefix + len(pre_diff) - 1
			else:
				del_end = 0
			adds.insert(0, self.vocabulary.w2i['<s>'])
			adds.append(self.vocabulary.w2i['</s>'])
			return prefix, del_end, adds
		
		def make_batch(buffer):
			if optimize_packing:
				pivot = random.choice(buffer)
				buffer = sorted(buffer, key=lambda b: abs(sample_len(b) - sample_len(pivot)))
			max_seq_len = 0
			indices_pre = []
			indices_post = []
			pre_locs = []
			if self.config["edits"]:
				pointer_locs = []
			#print("checkpoint, before for loop 1, and length of buffer: ",len(buffer))
			ck_ind=0
			for pre, (pre_start, pre_end), post in buffer:
				# Sub-tokenize input and update start/end pointers
				#print("for loop ck",ck_ind)
				tokenized = [self.vocabulary.tokenize(w) for w in pre]
				new_start = sum(len(w) for w in tokenized[:pre_start])
				new_end = new_start + sum(len(w) for w in tokenized[pre_start:pre_end+1])
				if new_end - new_start > self.config['max_bug_length']:
					continue
				tokenized = [self.vocabulary.vocab_key(s) for w in tokenized for s in w]
				post_tokens = [self.vocabulary.vocab_key(s) for w in post for s in self.vocabulary.tokenize(w)]
				
				seq_len = min(self.config['max_context_length'], len(tokenized)) + len(post_tokens)
				max_seq_len = max(max_seq_len, seq_len)
				#print("tok finished")
				if len(indices_pre) > 0 and max_seq_len * (len(indices_pre) + 1) > self.config['max_batch_size']:
					#print("do break")
					break
				
				# Remove tokens outside the context window (if any) and re-compute offsets, as symmetrically as possible without wasting space
				if len(tokenized) > self.config['max_context_length']:
					context_available = self.config['max_context_length'] - (new_end - new_start)
					max_right = min(context_available, len(tokenized) - new_end)
					left_available = max(context_available//2, context_available - max_right)
					left_bound = max(0, new_start - left_available)
					right_available = context_available - left_available
					right_bound = min(len(tokenized), new_end + right_available)
					tokenized = tokenized[left_bound:right_bound]
					new_start -= left_bound
					new_end -= left_bound
				#print("rm finished")
				# Replace target with edits, if applicable
				if self.config["edits"]:
					diff = find_simple_diff(tokenized[new_start:new_end], post_tokens[1:-1])
					pivot, del_end, post_tokens = diff
					pointer_locs.append([pivot + new_start, del_end + new_start])
				#print("rp finished")
				indices_pre.append(tokenized)
				indices_post.append(post_tokens)
				pre_locs.append([new_start, new_end])
				ck_ind+=1
			#print("checkpoint, after for loop 1")
			# Remove batch sequences from buffer and convert to tensors
			if not indices_pre: return (None, None)
			buffer = buffer[len(indices_pre):]
			pre = tf.ragged.constant(indices_pre).to_tensor()
			post = tf.ragged.constant(indices_post, dtype="int32").to_tensor()
			if self.config["edits"]:
				batch = (pre, pre_locs, post, pointer_locs)
			else:
				batch = (pre, pre_locs, post)
			return buffer, batch
		
		buffer = []
		for l in batch_data:
			buffer.append(l)
			if sum(sample_len(l) for l in buffer) > self.config["max_buffer_size"]*self.config['max_batch_size']:
				print("making batch")
				buffer, batch = make_batch(buffer)
				if batch is None: break
				print("yield")
				yield batch
		print("buffer",buffer)
		while buffer:
			buffer, batch = make_batch(buffer)
			if not batch: break
			yield batch
