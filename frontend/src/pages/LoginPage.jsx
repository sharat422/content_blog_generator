import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { signIn, user, loading } = useAuth(); // ✅ use signIn instead of login
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showReset, setShowReset] = useState(false);
const [resetEmail, setResetEmail] = useState("");
const [resetMsg, setResetMsg] = useState("");
const [resetLoading, setResetLoading] = useState(false);

  
 // console.log("LoginPage:", { user, loading });

  if (loading) return <p>Loading...</p>; // ✅ prevent blank screen

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await signIn(email, password); // ✅ call signIn
      window.location.href = "/"; // redirect after login
    } catch (err) {
      setError(err.message);
    }
  };
  const sendResetLink = async () => {
  setResetMsg("");
  if (!resetEmail) return setResetMsg("Enter your email.");

  setResetLoading(true);
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(resetEmail, {
      redirectTo: `${window.location.origin}/update-password`,
    });

    if (error) throw error;
    setResetMsg("✅ Password reset link sent. Check your email.");
  } catch (e) {
    setResetMsg(e.message || "Failed to send reset link.");
  } finally {
    setResetLoading(false);
  }
};

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md w-full max-w-sm"
      >
        <h2 className="text-xl font-bold mb-4 text-center text-gray-800 dark:text-gray-200">
          Login
        </h2>

        {error && (
          <p className="text-red-500 text-sm mb-3 text-center">{error}</p>
        )}

        <input
          type="email"
          placeholder="Email"
          className="w-full rounded-lg border border-slate-300 p-3 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full rounded-lg border border-slate-300 p-3 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 transition"
        >
          Login
        </button>
        <div style={{ marginTop: 12 }}>
  <button
    type="button"
    onClick={() => setShowReset((v) => !v)}
    style={{
      background: "transparent",
      border: "none",
      padding: 0,
      color: "#4f46e5",
      cursor: "pointer",
      textDecoration: "underline",
      fontWeight: 600,
    }}
  >
    Update / Forgot Password?
  </button>

  {showReset && (
    <div style={{ marginTop: 12 }}>
      <input
        type="email"
        placeholder="Enter your email"
        value={resetEmail}
        onChange={(e) => setResetEmail(e.target.value)}
        style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ccc" }}
      />

      <button
        type="button"
        onClick={sendResetLink}
        disabled={resetLoading}
        style={{
          marginTop: 10,
          width: "100%",
          padding: 10,
          borderRadius: 10,
          border: "none",
          background: "#111827",
          color: "white",
          cursor: "pointer",
          opacity: resetLoading ? 0.7 : 1,
        }}
      >
        {resetLoading ? "Sending..." : "Send reset link"}
      </button>

      {resetMsg && (
        <p style={{ marginTop: 8, fontSize: 14 }}>
          {resetMsg}
        </p>
      )}
    </div>
  )}
</div>

      </form>
    </div>
  );
}