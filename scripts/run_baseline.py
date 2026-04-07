import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI

# Allow running the script directly: python scripts/run_baseline.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from env.environment import InvoiceEnv
from env.models import InvoiceAction


SYSTEM_PROMPT = (
	"You are an invoice processing assistant. "
	"Return ONLY valid JSON with keys: extracted_fields, category, anomaly_flag. "
	"extracted_fields must contain vendor_name and invoice_date. "
	"category must be either one category or two ranked categories joined by '|', "
	"using values from Travel, Office Supplies, Utilities, Misc."
)


def _invoice_prompt(observation: Dict[str, Any]) -> str:
	return (
		"Process this invoice and return JSON only.\\n"
		f"Vendor: {observation['vendor_name']}\\n"
		f"Invoice Date: {observation['invoice_date']}\\n"
		f"Amount: {observation['amount']}\\n"
		f"Description: {observation['description']}\\n"
		f"Metadata: {json.dumps(observation['metadata'])}"
	)


def _extract_json(text: str) -> Dict[str, Any]:
	text = text.strip()
	if text.startswith("```"):
		text = text.strip("`")
		text = text.replace("json", "", 1).strip()

	try:
		return json.loads(text)
	except json.JSONDecodeError:
		start = text.find("{")
		end = text.rfind("}")
		if start != -1 and end != -1 and end > start:
			return json.loads(text[start : end + 1])
		raise


def query_model(client: OpenAI, model_name: str, observation: Dict[str, Any]) -> Dict[str, Any]:
	completion = client.chat.completions.create(
		model=model_name,
		temperature=0,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": _invoice_prompt(observation)},
		],
		response_format={"type": "json_object"},
	)
	response_text = completion.choices[0].message.content or "{}"
	return _extract_json(response_text)


def _safe_fallback_action(observation: Dict[str, Any]) -> Dict[str, Any]:
	"""Conservative fallback action to keep episodes running on API/parse failures."""
	return {
		"extracted_fields": {
			"vendor_name": observation.get("vendor_name", ""),
			"invoice_date": observation.get("invoice_date", ""),
		},
		"category": "Misc",
		"anomaly_flag": False,
	}


def _heuristic_category(observation: Dict[str, Any]) -> str:
	vendor = str(observation.get("vendor_name", "")).lower()
	description = str(observation.get("description", "")).lower()

	if any(token in vendor for token in ("uber", "lyft", "airlines", "marriott")):
		return "Travel"
	if any(token in vendor for token in ("amazon", "staples", "ikea")):
		return "Office Supplies"
	if any(token in vendor for token in ("electricity", "water", "internet", "gas")):
		return "Utilities"

	if any(token in description for token in ("flight", "hotel", "ride", "transport")):
		return "Travel|Misc"
	if any(token in description for token in ("printer", "paper", "furniture", "desk", "chair")):
		return "Office Supplies|Misc"
	if any(token in description for token in ("electricity", "water", "internet", "utility", "gas")):
		return "Utilities|Misc"

	return "Misc"


def _heuristic_action(observation: Dict[str, Any], seen_invoice_refs: set[str]) -> Dict[str, Any]:
	metadata = observation.get("metadata", {}) or {}
	invoice_ref = str(metadata.get("invoice_ref", "")).strip()

	is_duplicate = bool(invoice_ref and invoice_ref in seen_invoice_refs)
	if invoice_ref:
		seen_invoice_refs.add(invoice_ref)

	is_high_amount = float(observation.get("amount", 0.0) or 0.0) > 2500.0

	return {
		"extracted_fields": {
			"vendor_name": str(observation.get("vendor_name", "")),
			"invoice_date": str(observation.get("invoice_date", "")),
		},
		"category": _heuristic_category(observation),
		"anomaly_flag": is_duplicate or is_high_amount,
	}


def main() -> None:
	api_key = os.getenv("OPENAI_API_KEY")
	mode = os.getenv("BASELINE_MODE", "auto").strip().lower()
	if mode not in {"auto", "openai", "heuristic"}:
		raise RuntimeError("BASELINE_MODE must be one of: auto, openai, heuristic")

	use_openai = mode == "openai" or (mode == "auto" and bool(api_key))
	if mode == "openai" and not api_key:
		raise RuntimeError("OPENAI_API_KEY is required when BASELINE_MODE=openai")

	model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	client: Optional[OpenAI] = OpenAI(api_key=api_key) if use_openai and api_key else None

	env = InvoiceEnv(batch_size=12, seed=42, shuffle=True)
	observation = env.reset()
	seen_invoice_refs: set[str] = set()

	done = False
	total = 0.0
	step_count = 0

	mode_label = "openai" if use_openai else "heuristic"
	print(f"Starting baseline run (mode={mode_label})...")

	while not done:
		step_count += 1
		obs_payload = observation.model_dump()

		if use_openai and client is not None:
			try:
				raw_action = query_model(client, model_name, obs_payload)
			except Exception as exc:
				print(f"warning: model call failed at step {step_count}: {exc}")
				raw_action = _heuristic_action(obs_payload, seen_invoice_refs)
		else:
			raw_action = _heuristic_action(obs_payload, seen_invoice_refs)

		raw_category = raw_action.get("category")
		if isinstance(raw_category, list):
			raw_category = "|".join(str(item) for item in raw_category[:2])

		action = InvoiceAction(
			extracted_fields=raw_action.get("extracted_fields", {}),
			category=raw_category,
			anomaly_flag=raw_action.get("anomaly_flag"),
		)

		observation, reward, done, info = env.step(action)
		total += reward.score

		print(
			f"step={step_count:02d} "
			f"reward={reward.score:.3f} "
			f"extract={reward.details['extraction']:.3f} "
			f"cat={reward.details['category']:.3f} "
			f"anomaly={reward.details['anomaly']:.3f}"
		)

	avg_score = total / step_count if step_count else 0.0
	final_state = env.state()
	print("\nEpisode complete")
	print(f"steps={step_count}")
	print(f"total_score={total:.3f}")
	print(f"avg_score={avg_score:.3f}")
	print(f"anomaly_counts={final_state['anomaly_counts']}")


if __name__ == "__main__":
	main()
