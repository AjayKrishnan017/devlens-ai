function ComplexityPanel({
    complexity,
}) {
    const functions =
        complexity?.functions || [];

    return (
        <section className="panel">
            <div className="panel-header">
                <div>
                    <span className="eyebrow">
                        CODE QUALITY
                    </span>

                    <h2>Complexity</h2>
                </div>
            </div>

            {functions.length === 0 ? (
                <div className="empty-state">
                    No function complexity data.
                </div>
            ) : (
                <div className="complexity-list">
                    {functions.map(
                        (func, index) => (
                            <div
                                className="function-card"
                                key={`${func.name}-${index}`}
                            >
                                <div className="function-name">
                                    {func.name}()
                                </div>

                                <div className="metric-grid">
                                    <Metric
                                        label="Complexity"
                                        value={
                                            func.complexity
                                        }
                                    />

                                    <Metric
                                        label="Nesting"
                                        value={
                                            func.nesting_depth
                                        }
                                    />

                                    <Metric
                                        label="Parameters"
                                        value={
                                            func.parameters
                                        }
                                    />

                                    <Metric
                                        label="Lines"
                                        value={
                                            func.length
                                        }
                                    />
                                </div>

                                {func.risk && (
                                    <span
                                        className={`risk-badge ${func.risk.toLowerCase()}`}
                                    >
                                        {func.risk}
                                    </span>
                                )}
                            </div>
                        )
                    )}
                </div>
            )}
        </section>
    );
}

function Metric({ label, value }) {
    return (
        <div className="metric">
            <span>{label}</span>
            <strong>{value ?? 0}</strong>
        </div>
    );
}

export default ComplexityPanel;