import { useState } from "react";
import "./Login.css";

const API_URL = process.env.REACT_APP_API_URL;

function Login({ onLogin }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const name = e.target.name.value;
    const dob = e.target.dob.value;
    const pin = e.target.pin.value;

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, dob, pin }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Login failed");
        setLoading(false);
        return;
      }

      const session_id =
        crypto.randomUUID?.() ||
        Math.random().toString(36).substring(2);

      localStorage.setItem("name", name);
      localStorage.setItem("dob", dob);
      localStorage.setItem("pin", pin);
      localStorage.setItem("session_id", session_id);
      localStorage.setItem("user_id", data.user_id);

      onLogin();
    } catch (err) {
      setError("Network error. Backend not reachable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="login-title">Medical Assistant</div>
        <div className="login-subtitle">
          Secure medical chat powered by AI
        </div>

        {error && <div className="error-message">{error}</div>}

        <input name="name" placeholder="Full Name" required disabled={loading} />
        <input name="dob" type="date" required disabled={loading} />
        <input
          name="pin"
          type="password"
          maxLength="4"
          placeholder="4-digit PIN"
          required
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Authenticating..." : "Start Session"}
        </button>

        <div className="login-footer">
          Your data is private & session-based
        </div>
      </form>
    </div>
  );
}

export default Login;
