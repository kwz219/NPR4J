
RESERVED_TOKENS = ["<s>", "</s>", "<pad>"]
	
class VocabularyBuilder():
	
	def __init__(self, token_generator=None, vocab_path=None):
		self.load_vocab(vocab_path)
		self.vocab_dim = len(self.w2i)
		self.vocab_key = lambda w: self.w2i[w] if w in self.w2i else self.w2i["<unk>"] # Convenience function
		
		self.bpe_cache = {}
		self.bpe_lookup_dict = {}
		for token in self.w2i.keys():
			if token[:2] not in self.bpe_lookup_dict:
				self.bpe_lookup_dict[token[:2]] = set([token])
			else:
				self.bpe_lookup_dict[token[:2]].add(token)
	
	def load_vocab(self, vocab_path):
		with open(vocab_path, "r", encoding="utf8") as f:	
			vocab = [l.rstrip('\n').split()[1] for l in f.readlines()]
		print(len(vocab))
		self.w2i = {w:i for i, w in enumerate(vocab)}
		self.i2w = {i:w for w, i in self.w2i.items()}
	
	def tokenize(self, label):
		if label in RESERVED_TOKENS: return [label]
		label = "".join([c for c in label if ord(c) > 32 and ord(c) < 127]) + "#"
		tokens = []
		ix = 0
		if label in self.bpe_cache and self.bpe_cache[label] is not None:
			return self.bpe_cache[label]
		while ix < len(label):
			if ix == len(label) - 2:
				tokens.append(label[ix:])
				break
			else:
				candidates = self.bpe_lookup_dict.get(label[ix:ix+2], [])
				if not candidates: top_candidate = label[ix]
				else:
					# Only sub-tokens that match the next characters and don't leave the end-of-word marker left by itself
					candidates = [t for t in candidates if t == label[ix:ix+len(t)] and not len(label) == ix + len(t) + 1] 
					if not candidates: top_candidate = label[ix]
					else: top_candidate = max(candidates, key=lambda e: len(e))
				tokens.append(top_candidate)
				ix += len(top_candidate)
		self.bpe_cache[label] = tokens
		return tokens
	
	def undo_bpe(self, tokens):
		cleaned = []
		curr = ""
		for t in tokens:
			if t.endswith("#"):
				cleaned.append(curr+t[:-1])
				curr = ""
			elif curr == "" and t in RESERVED_TOKENS:
				cleaned.append(t)
			else: curr += t
		if curr: cleaned.append(curr)
		return cleaned


if __name__ == '__main__':
	from tqdm import tqdm
	vocab = VocabularyBuilder(vocab_path='data/temp_vocab')
	# with open('my_data/data.txt', encoding='utf-8') as fp:
	# 	fp = fp.readlines()
	with open('my_data/data.txt', encoding='utf-8') as fp:
		fp = fp.readlines()
	for line in tqdm(fp):
		line = line.split('###')
		buggy = line[1].split()
		fix = line[3].split()

		for word in buggy:
			tokens = vocab.tokenize(word)

		for word in fix:
			tokens = vocab.tokenize(word)



#看一下有没有哪个数字超出了词表长度
#比一下代码长度