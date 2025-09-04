import React, { useState } from "react";
import Button from "../ui/Button";
import Input from "../ui/Input";

export default function Hero({ onGenerate }) {
  const [prompt, setPrompt] = useState("");

  return (
    <section className="bg-slate-50 dark:bg-slate-900 py-20 text-center px-4">
      <h1 className="mx-auto max-w-2xl text-4xl font-bold text-slate-900 dark:text-slate-100">
        Create with AI
      </h1>
      <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600 dark:text-slate-300">
        Define what you need and hit generate to get started.
      </p>
      <div className="mx-auto mt-8 flex max-w-xl gap-2">
        <Input
          placeholder="e.g. Write a villain character sketch"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="flex-1"
        />
        <Button onClick={() => onGenerate(prompt)}>Generate</Button>
      </div>
    </section>
  );
}
