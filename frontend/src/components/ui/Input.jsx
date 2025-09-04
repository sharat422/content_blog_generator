import React from "react";

const cx = (...classes) => classes.filter(Boolean).join(" ");

export default function Input({
  label,
  description,
  error,
  icon,
  type = "text",
  className,
  ...props
}) {
  return (
    <div className="w-full">
      {label && (
        <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-200">
          {label}
        </label>
      )}
      <div
        className={cx(
          "relative flex items-center rounded-xl border bg-white dark:bg-slate-900",
          "focus-within:ring-2 focus-within:ring-indigo-500",
          error
            ? "border-rose-500 focus-within:ring-rose-500"
            : "border-slate-300 dark:border-slate-700",
          className
        )}
      >
        {icon && <span className="pl-3 text-slate-400">{icon}</span>}
        <input
          type={type}
          className={cx(
            "w-full rounded-xl bg-transparent px-3 py-2 text-sm outline-none",
            icon && "pl-2",
            "text-slate-900 placeholder-slate-400 dark:text-slate-100"
          )}
          {...props}
        />
      </div>
      {description && !error && (
        <p className="mt-1 text-xs text-slate-500">{description}</p>
      )}
      {error && <p className="mt-1 text-xs text-rose-500">{error}</p>}
    </div>
  );
}
