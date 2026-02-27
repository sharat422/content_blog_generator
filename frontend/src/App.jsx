import React from "react";
import { Routes, Route } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { useAuth } from "./context/AuthContext"; // ✅ import from your AuthContext
import ScrollToTopButton from "./components/ui/ScrollToTopButton";
import TwinPage from "./pages/TwinPage";

// UI kit
import Navbar from "./components/ui/Navbar";

// Pages
import HomePage from "./pages/HomePage";
import PricingPage from "./pages/PricingPage";
import FeaturesPage from "./pages/FeaturesPage";
import TermsPage from "./pages/TermsOfService";
import PrivacyPage from "./pages/PrivacyPolicy";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import VideoGeneratorPage from "./pages/VideoGeneratorPage";
import EcommercePage from "./pages/EcommercePage";
import ProtectedRoute from "./components/ProtectedRoute";
import AccountBillingPage from "./pages/AccountBillingPage";
import UpdatePassword from "./pages/UpdatePassword"


export default function App() {
  const { user } = useAuth(); // ✅ user comes from AuthProvider
  //window.supabase = supabase;
  return (
    <HelmetProvider>
      <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950">
        {/* ✅ Navbar can now show login/logout based on user */}
        <Navbar user={user} />

        <Routes>
          {/* ✅ HomePage always loads, we just pass user */}
          <Route path="/" element={<HomePage user={user} />} />
          <Route path="/" element={<HomePage user={user} />} />
          <Route path="/twin" element={<ProtectedRoute><TwinPage /></ProtectedRoute>} />

          {/* Public routes */}
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/videos" element={<VideoGeneratorPage />} />
          <Route path="/ecommerce" element={<EcommercePage />} />
          <Route path="/account" element={<ProtectedRoute><AccountBillingPage /></ProtectedRoute>} />
          <Route path="/update-password" element={<UpdatePassword />} />
          {/* Auth routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
        </Routes>
        <ScrollToTopButton />
      </div>
    </HelmetProvider>
  );
}
