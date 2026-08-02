---
id: "0013"
title: Build hybrid recommender and evaluation harness
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0011", "0012"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0013-build-hybrid-recommender-and-evaluation-harness
---

## Description
Implement `ml/hybrid.py` blending ALS collaborative and TF-IDF content scores, and build `ml/evaluate.py` testing precision@10, recall@10, and catalogue coverage against a popularity baseline.

## Acceptance Criteria
- [x] Hybrid model dynamically blends collaborative and content scores based on rating counts
- [x] `ml/evaluate.py` measures precision@10, recall@10, and coverage on held-out user test set
- [x] Model evaluation gate verifies hybrid recommender outperforms popularity baseline

## Notes / Links
- PRD §5, TRD §5.5
