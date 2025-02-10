"""
services/recommender.py

This module defines the hybrid recommendation merging logic.
The `hybrid_merge` function takes recommendations from multiple sources and
combines them using configurable weights, ensuring uniqueness and ranking the results.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def hybrid_merge(
    clicked_recs: List[Dict[str, Any]],
    search_recs: List[Dict[str, Any]],
    diverse_recs: List[Dict[str, Any]],
    weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Merge recommendations from clicked, search, and diverse recommendation sources 
    using configurable weights.

    By default, the weights are:
      - clicked: 0.5
      - search: 0.4
      - diverse: 0.1

    Each recommendation is assumed to be a dictionary containing at minimum:
      - "id": A unique identifier (e.g. a 10-character product id)
      - "score": A float score to be weighted

    If an item appears in more than one list, its scores are aggregated.

    Parameters:
        clicked_recs (List[Dict]): Recommendations from product clicks.
        search_recs (List[Dict]): Recommendations from search queries.
        diverse_recs (List[Dict]): Diverse (random or curated) recommendations.
        weights (Dict[str, float]): Weights for each recommendation source.

    Returns:
        List[Dict]: Sorted list of merged recommendations.
    """
    if weights is None:
        weights = {'clicked': 0.5, 'search': 0.4, 'diverse': 0.1}
    
    aggregated = {}

    def aggregate(recs: List[Dict[str, Any]], weight: float):
        for rec in recs:
            rec_id = rec.get('id')
            if rec_id is None:
                continue
            score = rec.get('score', 0) * weight
            if rec_id in aggregated:
                aggregated[rec_id]['score'] += score
            else:
                # Copy recommendation dict and multiply score by weight.
                aggregated[rec_id] = rec.copy()
                aggregated[rec_id]['score'] = score

    aggregate(clicked_recs, weights.get('clicked', 0))
    aggregate(search_recs, weights.get('search', 0))
    aggregate(diverse_recs, weights.get('diverse', 0))
    
    # Convert the aggregated dict to a list and sort by descending score.
    merged_list = list(aggregated.values())
    merged_list.sort(key=lambda x: x['score'], reverse=True)
    
    logger.debug("Hybrid merge produced %d recommendations.", len(merged_list))
    return merged_list 