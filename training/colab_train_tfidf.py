"""
🎯 TF-IDF Balanced Model Training Script
========================================
Train TF-IDF + Ensemble Models with Balanced Dataset

USAGE IN GOOGLE COLAB:
1. Upload this file to Colab
2. Run: !python colab_train_tfidf.py
3. Download models from models/ folder

OR copy-paste all code into a single Colab cell and run!

Estimated time: 10-15 minutes
"""

print("="*70)
print("🚀 TF-IDF + Ensemble Training (Colab)")
print("="*70)

# ============================================================================
# STEP 1: Upload CSV Files
# ============================================================================
print("\n[1/13] Upload CSV files...")
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
print("\n[2/13] Installing dependencies...")
os.system('pip install -q pandas numpy scikit-learn xgboost lightgbm imbalanced-learn tqdm joblib')
print("✅ Dependencies installed")

# ============================================================================
# STEP 3: Import Libraries
# ============================================================================
print("\n[3/13] Importing libraries...")
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
try:
    from imblearn.over_sampling import SMOTE  # type: ignore
except ImportError:
    SMOTE = None  # type: ignore
import pickle
from tqdm import tqdm
print("✅ Libraries imported successfully")

# ============================================================================
# STEP 4: Load Email Datasets
# ============================================================================
print("\n[4/13] Loading email datasets...")

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
                # Convert labels to binary
                df['binary_label'] = df[label_col].apply(
                    lambda x: 1 if str(x).lower() in ['1', 'spam', 'phishing', 'phishing email'] else 0
                )
                
                texts = df[text_col].dropna().astype(str).tolist()
                labels = df.loc[df[text_col].notna(), 'binary_label'].tolist()
                
                all_texts.extend(texts)
                all_labels.extend(labels)
                
                print(f"  ✅ {dataset}: {len(texts)} emails ({sum(labels)} phishing, {len(labels)-sum(labels)} legitimate)")
        except Exception as e:
            print(f"  ⚠️ Error loading {dataset}: {e}")

print(f"\n📊 Total emails loaded: {len(all_texts)}")
print(f"   Phishing: {sum(all_labels)} ({sum(all_labels)/len(all_labels)*100:.1f}%)")
print(f"   Legitimate: {len(all_labels)-sum(all_labels)} ({(len(all_labels)-sum(all_labels))/len(all_labels)*100:.1f}%)")

# ============================================================================
# STEP 5: Split Data
# ============================================================================
print("\n[5/13] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    all_texts, all_labels, test_size=0.2, random_state=42, stratify=all_labels
)
print(f"✅ Train set: {len(X_train)} emails")
print(f"✅ Test set: {len(X_test)} emails")

# ============================================================================
# STEP 6: Train TF-IDF Vectorizer
# ============================================================================
print("\n[6/13] Training TF-IDF vectorizer...")
tfidf = TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.8,
    ngram_range=(1, 2),
    stop_words='english'
)

X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

print(f"✅ TF-IDF vocabulary size: {len(tfidf.vocabulary_)}")
print(f"   Train matrix shape: {X_train_vec.shape}")
print(f"   Test matrix shape: {X_test_vec.shape}")

# ============================================================================
# STEP 7: Apply SMOTE
# ============================================================================
print("\n[7/13] Applying SMOTE for balancing...")
if SMOTE is None:
    raise ImportError("SMOTE not available. Install with: pip install imbalanced-learn")
smote = SMOTE(random_state=42, k_neighbors=3)  # type: ignore
X_train_balanced, y_train_balanced = smote.fit_resample(X_train_vec, y_train)

print(f"✅ Balanced training set:")
print(f"   Phishing: {sum(y_train_balanced)} ({sum(y_train_balanced)/len(y_train_balanced)*100:.1f}%)")
print(f"   Legitimate: {len(y_train_balanced)-sum(y_train_balanced)} ({(len(y_train_balanced)-sum(y_train_balanced))/len(y_train_balanced)*100:.1f}%)")

# ============================================================================
# STEP 8: Train Base Models
# ============================================================================
print("\n[8/13] Training base models...")

print("  [1/3] Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train_balanced, y_train_balanced)
print("      ✅ Random Forest trained")

print("  [2/3] XGBoost...")
xgb = XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1, use_label_encoder=False, eval_metric='logloss')
xgb.fit(X_train_balanced, y_train_balanced)
print("      ✅ XGBoost trained")

print("  [3/3] LightGBM...")
lgbm = LGBMClassifier(n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
lgbm.fit(X_train_balanced, y_train_balanced)
print("      ✅ LightGBM trained")

# ============================================================================
# STEP 9: Train Voting Classifier
# ============================================================================
print("\n[9/13] Training Voting Classifier...")
voting_clf = VotingClassifier(
    estimators=[('rf', rf), ('xgb', xgb), ('lgbm', lgbm)],  # type: ignore
    voting='soft'
)
voting_clf.fit(X_train_balanced, y_train_balanced)
print("✅ Voting Classifier trained")

# ============================================================================
# STEP 10: Train Stacking Classifier
# ============================================================================
print("\n[10/13] Training Stacking Classifier...")
stacking_clf = StackingClassifier(
    estimators=[('rf', rf), ('xgb', xgb), ('lgbm', lgbm)],  # type: ignore
    final_estimator=LogisticRegression(max_iter=1000),
    cv=5
)
stacking_clf.fit(X_train_balanced, y_train_balanced)
print("✅ Stacking Classifier trained")

# ============================================================================
# STEP 11: Test with Phishing Email
# ============================================================================
print("\n[11/13] Testing with obvious phishing email...")

test_phishing = [
    "URGENT! Your PayPal account suspended. Click to verify: http://fake-paypal.com Enter SSN and credit card NOW!"
]
test_vec = tfidf.transform(test_phishing)

print(f'\n🧪 Test email: "{test_phishing[0][:80]}..."\n')

voting_proba = voting_clf.predict_proba(test_vec)[0]
print(f"Voting Classifier:")
print(f"  Legitimate: {voting_proba[0]*100:.1f}%")
print(f"  Phishing:   {voting_proba[1]*100:.1f}%")
print(f"  Prediction: {'PHISHING ✅' if voting_proba[1] > 0.5 else 'LEGITIMATE ❌'}")

stacking_proba = stacking_clf.predict_proba(test_vec)[0]
print(f"\nStacking Classifier:")
print(f"  Legitimate: {stacking_proba[0]*100:.1f}%")
print(f"  Phishing:   {stacking_proba[1]*100:.1f}%")
print(f"  Prediction: {'PHISHING ✅' if stacking_proba[1] > 0.5 else 'LEGITIMATE ❌'}")

avg_phishing = (voting_proba[1] + stacking_proba[1]) / 2
print(f"\nAverage (Production API):")
print(f"  Phishing:   {avg_phishing*100:.1f}%")
print(f"  Prediction: {'PHISHING ✅' if avg_phishing > 0.5 else 'LEGITIMATE ❌'}")

if avg_phishing > 0.8:
    print("\n🎉 SUCCESS! Model is working properly (>80% phishing score)")
elif avg_phishing > 0.5:
    print("\n⚠️ Model works but score is low. Expected >80%, got {avg_phishing*100:.1f}%")
else:
    print("\n❌ FAILED! Model classified phishing as legitimate")

# ============================================================================
# STEP 12: Evaluate on Test Set
# ============================================================================
print("\n[12/13] Evaluating on full test set...")

voting_pred = voting_clf.predict(X_test_vec)
stacking_pred = stacking_clf.predict(X_test_vec)

print("\n" + "="*50)
print("Voting Classifier:")
print("="*50)
print(classification_report(y_test, voting_pred, target_names=['Legitimate', 'Phishing']))
print(f"Accuracy: {accuracy_score(y_test, voting_pred)*100:.2f}%")

print("\n" + "="*50)
print("Stacking Classifier:")
print("="*50)
print(classification_report(y_test, stacking_pred, target_names=['Legitimate', 'Phishing']))
print(f"Accuracy: {accuracy_score(y_test, stacking_pred)*100:.2f}%")

# ============================================================================
# STEP 13: Save Models
# ============================================================================
print("\n[13/13] Saving models...")

os.makedirs('models', exist_ok=True)

with open('models/tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)
print("  ✅ TF-IDF vectorizer saved (models/tfidf_vectorizer.pkl)")

with open('models/email_detector_voting.pkl', 'wb') as f:
    pickle.dump(voting_clf, f)
print("  ✅ Voting classifier saved (models/email_detector_voting.pkl)")

with open('models/email_detector_stacking.pkl', 'wb') as f:
    pickle.dump(stacking_clf, f)
print("  ✅ Stacking classifier saved (models/email_detector_stacking.pkl)")

print("\n" + "="*70)
print("🎉 TRAINING COMPLETE!")
print("="*70)
print("\n📥 Download these files from the 'models' folder:")
print("   1. tfidf_vectorizer.pkl (~180 KB)")
print("   2. email_detector_voting.pkl (~30 MB)")
print("   3. email_detector_stacking.pkl (~30 MB)")
print("\n📂 Copy them to your local models/ folder")
print("🐳 Restart Docker: docker-compose restart api")
print("\n✅ Done!")
