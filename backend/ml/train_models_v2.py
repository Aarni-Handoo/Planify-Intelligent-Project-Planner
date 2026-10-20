
import os
import json
import joblib
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import (
    accuracy_score, f1_score,
    mean_absolute_error, r2_score,
    classification_report
)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data", "processed")
MODELS = os.path.join(BASE, "models", "final_v2")
os.makedirs(MODELS, exist_ok=True)

train = pd.read_csv(os.path.join(DATA, "train_v2.csv"))
val = pd.read_csv(os.path.join(DATA, "validation_v2.csv"))
test = pd.read_csv(os.path.join(DATA, "test_v2.csv"))

def make_text(df):
    return (
        df["project_type"].astype(str) + " " +
        df["task_description"].astype(str)
    )

tfidf = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    stop_words="english"
)

X_train = tfidf.fit_transform(make_text(train))
X_val = tfidf.transform(make_text(val))
X_test = tfidf.transform(make_text(test))

results = []

def record(name, metric, score):
    results.append({
        "Model": name,
        "Metric": metric,
        "Score": round(float(score), 4)
    })

def save(model, name):
    joblib.dump(model, os.path.join(MODELS, name))

save(tfidf, "tfidf_vectorizer.pkl")

# ======================================
# MODEL 1: CATEGORY
# ======================================

category_model = LogisticRegression(
    max_iter=2000,
    random_state=42
)

category_model.fit(X_train, train["category"])
category_pred = category_model.predict(X_test)

record(
    "Category", "Accuracy",
    accuracy_score(test["category"], category_pred)
)
save(category_model, "category_model.pkl")

# ======================================
# MODEL 2: COMPLEXITY
# ======================================

complexity_model = RandomForestClassifier(
    n_estimators=200,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

complexity_model.fit(X_train, train["complexity"])
complexity_pred = complexity_model.predict(X_test)

record(
    "Complexity", "Accuracy",
    accuracy_score(test["complexity"], complexity_pred)
)
save(complexity_model, "complexity_model.pkl")

# ======================================
# MODEL 3: PRIORITY
# ======================================

priority_model = RandomForestClassifier(
    n_estimators=200,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

priority_model.fit(X_train, train["priority"])
priority_pred = priority_model.predict(X_test)

record(
    "Priority", "Accuracy",
    accuracy_score(test["priority"], priority_pred)
)
save(priority_model, "priority_model.pkl")

# ======================================
# MODEL 4: ESTIMATED HOURS
# ======================================

hours_model = RandomForestRegressor(
    n_estimators=250,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

hours_model.fit(X_train, train["estimated_hours"])
hours_pred = hours_model.predict(X_test)

record(
    "Estimated Hours", "MAE",
    mean_absolute_error(test["estimated_hours"], hours_pred)
)

record(
    "Estimated Hours", "R2",
    r2_score(test["estimated_hours"], hours_pred)
)

save(hours_model, "hours_model.pkl")

# ======================================
# MODEL 5: REQUIRED SKILLS
# ======================================

def split_skills(series):
    return series.fillna("").apply(
        lambda value: [
            skill.strip()
            for skill in str(value).split(",")
            if skill.strip()
        ]
    )

encoder = MultiLabelBinarizer()

y_train_skills = encoder.fit_transform(
    split_skills(train["required_skills"])
)

y_test_skills = encoder.transform(
    split_skills(test["required_skills"])
)

skill_model = OneVsRestClassifier(
    LogisticRegression(
        max_iter=2000,
        random_state=42
    ),
    n_jobs=-1
)

skill_model.fit(X_train, y_train_skills)

# Use top-k instead of returning every skill.
# This is a candidate-skill recommendation policy.
skill_prob = skill_model.predict_proba(X_test)

skill_pred = np.zeros_like(skill_prob, dtype=int)

for i, probabilities in enumerate(skill_prob):
    top = np.argsort(probabilities)[::-1][:3]
    selected = [
        j for j in top
        if probabilities[j] >= 0.25
    ]

    if not selected:
        selected = [top[0]]

    skill_pred[i, selected] = 1

record(
    "Required Skills", "Micro F1",
    f1_score(
        y_test_skills, skill_pred,
        average="micro", zero_division=0
    )
)

save(skill_model, "skill_model.pkl")
save(encoder, "skill_encoder.pkl")

# ======================================
# MODEL 6: DELAY RISK
# ======================================

# These features must be available at prediction time.
DELAY_FEATURES = [
    "complexity",
    "estimated_hours",
    "deadline_days",
    "team_size",
    "skill_count"
]

def delay_features(text_features, df):
    numeric = df[DELAY_FEATURES].astype(float).copy()

    # Scale numeric features for Logistic Regression
    numeric = numeric / np.array([5, 40, 15, 8, 4])

    return hstack([
        text_features,
        csr_matrix(numeric.to_numpy())
    ]).tocsr()

X_delay_train = delay_features(X_train, train)
X_delay_test = delay_features(X_test, test)

y_delay_train = (train["delay_hours"] > 0).astype(int)
y_delay_test = (test["delay_hours"] > 0).astype(int)

delay_model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)

delay_model.fit(X_delay_train, y_delay_train)
delay_pred = delay_model.predict(X_delay_test)

record(
    "Delay Risk", "F1",
    f1_score(y_delay_test, delay_pred, zero_division=0)
)

record(
    "Delay Risk", "Accuracy",
    accuracy_score(y_delay_test, delay_pred)
)

save(delay_model, "delay_model.pkl")

# ======================================
# RESULTS
# ======================================

results_df = pd.DataFrame(results)

print("\n========== V2 RESULTS ==========")
print(results_df.to_string(index=False))

print("\n========== DELAY REPORT ==========")
print(classification_report(
    y_delay_test, delay_pred,
    zero_division=0
))

results_df.to_csv(
    os.path.join(MODELS, "metrics_v2.csv"),
    index=False
)

# ======================================
# TEST SAMPLE PREDICTIONS
# ======================================

def predict_task(project_type, description):
    text = project_type + " " + description
    vector = tfidf.transform([text])

    probabilities = skill_model.predict_proba(vector)[0]
    top = np.argsort(probabilities)[::-1][:3]

    selected = [
        j for j in top
        if probabilities[j] >= 0.25
    ]

    if not selected:
        selected = [top[0]]

    skills = encoder.classes_[selected].tolist()

    return {
        "category": category_model.predict(vector)[0],
        "skills": skills,
        "complexity": int(
            complexity_model.predict(vector)[0]
        ),
        "priority": priority_model.predict(vector)[0],
        "estimated_hours": round(
            float(hours_model.predict(vector)[0]), 1
        )
    }

samples = [
    ("E-Commerce", "create responsive checkout interface"),
    ("Healthcare", "train image classification model for medical images"),
    ("Banking", "implement secure transaction api"),
    ("Portfolio Website", "design responsive mobile navigation"),
    ("Food Delivery", "create database for restaurant orders")
]

print("\n========== SAMPLE PREDICTIONS ==========")

for project, task in samples:
    print("\nPROJECT:", project)
    print("TASK:", task)
    print(predict_task(project, task))

print("\nPHASE 3 V2 TRAINING COMPLETE")
