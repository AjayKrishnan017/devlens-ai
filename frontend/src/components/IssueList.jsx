function IssueList({ issues = [] }) {
    return (
        <section className="panel">
            <div className="panel-header">
                <div>
                    <span className="eyebrow">
                        STATIC ANALYSIS
                    </span>

                    <h2>Detected Issues</h2>
                </div>

                <span className="count-badge">
                    {issues.length}
                </span>
            </div>

            {issues.length === 0 ? (
                <div className="empty-state">
                    No static-analysis issues detected.
                </div>
            ) : (
                <div className="issue-list">
                    {issues.map((issue, index) => (
                        <div
                            className="issue"
                            key={`${issue.type}-${index}`}
                        >
                            <div className="issue-top">
                                <span
                                    className={`severity ${issue.severity?.toLowerCase()}`}
                                >
                                    {issue.severity}
                                </span>

                                <strong>
                                    {issue.type}
                                </strong>
                            </div>

                            <p>
                                {issue.message ||
                                    "Code issue detected."}
                            </p>

                            {issue.line && (
                                <span className="line-number">
                                    Line {issue.line}
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}

export default IssueList;