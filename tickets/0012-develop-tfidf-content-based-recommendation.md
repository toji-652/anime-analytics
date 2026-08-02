---
id: "0012"
title: Develop TF-IDF content-based recommendation model
status: done
assigned-role: backend-developer
assigned-agent: antigravity
depends-on: ["0008"]
created-by: scrum-master
created: 2026-08-02
branch: ticket/0012-develop-tfidf-content-based-recommendation
---

## Description
Develop `ml/train_content.py` using TF-IDF over anime synopses combined with one-hot encoded genres, studios, and source types to build cosine similarity matrices.

## Acceptance Criteria
- [x] TF-IDF vectorizer built on `synopsis` combined with genre and studio metadata
- [x] Cosine similarity matrix computed for all catalogue items
- [x] Cold-start handling verified for titles with 0 user ratings

## Notes / Links
- TRD §5.5
