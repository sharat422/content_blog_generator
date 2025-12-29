import React, { useState } from "react";
import { motion } from "framer-motion";
import { Helmet } from "react-helmet-async";
import { useNavigate } from "react-router-dom";
//import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { remaining, consume } from "../utils/guestLimits";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Features from "../components/landing/Features";
import Testimonials from "../components/landing/Testimonials";

export default function HomePage() {
  const [prompt, setPrompt] = useState("");
  const [template, setTemplate] = useState("Blog Post");
  const [result, setResult] = useState("");
  //const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const {user, loading, getToken } = useAuth();

  console.log("HOME user:", user);
  //console.log("HOME token exists:", !!session?.access_token);
  const seoTitle = result
    ? `${template} - AI Generated | Content Generator`
    : "AI Content & Blog Generator | SEO Optimized Writing Tool";

  const seoDescription = result
    ? result.substring(0, 160).replace(/\n/g, " ")
    : "Generate SEO-optimized blog posts, product descriptions, social media posts, and emails instantly with AI.";

  const handleGenerate = async () => {
    if (loading) return;
    if (!prompt.trim()) return;

    // ✅ Redirect to login using React Router, no blank reload
    // ✅ Guest limits BEFORE login:
// Blog Post = 1 time, all other templates = 2 times
if (!user) {
  const isBlog = (template || "").toLowerCase().includes("blog");
  const key = isBlog ? "guest_blog_generate" : "guest_other_generate";
  const limit = isBlog ? 1 : 2;

  if (remaining(key, limit) <= 0) {
    navigate("/pricing"); // or "/signup" if you prefer
    return;
  }

  // Consume the guest attempt
  consume(key);

  // IMPORTANT:
  // Your backend /api/generator/ requires Authorization right now,
  // so guests still can't actually generate without a guest endpoint.
  // We'll send them to signup after consuming the trial click.
  navigate("/signup");
  return;
}

  const token = await getToken();
if (!token) {
  navigate("/login");
  return;
}


    setLoading(true);
    setError("");
    setResult("");

    const API_BASE_URL =
      import.meta.env.VITE_API_URL || "http://localhost:8000";

    try {
      const res = await fetch(`${API_BASE_URL}/api/generator/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ prompt, template }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data = await res.json();

      if (data.content) {
        if (Array.isArray(data.content.sections)) {
          setResult(
            data.content.sections.map((sec) => sec.content).join("\n\n")
          );
        } else if (typeof data.content === "string") {
          setResult(data.content);
        } else {
          setResult(JSON.stringify(data.content, null, 2));
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
      {/* ✅ SEO */}
      <Helmet>
        <title>{seoTitle}</title>
        <meta name="description" content={seoDescription} />
      </Helmet>
{/*<section className="py-16 bg-slate-950 border-t border-slate-800">
  <div className="max-w-5xl mx-auto px-4 text-center">
    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
      Turn ideas into AI videos in seconds
    </h2>
    <p className="text-slate-300 mb-6">
      WriteSwift now generates vertical-ready video slides from your topics. Plan scenes, edit them,
      and render a downloadable MP4.
    </p>
    <Link
      to="/videos"
      className="inline-flex items-center px-6 py-3 rounded-lg bg-emerald-500 text-slate-950 font-semibold hover:bg-emerald-400 transition"
    >
      🎬 Try the AI Video Generator
    </Link>
  </div>
</section> 
      {/* Hero / Generator */}
      <section className="flex-1 px-4 py-16 text-center">
        <h1 className="mx-auto max-w-2xl text-4xl font-bold text-slate-900 dark:text-slate-100">
          Content & Blog Generator
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600 dark:text-slate-300">
          Choose a template, describe your idea, and let AI create content for you.
        </p>

        <div className="mx-auto mt-8 max-w-2xl space-y-4">
          <Card>
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

            <textarea
              rows={4}
              className="w-full rounded-lg border border-slate-300 p-3 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
              placeholder="Enter your prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />

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

        {error && (
          <p className="mt-4 text-red-600 dark:text-red-400">{error}</p>
        )}

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

      {/* Features & Testimonials */}
      <Features />
      <Testimonials />

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-900 py-10 text-center border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              &copy; 2025 WriteSwift. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
