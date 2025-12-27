"""
⚡ FastText Email Detector Training Script
==========================================
Train FastText model for phishing detection

USAGE IN GOOGLE COLAB:
1. Upload this file to Colab
2. Run: !python colab_train_fasttext.py
3. Download model from models/ folder

OR copy-paste all code into a single Colab cell and run!

Estimated time: 5-10 minutes
"""

print("="*70)
print("🚀 FastText Training (Colab)")
print("="*70)

# ============================================================================
# STEP 1: Upload CSV Files
# ============================================================================
print("\n[1/12] Upload CSV files...")
print("📤 Please upload these 7 CSV files:")
print("   1. CEAS_08.csv")
print("   2. Enron.csv")
print("   3. Ling.csv")
print("   4. Nazario.csv")
print("   5. Nigerian_Fraud.csv")
print("   6. SpamAssasin.csv")
print("   7. phishing_email.csv")
print("\nClick 'Choose Files' button and select all 7 CSV files...")

import os
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
    print("⚠️  Not in Colab - assuming files are already in dataset/ folder")
    if not os.path.exists('dataset'):
        print("❌ ERROR: dataset/ folder not found!")
        sys.exit(1)

# ============================================================================
# STEP 2: Install Dependencies
# ============================================================================
print("\n[2/12] Installing dependencies...")
os.system('pip install -q fasttext-wheel pandas numpy scikit-learn tqdm')
print("✅ Dependencies installed")

# ============================================================================
# STEP 3: Import Libraries
# ============================================================================
print("\n[3/12] Importing libraries...")
import pandas as pd
import numpy as np
import fasttext
import re
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Suppress FastText warnings (only works in some versions)
if hasattr(fasttext.FastText, 'eprint'):
    fasttext.FastText.eprint = lambda x: None
print("✅ Libraries imported successfully")

# ============================================================================
# STEP 4: Load Email Datasets
# ============================================================================
print("\n[4/12] Loading email datasets...")

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
            df = pd.read_csv(dataset)
            
            # Find text column
            text_cols = ['body', 'text', 'email', 'message', 'content', 'Email Text']
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
                # Convert labels to string
                df['label_str'] = df[label_col].apply(
                    lambda x: 'phishing' if str(x).lower() in ['1', 'spam', 'phishing', 'phishing email'] else 'legitimate'
                )
                
                texts = df[text_col].dropna().astype(str).tolist()
                labels = df.loc[df[text_col].notna(), 'label_str'].tolist()
                
                all_texts.extend(texts)
                all_labels.extend(labels)
                
                phishing_count = sum(1 for l in labels if l == 'phishing')
                print(f"  ✅ {dataset}: {len(texts)} emails ({phishing_count} phishing, {len(labels)-phishing_count} legitimate)")
        except Exception as e:
            print(f"  ⚠️ Error loading {dataset}: {e}")

phishing_total = sum(1 for l in all_labels if l == 'phishing')
print(f"\n📊 Total emails loaded: {len(all_texts)}")
print(f"   Phishing: {phishing_total} ({phishing_total/len(all_labels)*100:.1f}%)")
print(f"   Legitimate: {len(all_labels)-phishing_total} ({(len(all_labels)-phishing_total)/len(all_labels)*100:.1f}%)")

# ============================================================================
# STEP 5: Preprocess Text
# ============================================================================
print("\n[5/12] Preprocessing text...")

def preprocess_text(text):
    text = text.lower()
    text = ' '.join(text.split())
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text

all_texts_processed = [preprocess_text(t) for t in tqdm(all_texts, desc="Preprocessing")]
print("✅ Preprocessing complete")

# ============================================================================
# STEP 6: Split Data
# ============================================================================
print("\n[6/12] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    all_texts_processed, all_labels, test_size=0.2, random_state=42, stratify=all_labels
)
print(f"✅ Train set: {len(X_train)} emails")
print(f"✅ Test set: {len(X_test)} emails")

# ============================================================================
# STEP 7: Create FastText Files
# ============================================================================
print("\n[7/12] Creating FastText training files...")

os.makedirs('data', exist_ok=True)

train_file = 'data/fasttext_train.txt'
test_file = 'data/fasttext_test.txt'

with open(train_file, 'w', encoding='utf-8') as f:
    for text, label in zip(X_train, y_train):
        f.write(f'__label__{label} {text}\n')

with open(test_file, 'w', encoding='utf-8') as f:
    for text, label in zip(X_test, y_test):
        f.write(f'__label__{label} {text}\n')

print(f"✅ Training file: {train_file}")
print(f"✅ Test file: {test_file}")

# ============================================================================
# STEP 8: Train FastText Model
# ============================================================================
print("\n[8/12] Training FastText model...")
print("   This may take 5-10 minutes...\n")

model = fasttext.train_supervised(
    input=train_file,
    lr=0.5,
    epoch=25,
    wordNgrams=2,
    dim=100,
    ws=5,
    minCount=2,
    loss='softmax',
    thread=4,
    verbose=2
)

print("\n✅ FastText model trained!")

# ============================================================================
# STEP 9: Evaluate on Test File
# ============================================================================
print("\n[9/12] Evaluating on test file...")

n, precision, recall = model.test(test_file)
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"Test set evaluation:")
print(f"  Samples: {n}")
print(f"  Precision: {precision:.4f}")
print(f"  Recall: {recall:.4f}")
print(f"  F1-Score: {f1:.4f}")

# ============================================================================
# STEP 10: Test with Phishing Email
# ============================================================================
print("\n[10/12] Testing with obvious phishing email...")

test_email = "urgent your paypal account suspended click to verify http fake paypal com enter ssn and credit card now"

labels, scores = model.predict(test_email)  # Returns (labels, scores)
label = labels[0].replace('__label__', '')
confidence = float(scores[0])
phishing_score = confidence*100 if label == 'phishing' else (1-confidence)*100

print(f'\n🧪 Test email: "{test_email}"\n')
print(f"Prediction: {label.upper()}")
print(f"Confidence: {confidence*100:.1f}%")
print(f"Phishing Score: {phishing_score:.1f}%")

if phishing_score > 80:
    print("\n🎉 SUCCESS! Model detected phishing (>80% score)")
elif phishing_score > 50:
    print(f"\n⚠️ Model works but score is low. Expected >80%, got {phishing_score:.1f}%")
else:
    print("\n❌ FAILED! Model classified phishing as legitimate")

# ============================================================================
# STEP 11: Detailed Test Set Evaluation
# ============================================================================
print("\n[11/12] Detailed test set evaluation...")

y_pred = []
for text in tqdm(X_test, desc="Predicting"):
    labels, _ = model.predict(text)
    pred = labels[0].replace('__label__', '')
    y_pred.append(pred)

print("\n" + "="*50)
print("Classification Report:")
print("="*50)
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
print(f"\nAccuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")

# ============================================================================
# STEP 12: Save Model
# ============================================================================
print("\n[12/12] Saving model...")

os.makedirs('models', exist_ok=True)
model.save_model('models/fasttext_email_detector.bin')

print("✅ Model saved: models/fasttext_email_detector.bin")

print("\n" + "="*70)
print("🎉 TRAINING COMPLETE!")
print("="*70)
print("\n📥 Download this file from the 'models' folder:")
print("   - fasttext_email_detector.bin (~885 MB)")
print("\n📂 Copy it to your local models/ folder")
print("🐳 Restart Docker: docker-compose restart api")
print("\n⚠️ Don't forget to add 'fasttext-wheel>=0.9.2' to requirements.txt!")
print("\n✅ Done!")
