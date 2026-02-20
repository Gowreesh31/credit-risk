"""
Random Forest Model Training Pipeline.

Trains a credit risk classifier on engineered features:
- 80/20 train-test split
- 5-fold cross-validation
- Feature importance analysis
- Saves model + feature columns to disk
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import config
from ml.data_prep import prepare_training_data


def train_model():
    """Train Random Forest classifier and evaluate performance."""
    print("=" * 60)
    print("🧠 CREDIT RISK MODEL TRAINING PIPELINE")
    print("=" * 60)

    # ─── Step 1: Prepare data ───────────────────────────────────
    print("\n📊 Step 1: Preparing training data...")
    X, y, feature_columns = prepare_training_data()

    # ─── Step 2: Train-test split ───────────────────────────────
    print("\n📊 Step 2: Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set:     {len(X_test)} samples")

    # ─── Step 3: Train Random Forest ────────────────────────────
    print("\n🌲 Step 3: Training Random Forest classifier...")
    start_time = time.time()

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        min_samples_split=5,
        min_samples_leaf=2
    )
    model.fit(X_train, y_train)
    train_time = time.time() - start_time
    print(f"   Training time: {train_time:.2f}s")

    # ─── Step 4: Evaluate on test set ───────────────────────────
    print("\n📈 Step 4: Evaluating model performance...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)

    print(f"\n   Test Results:")
    print(f"   ─────────────────────────────────")
    print(f"   Accuracy:  {accuracy:.2%}")
    print(f"   Precision: {precision:.2%}")
    print(f"   Recall:    {recall:.2%}")
    print(f"   F1 Score:  {f1:.2%}")
    print(f"   ROC-AUC:   {roc_auc:.2%}")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n   Confusion Matrix:")
    print(f"   ─────────────────────────────────")
    print(f"                  Predicted")
    print(f"                  Low Risk  High Risk")
    print(f"   Actual Low  :  {cm[0][0]:>6}    {cm[0][1]:>6}")
    print(f"   Actual High :  {cm[1][0]:>6}    {cm[1][1]:>6}")

    # ─── Step 5: Cross-validation ───────────────────────────────
    print("\n🔄 Step 5: 5-fold cross-validation...")
    cv_accuracy = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    cv_roc_auc = cross_val_score(model, X, y, cv=5, scoring='roc_auc')

    print(f"   Mean Accuracy: {cv_accuracy.mean():.2%} ± {cv_accuracy.std():.2%}")
    print(f"   Mean ROC-AUC:  {cv_roc_auc.mean():.2%} ± {cv_roc_auc.std():.2%}")

    # Overfitting check
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    gap = train_accuracy - accuracy
    print(f"   Overfitting Check: Train-Test Gap = {gap:.2%} {'(excellent)' if gap < 0.03 else '(acceptable)' if gap < 0.05 else '(⚠️ possible overfitting)'}")

    # ─── Step 6: Feature importance ─────────────────────────────
    print("\n🏆 Step 6: Top 10 most important features:")
    importances = model.feature_importances_
    feature_imp = sorted(
        zip(feature_columns, importances),
        key=lambda x: x[1],
        reverse=True
    )

    for rank, (feat, imp) in enumerate(feature_imp[:10], 1):
        bar = '█' * int(imp * 100)
        print(f"   {rank:2}. {feat:<30} {imp:.4f}  {bar}")

    # ─── Step 7: Save model ─────────────────────────────────────
    print("\n💾 Step 7: Saving model artifacts...")
    os.makedirs(config.MODEL_DIR, exist_ok=True)

    joblib.dump(model, config.MODEL_PATH)
    joblib.dump(feature_columns, config.FEATURE_COLUMNS_PATH)

    model_size = os.path.getsize(config.MODEL_PATH) / 1024
    print(f"   Model saved: {config.MODEL_PATH} ({model_size:.0f} KB)")
    print(f"   Features saved: {config.FEATURE_COLUMNS_PATH}")

    # ─── Summary ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ MODEL TRAINING COMPLETE")
    print("=" * 60)
    print(f"   ✓ Training set: {len(X_train)} samples")
    print(f"   ✓ Test Accuracy: {accuracy:.2%}")
    print(f"   ✓ Test ROC-AUC: {roc_auc:.2%}")
    print(f"   ✓ Model saved successfully")

    return model, feature_columns


if __name__ == '__main__':
    train_model()
