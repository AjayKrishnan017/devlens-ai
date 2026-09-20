function Navbar() {
    return (
        <nav className="navbar">
            <div>
                <h1>DevLens AI</h1>
                <span className="subtitle">
                    AI-Powered Code Intelligence
                </span>
            </div>

            <div className="status">
                <span className="status-dot"></span>
                Analysis Engine Online
            </div>
        </nav>
    );
}

export default Navbar;