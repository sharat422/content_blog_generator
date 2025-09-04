import React from "react";
import Card from "../ui/Card";

const testimonials = [
  { name: "David S. Harper", quote: "Squibler helped me stay organized and finish fast." },
  { name: "Becky Prospero", quote: "User-friendly and super helpful support team." },
];

export default function Testimonials() {
  return (
    <section className="bg-white dark:bg-slate-800 py-16 px-4">
      <h2 className="text-center text-3xl font-semibold text-slate-900 dark:text-slate-100">
        Loved by Writers Worldwide
      </h2>
      <div className="mt-8 grid gap-6 sm:grid-cols-1 md:grid-cols-2 max-w-4xl mx-auto">
        {testimonials.map((t) => (
          <Card key={t.name} hover>
            <p className="italic text-slate-600 dark:text-slate-300">“{t.quote}”</p>
            <p className="mt-4 font-semibold text-slate-800 dark:text-slate-200">
              — {t.name}
            </p>
          </Card>
        ))}
      </div>
    </section>
  );
}
