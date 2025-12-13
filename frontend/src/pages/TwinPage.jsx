import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import { useAuth } from "../context/AuthContext";
import { supabase } from "../lib/supabaseClient";

const MODES = [
  { id: "reflect", label: "Reflect (Insights)" },
  { id: "plan", label: "Plan (Roadmap)" },
  { id: "create", label: "Create (Ideas & Content)" },
];

export default function TwinPage() {
  const { user } = useAuth();

  const [mode, setMode] = useState("reflect");
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [profile, setProfile] = useState(null);
  const [memories, setMemories] = useState([]);

  // FIX 1 — add fallback so undefined doesn't break URLs
  const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";

  //console.log("TwinPage API_BASE_URL = ", API_BASE_URL);

  // -----------------------------------------
  // LOAD PROFILE + MEMORIES
  // -----------------------------------------
  useEffect(() => {
    if (!user) return;
    fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
    try {
      const { data: { session }} = await supabase.auth.getSession();
      const token = session?.access_token;

      if (!token) return;

      const res = await fetch(`${API_BASE_URL}/api/twin/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!res.ok) {
        console.error("Profile load failed:", res.status);
        return;
      }

      const data = await res.json();
      setProfile(data.profile || null);
      setMemories(data.memories || []);

    } catch (err) {
      console.error("Profile fetch error:", err);
    }
  };

  // -----------------------------------------
  // GENERATE TWIN OUTPUT
  // -----------------------------------------
  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError("");
    setResult("");

    try {
      const { data: { session }} = await supabase.auth.getSession();
      const token = session?.access_token;

      if (!token) {
        setError("Login expired. Please re-login.");
        setLoading(false);
        return;
      }

      const res = await fetch(`${API_BASE_URL}/api/twin/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ prompt, mode })
      });

      if (!res.ok) {
        const text = await res.text();
        console.error("Bad generate response:", text);
        setError("Server error. Try again.");
        setLoading(false);
        return;
      }

      const data = await res.json();
      //console.log("Twin response =", data);

      setResult(data.output || data.response ||data.content || "");
      fetchProfile();

    } catch (err) {
      console.error("Twin generate error:", err);
      setError("Something went wrong.");
    }

    setLoading(false);
  };

  // -----------------------------------------
  // UNAUTH VIEW
  // -----------------------------------------
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <p className="text-slate-700 dark:text-slate-200">
          Please log in to talk to your Synthetic Twin.
        </p>
      </div>
    );
  }

  // -----------------------------------------
  // MAIN UI
  // -----------------------------------------
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pt-20 px-4 pb-16">
      <div className="max-w-4xl mx-auto space-y-10">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
            Your Synthetic Twin
          </h1>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            An evolving AI co-creator powered by memory.
          </p>

          {profile && (
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              Tone: <strong>{profile.tone}</strong> · Creativity:{" "}
              <strong>{profile.creativity}</strong>
            </p>
          )}
        </motion.div>

        {/* Interaction Card */}
        <Card>
          <div className="flex flex-wrap gap-3 mb-4">
            {MODES.map((m) => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`px-3 py-1 rounded-full text-sm font-medium border transition ${
                  mode === m.id
                    ? "bg-indigo-600 text-white border-indigo-600"
                    : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border-slate-300 dark:border-slate-700 hover:border-indigo-500"
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>

          <textarea
            rows={4}
            className="w-full rounded-lg border border-slate-300 p-3 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            placeholder="Ask your Synthetic Twin something..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />

          <div className="mt-4 flex justify-end">
            <Button type="button" onClick={handleGenerate} isLoading={loading}>
              {loading ? "Thinking..." : "Ask Your Twin"}
            </Button>
          </div>

          {error && (
            <p className="mt-3 text-red-600 dark:text-red-400 text-sm">
              {error}
            </p>
          )}
        </Card>

        {/* Twin Response */}
        {result && (
          <Card>
            <div className="whitespace-pre-wrap text-slate-700 dark:text-slate-200">
              {result}
            </div>
          </Card>
        )}

      </div>
    </div>
  );
}
