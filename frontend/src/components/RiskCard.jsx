function RiskCard({ prediction }) {
    if (!prediction) {
        return (
            <div className="risk-panel">
                <span className="card-label">
                    ML DEFECT RISK
                </span>

                <h3>Waiting for analysis</h3>
            </div>
        );
    }

    if (!prediction.success) {
        return (
            <div className="risk-panel">
                <span className="card-label">
                    ML DEFECT RISK
                </span>

                <h3>Unavailable</h3>

                <p>
                    {prediction.message ||
                        "ML prediction unavailable."}
                </p>
            </div>
        );
    }

    const probability =
        prediction.probability_percent ?? 0;

    return (
        <div className="risk-panel">
            <div className="risk-header">
                <span className="card-label">
                    ML DEFECT RISK
                </span>

                <span
                    className={`risk-badge ${prediction.risk?.toLowerCase()}`}
                >
                    {prediction.risk}
                </span>
            </div>

            <div className="risk-percentage">
                {probability}%
            </div>

            <div className="progress-track">
                <div
                    className="progress-bar"
                    style={{
                        width: `${Math.min(
                            probability,
                            100
                        )}%`,
                    }}
                ></div>
            </div>

            <div className="model-info">
                <span>
                    Model:{" "}
                    {prediction.model ||
                        "DevLens ML"}
                </span>

                <span>
                    Version:{" "}
                    {prediction.model_version ||
                        "v1"}
                </span>
            </div>

            <p className="disclaimer">
                {prediction.disclaimer}
            </p>
        </div>
    );
}

export default RiskCard;