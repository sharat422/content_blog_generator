import React from "react";

const cx = (...classes) => classes.filter(Boolean).join(" ");

export default function Badge({
  children,
  variant = "default",
  size = "sm",
  className,
}) {
  const variants = {
    default: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200",
    success: "bg-emerald-100 text-emerald-800 dark:bg-emerald-800 dark:text-emerald-100",
    warning: "bg-amber-100 text-amber-800 dark:bg-amber-700 dark:text-amber-100",
    destructive: "bg-rose-100 text-rose-800 dark:bg-rose-800 dark:text-rose-100",
    info: "bg-indigo-100 text-indigo-800 dark:bg-indigo-800 dark:text-indigo-100",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs font-medium",
    md: "px-3 py-1 text-sm font-medium",
  };

  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}
