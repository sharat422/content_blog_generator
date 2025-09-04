import React, { useState, useEffect } from "react";
import Button from "./Button";
import Badge from "../ui/Badge";
import AuthModal from "./AuthModal";
import { supabase } from "../../lib/supabaseClient";
import { Link } from "react-router-dom";
import { PenTool, Sparkles } from "lucide-react";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      if (data?.user) setUser(data.user);
    });

    const { data: subscription } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user || null);
      }
    );

    return () => subscription?.subscription.unsubscribe();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setOpen(false); // close mobile menu if open
  };

  // ✅ Added Home link
  const navLinks = [
    { name: "Home", to: "/" },
    { name: "Features", to: "/features" },
    //{ name: "Pricing", to: "/pricing" },
  ];

  return (
    <nav className="bg-white shadow-md dark:bg-slate-900">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <Link to="/" className="flex items-center space-x-2">
            <div className="relative">
              <PenTool className="h-8 w-8 text-primary" />
              <Sparkles className="h-4 w-4 text-creative absolute -top-1 -right-1 animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">
                CreativeAI
              </h1>
              <Badge variant="secondary" className="text-xs -mt-1">
                Beta
              </Badge>
            </div>
          </Link>
        </div>

        {/* Desktop Nav */}
        <div className="hidden items-center space-x-6 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.to}
              className="text-sm font-medium text-slate-600 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400"
            >
              {link.name}
            </Link>
          ))}

          {user ? (
            <>
              <span className="text-sm text-slate-600 dark:text-slate-300">
                Signed in as <strong>{user.email}</strong>
              </span>
              <Button size="sm" variant="outline" onClick={handleSignOut}>
                Sign Out
              </Button>
            </>
          ) : (
            <Button size="sm" onClick={() => setShowAuth(true)}>
              Sign In
            </Button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setOpen(!open)}
          className="text-slate-600 dark:text-slate-300 md:hidden"
        >
          {open ? "✕" : "☰"}
        </button>
      </div>

      {/* ✅ Mobile Menu */}
      {open && (
        <div className="md:hidden px-4 pb-4 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.to}
              onClick={() => setOpen(false)} // close menu after click
              className="block text-sm font-medium text-slate-600 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400"
            >
              {link.name}
            </Link>
          ))}

          {user ? (
            <Button
              size="sm"
              variant="outline"
              className="w-full mt-2"
              onClick={() => {
                handleSignOut();
                setOpen(false);
              }}
            >
              Sign Out
            </Button>
          ) : (
            <Button
              size="sm"
              className="w-full mt-2"
              onClick={() => {
                setShowAuth(true);
                setOpen(false);
              }}
            >
              Sign In
            </Button>
          )}
        </div>
      )}

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuth}
        onClose={() => setShowAuth(false)}
        onAuth={setUser}
      />
    </nav>
  );
}
