# Experiment Log

## Baseline (2025-02-15)

**Hyperparameters:**
- n_estimators: 100
- max_depth: 10
- class_weight: None

**Results:**
- Accuracy: 70.1%
- Recall: 0.3%
- F1 Score: 0.6%
- ROC AUC: 0.496

**Conclusion:** Model broken (predicts no churn for almost everyone)

---

## Experiment 1: Balanced Classes (2025-02-15)

**Hyperparameters:**
- n_estimators: 100
- max_depth: 10
- class_weight: balanced ← CHANGED

**Results:**
- Accuracy: 69.8%
- Recall: 67.8% ← 226x improvement!
- F1 Score: 60.2%
- ROC AUC: 0.764

**Conclusion:** Much better! Model now catches churners.

---

## Future Experiments

### To Try:
- [ ] Increase n_estimators to 200
- [ ] Increase max_depth to 15
- [ ] Try XGBoost
- [ ] Add more features (interaction terms)
- [ ] Hyperparameter tuning with GridSearchCV
