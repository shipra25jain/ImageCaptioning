import torch
import torch.nn as nn


class LSTM(nn.Module):
    def __init__(self, num_of_features, dim_of_features, hidden_size, vocab_size, embedding_size):
        super(LSTM, self).__init__()
        
        self.num_of_features = num_of_features
        self.dim_of_features = dim_of_features
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.embedding_size = embedding_size
        self.word_embed = nn.Embedding(self.vocab_size, self.embedding_size)
        
        # LSTM related variables
        self.lstm_cell = nn.LSTMCell(embedding_size+dim_of_features, hidden_size)
        self.deep_output = nn.Linear(self.hidden_size, self.vocab_size)


    # Initializes the hidden and memory states of the LSTM    
    def initialize_states(self, features):
      mean_features = features.mean(dim=1)
     
      if self.dim_of_features!= self.hidden_size:
        hidden_mlp_layer = nn.Linear(self.dim_of_features, self.hidden_size)
        memory_mlp_layer = nn.Linear(self.dim_of_features, self.hidden_size)
        # Initial states of the RNN are MLP outputs from a mean feature vector
        h0 = hidden_mlp_layer(mean_features)
        c0 = memory_mlp_layer(mean_features)

      else:
        h0 = mean_features
        c0 = mean_features

      return h0, c0


    # Finds the feature to be focused for the current time step 
    def build_attention_model(self, features, hidden):
      # To be added by Xenia
      return
      
      
    # Runs the forward pass of the LSTM 
    def forward(self, img_features, captions, dropout =
               False):
      # Initializing the required variables
      batch_size = img_features.size(0)
      h0, c0 = self.initialize_states(img_features)
      max_cap_len = max([len(caption) for caption in captions]) - 1
      predictions = torch.zeros(batch_size, max_cap_len, self.vocab_size).cuda()
      alphas = torch.zeros(batch_size, max_cap_len, img_features.size(1)).cuda()
        
      word_embeddings = self.word_embed(captions)
      if dropout:
        word_embeddings = nn.Dropout(0.5)(word_embeddings)
      
      for t in range(max_cap_len):
        context, alpha = self.build_attention_model(img_features, h0)
        lstm_input = torch.cat((word_embeddings[:, t,:].squeeze(1), context), dim=1)
        
        h0, c0 = self.lstm_cell(lstm_input, (h0, c0))
        output = self.deep_output(nn.Dropout()(h0))

        predictions[:, t, :] = output
        alphas[:, t, :] = alpha

        return predictions, alphas
      