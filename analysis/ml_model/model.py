
import torch.nn as nn
import torch

class FastSentimentGRU(nn.Module):
    def __init__(self, vocab_size, embedding_dim=128, hidden_dim=128, 
                 output_dim=1, n_layers=1, dropout=0.1):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.gru = nn.GRU(embedding_dim, hidden_dim, 
                         num_layers=n_layers,
                         batch_first=True,
                         dropout=dropout if n_layers > 1 else 0)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, text, text_lengths):
        embedded = self.dropout(self.embedding(text))
        packed = nn.utils.rnn.pack_padded_sequence(embedded, text_lengths, 
                                                 batch_first=True,
                                                 enforce_sorted=False)
        _, hidden = self.gru(packed)
        return torch.sigmoid(self.fc(self.dropout(hidden[-1])))