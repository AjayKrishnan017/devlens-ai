import { useState } from "react";

import Navbar from "./components/Navbar";
import CodeEditor from "./components/CodeEditor";
import ScoreCard from "./components/ScoreCard";
import RiskCard from "./components/RiskCard";
import IssueList from "./components/IssueList";
import ComplexityPanel from "./components/ComplexityPanel";
import StructurePanel from "./components/StructurePanel";

import { analyzeCode } from "./services/api";

import "./App.css";


const SAMPLE_CODE = `def process(a, b, c, d, e, f):
    if a:
        if b:
            for item in c:
                if item:
                    if d:
                        while e:
                            if f:
                                return eval(item)

    return False`;


function App() {
    const [code, setCode] =
        useState(SAMPLE_CODE);

    const [report, setReport] =
        useState(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    const handleAnalyze = async () => {
        if (!code.trim()) {
            setError(
                "Enter Python code before analyzing."
            );
            return;
        }

        setLoading(true);
        setError("");

        try {
            const response =
                await analyzeCode(code);

            const analysis =
                response.report || response;

            setReport(analysis);
        } catch (err) {
            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to connect to the DevLens API."
            );
        } finally {
            setLoading(false);
        }
    };


    const summary =
        report?.summary || {};

    return (
        <div className="app">
            <Navbar />

            <main className="container">
                <section className="hero">
                    <span className="hero-tag">
                        DEVELOPER INTELLIGENCE
                    </span>

                    <h2>
                        Understand your code
                        <span>
                            {" "}
                            before it becomes a problem.
                        </span>
                    </h2>

                    <p>
                        DevLens combines static analysis,
                        complexity metrics and machine
                        learning to estimate code quality
                        and defect risk.
                    </p>
                </section>

                {error && (
                    <div className="error-box">
                        {error}
                    </div>
                )}

                <div className="workspace">
                    <CodeEditor
                        code={code}
                        setCode={setCode}
                        analyze={handleAnalyze}
                        loading={loading}
                    />

                    <div className="results">
                        {!report ? (
                            <div className="panel welcome-panel">
                                <div>
                                    <span className="eyebrow">
                                        READY
                                    </span>

                                    <h2>
                                        Run your first analysis
                                    </h2>

                                    <p>
                                        Paste Python code on
                                        the left and select
                                        Analyze Code.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="score-grid">
                                    <ScoreCard
                                        title="HEALTH"
                                        value={
                                            summary.health_score ??
                                            0
                                        }
                                        suffix="/100"
                                        description={`Grade ${
                                            summary.grade ??
                                            "-"
                                        }`}
                                    />

                                    <ScoreCard
                                        title="SECURITY"
                                        value={
                                            summary.security_score ??
                                            0
                                        }
                                        suffix="/100"
                                        description="Static security score"
                                    />

                                    <ScoreCard
                                        title="ISSUES"
                                        value={
                                            summary.total_issues ??
                                            0
                                        }
                                        description="Detected findings"
                                    />
                                </div>

                                <RiskCard
                                    prediction={
                                        report.ml_prediction
                                    }
                                />

                                <StructurePanel
                                    structure={
                                        report.structure
                                    }
                                />

                                <ComplexityPanel
                                    complexity={
                                        report.complexity
                                    }
                                />

                                <IssueList
                                    issues={
                                        report.issues
                                    }
                                />
                            </>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}


export default App;