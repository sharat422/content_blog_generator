import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
import { motion } from "framer-motion";
import { HelmetProvider } from "react-helmet-async";
import { Helmet } from "react-helmet-async";

// UI kit
import Navbar from "./components/ui/Navbar";
import Button from "./components/ui/Button";
import Card from "./components/ui/Card";

// Landing sections
import Features from "./components/landing/Features";
import Testimonials from "./components/landing/Testimonials";

// Pages
import PricingPage from "./pages/PricingPage";
import FeaturesPage from "./pages/FeaturesPage";

function HomePage() {
  const [prompt, setPrompt] = useState("");
  const [template, setTemplate] = useState("Blog Post");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const seoTitle = result
    ? `${template} - AI Generated | Content Generator`
    : "AI Content & Blog Generator | SEO Optimized Writing Tool";
  const seoDescription = result
    ? result.substring(0, 160).replace(/\n/g, " ")
    : "Generate SEO-optimized blog posts, product descriptions, social media posts, and emails instantly with AI.";

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError("");
    setResult("");

    try {
      const res = await fetch("http://localhost:8000/api/generator/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, template }),
      });

      const data = await res.json();

      // --- Transform content: remove title/heading, show only paragraphs ---
      if (data.content) {
        if (Array.isArray(data.content.sections)) {
          setResult(
            data.content.sections.map((sec) => sec.content).join("\n\n")
          );
        } else if (typeof data.content === "string") {
          setResult(data.content);
        } else {
          setResult(JSON.stringify(data.content, null, 2)); // fallback
        }
      }
    } catch (err) {
      console.error("Error generating content:", err);
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
    {/* ✅ SEO HEAD TAGS */}
      <Helmet>
        <title>{seoTitle}</title>
        <meta name="description" content={seoDescription} />
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDescription} />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://yourdomain.com/" />
        <meta property="og:image" content="https://yourdomain.com/preview.png" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={seoTitle} />
        <meta name="twitter:description" content={seoDescription} />
        <meta name="twitter:image" content="https://yourdomain.com/preview.png" />
      </Helmet>
      {/* Hero / Generator section */}
      <section className="flex-1 px-4 py-16 text-center">
        <h1 className="mx-auto max-w-2xl text-4xl font-bold text-slate-900 dark:text-slate-100">
          Content & Blog Generator
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600 dark:text-slate-300">
          Choose a template, describe your idea, and let AI create content for
          you.
        </p>

        <div className="mx-auto mt-8 max-w-2xl space-y-4">
          <Card>
            {/* Template select */}
            <select
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="mb-4 w-full rounded-lg border border-slate-300 p-2 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            >
              <option value="Blog Post">Blog Post</option>
            <option value="Product Description">Product Description</option>
            <option value="Social Media Post">Social Media Post</option>
            <option value="Email">Email</option>
            <option value="Report">Report</option>
            </select>

            {/* Prompt input */}
            <textarea
              rows={4}
              className="w-full rounded-lg border border-slate-300 p-3 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              placeholder="Enter your prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />

            {/* Generate button */}
            <div className="mt-4 flex justify-end">
              <Button
                type="button"
                onClick={handleGenerate}
                isLoading={loading}
              >
                {loading ? "Generating..." : "Generate"}
              </Button>
            </div>
          </Card>
        </div>

        {/* Error */}
        {error && <p className="mt-4 text-red-600 dark:text-red-400">{error}</p>}

        {/* Result */}
        {result && (
          <motion.div
            className="mx-auto mt-8 max-w-2xl"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card title="Generated Content">
              <div className="whitespace-pre-wrap text-slate-700 dark:text-slate-200">
                {result}
              </div>
            </Card>
          </motion.div>
        )}
      </section>

      {/* Features */}
      <Features />

      {/* Testimonials */}
      <Testimonials />

      {/* Footer CTA */}
      <footer className="bg-white dark:bg-slate-900 py-10 text-center border-t border-slate-200 dark:border-slate-800">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200">
          Ready to start creating?
        </h3>
        <p className="mt-1 text-slate-600 dark:text-slate-400">
          Sign up now and supercharge your writing with AI.
        </p>
        <div className="mt-4">
          <Button size="lg" type="button">
            Get Started
          </Button>
        </div>
      </footer>
    </>
  );
}

export default function App() {
  return (
    <HelmetProvider>
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/features" element={<FeaturesPage />} />
      </Routes>
    </div>
    </HelmetProvider>
  );
}
