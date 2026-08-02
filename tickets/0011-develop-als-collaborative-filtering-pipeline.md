---
id: "0011"
title: Develop ALS collaborative filtering pipeline with MLflow
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0008"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0011-develop-als-collaborative-filtering-pipeline
---

## Description
Develop `ml/train_collaborative.py` using `implicit` library ALS matrix factorization on user-anime interaction matrices, logging parameters and metrics to MLflow.

## Acceptance Criteria
- [x] ALS matrix factorization model trains on user x anime interaction matrix
- [x] Hyperparameters (factors, regularization, iterations) logged to MLflow
- [x] Model artifacts saved cleanly in `ml/artifacts/`

## Notes / Links
- TRD §5.5
