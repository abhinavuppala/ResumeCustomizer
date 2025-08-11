"use client";
import React, { useState, useRef } from "react";

export default function Home() {
  const [jobInfo, setJobInfo] = useState("");
  const [progress, setProgress] = useState<string[]>([]);
  const [changelog, setChangelog] = useState<string[]>([]);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const downloadRef = useRef<HTMLAnchorElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setProgress([]);
    setChangelog([]);
    setPdfUrl(null);
    setLoading(true);

    // Prepare form data
    const formData = new FormData();
    formData.append("job_info", jobInfo);

    // POST to backend and stream progress
    const response = await fetch("http://127.0.0.1:8080/resume", {
      method: "POST",
      body: formData,
    });

    if (!response.body) {
      setProgress(["No response body"]);
      setLoading(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let key: string | null = null;
    let buffer = "";

    // read values from streaming response until done received
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // Split on double newlines (SSE event delimiter)
      let parts = buffer.split("\n\n");
      buffer = parts.pop() || "";

      // Collect all data lines for this event
      // accomodating for multiline inputs
      for (const part of parts) {
        const eventMatch = part.match(/^event: (.+)$/m);
        const dataLines = Array.from(part.matchAll(/^data: (.*)$/gm)).map(m => m[1]);
        
        // regex match
        if (eventMatch && dataLines.length) {
          const event = eventMatch[1].trim();
          const data = dataLines.join('\n');

          // progress -> add to changelog or progress lists
          if (event === "progress") {
            if (data.startsWith(">>")) {
              setChangelog((prev) => [...prev, data]);
            }
            else {
              setProgress((prev) => [...prev, data]);
            }

          // if done, we add final event based on if we got a key back
          } else if (event === "done") {
            try {
              const obj = JSON.parse(data);
              key = obj.key;
              setProgress((prev) => [...prev, "Resume ready! Downloading PDF..."]);
            } catch {
              setProgress((prev) => [...prev, "Error parsing key"]);
            }
          }
        }
      }
    }

    // GET the PDF if key was found
    if (key) {
      const pdfResp = await fetch(`http://127.0.0.1:8080/resume/${key}`);
      
      // set download url for PDF
      if (pdfResp.ok) {
        const blob = await pdfResp.blob();
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
        setProgress((prev) => [...prev, "PDF ready for download!"]);
        
        // autoclick download button
        setTimeout(() => downloadRef.current?.click(), 500);
      } else {
        setProgress((prev) => [...prev, "Failed to download PDF"]);
      }
    } else {
      setProgress((prev) => [...prev, "No key received from backend"]);
    }
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Resume Customizer</h1>
      {pdfUrl && (
        <div style={{ marginBottom: "1rem" }}>
          <a
            href={pdfUrl}
            download="AbhinavUppala_Resume.pdf"
            ref={downloadRef}
            style={{
              display: "inline-block",
              padding: "0.5rem 1rem",
              background: "#0070f3",
              color: "#fff",
              borderRadius: 4,
              textDecoration: "none",
              fontWeight: "bold",
            }}
          >
            Download PDF
          </a>
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <textarea
          rows={8}
          style={{
            width: "100%",
            marginBottom: 8,
            border: "2px solid #ccc",
            padding: 8,
          }}
          placeholder="Paste job description here..."
          value={jobInfo}
          onChange={(e) => setJobInfo(e.target.value)}
          required
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.5rem 1rem",
            background: "#0070f3",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Generating..." : "Generate Resume"}
        </button>
      </form>
      <div style={{ marginTop: 16 }}>
        {progress.map((msg, i) => (
          <div key={i} style={{ whiteSpace: "pre-wrap" }}>{msg}</div>
        ))}
      </div>
      {changelog.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h2>Changelog</h2>
          {changelog.map((msg, i) => (
            <pre
              key={i}
              style={{
                background: "#f5f5f5",
                padding: 8,
                borderRadius: 4,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {msg}
            </pre>
          ))}
        </div>
      )}
    </div>
  );
}
