import React from "react";

/* Utility */
const cx = (...classes) => classes.filter(Boolean).join(" ");

/* ---------------------------
   BASE CARD
---------------------------- */
export function Card({
  children,
  className,
  hover = true,
  padded = true,
  ...props
}) {
  return (
    <div
      className={cx(
        "group relative rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900",
        hover && "transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-xl",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/* ---------------------------
   HEADER
---------------------------- */
export function CardHeader({ children, padded = true, className }) {
  return (
    <div
      className={cx(
        padded ? "px-6 py-4" : "p-4",
        "border-b border-slate-100 dark:border-slate-800",
        className
      )}
    >
      {children}
    </div>
  );
}

/* ---------------------------
   TITLE
---------------------------- */
export function CardTitle({ children, className }) {
  return (
    <h3 className={cx("text-lg font-semibold text-slate-900 dark:text-white", className)}>
      {children}
    </h3>
  );
}

/* ---------------------------
   CONTENT
---------------------------- */
export function CardContent({ children, padded = true, className }) {
  return (
    <div className={cx(padded ? "px-6 py-4" : "p-4", className)}>
      {children}
    </div>
  );
}

/* ---------------------------
   FOOTER
---------------------------- */
export function CardFooter({ children, padded = true, className }) {
  return (
    <div
      className={cx(
        "border-t border-slate-100 dark:border-slate-800",
        padded ? "px-6 py-4" : "p-4",
        className
      )}
    >
      {children}
    </div>
  );
}

/* ---------------------------
   DEFAULT EXPORT
---------------------------- */
export default Card;
