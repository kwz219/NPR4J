import numpy as np
import tensorflow as tf

class AttentionLayer(tf.keras.layers.Layer):
	def __init__(self, attention_dim, num_heads=None, hidden_dim=None, bias_dim=None):
		super(AttentionLayer, self).__init__()
		if hidden_dim is None: hidden_dim = attention_dim
		self.attention_dim = attention_dim
		self.hidden_dim = hidden_dim
		self.num_heads = 1 if num_heads is None else num_heads
		self.attention_dim_per_head = self.attention_dim // self.num_heads
		self.bias_dim = bias_dim
	
	def build(self, _):
		self.attn_query = self.add_weight(name='q', shape=(self.hidden_dim, self.num_heads, self.attention_dim_per_head), initializer="glorot_uniform")
		self.attn_keys = self.add_weight(name='k', shape=(self.hidden_dim, self.num_heads, self.attention_dim_per_head), initializer="glorot_uniform")
		self.attn_values = self.add_weight(name='v', shape=(self.hidden_dim, self.num_heads, self.attention_dim_per_head), initializer="glorot_uniform")
		self.weight_out = self.add_weight(name='o', shape=(self.num_heads, self.attention_dim_per_head, self.hidden_dim), initializer="glorot_uniform")
		if self.bias_dim is not None:
			self.bias_embs = self.add_weight(name='e1', shape=(self.bias_dim, self.attention_dim_per_head), initializer="glorot_uniform")
			self.bias_scalar = self.add_weight(name='e2', shape=(self.attention_dim_per_head, 1), initializer="glorot_uniform")
	
	def call(self, states, masks, attention_bias):
		if len(states) == 2:
			states, key_states = states
		else:
			states, key_states = states[0], states[0]
		return self.call_internal(states, key_states, masks, attention_bias)
	
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, 4), dtype=tf.int32)])
	def call_internal(self, states, key_states, masks, attention_bias):
		# Compute key, query and value vectors, reshaped to [Batch, Heads, Time, Dim] where Dim is attention_dim//num_heads
		query, keys, values = self.compute_qkv(states, key_states)
		
		# Compute attention weights, and context from these
		alpha = self.get_attention_weights(query, keys, masks, attention_bias)
		context = tf.einsum('bhqk,bkha->bqha', alpha, values)
		context = tf.einsum('btha,had->btd', context, self.weight_out)
		return context
	
	# Compute key, query and value vectors. If separate key_states are provided, attend over the input instead and thus assume attention is not masked
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None), dtype=tf.float32)])
	def compute_qkv(self, states, key_states):
		query = tf.einsum('btd,dha->btha', states, self.attn_query) # Queries are always computed on states
		keys = tf.einsum('btd,dha->btha', states if key_states is None else key_states, self.attn_keys)
		values = tf.einsum('btd,dha->btha', states if key_states is None else key_states, self.attn_values)
		return query, keys, values
	
	# Compute attention weights from cross-product between keys and queries (scaled, masked, softmaxed)
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, 4), dtype=tf.int32)])
	def get_attention_weights(self, query, keys, masks, attention_bias):
		alpha = tf.einsum('bkha,bqha->bhqk', keys, query)
		if self.bias_dim is not None:
			keys = tf.reduce_sum(keys, -1) # bkh
			bias = tf.matmul(tf.one_hot(attention_bias[:, -1], self.bias_dim), self.bias_embs) # bqka
			bias = tf.squeeze(tf.matmul(bias, self.bias_scalar), -1) # bqk
			bias_shape = tf.shape(alpha)
			bias_shape = tf.stack([bias_shape[0], bias_shape[2], bias_shape[3]])
			bias = tf.scatter_nd(attention_bias[:, :-1], bias, bias_shape)
			bias = tf.einsum('bqk,bkh->bhqk', bias, keys)
			alpha += bias
		alpha *= tf.math.rsqrt(tf.cast(self.attention_dim_per_head, "float32"))
		if masks is not None:
			alpha = alpha * masks + (1.0 - tf.math.ceil(masks)) * tf.float32.min
		alpha = tf.nn.softmax(alpha)
		if masks is not None:
			alpha *= masks
		return alpha

class Transformer(tf.keras.layers.Layer):
	def __init__(self, model_config, vocab_dim, shared_embedding=None, bias_dim=None):
		super(Transformer, self).__init__()
		self.embed_dim = model_config["embed_dim"]
		self.hidden_dim = model_config["hidden_dim"]
		self.ff_dim = model_config["ff_dim"]
		self.attention_dim = model_config["attention_dim"]
		self.num_layers = model_config["num_layers"]
		self.num_heads = model_config["num_heads"]
		self.dropout_rate = model_config["dropout_rate"]
		self.bias_dim = bias_dim
		
		self.vocab_dim = vocab_dim
		self.embed = shared_embedding
		self.pos_enc = tf.constant(positional_encoding(model_config["embed_dim"], 2000))
	
	def build(self, _):
		# Set up embedding and multi-headed attention layers
		if self.embed is None:
			random_init = tf.random_normal_initializer(stddev=self.hidden_dim ** -0.5)
			self.embed = tf.Variable(random_init([self.vocab_dim, self.embed_dim]), dtype=tf.float32)
		
		make_att = lambda : AttentionLayer(self.attention_dim, self.num_heads, self.hidden_dim, self.bias_dim)
		self.attention = [make_att() for _ in range(self.num_layers)]#make_att_deprecated
		self.enc_attention = [make_att() for _ in range(self.num_layers)]
		
		# Layer normalization for every residual layer
		self.ln = [[tf.keras.layers.LayerNormalization() for _ in range(3)] for _ in range(self.num_layers)]
		self.ln_out = tf.keras.layers.LayerNormalization()
		
		# Two-layer feed-forward with wide layer in the middle
		self.ff_1 = [tf.keras.layers.Dense(self.ff_dim, activation="relu") for _ in range(self.num_layers)]
		self.ff_2 = [tf.keras.layers.Dense(self.hidden_dim) for _ in range(self.num_layers)]
	
	"""Transformer language model: converts indices into hidden states through 6 layers of multi-headed attention
		To generate language from the resulting states, pass the states to "predict". Note that predict assumes input vocabulary is output vocabulary.
	
	Args:
		mask: if not None, used to mask tokens e.g. "future" tokens. See "get_sequence_mask" to get a mask specifically for this purpose
		enc_states: If not None, applies both self-attention and input attention. In that case, we never mask attention -- encoded states are assumed to be fully known
	"""
	def call(self, inputs, masks, training, attention_bias=None):
		is_enc_dec = len(inputs) == 2
		if is_enc_dec:
			inputs, key_states = inputs
			masks, key_masks = masks
		else:
			inputs = inputs[0]
			masks = masks[0]
		if attention_bias is None: attention_bias = tf.zeros((0,4), dtype='int32')
		if is_enc_dec:
			return self.enc_dec_attention(inputs, masks, key_states, key_masks, attention_bias, training)
		else:
			return self.self_attention(inputs, masks, attention_bias, training)

	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None), dtype=tf.int32)])
	def embed_inputs(self, inputs):
		states = tf.nn.embedding_lookup(self.embed, inputs)
		states *= tf.math.sqrt(tf.cast(tf.shape(states)[-1], "float32"))
		states += self.pos_enc[:tf.shape(states)[1]]
		return states
	
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None), dtype=tf.int32), tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, 4), dtype=tf.int32), tf.TensorSpec(shape=None, dtype=tf.bool)])
	def self_attention(self, inputs, masks, attention_bias, training):
		states = self.embed_inputs(inputs)
		for ix in range(self.num_layers):
			new_states = (self.ln[ix][0](states),)
			new_states = self.attention[ix](new_states, masks, attention_bias)
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			states += new_states
			
			new_states = self.ff_1[ix](self.ln[ix][1](states))
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			new_states = self.ff_2[ix](new_states)
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			states += new_states
		return self.ln_out(states)
	
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None), dtype=tf.int32), tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, None, None, None), dtype=tf.float32), tf.TensorSpec(shape=(None, 4), dtype=tf.int32), tf.TensorSpec(shape=None, dtype=tf.bool)])
	def enc_dec_attention(self, inputs, masks, key_states, key_masks, attention_bias, training):
		states = self.embed_inputs(inputs)
		for ix in range(self.num_layers):
			new_states = (self.ln[ix][0](states),)
			new_states = self.attention[ix](new_states, masks, tf.zeros((0,4), dtype='int32'))
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			states += new_states

			new_states = self.ln[ix][2](states)
			new_states = self.enc_attention[ix]((new_states, key_states), key_masks, attention_bias)
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			states += new_states
			
			new_states = self.ff_1[ix](self.ln[ix][1](states))
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			new_states = self.ff_2[ix](new_states)
			if training: new_states = tf.nn.dropout(new_states, rate=self.dropout_rate)
			states += new_states
		return self.ln_out(states)
	
	"""Returns a sequence mask in which each token can only see states up to its own position. Useful for generative language modeling (e.g. decoding)."""
	def get_sequence_mask(self, seq_len):
		return tf.sequence_mask(lengths=tf.range(1, seq_len + 1), maxlen=seq_len, dtype=tf.float32)
	
	"""Generates tokens from transformer states using the transposed embedding layer"""
	@tf.function(input_signature=[tf.TensorSpec(shape=(None, None, None), dtype=tf.float32)])
	def predict(self, states):
		return tf.matmul(states, self.embed, transpose_b=True)


# Based on https://github.com/DongjunLee/transformer-tensorflow/blob/master/transformer/attention.py
def positional_encoding(dim, sentence_length, dtype=tf.float32):
	encoded_vec = np.array([pos/np.power(10000, 2*i/dim) for pos in range(sentence_length) for i in range(dim)])
	encoded_vec[::2] = np.sin(encoded_vec[::2])
	encoded_vec[1::2] = np.cos(encoded_vec[1::2])
	pos_enc = tf.constant(encoded_vec.reshape([sentence_length, dim]), dtype=dtype)
	return pos_enc