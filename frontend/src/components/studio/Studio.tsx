import React, { useEffect, useState } from "react";
import {
  Script,
  VideoJob,
  createVideo,
  generateScript,
  getVideo,
  saveProject,
} from "../../services/api";

const STEPS = ["写脚本", "确认镜头", "渲染导出"];

export default function Studio() {
  const [step, setStep] = useState(0);
  const [topic, setTopic] = useState("");
  const [style, setStyle] = useState("educational");
  const [duration, setDuration] = useState("30s");
  const [script, setScript] = useState<Script | null>(null);
  const [job, setJob] = useState<VideoJob | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [bg, setBg] = useState("#0F1C2E");

  useEffect(() => {
    if (!job || job.status === "completed" || job.status === "failed") return;
    const timer = setInterval(async () => {
      try {
        const latest = await getVideo(job.id);
        setJob(latest);
      } catch {
        /* ignore transient poll errors */
      }
    }, 1500);
    return () => clearInterval(timer);
  }, [job]);

  const onGenerate = async () => {
    setError("");
    setBusy(true);
    try {
      const result = await generateScript({ topic: topic.trim(), style, duration });
      setScript(result);
      setStep(1);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "脚本生成失败");
    } finally {
      setBusy(false);
    }
  };

  const onSaveProject = async () => {
    if (!script) return;
    setBusy(true);
    setError("");
    try {
      await saveProject({
        title: script.title,
        script,
        config: { style, duration, background_color: bg },
      });
    } catch (err: any) {
      setError(err?.response?.data?.detail || "保存失败");
    } finally {
      setBusy(false);
    }
  };

  const onRender = async () => {
    if (!script) return;
    setError("");
    setBusy(true);
    setStep(2);
    try {
      const created = await createVideo({
        script,
        background_color: bg,
        export_config: { resolution: "720p", fps: 24, format: "mp4" },
      });
      setJob(created);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "创建渲染任务失败");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="step-rail">
        {STEPS.map((label, index) => (
          <button
            key={label}
            type="button"
            className={`step-chip ${step === index ? "active" : ""}`}
            onClick={() => {
              if (index === 0 || script) setStep(index);
            }}
          >
            {index + 1}. {label}
          </button>
        ))}
      </div>

      <section className="panel">
        {step === 0 && (
          <>
            <h2 className="hero-title">先写一句主题</h2>
            <p className="hero-copy">
              短镜会生成可直接渲染的分镜脚本。没有 OpenAI Key 时使用本地模板，装上 Key 后自动走模型。
            </p>
            <div className="field-grid">
              <div className="field">
                <label htmlFor="topic">主题</label>
                <input
                  id="topic"
                  placeholder="例如：三分钟讲清冷萃咖啡"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="style">风格</label>
                <select id="style" value={style} onChange={(e) => setStyle(e.target.value)}>
                  <option value="educational">知识讲解</option>
                  <option value="entertainment">轻松娱乐</option>
                  <option value="commercial">种草带货</option>
                  <option value="news">资讯快报</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="duration">时长</label>
                <select
                  id="duration"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                >
                  <option value="15s">15 秒</option>
                  <option value="30s">30 秒</option>
                  <option value="60s">60 秒</option>
                </select>
              </div>
            </div>
            <div className="actions">
              <button
                className="btn btn-primary"
                type="button"
                disabled={busy || !topic.trim()}
                onClick={onGenerate}
              >
                {busy ? "生成中…" : "生成脚本"}
              </button>
            </div>
          </>
        )}

        {step === 1 && script && (
          <>
            <h2 className="hero-title">{script.title}</h2>
            <p className="hero-copy">
              共 {script.scenes.length} 个镜头 · {script.total_duration}s · 来源{" "}
              {script.source === "openai" ? "模型" : "模板"}
            </p>
            <div className="field">
              <label htmlFor="bg">画面底色</label>
              <input id="bg" type="color" value={bg} onChange={(e) => setBg(e.target.value)} />
            </div>
            <div className="scene-list">
              {script.scenes.map((scene, index) => (
                <article className="scene-item" key={`${scene.text}-${index}`}>
                  <strong>
                    镜头 {index + 1} · {scene.duration}s
                  </strong>
                  <div>{scene.text}</div>
                </article>
              ))}
            </div>
            <div className="actions">
              <button className="btn btn-ghost" type="button" onClick={() => setStep(0)}>
                返回修改
              </button>
              <button className="btn btn-ghost" type="button" disabled={busy} onClick={onSaveProject}>
                保存项目
              </button>
              <button className="btn btn-primary" type="button" disabled={busy} onClick={onRender}>
                开始渲染
              </button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="hero-title">渲染中</h2>
            <p className="hero-copy">
              {job
                ? `${job.message || job.status} · ${job.progress}%`
                : "正在创建任务…"}
            </p>
            <div className="progress-track">
              <div
                className="progress-bar"
                style={{
                  width: `${job?.progress || 8}%`,
                  animation: job?.status === "completed" ? "none" : undefined,
                }}
              />
            </div>
            {job?.status === "completed" && job.download_url && (
              <div className="actions">
                <a className="btn btn-primary" href={job.download_url} download>
                  下载视频
                </a>
                <button className="btn btn-ghost" type="button" onClick={() => setStep(0)}>
                  再做一支
                </button>
              </div>
            )}
            {job?.status === "failed" && (
              <div className="error-text">{job.error || "渲染失败"}</div>
            )}
          </>
        )}

        {error && <div className="error-text">{error}</div>}
      </section>
    </div>
  );
}
