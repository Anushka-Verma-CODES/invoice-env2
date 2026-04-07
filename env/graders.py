from __future__ import annotations

from typing import Any, Dict, Optional

from rapidfuzz import fuzz


def _normalize(value: str) -> str:
	return value.strip().lower()


def grade_extraction(extracted_fields: Dict[str, Any], invoice: Dict[str, Any]) -> float:
	"""
	Grade field extraction for vendor_name and invoice_date.
	Exact match: 1.0, fuzzy (>80): partial score, otherwise 0.
	"""
	required = ("vendor_name", "invoice_date")
	per_field_scores = []

	for key in required:
		pred = str(extracted_fields.get(key, "") or "")
		truth = str(invoice.get(key, "") or "")

		if _normalize(pred) == _normalize(truth):
			per_field_scores.append(1.0)
			continue

		ratio = fuzz.ratio(_normalize(pred), _normalize(truth))
		if ratio >= 80:
			per_field_scores.append(round(ratio / 100.0, 4))
		else:
			per_field_scores.append(0.0)

	return round(sum(per_field_scores) / len(required), 4)


def grade_category(predicted_category: Optional[str], invoice: Dict[str, Any]) -> float:
	"""
	Grade category classification.
	Correct: 1.0, close guess: 0.5, otherwise 0.0.
	Also accepts optional top-2 format "A|B" where second position gets 0.5.
	"""
	truth = invoice.get("category")
	if predicted_category is None:
		return 0.0

	tokens = [piece.strip() for piece in predicted_category.replace("|", ",").split(",") if piece.strip()]
	if not tokens:
		return 0.0

	if tokens[0] == truth:
		return 1.0
	if truth in tokens[:2]:
		return 0.5

	close_pairs = {
		frozenset(("Travel", "Misc")),
		frozenset(("Office Supplies", "Misc")),
		frozenset(("Utilities", "Misc")),
	}
	if frozenset((tokens[0], truth)) in close_pairs:
		return 0.5
	return 0.0


def detection_metrics(tp: int, fp: int, fn: int) -> Dict[str, float]:
	"""Compute precision, recall, and F1 for anomaly detection."""
	precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
	recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
	if precision + recall == 0:
		f1 = 0.0
	else:
		f1 = 2 * precision * recall / (precision + recall)
	return {
		"precision": round(precision, 4),
		"recall": round(recall, 4),
		"f1": round(f1, 4),
	}


def grade_anomaly(
	predicted_flag: Optional[bool],
	invoice: Dict[str, Any],
	*,
	tp: int,
	fp: int,
	fn: int,
) -> float:
	"""
	Grade anomaly detection using F1 over running confusion counts.
	"""
	truth = bool(invoice.get("anomaly_flag", False))
	pred = bool(predicted_flag) if predicted_flag is not None else False

	next_tp = tp + int(pred and truth)
	next_fp = fp + int(pred and not truth)
	next_fn = fn + int((not pred) and truth)

	return detection_metrics(next_tp, next_fp, next_fn)["f1"]
