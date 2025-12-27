"""
BERT Fine-Tuning Script (Overnight Training)
=============================================
Expected time: 8-12 hours (CPU) or 2-3 hours (GPU)

This script will:
1. Load 39,154 emails from dataset
2. Split into train/val (80/20)
3. Fine-tune DistilBERT for 3 epochs
4. Save fine-tuned model
5. Evaluate on validation set

Start before bed, wake up to a trained model! 😴☕
"""

import os
import time
from datetime import datetime
import torch
from transformers import (
    DistilBertTokenizer, 
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer
)
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
import numpy as np

# Import our data loader
from src.utils.data_loader import DataLoader

print("=" * 70)
print("🌙 BERT Overnight Training")
print("=" * 70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("⏰ Estimated time: 8-12 hours (CPU) or 2-3 hours (GPU)")
print("=" * 70)

# Check for GPU
device: str = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n🖥️  Device: {device.upper()}")
if device == "cuda":
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print("   ⚡ Training will be much faster!")
else:
    print("   💤 CPU training - grab some sleep, this will take 8-12 hours")

# Step 1: Load data
print("\n[1/6] Loading email dataset...")
load_start = time.time()

loader = DataLoader()
texts, labels = loader.load_all_emails()

load_time = time.time() - load_start
print(f"✅ Loaded {len(texts)} emails in {load_time:.2f} seconds")
print(f"   - Phishing: {sum(labels)} emails")
print(f"   - Legitimate: {len(labels) - sum(labels)} emails")

# Step 2: Split train/val
print("\n[2/6] Splitting into train/validation sets...")
X_train, X_val, y_train, y_val = train_test_split(
    texts, labels, 
    test_size=0.2, 
    random_state=42,
    stratify=labels
)
print(f"✅ Train set: {len(X_train)} emails")
print(f"✅ Val set: {len(X_val)} emails")

# Step 3: Initialize tokenizer and model
print("\n[3/6] Loading DistilBERT tokenizer and model...")
model_name = "distilbert-base-uncased"

tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)
# Move model to device (CPU or GPU)
model = model.to(device)  # type: ignore
print("✅ Model loaded and moved to device")

# Step 4: Tokenize data
print("\n[4/6] Tokenizing emails...")
print("   This may take a few minutes...")
tokenize_start = time.time()

class EmailDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.encodings = tokenizer(
            texts, 
            truncation=True, 
            padding=True, 
            max_length=max_length,
            return_tensors='pt'
        )
        self.labels = torch.tensor(labels)
    
    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx]
        return item
    
    def __len__(self):
        return len(self.labels)

train_dataset = EmailDataset(X_train, y_train, tokenizer)
val_dataset = EmailDataset(X_val, y_val, tokenizer)

tokenize_time = time.time() - tokenize_start
print(f"✅ Tokenization completed in {tokenize_time:.2f} seconds ({tokenize_time/60:.1f} minutes)")

# Step 5: Configure training
print("\n[5/6] Configuring training parameters...")

training_args = TrainingArguments(
    output_dir='./models/bert_checkpoints',
    num_train_epochs=3,
    per_device_train_batch_size=16 if device == "cuda" else 8,
    per_device_eval_batch_size=16 if device == "cuda" else 8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    fp16=True if device == "cuda" else False,
)

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    accuracy = (predictions == labels).mean()
    return {'accuracy': accuracy}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print("✅ Training configuration ready")
print(f"   - Epochs: 3")
print(f"   - Batch size: {training_args.per_device_train_batch_size}")
print(f"   - Mixed precision: {training_args.fp16}")

# Step 6: Train!
print("\n[6/6] Starting training...")
print("=" * 70)
print("🚀 BERT FINE-TUNING IN PROGRESS")
print("=" * 70)
print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("💤 This will take several hours. Go get some sleep!")
print("=" * 70)

train_start = time.time()

try:
    # Train the model
    trainer.train()
    
    train_time = time.time() - train_start
    hours = train_time / 3600
    
    print("\n" + "=" * 70)
    print("🎉 TRAINING COMPLETED!")
    print("=" * 70)
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⌛ Training time: {train_time:.2f} seconds ({hours:.2f} hours)")
    
    # Step 7: Evaluate
    print("\n📊 Evaluating on validation set...")
    eval_results = trainer.evaluate()
    
    print(f"✅ Validation Accuracy: {eval_results['eval_accuracy']*100:.2f}%")
    print(f"✅ Validation Loss: {eval_results['eval_loss']:.4f}")
    
    # Step 8: Save model
    print("\n💾 Saving fine-tuned model...")
    save_start = time.time()
    
    output_dir = "models/bert_finetuned"
    os.makedirs(output_dir, exist_ok=True)
    
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    save_time = time.time() - save_start
    print(f"✅ Model saved to {output_dir}")
    print(f"   Save time: {save_time:.2f} seconds")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TRAINING SUMMARY")
    print("=" * 70)
    print(f"Dataset size: {len(texts)} emails")
    print(f"Train set: {len(X_train)} emails")
    print(f"Val set: {len(X_val)} emails")
    print(f"Device: {device.upper()}")
    print(f"Load time: {load_time:.2f}s")
    print(f"Tokenize time: {tokenize_time:.2f}s ({tokenize_time/60:.1f} min)")
    print(f"Train time: {train_time:.2f}s ({hours:.2f} hours)")
    print(f"Save time: {save_time:.2f}s")
    print(f"Total time: {(time.time() - load_start)/3600:.2f} hours")
    print(f"\n✅ Validation Accuracy: {eval_results['eval_accuracy']*100:.2f}%")
    print("=" * 70)
    print("🎉 BERT model is ready for production!")
    print("=" * 70)
    
    # Quick test
    print("\n🧪 Quick Test...")
    test_emails = [
        "URGENT! Your PayPal account will be suspended. Click here to verify: http://fake-paypal.com",
        "Hi John, the meeting is scheduled for tomorrow at 2 PM. Best regards, Sarah"
    ]
    
    for i, email in enumerate(test_emails, 1):
        inputs = tokenizer(email, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            prediction = torch.argmax(outputs.logits, dim=1).item()
            confidence = torch.softmax(outputs.logits, dim=1).max().item()
        
        label = "Phishing" if prediction == 1 else "Safe"
        print(f"\n{i}. Email: {email[:60]}...")
        print(f"   Prediction: {label}")
        print(f"   Confidence: {confidence*100:.2f}%")
    
    print("\n" + "=" * 70)
    print("☕ Good morning! Your BERT model is ready!")
    print("=" * 70)
    
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR DURING TRAINING")
    print("=" * 70)
    print(f"Error: {str(e)}")
    print("\nThis is likely a memory or dependency issue.")
    print("Check the logs above for details.")
    print("=" * 70)
    raise

print("\nScript completed successfully!")
