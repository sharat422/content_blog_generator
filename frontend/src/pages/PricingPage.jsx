// src/pages/PricingPage.jsx
import React from "react";
import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { supabase } from "../lib/supabaseClient";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const PRO_PRICE_ID =
  import.meta.env.VITE_STRIPE_PRICE_ID_PRO || "price_1SYf2oLSGCDaShjEzUijuuGC";

const tiers = [
  {
    name: "Starter",
    price: "Free",
    description: "Get started with AI writing.",
    features: ["100 free credits", "Basic templates", "Community support"],
    cta: "Start Free",
    priceId: "free",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$11.99/mo",
    description: "Perfect for creators scaling content.",
    features: [
      "6000 credits",
      "All templates unlocked",
      "Export tools",
      "Tone customization",
      "Priority support",
    ],
    cta: "Get Pro",
    priceId: PRO_PRICE_ID,
    highlighted: true,
  },
];

export default function PricingPage() {
  const { user, plan, loading } = useAuth();
  const navigate = useNavigate();

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center text-white">
        Loading...
      </div>
    );

  const normalizedPlan = plan?.toLowerCase();

  const handleStartFree = () => {
    if (user) navigate("/");
    else navigate("/signup");
  };

  const handleCheckout = async (priceId) => {
    if (!user) return navigate("/signup");
    if (normalizedPlan === "pro") return;

    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session?.access_token) return alert("Please log in again.");

    const res = await fetch(`${API_BASE}/api/billing/checkout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({ price_id: priceId }),
    });

    const data = await res.json();
    if (data.checkout_url) window.location.href = data.checkout_url;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white py-16 px-6">
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold">Pricing Plans</h1>
        <p className="mt-3 opacity-70">
          Choose the plan that fits your content creation workflow.
        </p>
      </motion.div>

      <div className="grid gap-8 sm:grid-cols-2 max-w-5xl mx-auto">
        {tiers.map((tier, idx) => (
          <motion.div
            key={tier.name}
            className={`flex flex-col rounded-xl border p-6 shadow-md ${
              tier.highlighted
                ? "bg-indigo-600 text-white"
                : "bg-slate-900 text-white border-slate-800"
            }`}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <h3 className="text-2xl font-semibold">{tier.name}</h3>
            <div className="text-3xl font-bold my-4">{tier.price}</div>

            <ul className="space-y-3 flex-1">
              {tier.features.map((f) => (
                <li key={f} className="flex items-start space-x-2">
                  <Check className="w-5 h-5 text-green-400" />
                  <span className="opacity-90">{f}</span>
                </li>
              ))}
            </ul>

            <button
              disabled={tier.name === "Pro" && normalizedPlan === "pro"}
              onClick={() =>
                tier.priceId === "free"
                  ? handleStartFree()
                  : handleCheckout(tier.priceId)
              }
              className={`mt-6 w-full py-3 rounded-lg font-semibold transition ${
                tier.name === "Pro" && normalizedPlan === "pro"
                  ? "bg-green-600 cursor-default"
                  : "bg-white text-indigo-600 hover:bg-slate-200"
              }`}
            >
              {tier.name === "Pro" && normalizedPlan === "pro"
                ? "Subscribed ✓"
                : tier.cta}
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
