import React from "react";

/**
 * Card with optional header, subtitle, icon, actions, and footer.
 *
 * Props:
 * - title?: string | ReactNode
 * - subtitle?: string | ReactNode
 * - icon?: ReactNode
 * - actions?: ReactNode   (buttons, menus, etc.)
 * - footer?: ReactNode
 * - hover?: boolean       (adds lift on hover)
 * - padded?: boolean      (toggle inner padding)
 * - className?: string
 */
const cx = (...classes) => classes.filter(Boolean).join(" ");

export default function Card({
  children,
  title,
  subtitle,
  icon,
  actions,
  footer,
  hover = true,
  padded = true,
  className,
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
      {(title || actions || icon || subtitle) && (
        <div className={cx("flex items-start gap-3", padded ? "p-6 pb-3" : "p-4 pb-2")}>
          {icon && (
            <div className="mt-0.5 rounded-xl bg-slate-100 p-2 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
              {icon}
            </div>
          )}
          <div className="flex-1">
            {title && (
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
                {subtitle}
              </p>
            )}
          </div>
          {actions && <div className="shrink-0">{actions}</div>}
        </div>
      )}

      <div className={cx(padded ? "px-6 py-4" : "p-4")}>{children}</div>

      {footer && (
        <div
          className={cx(
            "border-t border-slate-100 dark:border-slate-800",
            padded ? "px-6 py-4" : "p-4"
          )}
        >
          {footer}
        </div>
      )}
    </div>
  );
}
