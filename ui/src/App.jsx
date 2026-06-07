import { useState } from "react";

const API = "http://localhost:5050/sort";

function Bar({ label, timeMs, maxTime, color, complexity }) {
  const pct = maxTime > 0 ? (timeMs / maxTime) * 100 : 0;
  return (
    <div style={{ marginBottom: 18 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 4,
          fontSize: 13,
        }}
      >
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span style={{ color: "#888", fontFamily: "monospace" }}>
          {complexity}
        </span>
      </div>
      <div
        style={{
          background: "#eee",
          borderRadius: 2,
          height: 10,
          width: "100%",
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            background: color,
            height: "100%",
            borderRadius: 2,
            transition: "width 0.4s ease",
          }}
        />
      </div>
      <div
        style={{
          fontSize: 12,
          color: "#555",
          marginTop: 4,
          fontFamily: "monospace",
        }}
      >
        {timeMs.toFixed(4)} ms
      </div>
    </div>
  );
}

export default function App() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRun() {
    setError("");
    setResult(null);

    const nums = input
      .split(/[\s,]+/)
      .map((s) => s.trim())
      .filter(Boolean)
      .map(Number);

    if (nums.some(isNaN)) {
      setError("Enter only numbers separated by spaces or commas.");
      return;
    }
    if (nums.length < 2) {
      setError("Enter at least 2 numbers.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ numbers: nums }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(
        "Could not reach backend. Is the Flask server running on port 5050?",
      );
    }
    setLoading(false);
  }

  const maxTime = result
    ? Math.max(result.bubble.time_ms, result.merge.time_ms)
    : 1;

  return (
    <div
      style={{
        fontFamily: "Georgia, serif",
        maxWidth: 520,
        margin: "60px auto",
        padding: "0 20px",
        color: "#222",
      }}
    >
      <h2 style={{ fontWeight: 700, fontSize: 22, marginBottom: 4 }}>
        Sort Complexity
      </h2>
      <p
        style={{ color: "#777", fontSize: 13, marginBottom: 28, marginTop: 0 }}
      >
        Bubble sort vs Merge sort — real timing via Python
      </p>

      <label
        style={{
          fontSize: 13,
          fontWeight: 600,
          display: "block",
          marginBottom: 6,
        }}
      >
        Numbers
      </label>
      <textarea
        rows={3}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g. 5 3 8 1 9 2 7 4 6"
        style={{
          width: "100%",
          boxSizing: "border-box",
          fontFamily: "monospace",
          fontSize: 14,
          padding: "8px 10px",
          border: "1px solid #ccc",
          borderRadius: 3,
          resize: "none",
          outline: "none",
        }}
      />

      <button
        onClick={handleRun}
        disabled={loading}
        style={{
          marginTop: 10,
          padding: "8px 20px",
          background: "#222",
          color: "#fff",
          border: "none",
          borderRadius: 3,
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: 13,
          opacity: loading ? 0.6 : 1,
        }}
      >
        {loading ? "Running..." : "Run"}
      </button>

      {error && (
        <p style={{ color: "#c00", fontSize: 13, marginTop: 12 }}>{error}</p>
      )}

      {result && (
        <div style={{ marginTop: 32 }}>
          <div style={{ fontSize: 12, color: "#888", marginBottom: 18 }}>
            n = {result.input_size}
          </div>

          <Bar
            label="Bubble Sort"
            timeMs={result.bubble.time_ms}
            maxTime={maxTime}
            color="#e07b39"
            complexity={result.bubble.complexity}
          />
          <Bar
            label="Merge Sort"
            timeMs={result.merge.time_ms}
            maxTime={maxTime}
            color="#3a7bd5"
            complexity={result.merge.complexity}
          />

          <div
            style={{
              borderTop: "1px solid #eee",
              marginTop: 20,
              paddingTop: 16,
              fontSize: 13,
            }}
          >
            <div style={{ marginBottom: 6, color: "#555" }}>
              <strong>Sorted output:</strong>
            </div>
            <div
              style={{
                fontFamily: "monospace",
                background: "#f5f5f5",
                padding: "8px 12px",
                borderRadius: 3,
                fontSize: 13,
                wordBreak: "break-all",
              }}
            >
              [{result.sorted.join(", ")}]
            </div>
          </div>

          <div style={{ marginTop: 16, fontSize: 12, color: "#999" }}>
            Bubble{" "}
            {result.bubble.time_ms < result.merge.time_ms ? "faster" : "slower"}{" "}
            than Merge by{" "}
            {Math.abs(result.bubble.time_ms - result.merge.time_ms).toFixed(4)}{" "}
            ms on this input.
          </div>
        </div>
      )}
    </div>
  );
}
