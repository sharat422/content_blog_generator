import React from "react";
import { motion } from "framer-motion";
import {
  Zap,
  PenTool,
  Share2,
  Layers,
  BarChart,
  ShieldCheck,
} from "lucide-react";

const features = [
  {
    name: "AI-Powered Writing",
    description:
      "Generate high-quality blogs, social media posts, and product descriptions in seconds.",
    icon: PenTool,
  },
  {
    name: "Fast & Efficient",
    description:
      "Save hours of work with instant content generation powered by cutting-edge AI.",
    icon: Zap,
  },
  {
    name: "Collaboration Tools",
    description:
      "Invite your team, manage projects, and co-create content together in real-time.",
    icon: Share2,
  },
  {
    name: "Custom Templates",
    description:
      "Choose from a wide range of content templates or build your own tailored to your needs.",
    icon: Layers,
  },
  {
    name: "Analytics Dashboard",
    description:
      "Track engagement and performance of your generated content with built-in insights.",
    icon: BarChart,
  },
  {
    name: "Enterprise-Grade Security",
    description:
      "Your data is protected with industry-leading security and compliance standards.",
    icon: ShieldCheck,
  },
];

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-16 px-6">
      {/* Header */}
      <motion.div
        className="text-center mb-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
          Why Choose CreativeAI?
        </h1>
        <p className="mt-3 text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
          Our platform combines advanced AI with user-friendly tools so you can
          create better content faster. Whether you’re a solo creator or a large
          team, we’ve got you covered.
        </p>
      </motion.div>

      {/* Features Grid */}
      <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
        {features.map((feature, i) => (
          <motion.div
            key={feature.name}
            className="rounded-2xl p-6 shadow-md border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.1 }}
            viewport={{ once: true }}
          >
            <feature.icon className="h-10 w-10 text-indigo-600 dark:text-indigo-400 mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
              {feature.name}
            </h3>
            <p className="mt-2 text-slate-600 dark:text-slate-400">
              {feature.description}
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
