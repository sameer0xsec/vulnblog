from app import create_app
app = create_app()
if __name__ == "__main__":
    # VULN: host 0.0.0.0 + debug=True -> Werkzeug interactive debugger is
    # reachable on any unhandled exception, which is a remote code execution
    # primitive (the debugger PIN can often be derived/brute-forced).
    app.run(host="0.0.0.0", port=5000, debug=True)
