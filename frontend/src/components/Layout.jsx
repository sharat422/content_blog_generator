import React from "react";
import Navbar from "./ui/Navbar";
import { Link } from "react-router-dom";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950">
      {/* Navbar */}
      <Navbar />

      {/* Page Content */}
      <main className="flex-grow">{children}</main>

      {/* Footer */}
      <footer className="bg-white dark:bg-slate-900 py-6 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 text-sm">
            &copy; {new Date().getFullYear()} All rights reserved.
          </p>
          <div className="flex space-x-6 mt-3 md:mt-0">
            <Link to="/privacy" className="text-gray-500 hover:text-gray-800 text-sm transition-colors">
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-gray-500 hover:text-gray-800 text-sm transition-colors">
              Terms of Service
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
