import { useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [trace, setTrace] = useState(null);
  const [loading, setLoading] = useState(false);

  // -------------------------
  // Ingest document
  // -------------------------
  const handleIngest = async () => {
    if (!file) return alert("Please select a file first");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      await fetch(`${API_BASE}/ingest`, {
        method: "POST",
        body: formData,
      });
      alert("Document ingested successfully");
    } catch {
      alert("Ingest failed");
    } finally {
      setLoading(false);
    }
  };

  // -------------------------
  // Ask question
  // -------------------------
  const handleAsk = async () => {
    if (!question.trim() || loading) return;

    try {
      setLoading(true);
      setAnswer("");
      setEvaluation(null);
      setTrace(null);

      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      setAnswer(data.answer);
      setEvaluation(data.evaluation);
      setTrace(data.trace);
    } catch {
      setAnswer("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div className="app-container">
        <h1 className="app-title">
          🤖 Agentic <span>Knowledge Assistant</span>
        </h1>

        {/* Upload Section */}
        <div className="section">
          <div className="section-title">
            Upload Knowledge (PDF / CSV / TXT)
          </div>
          <div className="upload-row">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button onClick={handleIngest} disabled={loading}>
              {loading ? "Processing..." : "Ingest"}
            </button>
          </div>
        </div>

        {/* Ask Section */}
        <div className="section">
          <div className="section-title">Ask</div>
          <textarea
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                handleAsk();
              }
            }}
          />
          <br />
          <button onClick={handleAsk} disabled={loading}>
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {/* Answer */}
        {answer && (
          <div className="section">
            <div className="section-title">Answer</div>
            <div className="answer-card">{answer}</div>
          </div>
        )}

        {/* Evaluation */}
        {evaluation && (
          <div className="section">
            <div className="section-title">Evaluation</div>
            <pre className="code-block">
              {JSON.stringify(evaluation, null, 2)}
            </pre>
          </div>
        )}

        {/* Reasoning Trace */}
        {trace && (
          <div className="section">
            <div className="section-title">Reasoning Trace</div>
            <pre className="code-block">
              {JSON.stringify(trace, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
