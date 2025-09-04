import React, { useState } from "react";
import Button from "./Button";
import Input from "./Input";
import { supabase } from "../../lib/supabaseClient";

export default function AuthModal({ isOpen, onClose, onAuth }) {
  const [mode, setMode] = useState("signin"); // "signin" or "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (mode === "signin") {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        onAuth(data.user);
      } else {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        onAuth(data.user);
      }
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-900">
        <h2 className="mb-4 text-xl font-bold text-slate-800 dark:text-slate-100">
          {mode === "signin" ? "Sign In" : "Sign Up"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            label="Password"
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="text-sm text-rose-500">{error}</p>}

          <div className="flex justify-between items-center">
            <Button type="submit" isLoading={loading}>
              {loading
                ? mode === "signin"
                  ? "Signing In..."
                  : "Signing Up..."
                : mode === "signin"
                ? "Sign In"
                : "Sign Up"}
            </Button>

            <button
              type="button"
              onClick={() =>
                setMode(mode === "signin" ? "signup" : "signin")
              }
              className="text-sm text-indigo-600 hover:underline"
            >
              {mode === "signin"
                ? "New here? Create an account"
                : "Already have an account? Sign in"}
            </button>
          </div>
        </form>

        <div className="mt-4 flex justify-end">
          <Button variant="ghost" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
