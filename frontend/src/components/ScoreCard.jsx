function ScoreCard({
    title,
    value,
    suffix = "",
    description,
}) {
    return (
        <div className="score-card">
            <span className="card-label">
                {title}
            </span>

            <div className="score-value">
                {value}
                {suffix && (
                    <span className="suffix">
                        {suffix}
                    </span>
                )}
            </div>

            {description && (
                <span className="card-description">
                    {description}
                </span>
            )}
        </div>
    );
}

export default ScoreCard;