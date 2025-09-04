import React from "react";
import { motion } from "framer-motion";
import { Check } from "lucide-react";

const tiers = [
  {
    name: "Starter",
    price: "Free",
    description: "Get started with AI-powered content generation.",
    features: [
      "10 AI generations / month",
      "Basic templates (Blog, Social Media)",
      "Single user only",
      "Community support",
    ],
    cta: "Start Free",
    priceId: null, // no checkout for free plan
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$19/mo",
    description: "For freelancers & creators who want to scale content.",
    features: [
      "50,000 words / month",
      "All templates unlocked",
      "Export to PDF, Word, Markdown",
      "Tone & voice customization",
      "Priority email support",
    ],
    cta: "Get Pro",
    priceId: "price_12345", // 🔑 Replace with real Stripe Price ID
    highlighted: true,
  },
  {
    name: "Business",
    price: "$59/mo",
    description: "For teams & agencies creating content at scale.",
    features: [
      "200,000 words / month",
      "Team collaboration (5 seats)",
      "Brand voice customization",
      "Analytics dashboard",
      "API access & integrations",
      "Priority live chat support",
    ],
    cta: "Get Business",
    priceId: "price_67890", // 🔑 Replace with real Stripe Price ID
    highlighted: false,
  },
];

export default function PricingPage() {
  const handleCheckout = async (priceId) => {
    if (!priceId) return; // free plan → no checkout

    try {
      const res = await fetch("http://localhost:8000/create-checkout-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ priceId }),
      });

      const data = await res.json();
      if (data.url) {
        window.location.href = data.url; // redirect to Stripe Checkout
      }
    } catch (err) {
      console.error("Checkout error:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-16 px-6">
      {/* Header */}
      <motion.div
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
          Pricing Plans
        </h1>
        <p className="mt-4 text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
          Choose a plan that fits your needs. Upgrade anytime as your business
          grows.
        </p>
      </motion.div>

      {/* Pricing Tiers */}
      <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
        {tiers.map((tier, i) => (
          <motion.div
            key={tier.name}
            className={`flex flex-col rounded-2xl border shadow-md p-6 ${
              tier.highlighted
                ? "bg-gradient-primary text-white"
                : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
            }`}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.1 }}
            viewport={{ once: true }}
          >
            <h3
              className={`text-2xl font-bold mb-2 ${
                tier.highlighted ? "text-white" : "text-slate-900 dark:text-white"
              }`}
            >
              {tier.name}
            </h3>
            <p
              className={`mb-4 ${
                tier.highlighted
                  ? "text-white/90"
                  : "text-slate-600 dark:text-slate-400"
              }`}
            >
              {tier.description}
            </p>

            <div className="text-3xl font-bold mb-6">{tier.price}</div>

            <ul className="space-y-3 flex-1">
              {tier.features.map((feature) => (
                <li key={feature} className="flex items-start space-x-2">
                  <Check
                    className={`h-5 w-5 flex-shrink-0 ${
                      tier.highlighted
                        ? "text-white"
                        : "text-indigo-600 dark:text-indigo-400"
                    }`}
                  />
                  <span
                    className={
                      tier.highlighted
                        ? "text-white"
                        : "text-slate-700 dark:text-slate-300"
                    }
                  >
                    {feature}
                  </span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleCheckout(tier.priceId)}
              disabled={!tier.priceId}
              className={`mt-6 w-full rounded-xl px-4 py-3 font-semibold transition ${
                tier.highlighted
                  ? "bg-white text-indigo-600 hover:bg-slate-100"
                  : "bg-indigo-600 text-white hover:bg-indigo-700"
              } ${!tier.priceId ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              {tier.cta}
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
