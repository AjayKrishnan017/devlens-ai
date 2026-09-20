\# DevLens AI



DevLens AI is an AI-powered code intelligence platform that combines static code analysis, software quality metrics, security checks, and machine learning to estimate defect risk in Python code.



\## Features



\- Python AST-based code analysis

\- Code structure extraction

\- Cyclomatic complexity analysis

\- Nesting-depth analysis

\- Function-length and parameter analysis

\- Static issue detection

\- Security checks for dangerous operations

\- Code health scoring

\- Security scoring

\- ML-based defect-risk estimation

\- React analytics dashboard

\- FastAPI REST API



\## Architecture



```text

React Dashboard

&#x20;     |

&#x20;     v

FastAPI Backend

&#x20;     |

&#x20;     +-------------------+

&#x20;     |                   |

&#x20;     v                   v

Static Analysis      Feature Extraction

&#x20;     |                   |

&#x20;     v                   v

Health/Security      ML Risk Model

&#x20;     |                   |

&#x20;     +---------+---------+

&#x20;               |

&#x20;               v

&#x20;       Analysis Report

