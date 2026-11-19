from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import Counter
from algorithms import run_aho_corasick, run_kmp_multi

app = FastAPI(title="DSA2-P065 Keyword Search Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    mode: str          # "nlp" | "plagiarism" | "dna"
    text: str          # Main text / Document A / DNA Sequence
    secondary: str     # Keywords / Document B / DNA Motifs
    case_sensitive: bool = False


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.text.strip() or not req.secondary.strip():
        raise HTTPException(status_code=400, detail="Both text and pattern/document inputs are required.")

    raw_text = req.text
    search_text = raw_text if req.case_sensitive else raw_text.lower()
    sec_input = req.secondary if req.case_sensitive else req.secondary.lower()

    # Mode-specific pattern extraction
    if req.mode == "dna":
        dna_clean = raw_text.upper().replace("\n", "").replace(" ", "")
        if not set(dna_clean).issubset({"A", "T", "C", "G"}):
            raise HTTPException(status_code=400, detail="DNA sequence must only contain A, T, C, G characters.")
        search_text = raw_text.upper()
        patterns = [p.strip().upper() for p in req.secondary.split(",") if p.strip()]
        for p in patterns:
            if not set(p).issubset({"A", "T", "C", "G"}):
                raise HTTPException(status_code=400, detail=f"Invalid DNA motif '{p}'. Use only A, T, C, G.")

    elif req.mode == "plagiarism":
        # Break Document B into overlapping 4-word phrases (shingles)
        words = sec_input.split()
        window = 4 if len(words) >= 4 else max(1, len(words))
        patterns = list({
            " ".join(words[i:i + window])
            for i in range(len(words) - window + 1)
        })

    else:  # "nlp"
        patterns = [p.strip() for p in sec_input.split(",") if p.strip()]

    if not patterns:
        raise HTTPException(status_code=400, detail="No valid search patterns extracted.")

    # Execute both algorithms for comparison
    ac_results = run_aho_corasick(search_text, patterns)
    kmp_results = run_kmp_multi(search_text, patterns)

    # Restore original-case matched substrings & build context snippets
    freq_counter = Counter()
    contexts = []
    for m in ac_results["matches"]:
        original_slice = raw_text[m["start"]:m["end"]]
        m["matched_text"] = original_slice
        freq_counter[m["pattern"]] += 1

        if len(contexts) < 100:  # Cap UI snippet list to 100 entries
            c_start = max(0, m["start"] - 25)
            c_end = min(len(raw_text), m["end"] + 25)
            contexts.append({
                "pattern": m["pattern"],
                "start": m["start"],
                "end": m["end"],
                "before": raw_text[c_start:m["start"]],
                "match": original_slice,
                "after": raw_text[m["end"]:c_end]
            })

    return {
        "mode": req.mode,
        "patterns_count": len(set(patterns)),
        "pattern_frequencies": dict(freq_counter),
        "aho_corasick": ac_results,
        "kmp": kmp_results,
        "contexts": contexts
    }