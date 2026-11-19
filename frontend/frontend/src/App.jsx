import { useState } from "react";

const SAMPLES = {
  nlp: {
    text: "Natural Language Processing (NLP) enables computers to understand human language. Modern NLP pipelines rely on tokenization, embeddings, and fast keyword search algorithms to index millions of documents.",
    secondary: "NLP, language, search, algorithms, tokenization",
  },
  plagiarism: {
    text: "Data structures and algorithms form the foundation of computer science. Choosing the optimal data structure reduces time complexity from quadratic to linear in large-scale text processing systems.",
    secondary: "Modern software relies on good design. Choosing the optimal data structure reduces time complexity significantly. In large-scale text processing systems, efficiency matters.",
  },
  dna: {
    text: "ATGCGATACGCTTGAACGTAGCTAGCATCGATCGTAGCTAGCTAGCATCGATCGATCGATCGTAGCTAGCATCG",
    secondary: "ATG, CGAT, TAGC, GCTA",
  },
};

export default function App() {
  const [mode, setMode] = useState("nlp");
  const [text, setText] = useState(SAMPLES.nlp.text);
  const [secondary, setSecondary] = useState(SAMPLES.nlp.secondary);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setText(SAMPLES[newMode].text);
    setSecondary(SAMPLES[newMode].secondary);
    setResult(null);
    setError("");
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, text, secondary, case_sensitive: caseSensitive }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Merge overlapping match intervals so <mark> tags render cleanly
  const renderHighlightedText = () => {
    if (!result || result.aho_corasick.matches.length === 0) {
      return <span>{text}</span>;
    }

    const sorted = [...result.aho_corasick.matches].sort((a, b) => a.start - b.start);
    const merged = [{ ...sorted[0] }];
    for (let i = 1; i < sorted.length; i++) {
      const prev = merged[merged.length - 1];
      const curr = sorted[i];
      if (curr.start <= prev.end) {
        prev.end = Math.max(prev.end, curr.end);
      } else {
        merged.push({ ...curr });
      }
    }

    const elements = [];
    let cursor = 0;
    merged.forEach((m, idx) => {
      if (m.start > cursor) {
        elements.push(<span key={`txt-${idx}`}>{text.slice(cursor, m.start)}</span>);
      }
      elements.push(
        <mark key={`mk-${idx}`} style={{ backgroundColor: "#fde047", padding: "1px 3px", borderRadius: "3px" }}>
          {text.slice(m.start, m.end)}
        </mark>
      );
      cursor = m.end;
    });
    if (cursor < text.length) {
      elements.push(<span key="txt-end">{text.slice(cursor)}</span>);
    }
    return elements;
  };

  return (
    <div style={{ maxWidth: "960px", margin: "24px auto", fontFamily: "system-ui, sans-serif", padding: "0 16px" }}>
      <h2>Keyword Search Analyzer (DSA2-P065)</h2>

      {/* Mode Selector */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
        {[
          { id: "nlp", label: "NLP Keyword Search" },
          { id: "plagiarism", label: "Plagiarism Check" },
          { id: "dna", label: "DNA Motif Search" },
        ].map((m) => (
          <button
            key={m.id}
            onClick={() => handleModeChange(m.id)}
            style={{
              padding: "8px 14px",
              cursor: "pointer",
              fontWeight: mode === m.id ? "bold" : "normal",
              backgroundColor: mode === m.id ? "#2563eb" : "#e5e7eb",
              color: mode === m.id ? "#fff" : "#111",
              border: "none",
              borderRadius: "6px",
            }}
          >
            {m.label}
          </button>
        ))}
      </div>

      {/* Input Text Areas */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "12px" }}>
        <div>
          <label style={{ fontWeight: "bold", display: "block", marginBottom: "4px" }}>
            {mode === "dna" ? "Target DNA Sequence" : "Target Document / Text"}
          </label>
          <textarea
            rows={6}
            value={text}
            onChange={(e) => setText(e.target.value)}
            style={{ width: "100%", padding: "8px", fontFamily: mode === "dna" ? "monospace" : "inherit" }}
          />
        </div>

        <div>
          <label style={{ fontWeight: "bold", display: "block", marginBottom: "4px" }}>
            {mode === "plagiarism"
              ? "Comparison Document (Suspect Source)"
              : "Patterns (Comma-Separated)"}
          </label>
          <textarea
            rows={6}
            value={secondary}
            onChange={(e) => setSecondary(e.target.value)}
            style={{ width: "100%", padding: "8px", fontFamily: mode === "dna" ? "monospace" : "inherit" }}
          />
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "20px" }}>
        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            padding: "10px 20px",
            backgroundColor: "#16a34a",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          {loading ? "Analyzing..." : "Search & Compare Algorithms"}
        </button>

        {mode === "nlp" && (
          <label style={{ cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={caseSensitive}
              onChange={(e) => setCaseSensitive(e.target.checked)}
            />{" "}
            Case Sensitive
          </label>
        )}
      </div>

      {error && (
        <div style={{ padding: "10px", backgroundColor: "#fee2e2", color: "#b91c1c", borderRadius: "6px", marginBottom: "16px" }}>
          {error}
        </div>
      )}

      {/* Results Dashboard */}
      {result && (
        <div>
          {/* 1. Algorithm Comparison Table */}
          <h3>Algorithm Benchmark Comparison</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "20px", textAlign: "left" }}>
            <thead>
              <tr style={{ backgroundColor: "#f3f4f6", borderBottom: "2px solid #d1d5db" }}>
                <th style={{ padding: "8px" }}>Algorithm</th>
                <th style={{ padding: "8px" }}>Time Complexity</th>
                <th style={{ padding: "8px" }}>Total Time (ms)</th>
                <th style={{ padding: "8px" }}>Char Comparisons</th>
                <th style={{ padding: "8px" }}>Aux Memory (Nodes/Cells)</th>
                <th style={{ padding: "8px" }}>Matches Found</th>
              </tr>
            </thead>
            <tbody>
              {[result.aho_corasick, result.kmp].map((algo) => (
                <tr key={algo.algorithm} style={{ borderBottom: "1px solid #e5e7eb" }}>
                  <td style={{ padding: "8px", fontWeight: "bold" }}>{algo.algorithm}</td>
                  <td style={{ padding: "8px", fontFamily: "monospace" }}>{algo.time_complexity}</td>
                  <td style={{ padding: "8px" }}>{algo.total_time_ms} ms</td>
                  <td style={{ padding: "8px" }}>{algo.comparisons}</td>
                  <td style={{ padding: "8px" }}>{algo.memory_units}</td>
                  <td style={{ padding: "8px" }}>{algo.total_matches}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* 2. Highlighted Document View */}
          <h3>
            {mode === "plagiarism" ? "Highlighted Matching Regions" : "Highlighted Matches"} (
            {result.aho_corasick.total_matches} total)
          </h3>
          <div
            style={{
              padding: "12px",
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              backgroundColor: "#fafafa",
              whiteSpace: "pre-wrap",
              lineHeight: "1.6",
              marginBottom: "20px",
              fontFamily: mode === "dna" ? "monospace" : "inherit",
            }}
          >
            {renderHighlightedText()}
          </div>

          {/* 3. Pattern Occurrence Counts */}
          <h3>Pattern Frequency Breakdown</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "20px" }}>
            {Object.entries(result.pattern_frequencies).map(([pat, count]) => (
              <span
                key={pat}
                style={{ padding: "4px 10px", backgroundColor: "#e0f2fe", borderRadius: "12px", fontSize: "14px" }}
              >
                <strong>{pat}</strong>: {count}
              </span>
            ))}
          </div>

          {/* 4. Context & Index Table */}
          <h3>Occurrence Indices & Context</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "14px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f3f4f6", borderBottom: "2px solid #d1d5db" }}>
                <th style={{ padding: "6px" }}>Pattern</th>
                <th style={{ padding: "6px" }}>Index [Start, End)</th>
                <th style={{ padding: "6px" }}>Context Snippet</th>
              </tr>
            </thead>
            <tbody>
              {result.contexts.map((ctx, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #e5e7eb" }}>
                  <td style={{ padding: "6px", fontWeight: "bold" }}>{ctx.pattern}</td>
                  <td style={{ padding: "6px", fontFamily: "monospace" }}>
                    [{ctx.start}, {ctx.end})
                  </td>
                  <td style={{ padding: "6px" }}>
                    ...{ctx.before}
                    <mark style={{ backgroundColor: "#fde047", fontWeight: "bold" }}>{ctx.match}</mark>
                    {ctx.after}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}