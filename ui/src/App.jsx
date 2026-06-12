import { useState } from "react";
import "./App.css";
import { dynamic } from "./styles.js";

const API = "http://localhost:5050";

const ALGORITHMS = {
  bubble: { label: "Bubble", full: "Bubble Sort", color: "#c0392b" },
  merge: { label: "Merge", full: "Merge Sort", color: "#2471a3" },
};

const ALGO_KEYS = ["bubble", "merge"];

function buildRandomNumbers(count, minValue, maxValue) {
  const lower = Math.min(minValue, maxValue);
  const upper = Math.max(minValue, maxValue);
  const range = upper - lower + 1;
  return Array.from({ length: count }, () => Math.floor(Math.random() * range) + lower);
}

export default function App() {
  const [input, setInput] = useState("");
  const [count, setCount] = useState(20);
  const [minValue, setMinValue] = useState(0);
  const [maxValue, setMaxValue] = useState(99);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function post(url, body) {
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const response = await fetch(API + url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setResult(await response.json());
    } catch {
      setError("Flask server not reachable on port 5050.");
    }
    setLoading(false);
  }

  function runComparison() {
    const nums = input
      .split(/[\s,]+/)
      .filter(Boolean)
      .map(Number);

    if (nums.some(Number.isNaN)) {
      setError("Numbers only please.");
      return;
    }

    if (nums.length < 2) {
      setError("Need at least 2 numbers.");
      return;
    }

    post("/sort", { numbers: nums, algorithms: ALGO_KEYS });
  }

  function generateRandomInput() {
    const size = Number(count);
    const min = Number(minValue);
    const max = Number(maxValue);

    if (!Number.isFinite(size) || size < 2) {
      setError("Enter a random array size of at least 2.");
      return;
    }

    if (!Number.isFinite(min) || !Number.isFinite(max)) {
      setError("Random range must be numeric.");
      return;
    }

    setInput(buildRandomNumbers(size, min, max).join(" "));
    setError("");
    setResult(null);
  }

  const maxTime = result ? Math.max(...Object.values(result.results).map(r => r.time_ms)) : 1;

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">sorting visualizer</p>
          <h1>bubble vs merge sort</h1>
          <p className="sub">
            Generate a random number list or paste your own, then compare Bubble Sort against Merge Sort on the same input.
          </p>
        </div>
      </section>

      <section className="content-grid">
        <div className="control-column">
          <section className="panel-card">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">1. algorithms</p>
                <h2>Two fixed sort choices</h2>
              </div>
            </div>

            <div className="algo-grid" role="list" aria-label="algorithm selection">
              {ALGO_KEYS.map(key => {
                const meta = ALGORITHMS[key];
                return (
                  <div
                    key={key}
                    className="algo-card on"
                    style={{ borderColor: meta.color, boxShadow: `0 18px 35px ${meta.color}22` }}
                  >
                    <span className="algo-name">{meta.full}</span>
                    <span className="algo-short">{meta.label}</span>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="panel-card">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">2. input</p>
                <h2>Generate a random list or paste your own</h2>
              </div>
            </div>

            <div className="input-stack">
              <div className="random-grid">
                <label className="mini-field">
                  <span className="field-label">count</span>
                  <input
                    type="number"
                    className="num-input"
                    min={2}
                    max={2000}
                    value={count}
                    onChange={e => setCount(e.target.value)}
                  />
                </label>
                <label className="mini-field">
                  <span className="field-label">min</span>
                  <input
                    type="number"
                    className="num-input"
                    value={minValue}
                    onChange={e => setMinValue(e.target.value)}
                  />
                </label>
                <label className="mini-field">
                  <span className="field-label">max</span>
                  <input
                    type="number"
                    className="num-input"
                    value={maxValue}
                    onChange={e => setMaxValue(e.target.value)}
                  />
                </label>
              </div>

              <div className="action-row">
                <button className="run-btn secondary" onClick={generateRandomInput} disabled={loading} type="button">
                  generate random numbers
                </button>
                <span className="helper-note">This fills the input box with a fresh random list.</span>
              </div>

              <span className="field-label">numbers separated by spaces or commas</span>
              <textarea
                rows={5}
                className="text-input"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="5 3 8 1 9 2 7 4 6"
              />

              <div className="action-row">
                <button className="run-btn" onClick={runComparison} disabled={loading} type="button">
                  {loading ? "running..." : "run comparison"}
                </button>
                <span className="helper-note">The backend compares only Bubble Sort and Merge Sort now.</span>
              </div>
            </div>

            {error && <div className="error-msg">{error}</div>}
          </section>
        </div>

        <aside className="preview-column">
          <section className="panel-card result-card">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">3. results</p>
                <h2>Performance report</h2>
              </div>
            </div>

            {result ? (
              <>
                <div className="result-meta">n = {result.input_size}</div>

                <div className="result-bars">
                  {ALGO_KEYS.map(key => {
                    const r = result.results[key];
                    const pct = Math.max(4, (r.time_ms / maxTime) * 100);
                    const isWinner = result.winner === key;
                    return (
                      <div key={key} className="result-item">
                        <div className="bar-label">
                          <span>
                            {ALGORITHMS[key].full}
                            {isWinner && <span className="bar-winner">fastest</span>}
                          </span>
                          <span className="complexity">{r.complexity}</span>
                        </div>
                        <div className="bar-track">
                          <div style={dynamic.barFill(pct, ALGORITHMS[key].color)} />
                        </div>
                        <div className="bar-time">{r.time_ms.toFixed(4)} ms</div>
                      </div>
                    );
                  })}
                </div>

                <div className="insight-box">{result.insight}</div>

                {result.sorted && <div className="code-block">sorted: [{result.sorted.join(", ")}]</div>}
              </>
            ) : (
              <div className="empty-state">
                <p>No run yet.</p>
                <span>Generate a random list or paste numbers, then run the comparison.</span>
              </div>
            )}
          </section>
        </aside>
      </section>
    </main>
  );
}