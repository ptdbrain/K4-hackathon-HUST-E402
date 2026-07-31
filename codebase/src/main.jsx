import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "/api";
const assignmentRepo = "https://github.com/VinUni-AI20k/day03-cohorts34-chatbot-agentic-agent";
const steps = ["Nguồn yêu cầu", "Xác nhận", "Bài làm", "Kết quả"];
const sampleCodelab = "Bài Lab cần 5 test cases, Baseline không gọi Tool, ReAct chọn Tool động và có MAX_ITERATIONS. Không commit API key. Ghi failed trace và RCA.";

async function request(path, options) {
  const response = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : data.detail?.map(item => item.msg).join(", ") || "Không thể xử lý yêu cầu.");
  return data;
}

function Stepper({ step }) {
  return (
    <nav className="stepper" aria-label="Tiến trình">
      {steps.map((label, index) => (
        <div className={index <= step ? "step active" : "step"} key={label}>
          <span>{index < step ? "✓" : index + 1}</span>{label}
        </div>
      ))}
    </nav>
  );
}

function Sources({ onDone }) {
  const [files, setFiles] = useState([]);
  const [text, setText] = useState("");
  const [repo, setRepo] = useState(assignmentRepo);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function loadFiles(event) {
    const selected = [...event.target.files];
    setFiles(selected);
    setText((await Promise.all(selected.map(file => file.text()))).join("\n\n"));
  }

  async function extract() {
    setBusy(true);
    setError("");
    try {
      const data = await request("/assignments/extract", {
        method: "POST",
        body: JSON.stringify({
          assignment_repo_url: repo,
          codelab_text: text,
          codelab_files: files.map(({ name, type, size }) => ({ name, type, size })),
        }),
      });
      onDone(data);
    } catch (reason) {
      setError(reason.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel two-col">
      <div>
        <p className="eyebrow">01 · Codelab</p>
        <h2>Thêm hướng dẫn thực hành</h2>
        <label className="dropzone">
          <input type="file" accept=".md,.txt,text/plain,text/markdown" multiple onChange={loadFiles} />
          <span className="upload-icon">↥</span>
          <strong>Kéo thả Markdown hoặc text</strong>
          <small>MD hoặc TXT · nội dung được gửi để trích xuất yêu cầu</small>
        </label>
        {files.length > 0 ? <p className="success">✓ Đã chọn {files.length} tệp Codelab</p> : null}
        <div className="or"><span>hoặc dán nội dung</span></div>
        <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Dán nội dung Codelab tại đây…" />
      </div>
      <div className="source-right">
        <p className="eyebrow">02 · GitHub đề bài</p>
        <h2>Đọc rubric và artifact</h2>
        <label>URL repo public</label>
        <input value={repo} onChange={e => setRepo(e.target.value)} />
        <div className="read-list">
          <p><span>README.md</span><b>Rubric & trọng số</b></p>
          <p><span>Repository tree</span><b>Artifact bắt buộc</b></p>
          <p><span>docs/*.md</span><b>Tiêu chí báo cáo</b></p>
        </div>
        <button className="primary" onClick={extract} disabled={busy || (!files.length && !text.trim())}>
          {busy ? "Đang tổng hợp…" : "Đọc và tổng hợp yêu cầu →"}
        </button>
        {!files.length && !text.trim() ? <button className="link" onClick={() => setText(sampleCodelab)}>Dùng Codelab mẫu đã tải sẵn</button> : null}
        {error ? <p className="error">{error}</p> : null}
      </div>
    </section>
  );
}

function Requirements({ pack, onDone }) {
  const [items, setItems] = useState(pack.requirements);
  const [filter, setFilter] = useState("all");
  const categories = ["all", "artifact", "implementation", "report", "security", "conflict"];
  const visible = items.filter(item => filter === "all" || (filter === "conflict" ? item.source_conflict : item.category === filter));

  async function confirm() {
    const enabled = items.filter(item => item.enabled !== false);
    await request(`/assignments/${pack.assignment_id}/confirm`, {
      method: "POST",
      body: JSON.stringify({ requirements: enabled }),
    });
    onDone({ ...pack, requirements: enabled });
  }

  const counts = items.reduce((out, item) => ({ ...out, [item.severity]: (out[item.severity] || 0) + 1 }), {});
  return (
    <section className="panel stack">
      <div className="review-head">
        <div><p className="eyebrow">Requirement Pack</p><h2>{items.filter(x => x.enabled !== false).length} yêu cầu được phát hiện</h2></div>
        <div className="severity-summary"><b>{counts.critical || 0} Critical</b><span>{counts.high || 0} High</span><span>{counts.medium || 0} Medium</span></div>
      </div>
      {pack.conflicts.length ? <div className="conflict-banner"><b>⚠ Xung đột nguồn</b><span>{pack.conflicts.length} yêu cầu khác nhau giữa các nguồn. Mặc định giữ để kiểm tra an toàn.</span></div> : null}
      <div className="conflict-banner">
        <b>{pack.source_summary.ai_trace.mode === "ai" ? "✓ AI thật" : "○ Offline mock"}</b>
        <span>{pack.source_summary.ai_trace.mode === "ai" ? `${pack.source_summary.ai_trace.provider} · ${pack.source_summary.ai_trace.model} đã tạo requirement từ Codelab và GitHub.` : `${pack.source_summary.ai_trace.reason}; đang dùng pack dự phòng.`}</span>
      </div>
      <div className="filters">
        {categories.map(category => <button className={filter === category ? "selected" : ""} onClick={() => setFilter(category)} key={category}>{category === "all" ? "Tất cả" : category}</button>)}
      </div>
      <div className="requirement-list">
        {visible.map(item => (
          <label className={item.enabled === false ? "requirement disabled" : "requirement"} key={item.id}>
            <input type="checkbox" checked={item.enabled !== false} onChange={() => setItems(items.map(x => x.id === item.id ? { ...x, enabled: x.enabled === false } : x))} />
            <span className={`status-dot ${item.severity}`}></span>
            <span className="requirement-copy"><strong>{item.title}</strong><small>Artifact: {item.artifacts.join(", ")} · {item.check_type === "semantic" ? "AI semantic review" : "Kiểm tra tự động"}</small></span>
            <span className="source">{item.sources.map(x => x.location).join(" · ")}</span>
          </label>
        ))}
      </div>
      <button className="primary align-right" onClick={confirm}>Xác nhận bộ yêu cầu →</button>
    </section>
  );
}

function Submission({ pack, onDone }) {
  const [repo, setRepo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function analyze(isDemo = false) {
    setBusy(true);
    setError("");
    try {
      const data = await request("/analysis", {
        method: "POST",
        body: JSON.stringify({ assignment_id: pack.assignment_id, submission_repo_url: isDemo ? "demo://not-ready" : repo }),
      });
      onDone(data);
    } catch (reason) {
      setError(reason.message);
      setBusy(false);
    }
  }

  return (
    <section className="panel submit-panel">
      <div className="shield">⌁</div>
      <p className="eyebrow">Repo bài làm</p>
      <h2>Sẵn sàng kiểm tra trước khi nộp?</h2>
      <p className="muted">LabGuard chỉ đọc repo public và không chạy code của bạn.</p>
      <label>URL GitHub repo bài làm</label>
      <div className="repo-row">
        <input value={repo} onChange={e => setRepo(e.target.value)} placeholder="https://github.com/team/repo" />
        <button className="primary" onClick={() => analyze()} disabled={!repo || busy}>{busy ? "Đang quét…" : "Kiểm tra bài →"}</button>
      </div>
      <button className="demo-button" onClick={() => analyze(true)} disabled={busy}>▶ Dùng repo demo chưa hoàn thiện</button>
      {busy ? <div className="scan"><span>✓ Đã đọc cây thư mục</span><span>✓ Đã kiểm tra artifact</span><span className="running">● Đang đánh giá ReAct loop…</span></div> : null}
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}

function Results({ result, onRerun, rerunning, rerunError }) {
  const [feedback, setFeedback] = useState(false);
  const risk = result.highest_risk;
  useEffect(() => setFeedback(false), [result.checked_at]);
  async function markWrong() {
    await request(`/analysis/${result.analysis_id}/feedback`, {
      method: "POST",
      body: JSON.stringify({ requirement_id: risk.requirement_id, reason: "AI đọc sai code" }),
    });
    setFeedback(true);
  }
  return (
    <section className="results-grid">
      <div className="result-main">
        <div className="readiness">
          <span className={result.readiness}>{result.readiness === "ready" ? "READY" : "NOT READY"}</span>
          <div>
            <b>{result.summary.pass} đạt</b> · {result.summary.fail} chưa đạt · {result.summary.needs_review} cần xem xét
            <small className="run-time">Kiểm tra lúc {new Date(result.checked_at).toLocaleTimeString("vi-VN")}</small>
          </div>
        </div>
        {risk ? <article className="risk-card">
          <p className="critical-label">CRITICAL · RỦI RO CAO NHẤT</p>
          <h2>{risk.summary}</h2>
          <div className="evidence">
            <p><b>Yêu cầu</b><span>{risk.requirement_title}</span></p>
            <p><b>Bằng chứng</b><span>{risk.repo_evidence[0]?.file || "Toàn repo"} — {risk.repo_evidence[0]?.detail}</span></p>
            <p><b>Ảnh hưởng</b><span>{risk.impact}</span></p>
          </div>
          <div className="action"><b>Hành động tiếp theo</b><ol>{risk.recommended_action.map(item => <li key={item}>{item}</li>)}</ol></div>
          <div className="card-actions">
            {risk.repo_evidence[0]?.url ? <a href={risk.repo_evidence[0].url} target="_blank">Mở file trên GitHub ↗</a> : null}
            <button onClick={markWrong} disabled={feedback}>{feedback ? "Đã chuyển sang Human review" : "AI đánh giá sai"}</button>
          </div>
        </article> : null}
      </div>
      <aside className="checklist">
        <p className="eyebrow">Checklist</p>
        <h3>Tất cả yêu cầu</h3>
        {result.findings.map(finding => <div className="check-item" key={finding.requirement_id}><span className={finding.status}>{finding.status === "pass" ? "✓" : finding.status === "fail" ? "×" : "!"}</span><div><b>{finding.requirement_title}</b><small>{finding.summary}</small></div></div>)}
        <button className="primary full" onClick={onRerun} disabled={rerunning}>{rerunning ? "Đang kiểm tra…" : "↻ Kiểm tra lại"}</button>
        {rerunError ? <p className="error">{rerunError}</p> : null}
      </aside>
    </section>
  );
}

function App() {
  const [step, setStep] = useState(0);
  const [pack, setPack] = useState();
  const [result, setResult] = useState();
  const [rerunning, setRerunning] = useState(false);
  const [rerunError, setRerunError] = useState("");
  async function rerun() {
    setRerunning(true);
    setRerunError("");
    try {
      setResult(await request(`/analysis/${result.analysis_id}/rerun`, { method: "POST" }));
    } catch (reason) {
      setRerunError(reason.message);
    } finally {
      setRerunning(false);
    }
  }
  return (
    <>
      <header><div className="brand"><span>LG</span><div><b>LabGuard</b><small>AI pre-submission checker</small></div></div><div className="lab-chip">Multi-lab · Dynamic rubric</div></header>
      <main>
        <div className="hero"><div><p className="eyebrow">Kiểm tra trước. Nộp bài tự tin.</p><h1>Bài Lab của bạn<br /><em>đã thật sự sẵn sàng?</em></h1></div><p>Đối chiếu Codelab, rubric và repo trong một luồng kiểm tra. Tìm đúng rủi ro quan trọng nhất trước khi dùng lượt nộp.</p></div>
        <Stepper step={step} />
        {step === 0 ? <Sources onDone={data => { setPack(data); setStep(1); }} /> : null}
        {step === 1 ? <Requirements pack={pack} onDone={data => { setPack(data); setStep(2); }} /> : null}
        {step === 2 ? <Submission pack={pack} onDone={data => { setResult(data); setStep(3); }} /> : null}
        {step === 3 ? <Results result={result} onRerun={rerun} rerunning={rerunning} rerunError={rerunError} /> : null}
      </main>
      <footer><b>LabGuard</b><span>Không tự sửa · Không chạy code · Không tự nộp bài</span></footer>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
