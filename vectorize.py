
import numpy as np
import tensorflow as tf
import pickle
class Vectorize:
    def __init__(self,col,tokenizer):
        self.col=[i.strip() for i in col]
        self.tokenizer=tokenizer
        
    def tokenize(self):
        self.tokenizer[0].fit_on_texts(self.col)
        pickle.dump(self.tokenizer[0],open(self.tokenizer[1], "wb"))
        self.tokens=self.tokenizer[0].texts_to_sequences(self.col)

        return self.tokenizer[0].word_index,self.tokenizer[0],self.tokens
    
    def padding(self):
        maxlength=max([len(i) for i in self.tokens])
        self.padded=tf.keras.preprocessing.sequence.pad_sequences(self.tokens,maxlength)
        return self.padded
    
    def embedding(self):
        in_dim=len(self.tokenizer[0].word_index)+1
        out_dim=3
        self.embedding_layer=tf.keras.layers.Embedding(input_dim=in_dim,output_dim=out_dim)
        self.model=tf.keras.models.Sequential()
        self.model.add(self.embedding_layer)
        self.model.add(tf.keras.layers.LSTM(16))
        self.model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return self.model
    
    def train(self):
        history=self.model.fit(self.padded,
                          np.zeros(len(self.padded)),
                          epochs=1,
                          batch_size=16,
                          validation_split=0.2)
        return self.model
    
    def get_vectors(self):
        self.embedding_layer=self.model.layers[0]
        self.embedding_weights=self.embedding_layer.get_weights()[0]
        word_index = self.tokenize.word_index
        self.word_vectors = {}
        for word, index in word_index.items():
            vector = self.embedding_weights[index]
            self.word_vectors[word] = vector
            
        return self.word_vectors
    
    def padded_embedding(self):
        self.embedding_model = tf.keras.models.Sequential()
        self.embedding_model.add(self.embedding_layer)
        self.embedding_model.add(tf.keras.layers.GlobalAveragePooling1D())
        
        return self.embedding_model
        