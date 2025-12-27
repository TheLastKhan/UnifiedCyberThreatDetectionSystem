"""
BERT-based Email Phishing Detector
====================================

Fine-tuned DistilBERT model for email phishing detection.
Provides higher accuracy than TF-IDF while maintaining reasonable inference time.

Architecture: DistilBERT (6 layers, 66M parameters)
Training Dataset: Email classification dataset (phishing vs legitimate)
Output: Probability score (0-1) + Confidence level
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path
import json
import pickle

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)

# LIME for explainability
try:
    from lime.lime_text import LimeTextExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logger.warning("LIME not available. Install with: pip install lime")

logger = logging.getLogger(__name__)


@dataclass
class BertPrediction:
    """BERT model prediction output"""
    score: float  # 0-1 probability
    label: str  # "phishing" or "legitimate"
    confidence: float  # confidence level (0-1)
    tokens: int  # number of tokens processed
    model_type: str = "BERT"


class BertEmailDetector:
    """
    BERT-based email phishing detector
    
    Uses DistilBERT for efficient detection:
    - Faster inference (6 layers vs 12 for BERT)
    - ~40% smaller than full BERT
    - 97-99% accuracy of full BERT
    
    Compared to TF-IDF:
    - ~5-10% higher accuracy
    - ~2-3x slower inference
    - Better understanding of context and semantics
    - More robust to adversarial emails
    """
    
    # Pre-trained model identifier
    MODEL_NAME = "distilbert-base-uncased"
    CUSTOM_MODEL_PATH = "models/bert_email_detector"
    
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize BERT detector
        
        Args:
            model_path: Path to fine-tuned model (if None, use pre-trained)
            device: "cuda" or "cpu" (auto-detect if None)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        self.model_path = model_path
        self._load_model()
        
    def _load_model(self):
        """Load tokenizer and model"""
        try:
            # Check if custom fine-tuned model exists
            if self.model_path and Path(self.model_path).exists():
                logger.info(f"Loading fine-tuned model from {self.model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_path,
                    num_labels=2  # binary classification
                )
            else:
                # Use pre-trained DistilBERT
                logger.info(f"Loading pre-trained model: {self.MODEL_NAME}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.MODEL_NAME,
                    num_labels=2  # binary classification
                )
            
            self.model.to(self.device)
            self.model.eval()
            
            # Create pipeline for easier inference
            self.pipeline = TextClassificationPipeline(
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1  # -1 for CPU
            )
            
            # Initialize LIME explainer
            if LIME_AVAILABLE:
                self.lime_explainer = LimeTextExplainer(
                    class_names=['Legitimate', 'Phishing']
                )
                logger.info("LIME explainer initialized")
            else:
                self.lime_explainer = None
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict(
        self,
        text: str,
        return_proba: bool = True,
        max_length: int = 512
    ) -> BertPrediction:
        """
        Predict if email is phishing or legitimate
        
        Args:
            text: Email content to analyze
            return_proba: Return probability scores
            max_length: Maximum sequence length (512 for BERT)
        
        Returns:
            BertPrediction object with score, label, confidence
        
        Example:
            >>> detector = BertEmailDetector()
            >>> result = detector.predict("Click here to verify your account")
            >>> print(f"Phishing: {result.score:.2%}")
        """
        try:
            # Truncate text to max length
            text = text[:max_length * 4]  # Rough estimate (4 chars per token)
            
            # Get prediction from pipeline
            with torch.no_grad():
                prediction = self.pipeline(text, truncation=True)[0]
            
            # Extract components
            label = prediction['label'].lower()
            score = prediction['score']
            
            # Map label to our convention: higher score = more phishing
            # LABEL_0 = legitimate (0), LABEL_1 = phishing (1)
            if label == "label_1":  # LABEL_1 means phishing
                phishing_score = score
            elif label == "label_0":  # LABEL_0 means legitimate
                phishing_score = 1 - score
            elif label == "negative":  # Fallback for base model
                phishing_score = score
            else:  # Default fallback
                phishing_score = 1 - score
            
            # Tokenize to count tokens
            tokens = self.tokenizer.encode(text, truncation=True)
            num_tokens = len(tokens)
            
            return BertPrediction(
                score=phishing_score,
                label="phishing" if phishing_score > 0.5 else "legitimate",
                confidence=max(score, 1 - score),
                tokens=num_tokens,
                model_type="BERT"
            )
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise
    
    def batch_predict(
        self,
        texts: List[str],
        batch_size: int = 8
    ) -> List[BertPrediction]:
        """
        Predict for multiple emails
        
        Args:
            texts: List of email contents
            batch_size: Processing batch size
        
        Returns:
            List of BertPrediction objects
        """
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                try:
                    result = self.predict(text)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error predicting batch item: {e}")
                    results.append(None)
        
        return results
    
    def explain_prediction(self, text: str, top_k: int = 10) -> Dict:
        """
        Explain what features the model found important
        
        Args:
            text: Email content
            top_k: Number of top important tokens
        
        Returns:
            Dictionary with explanation data
        """
        # This is a simplified explanation
        # For full explainability, use LIME or SHAP
        
        tokens = self.tokenizer.encode(text, return_tensors='pt').to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tokens, output_attentions=True)
        
        prediction = self.predict(text)
        
        return {
            "prediction": prediction.score,
            "label": prediction.label,
            "confidence": prediction.confidence,
            "num_tokens": prediction.tokens,
            "explanation": "Use LIME or SHAP for detailed token importance"
        }
    
    def predict_with_explanation(
        self,
        text: str,
        num_features: int = 5,
        num_samples: int = 100
    ) -> Dict:
        """
        Predict with LIME explanation for XAI
        
        Args:
            text: Email content to analyze
            num_features: Number of top features to return
            num_samples: Number of samples for LIME (more = better but slower)
        
        Returns:
            Dictionary with prediction and lime_breakdown
        
        Example:
            >>> detector = BertEmailDetector()
            >>> result = detector.predict_with_explanation("Urgent! Click here now!")
            >>> print(result['lime_breakdown'])
            [{'feature': 'urgent', 'contribution': 35.2, 'positive': True}, ...]
        """
        # Get basic prediction
        prediction = self.predict(text)
        
        # If LIME not available, return without explanation
        if not self.lime_explainer:
            logger.warning("LIME not available, returning prediction without explanation")
            return {
                'prediction': prediction.label,
                'confidence': prediction.confidence,
                'score': prediction.score,
                'lime_breakdown': []
            }
        
        try:
            # Create prediction function for LIME
            def predict_proba(texts):
                """Wrapper for LIME - returns probability array"""
                results = []
                for t in texts:
                    pred = self.predict(t)
                    # LIME expects [prob_class_0, prob_class_1]
                    # class_0 = legitimate, class_1 = phishing
                    prob_phishing = pred.score
                    prob_legit = 1 - prob_phishing
                    results.append([prob_legit, prob_phishing])
                return np.array(results)
            
            # Get LIME explanation
            explanation = self.lime_explainer.explain_instance(
                text,
                predict_proba,
                num_features=num_features,
                num_samples=num_samples
            )
            
            # Format LIME output for frontend
            lime_breakdown = []
            for feature, weight in explanation.as_list():
                # Calculate contribution as percentage
                contribution = abs(weight) * prediction.score * 100
                lime_breakdown.append({
                    'feature': feature,
                    'contribution': round(contribution, 1),
                    'positive': weight > 0  # True if increases phishing probability
                })
            
            return {
                'prediction': prediction.label,
                'confidence': prediction.confidence,
                'score': prediction.score,
                'lime_breakdown': lime_breakdown,
                'tokens': prediction.tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating LIME explanation: {e}")
            return {
                'prediction': prediction.label,
                'confidence': prediction.confidence,
                'score': prediction.score,
                'lime_breakdown': []
            }
    
    def get_model_info(self) -> Dict:
        """Get model information and statistics"""
        return {
            "model_name": self.MODEL_NAME,
            "model_path": self.model_path,
            "device": self.device,
            "num_parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            ),
            "max_sequence_length": 512,
            "architecture": "DistilBERT-base-uncased",
            "num_labels": 2,
        }


class BertTrainer:
    """
    Fine-tune BERT model on custom email dataset
    
    Usage:
        >>> trainer = BertTrainer()
        >>> trainer.train(train_texts, train_labels)
        >>> trainer.save_model("models/bert_email_detector")
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased", device: Optional[str] = None):
        """
        Initialize trainer
        
        Args:
            model_name: Pre-trained model name
            device: "cuda" or "cpu"
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2
        )
        self.model.to(self.device)
        
        logger.info(f"Trainer initialized on {self.device}")
    
    def prepare_dataset(self, texts: List[str], labels: List[int]) -> Dict:
        """
        Prepare dataset for training
        
        Args:
            texts: List of email texts
            labels: List of labels (0=legitimate, 1=phishing)
        
        Returns:
            Encoded dataset
        """
        logger.info(f"Preparing dataset with {len(texts)} samples")
        
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        
        encodings['labels'] = torch.tensor(labels)
        
        return encodings
    
    def train(
        self,
        train_texts: List[str],
        train_labels: List[int],
        val_texts: Optional[List[str]] = None,
        val_labels: Optional[List[int]] = None,
        epochs: int = 3,
        learning_rate: float = 2e-5,
        batch_size: int = 16,
    ) -> Dict:
        """
        Fine-tune model on dataset
        
        Args:
            train_texts: Training email texts
            train_labels: Training labels
            val_texts: Validation texts (optional)
            val_labels: Validation labels (optional)
            epochs: Number of training epochs
            learning_rate: Learning rate
            batch_size: Batch size
        
        Returns:
            Training metrics
        """
        from torch.optim import AdamW
        from torch.utils.data import TensorDataset, DataLoader
        
        logger.info("Preparing training data...")
        train_encodings = self.prepare_dataset(train_texts, train_labels)
        
        train_dataset = TensorDataset(
            train_encodings['input_ids'],
            train_encodings['attention_mask'],
            train_encodings['labels']
        )
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True
        )
        
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        
        logger.info(f"Starting training for {epochs} epochs...")
        
        training_stats = {
            "epochs": [],
            "train_loss": [],
            "val_loss": [],
            "val_accuracy": []
        }
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            total_loss = 0
            
            for batch_idx, batch in enumerate(train_loader):
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                labels = batch[2].to(self.device)
                
                optimizer.zero_grad()
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                
                if (batch_idx + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}, Loss: {loss.item():.4f}")
            
            avg_train_loss = total_loss / len(train_loader)
            training_stats["train_loss"].append(avg_train_loss)
            
            logger.info(f"Epoch {epoch+1} completed. Average loss: {avg_train_loss:.4f}")
            
            # Validation phase
            if val_texts is not None and val_labels is not None:
                val_loss, val_accuracy = self.evaluate(val_texts, val_labels, batch_size)
                training_stats["val_loss"].append(val_loss)
                training_stats["val_accuracy"].append(val_accuracy)
                logger.info(f"Validation loss: {val_loss:.4f}, Accuracy: {val_accuracy:.2%}")
        
        training_stats["epochs"] = list(range(1, epochs + 1))
        
        return training_stats
    
    def evaluate(
        self,
        texts: List[str],
        labels: List[int],
        batch_size: int = 16
    ) -> Tuple[float, float]:
        """
        Evaluate model on validation/test set
        
        Args:
            texts: Evaluation texts
            labels: Evaluation labels
            batch_size: Batch size
        
        Returns:
            (loss, accuracy)
        """
        from torch.utils.data import TensorDataset, DataLoader
        
        val_encodings = self.prepare_dataset(texts, labels)
        
        val_dataset = TensorDataset(
            val_encodings['input_ids'],
            val_encodings['attention_mask'],
            val_encodings['labels']
        )
        
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                labels = batch[2].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                logits = outputs.logits
                
                total_loss += loss.item()
                
                predictions = torch.argmax(logits, dim=1)
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def save_model(self, path: str):
        """
        Save fine-tuned model
        
        Args:
            path: Directory to save model
        """
        Path(path).mkdir(parents=True, exist_ok=True)
        
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        
        # Save training config
        config = {
            "model_name": self.model_name,
            "device": self.device,
            "model_type": "DistilBERT",
            "num_labels": 2,
        }
        
        with open(Path(path) / "config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Model saved to {path}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Load detector
    print("Loading BERT detector...")
    detector = BertEmailDetector()
    print(detector.get_model_info())
    
    # Test prediction
    test_email = "Click here to verify your account immediately or your account will be closed!"
    result = detector.predict(test_email)
    print(f"\nTest Email: {test_email[:50]}...")
    print(f"Prediction: {result.label.upper()}")
    print(f"Score: {result.score:.2%}")
    print(f"Confidence: {result.confidence:.2%}")
