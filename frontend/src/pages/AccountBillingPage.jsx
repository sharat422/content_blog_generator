import React, { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function AccountBillingPage() {
  const [loading, setLoading] = useState(true);
  const [billing, setBilling] = useState(null);
  const [error, setError] = useState("");

  const fetchBilling = async () => {
    setError("");
    setLoading(true);

    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session?.access_token) {
      setError("You must be logged in.");
      setLoading(false);
      return;
    }

    const res = await fetch(`${API_BASE}/api/billing/me`, {
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.detail || "Failed to load billing data");
    } else {
      setBilling(data);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchBilling();
  }, []);

  const openPortal = async () => {
    setError("");

    const {
      data: { session },
    } = await supabase.auth.getSession();

    const res = await fetch(`${API_BASE}/api/billing/portal`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${session.access_token}`,
      },
    });

    const data = await res.json();
    if (res.ok && data.url) {
      window.location.href = data.url;
    } else {
      setError(data.detail || "Could not open billing portal");
    }
  };

  if (loading) return <div className="p-6">Loading billing…</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Billing</h1>
      <p className="mb-2">
        Plan: <strong>{billing?.plan}</strong>
      </p>
      <p className="mb-4">
        Status: <strong>{billing?.subscription_status}</strong>
      </p>

      {billing?.plan === "pro" ? (
        <button
          onClick={openPortal}
          className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700"
        >
          Manage Subscription
        </button>
      ) : (
        <p>You’re on the free plan. Upgrade from the Pricing page.</p>
      )}
    </div>
  );
}
