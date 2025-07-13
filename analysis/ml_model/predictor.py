import torch
from pathlib import Path
import re
from transformers import AutoTokenizer
from .model import FastSentimentGRU

class SentimentPredictor:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = self._init_model()
        
        if model_path:
            self.load_model(model_path)
    
    def _init_model(self):
        """Initialize model with correct architecture"""
        return FastSentimentGRU(
            vocab_size=30522,
            embedding_dim=128,
            hidden_dim=128,
            n_layers=1,
            dropout=0.1
        ).to(self.device)
    
    def load_model(self, path):
        """Load model weights with proper error handling"""
        try:
            state_dict = torch.load(path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            # Initialize with random weights if loading fails
            self.model = self._init_model()
            return False
    
    def clean_text(self, text):
        """Clean input text"""
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        return text.lower().strip()
    
    def tokenize_text(self, text):
        """Tokenize text for model input"""
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors='pt'
        )
        return encoding['input_ids'].squeeze(0).to(self.device)
    
    def predict(self, text):
        """Make sentiment prediction"""
        if not self.model:
            return {
                "error": "Model not loaded",
                "status": "error"
            }
        
        try:
            # Preprocess text
            cleaned_text = self.clean_text(text)
            inputs = self.tokenize_text(cleaned_text)
            
            # Prepare model inputs
            mask = (inputs != 0).int()
            length = torch.tensor([mask.sum().item()], device=self.device)
            
            # Get prediction
            with torch.no_grad():
                output = self.model(inputs.unsqueeze(0), length)
            
            # Format results
            prob = output.item()
            sentiment = "POSITIVE" if prob > 0.5 else "NEGATIVE"
            confidence = prob if prob > 0.5 else 1 - prob
            
            return {
                "text": text,
                "sentiment": sentiment,
                "confidence": float(confidence),
                "raw_score": float(prob),
                "status": "success"
            }
        except Exception as e:
            return {
                "text": text,
                "error": str(e),
                "status": "error"
            }