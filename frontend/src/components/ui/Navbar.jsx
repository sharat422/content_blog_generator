import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PenTool, Sparkles, Moon, Sun } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState("light");


  // ⭐ Pull credits from AuthContext
  const { user, signOut, credits } = useAuth();
  //console.log("Navbar user:", user);
  //console.log("useAuth():", useAuth());


  const navigate = useNavigate();

  // 🌗 Load and apply saved theme
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = saved || (systemPrefersDark ? "dark" : "light");
    setTheme(initialTheme);
    document.documentElement.classList.toggle("dark", initialTheme === "dark");
  }, []);

  // 🌗 Toggle between dark/light
  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  const handleLogout = async () => {
    try {
      await signOut();
      setOpen(false);

      setTimeout(() => {
        navigate("/login");
        window.location.reload();
      }, 200);
    } catch (err) {
      console.error("Logout error:", err);
    }
  };


  const navLinks = [
    { name: "Home", to: "/" },
    { name: "Ecommerce", to: "/ecommerce" },
    { name: "Twin", to: "/twin" },
    { name: "Pricing", to: "/pricing" },
    { name: "Terms", to: "/terms" },
    { name: "Privacy", to: "/privacy" },
  ];

  return (
    <nav className="fixed top-0 left-0 w-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16">

        {/* Logo */}
        <Link to="/" className="flex items-center space-x-2">
          <div className="relative">
            <PenTool className="h-7 w-7 text-indigo-600 dark:text-indigo-400" />
            <Sparkles className="h-4 w-4 text-indigo-400 absolute -top-1 -right-1 animate-pulse" />
          </div>
          <h1 className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
            WriteSwift<span className="text-slate-700 dark:text-slate-300">.ai</span>
          </h1>
        </Link>

        {/* Desktop Navbar */}
        <div className="hidden md:flex items-center space-x-6">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.to}
              className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
            >
              {link.name}
            </Link>
          ))}

          {/* ⭐ CREDITS BADGE — Show only if logged in */}
          {/*{user && (
            <div className="px-4 py-1 rounded-full bg-indigo-100 dark:bg-indigo-800 text-indigo-700 dark:text-white font-semibold text-sm shadow">
              ⚡ Credits: {credits ?? 0}
            </div>
          )} */}

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {theme === "dark" ? (
              <Sun className="h-5 w-5 text-yellow-400" />
            ) : (
              <Moon className="h-5 w-5 text-slate-700" />
            )}
          </button>

          {/* Auth Buttons */}
          {!user ? (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-indigo-600"
              >
                Login
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition"
              >
                Sign Up
              </Link>
            </>
          ) : (
            <button
              onClick={() => {
                console.log("Logout button clicked!");
                handleLogout();
              }}
              className="px-4 py-2 rounded-lg bg-red-500 text-white font-semibold hover:bg-red-600 transition"
            >
              Logout
            </button>


          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setOpen(!open)}
          className="text-slate-700 dark:text-slate-300 md:hidden text-2xl focus:outline-none"
        >
          {open ? "✕" : "☰"}
        </button>
      </div>

      {/* Mobile Menu */}
      {open && (
        <div className="md:hidden px-4 pb-4 space-y-3 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 shadow-sm">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.to}
              onClick={() => setOpen(false)}
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition"
            >
              {link.name}
            </Link>
          ))}

          {/* ⭐ CREDITS IN MOBILE MENU */}
          {user && (
            <div className="w-full text-center py-2 rounded-lg bg-indigo-100 dark:bg-indigo-800 text-indigo-700 dark:text-white font-semibold text-sm shadow">
              ⚡ Credits: {credits ?? 0}
            </div>
          )}

          {/* Theme Toggle in Mobile */}
          <button
            onClick={toggleTheme}
            className="flex items-center justify-center w-full gap-2 py-2 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          >
            {theme === "dark" ? (
              <>
                <Sun className="h-5 w-5 text-yellow-400" />
                <span>Light Mode</span>
              </>
            ) : (
              <>
                <Moon className="h-5 w-5 text-slate-600" />
                <span>Dark Mode</span>
              </>
            )}
          </button>

          {/* Auth Buttons */}
          {!user ? (
            <>
              <Link
                to="/login"
                onClick={() => setOpen(false)}
                className="block w-full text-center px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
              >
                Login
              </Link>
              <Link
                to="/signup"
                onClick={() => setOpen(false)}
                className="block w-full text-center px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
              >
                Sign Up
              </Link>
            </>
          ) : (
            <button
              onClick={handleLogout}
              className="block w-full text-center px-4 py-2 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 transition"
            >
              Logout
            </button>
          )}
        </div>
      )}
    </nav>
  );
}
