function StructurePanel({ structure }) {
    const metrics =
        structure?.metrics || {};

    return (
        <section className="panel">
            <div className="panel-header">
                <div>
                    <span className="eyebrow">
                        AST ANALYSIS
                    </span>

                    <h2>Code Structure</h2>
                </div>
            </div>

            <div className="structure-grid">
                <StructureItem
                    label="Functions"
                    value={
                        metrics.function_count ?? 0
                    }
                />

                <StructureItem
                    label="Classes"
                    value={
                        metrics.class_count ?? 0
                    }
                />

                <StructureItem
                    label="Loops"
                    value={
                        metrics.loop_count ?? 0
                    }
                />

                <StructureItem
                    label="Conditionals"
                    value={
                        metrics.conditional_count ?? 0
                    }
                />

                <StructureItem
                    label="Try Blocks"
                    value={
                        metrics.try_block_count ?? 0
                    }
                />
            </div>
        </section>
    );
}

function StructureItem({
    label,
    value,
}) {
    return (
        <div className="structure-item">
            <strong>{value}</strong>
            <span>{label}</span>
        </div>
    );
}

export default StructurePanel;