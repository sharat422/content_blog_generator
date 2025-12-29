import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabaseClient"; // adjust path if yours differs

export default function UpdatePassword() {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpdate = async () => {
    setMsg("");
    if (!password || password.length < 6) return setMsg("Password must be at least 6 characters.");
    if (password !== confirm) return setMsg("Passwords do not match.");

    setLoading(true);
    try {
      // When user lands here from the reset email, Supabase will establish a session.
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;

      setMsg("✅ Password updated successfully. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1200);
    } catch (e) {
      setMsg(e.message || "Failed to update password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: "60px auto", padding: 20 }}>
      <h2 style={{ fontSize: 24, fontWeight: 800 }}>Update Password</h2>

      <input
        type="password"
        placeholder="New password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ccc", marginTop: 12 }}
      />

      <input
        type="password"
        placeholder="Confirm new password"
        value={confirm}
        onChange={(e) => setConfirm(e.target.value)}
        style={{ width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ccc", marginTop: 10 }}
      />

      <button
        onClick={handleUpdate}
        disabled={loading}
        style={{
          marginTop: 12,
          width: "100%",
          padding: 10,
          borderRadius: 10,
          border: "none",
          background: "#111827",
          color: "white",
          cursor: "pointer",
          opacity: loading ? 0.7 : 1,
        }}
      >
        {loading ? "Updating..." : "Update password"}
      </button>

      {msg && <p style={{ marginTop: 10, fontSize: 14 }}>{msg}</p>}
    </div>
  );
}
