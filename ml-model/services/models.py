"""
services/models.py

This module provides ML model wrappers:
    - ContentModel: Loads the content-based recommendation model (TF-IDF embeddings,
      FAISS index, and product IDs) for semantic search.
    - FPGrowthModel: Loads FP-Growth association rules from a JSON file for
      generating product association suggestions.
"""

import os
import logging
import joblib
import faiss
import numpy as np
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ContentModel:
    """
    A model wrapper for content-based recommendation using precomputed FAISS index
    and preprocessor components.

    Expects the following files in the model directory:
      - faiss_index.index: FAISS index file.
      - product_ids.npy: Numpy array of product IDs corresponding to index entries.
      - preprocessor.joblib: Preprocessing pipeline (e.g., TF-IDF and related transforms).
    """
    def __init__(self, model_dir: str = 'model'):
        self.model_dir = model_dir
        try:
            self.index = faiss.read_index(os.path.join(model_dir, 'faiss_index.index'))
            self.product_ids = np.load(os.path.join(model_dir, 'product_ids.npy'), allow_pickle=True).astype(str)
            self.preprocessor = joblib.load(os.path.join(model_dir, 'preprocessor.joblib'))
            logger.info("ContentModel loaded successfully from %s", model_dir)
        except Exception as e:
            logger.exception("Failed to load ContentModel components: %s", e)
            raise

    def get_similar_products(self, product_id: str, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Returns a list of similar products based on content recommendations.
        """
        try:
            idx = np.where(self.product_ids == product_id)[0]
            if len(idx) == 0:
                return []
            pos = int(idx[0])  # Ensure pos is a pure Python int.
            # Use reconstruct() instead of accessing self.index.xb directly.
            query_vector = self.index.reconstruct(pos)
            distances, indices = self.index.search(query_vector.reshape(1, -1), top_n)
            similar_ids = self.product_ids[indices[0]]
            # Optionally filter out the original product.
            similar = [{"id": pid} for pid in similar_ids if pid != product_id]
            return similar
        except Exception as e:
            logger.error("Error during product similarity search: %s", e)
            return []


class FPGrowthModel:
    """
    A model wrapper for association rules generated via FP-Growth.

    The association rules are loaded from a JSON file (by default, 'model/fp_rules.json').
    Each rule is expected to have the following keys:
      - antecedents: list of product IDs representing the left-hand side.
      - consequents: list of product IDs representing the right-hand side.
      - support: float value.
      - confidence: float value.
      - lift: float value.
    """
    def __init__(self, rules_file: str = 'model/fp_rules.json'):
        self.rules_file = rules_file
        try:
            with open(rules_file, 'r') as f:
                self.rules = json.load(f)
            logger.info("FPGrowthModel loaded %d association rules from %s", len(self.rules), rules_file)
        except Exception as e:
            logger.exception("Failed to load FP-Growth rules from %s: %s", rules_file, e)
            self.rules = []

    def get_associated_products(self, product_id: str, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Given a product_id, retrieve a list of associated products based on FP-Growth rules.
        Only rules with confidence greater than or equal to min_confidence are returned.
        The association rules where the product_id appears in the antecedents are filtered
        and then sorted by confidence in descending order.

        Parameters:
            product_id (str): The anchor product id.
            min_confidence (float): The minimum confidence threshold for the rules.

        Returns:
            List[Dict]: A list of association rule dictionaries.
                      Each dictionary contains keys: 'antecedents', 'consequents',
                      'support', 'confidence', and 'lift'.
        """
        associated_rules = []
        for rule in self.rules:
            if product_id in rule.get('antecedents', []) and rule.get('confidence', 0) >= min_confidence:
                associated_rules.append(rule)
        # Sort rules by confidence descending.
        associated_rules.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        logger.debug("Found %d association rules for product_id %s.", len(associated_rules), product_id)
        return associated_rules 