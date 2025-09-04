import React from "react";
import Card from "../ui/Card";
import Badge from "../ui/Badge"; // optional usage

const features = [
  {
    title: "Story Outlines",
    subtitle: "Generate structured ideas fast",
  },
  {
    title: "Character Sketches",
    subtitle: "Craft vivid, compelling profiles",
  },
  {
    title: "Content Posts",
    subtitle: "Social captions, blogs, and more",
  },
];

export default function Features() {
  return (
    <section className="py-16 px-4">
      <h2 className="text-center text-3xl font-semibold text-slate-800 dark:text-slate-100">
        What AI Can Do for You
      </h2>
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <Card key={f.title} title={f.title} subtitle={f.subtitle} hover>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Leverage AI to accelerate your creative process.
            </p>
          </Card>
        ))}
      </div>
    </section>
  );
}
