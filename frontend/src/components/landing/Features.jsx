import React from "react";
import { Sparkles, User, PenSquare } from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "Story Outlines",
    subtitle: "Generate structured ideas fast",
    description: "Quickly turn rough concepts into organized story structures.",
  },
  {
    icon: User,
    title: "Character Sketches",
    subtitle: "Craft vivid, compelling profiles",
    description: "Build detailed characters with personality, background, and goals.",
  },
  {
    icon: PenSquare,
    title: "Content Posts",
    subtitle: "Social captions, blogs, and more",
    description: "Create engaging posts for social media, blogs, and newsletters.",
  },
];

export default function Features() {
  return (
    <section className="py-20 px-6 bg-white dark:bg-slate-950">
      <div className="max-w-6xl mx-auto">

        {/* Section Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white">
            What AI Can Do for You
          </h2>
          <p className="mt-3 text-slate-600 dark:text-slate-400">
            Powerful tools to help you create faster and better.
          </p>
        </div>

        {/* Feature Grid */}
        <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.title}
                className="group rounded-xl border border-slate-200 dark:border-slate-800 p-6 hover:shadow-lg hover:-translate-y-1 transition-all bg-white dark:bg-slate-900"
              >
                {/* Icon */}
                <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-indigo-100 dark:bg-indigo-900 mb-4">
                  <Icon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>

                {/* Title */}
                <h3 className="text-lg font-semibold text-slate-800 dark:text-white">
                  {feature.title}
                </h3>

                {/* Subtitle */}
                <p className="text-sm text-indigo-600 dark:text-indigo-400 mt-1">
                  {feature.subtitle}
                </p>

                {/* Description */}
                <p className="mt-3 text-sm text-slate-600 dark:text-slate-400">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}