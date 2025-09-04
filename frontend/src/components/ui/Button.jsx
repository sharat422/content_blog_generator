import React from "react";

/**
 * Button component with variants, sizes, loading, icons, and accessibility.
 *
 * Props:
 * - variant: "primary" | "secondary" | "outline" | "ghost" | "destructive" | "success" | "warning"
 * - size: "sm" | "md" | "lg" | "icon"
 * - leftIcon / rightIcon: React nodes (e.g., <svg />)
 * - isLoading: boolean
 * - fullWidth: boolean
 * - className: string
 */
const cx = (...classes) => classes.filter(Boolean).join(" ");

export default function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className,
  ...props
}) {
  const variants = {
    primary:
      "bg-indigo-600 text-white shadow-sm hover:bg-indigo-700 active:bg-indigo-800 disabled:bg-indigo-300",
    secondary:
      "bg-slate-900 text-white hover:bg-slate-800 active:bg-slate-900 disabled:bg-slate-400 dark:bg-slate-700 dark:hover:bg-slate-600",
    outline:
      "border border-slate-300 text-slate-800 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-800",
    ghost:
      "text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800",
    destructive:
      "bg-rose-600 text-white hover:bg-rose-700 active:bg-rose-800 disabled:bg-rose-300",
    success:
      "bg-emerald-600 text-white hover:bg-emerald-700 active:bg-emerald-800 disabled:bg-emerald-300",
    warning:
      "bg-amber-500 text-slate-900 hover:bg-amber-600 active:bg-amber-700 disabled:bg-amber-300",
  };

  const sizes = {
    sm: "h-9 px-3 text-sm",
    md: "h-10 px-4 text-sm",
    lg: "h-12 px-6 text-base",
    icon: "h-10 w-10 p-0",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={cx(
        "inline-flex items-center justify-center gap-2 rounded-xl font-medium tracking-wide",
        "transition-transform duration-150",
        "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-500",
        "active:scale-[0.985]",
        "disabled:cursor-not-allowed disabled:opacity-70",
        variants[variant],
        sizes[size],
        fullWidth && "w-full",
        className
      )}
      {...props}
    >
      {isLoading && (
        <span
          aria-hidden="true"
          className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-transparent"
        />
      )}
      {leftIcon && <span className="-ml-0.5">{leftIcon}</span>}
      <span className="whitespace-nowrap">{children}</span>
      {rightIcon && <span className="-mr-0.5">{rightIcon}</span>}
    </button>
  );
}

