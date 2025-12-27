"""
🎯 BERT Phishing Detection - Single Script Training (Colab)
============================================================
Train DistilBERT on combined phishing datasets with GPU

USAGE IN GOOGLE COLAB:
1. Runtime → Change runtime type → T4 GPU
2. Copy-paste this ENTIRE file into a Colab cell
3. Run the cell (takes ~60-90 min)
4. Download bert_phishing_detector.zip

Estimated time: 60-90 minutes with T4 GPU
"""

print("="*70)
print("🚀 BERT Phishing Detection Training (Colab)")
print("="*70)

# ============================================================================
# STEP 1: Check GPU
# ============================================================================
print("\n[1/14] Checking GPU...")
import torch
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("⚠️ No GPU! Go to Runtime > Change runtime type > Select T4 GPU")
    print("   Training on CPU will take 10+ hours!")

# ============================================================================
# STEP 2: Install Dependencies
# ============================================================================
print("\n[2/14] Installing dependencies...")
import os
os.system('pip install -q transformers accelerate torch pandas scikit-learn tqdm')
print("✅ Dependencies installed")

# ============================================================================
# STEP 3: Upload CSV Files
# ============================================================================
print("\n[3/14] Upload CSV files...")
print("📤 Please upload these 7 CSV files:")
print("   1. CEAS_08.csv")
print("   2. Enron.csv")
print("   3. Ling.csv")
print("   4. Nazario.csv")
print("   5. Nigerian_Fraud.csv")
print("   6. SpamAssasin.csv")
print("   7. phishing_email.csv")
print("\nClick 'Choose Files' button and select all 7 CSV files...")

import sys
try:
    from google.colab import files
    uploaded = files.upload()
    print(f"\n✅ Uploaded {len(uploaded)} files")

    # Create dataset directory
    os.makedirs('dataset', exist_ok=True)
    for filename in uploaded.keys():
        with open(f'dataset/{filename}', 'wb') as f:
            f.write(uploaded[filename])
        print(f"   ✓ {filename}")
except ImportError:
    print("⚠️ Not in Colab - assuming files are in dataset/ folder")
    if not os.path.exists('dataset'):
        print("❌ ERROR: dataset/ folder not found!")
        sys.exit(1)

# ============================================================================
# STEP 4: Import Libraries
# ============================================================================
print("\n[4/14] Importing libraries...")
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from transformers import TrainingArguments, Trainer
from torch.utils.data import Dataset
from tqdm import tqdm
import shutil
print("✅ Libraries imported")

# ============================================================================
# STEP 5: Load Email Datasets
# ============================================================================
print("\n[5/14] Loading email datasets...")

datasets = [
    'dataset/CEAS_08.csv',
    'dataset/Enron.csv',
    'dataset/Ling.csv',
    'dataset/Nazario.csv',
    'dataset/Nigerian_Fraud.csv',
    'dataset/SpamAssasin.csv',
    'dataset/phishing_email.csv'
]

all_texts = []
all_labels = []

for dataset in tqdm(datasets, desc="Loading datasets"):
    if os.path.exists(dataset):
        try:
            df = pd.read_csv(dataset, encoding='utf-8')

            # Find text column
            text_cols = ['body', 'text', 'email', 'message', 'content', 'Email Text', 'text_combined']
            text_col = None
            for col in text_cols:
                if col in df.columns:
                    text_col = col
                    break

            # Find label column
            label_cols = ['label', 'class', 'spam', 'phishing', 'Email Type']
            label_col = None
            for col in label_cols:
                if col in df.columns:
                    label_col = col
                    break

            if text_col and label_col:
                # Convert labels to binary
                df['binary_label'] = df[label_col].apply(
                    lambda x: 1 if str(x).lower() in ['1', 'spam', 'phishing', 'phishing email'] else 0
                )

                # Clean and filter
                df = df[[text_col, 'binary_label']].dropna()
                df = df[df[text_col].astype(str).str.len() > 20]

                texts = df[text_col].astype(str).tolist()
                labels = df['binary_label'].tolist()

                all_texts.extend(texts)
                all_labels.extend(labels)

                print(f"  ✅ {os.path.basename(dataset)}: {len(texts)} emails ({sum(labels)} phishing, {len(labels)-sum(labels)} legit)")
        except Exception as e:
            print(f"  ⚠️ Error loading {dataset}: {e}")

print(f"\n📊 Total emails loaded: {len(all_texts)}")
print(f"   Phishing: {sum(all_labels)} ({sum(all_labels)/len(all_labels)*100:.1f}%)")
print(f"   Legitimate: {len(all_labels)-sum(all_labels)} ({(len(all_labels)-sum(all_labels))/len(all_labels)*100:.1f}%)")

# ============================================================================
# STEP 6: Split Data
# ============================================================================
print("\n[6/14] Splitting data (70% train, 15% val, 15% test)...")
X_temp, X_test, y_temp, y_test = train_test_split(
    all_texts, all_labels, test_size=0.15, random_state=42, stratify=all_labels
)
X_train, X_val, y_train, y_val = train_test_split(
    X_temp, y_temp, test_size=0.1765, random_state=42, stratify=y_temp  # 0.1765 of 85% = 15% of total
)

print(f"✅ Train set: {len(X_train)} emails")
print(f"✅ Val set: {len(X_val)} emails")
print(f"✅ Test set: {len(X_test)} emails")

# ============================================================================
# STEP 7: Load BERT Model
# ============================================================================
print("\n[7/14] Loading DistilBERT tokenizer and model...")
MODEL_NAME = 'distilbert-base-uncased'
MAX_LENGTH = 512

tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    problem_type="single_label_classification"
)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)
print(f"✅ Model loaded on {str(device).upper()}")

# ============================================================================
# STEP 8: Create Dataset Class
# ============================================================================
print("\n[8/14] Creating dataset class...")

class PhishingDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

train_dataset = PhishingDataset(X_train, y_train, tokenizer, MAX_LENGTH)
val_dataset = PhishingDataset(X_val, y_val, tokenizer, MAX_LENGTH)
test_dataset = PhishingDataset(X_test, y_test, tokenizer, MAX_LENGTH)

print(f"✅ Datasets created")

# ============================================================================
# STEP 9: Define Metrics
# ============================================================================
print("\n[9/14] Defining evaluation metrics...")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    
    accuracy = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average='binary'
    )
    
    return {
        'accuracy': accuracy * 100,
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100
    }

print("✅ Metrics defined")

# ============================================================================
# STEP 10: Configure Training
# ============================================================================
print("\n[10/14] Configuring training parameters...")

training_args = TrainingArguments(
    output_dir='./bert_checkpoints',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    fp16=torch.cuda.is_available(),  # Mixed precision only on GPU
    report_to="none"  # Disable wandb
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print("✅ Training configured")
print(f"   Epochs: 3")
print(f"   Batch size: 16")
print(f"   Mixed precision: {training_args.fp16}")

# ============================================================================
# STEP 11: Train Model
# ============================================================================
print("\n[11/14] Starting training...")
print("="*70)
print("🏋️ TRAINING IN PROGRESS")
print("="*70)
print("⏰ This will take 60-90 minutes with GPU...")
print("☕ Go grab coffee!")
print("="*70)

from datetime import datetime
train_start = datetime.now()
print(f"Started: {train_start.strftime('%H:%M:%S')}")

trainer.train()

train_end = datetime.now()
duration = (train_end - train_start).total_seconds() / 60
print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)
print(f"Duration: {duration:.1f} minutes")

# ============================================================================
# STEP 12: Evaluate on Test Set
# ============================================================================
print("\n[12/14] Evaluating on test set...")
test_results = trainer.evaluate(test_dataset)

print("\n📊 FINAL TEST RESULTS:")
print("="*70)
print(f"  Accuracy:  {test_results['eval_accuracy']:.2f}%")
print(f"  Precision: {test_results['eval_precision']:.2f}%")
print(f"  Recall:    {test_results['eval_recall']:.2f}% ⭐")
print(f"  F1 Score:  {test_results['eval_f1']:.2f}%")
print("="*70)

if test_results['eval_recall'] > 95:
    print("🎉 EXCELLENT! Recall >95% - Model will catch phishing!")
elif test_results['eval_recall'] > 90:
    print("✅ GOOD! Recall >90% - Acceptable performance")
else:
    print("⚠️ Recall <90% - Consider training longer or adjusting parameters")

# ============================================================================
# STEP 13: Test on Sample Phishing
# ============================================================================
print("\n[13/14] Testing on sample phishing email...")

sample_phishing = """
URGENT! Your PayPal account has been SUSPENDED due to unusual activity.
Please verify your identity immediately to avoid permanent closure.
Click here: http://paypal-security-verify.com/login.php
Provide your credit card number, CVV, and social security number NOW!
You have 24 hours before account deletion!
"""

inputs = tokenizer(
    sample_phishing,
    max_length=MAX_LENGTH,
    padding='max_length',
    truncation=True,
    return_tensors='pt'
).to(device)

with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    probs = torch.softmax(logits, dim=1)
    pred = torch.argmax(logits, dim=1).item()

print(f"\n🧪 Sample Test:")
print(f"  Email: {sample_phishing[:80]}...")
print(f"\n  Prediction: {'🚨 PHISHING' if pred == 1 else '✅ LEGITIMATE'}")
print(f"  Confidence: {probs[0][pred].item()*100:.1f}%")
print(f"  (Legit: {probs[0][0].item()*100:.1f}%, Phishing: {probs[0][1].item()*100:.1f}%)")

if pred == 1 and probs[0][1].item() > 0.9:
    print("\n🎉 Perfect! Model detected phishing with high confidence!")
elif pred == 1:
    print("\n✅ Correct prediction but confidence could be higher")
else:
    print("\n❌ ERROR! Model failed to detect obvious phishing!")

# ============================================================================
# STEP 14: Save and Download Model
# ============================================================================
print("\n[14/14] Saving model...")

output_dir = 'bert_phishing_detector'
os.makedirs(output_dir, exist_ok=True)

trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)
print(f"✅ Model saved to {output_dir}/")

# Zip the model
print("\n📦 Creating zip file...")
shutil.make_archive('bert_phishing_detector', 'zip', 'bert_phishing_detector')
print("✅ Model zipped")

# Download
print("\n📥 Downloading model...")
try:
    from google.colab import files
    files.download('bert_phishing_detector.zip')
    print("✅ Download started!")
except ImportError:
    print("⚠️ Not in Colab - model saved locally")

print("\n" + "="*70)
print("🎉 ALL DONE!")
print("="*70)
print("\n📋 Next Steps:")
print("1. Extract bert_phishing_detector.zip")
print("2. Replace models/bert_phishing_detector/ with extracted folder")
print("3. Restart Docker: docker-compose restart api")
print("4. Test in dashboard!")
print("\n✅ Training Summary:")
print(f"   - Total emails: {len(all_texts)}")
print(f"   - Training time: {duration:.1f} minutes")
print(f"   - Test accuracy: {test_results['eval_accuracy']:.2f}%")
print(f"   - Test recall: {test_results['eval_recall']:.2f}%")
print("="*70)
