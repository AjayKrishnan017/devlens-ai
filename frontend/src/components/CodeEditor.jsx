function CodeEditor({
    code,
    setCode,
    analyze,
    loading,
}) {
    return (
        <section className="panel editor-panel">
            <div className="panel-header">
                <div>
                    <span className="eyebrow">
                        INPUT
                    </span>

                    <h2>Python Code</h2>
                </div>

                <span className="language-badge">
                    Python
                </span>
            </div>

            <textarea
                className="code-editor"
                value={code}
                onChange={(event) =>
                    setCode(event.target.value)
                }
                spellCheck="false"
                placeholder="Paste Python code here..."
            />

            <button
                className="analyze-button"
                onClick={analyze}
                disabled={loading}
            >
                {loading
                    ? "Analyzing..."
                    : "Analyze Code"}
            </button>
        </section>
    );
}

export default CodeEditor;
