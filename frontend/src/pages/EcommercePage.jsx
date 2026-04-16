// src/pages/EcommercePage.jsx
// SEO-Optimized Ecommerce Content Generator for sellers

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Helmet } from "react-helmet-async";
import {
    Package,
    FileText,
    ShoppingCart,
    BookOpen,
    HelpCircle,
    Tag,
    Copy,
    Check,
    ChevronDown,
    ChevronUp,
    Sparkles,
    TrendingUp,
    AlertCircle,
    Code
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────

const CONTENT_TYPES = [
    {
        id: "product_description",
        label: "Product Description",
        icon: Package,
        color: "indigo",
        desc: "SEO product copy for Shopify, WooCommerce & Google Shopping",
        cost: 5,
    },
    {
        id: "blog_post",
        label: "Blog Post",
        icon: FileText,
        color: "emerald",
        desc: "Keyword-targeted blog posts that drive organic traffic",
        cost: 5,
    },
    {
        id: "marketplace_listing",
        label: "Marketplace Listing",
        icon: ShoppingCart,
        color: "orange",
        desc: "Amazon / eBay / Etsy listing with title, bullets & description",
        cost: 6,
    },
    {
        id: "category_page",
        label: "Category Page",
        icon: BookOpen,
        color: "purple",
        desc: "SEO collection/category page content for your store",
        cost: 4,
    },
    {
        id: "product_faq",
        label: "Product FAQ",
        icon: HelpCircle,
        color: "pink",
        desc: "Structured FAQs for featured snippets & buyer confidence",
        cost: 3,
    },
    {
        id: "meta_tags",
        label: "Meta Tags",
        icon: Tag,
        color: "teal",
        desc: "Title, meta description, Open Graph & Twitter Card tags",
        cost: 2,
    },
    {
        id: "full_campaign",
        label: "Full Campaign",
        icon: Sparkles,
        color: "indigo",
        desc: "All-in-one generator: description, social media captions, and ad copy aligned to your brand voice",
        cost: 10,
    },
];

const PLATFORMS = [
    { id: "shopify", label: "Shopify / WooCommerce" },
    { id: "amazon", label: "Amazon" },
    { id: "ebay", label: "eBay" },
    { id: "etsy", label: "Etsy" },
    { id: "general", label: "General / Google" },
];

const TONES = [
    { id: "professional", label: "Professional" },
    { id: "friendly", label: "Friendly" },
    { id: "persuasive", label: "Persuasive" },
    { id: "luxury", label: "Luxury / Premium" },
    { id: "playful", label: "Playful" },
];

const COLOR_CLASSES = {
    indigo: { ring: "ring-indigo-500", bg: "bg-indigo-50 dark:bg-indigo-950/40", icon: "text-indigo-600 dark:text-indigo-400", badge: "bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300" },
    emerald: { ring: "ring-emerald-500", bg: "bg-emerald-50 dark:bg-emerald-950/40", icon: "text-emerald-600 dark:text-emerald-400", badge: "bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300" },
    orange: { ring: "ring-orange-500", bg: "bg-orange-50 dark:bg-orange-950/40", icon: "text-orange-600 dark:text-orange-400", badge: "bg-orange-100 dark:bg-orange-900 text-orange-700 dark:text-orange-300" },
    purple: { ring: "ring-purple-500", bg: "bg-purple-50 dark:bg-purple-950/40", icon: "text-purple-600 dark:text-purple-400", badge: "bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300" },
    pink: { ring: "ring-pink-500", bg: "bg-pink-50 dark:bg-pink-950/40", icon: "text-pink-600 dark:text-pink-400", badge: "bg-pink-100 dark:bg-pink-900 text-pink-700 dark:text-pink-300" },
    teal: { ring: "ring-teal-500", bg: "bg-teal-50 dark:bg-teal-950/40", icon: "text-teal-600 dark:text-teal-400", badge: "bg-teal-100 dark:bg-teal-900 text-teal-700 dark:text-teal-300" },
};

// ─────────────────────────────────────────────────────────────────
// CopyButton Component
// ─────────────────────────────────────────────────────────────────
function CopyButton({ text }) {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => {
        navigator.clipboard.writeText(text).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };
    return (
        <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
        >
            {copied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
            {copied ? "Copied!" : "Copy"}
        </button>
    );
}

// ─────────────────────────────────────────────────────────────────
// SEO Score Gauge
// ─────────────────────────────────────────────────────────────────
function SeoScoreGauge({ score }) {
    const color = score >= 80 ? "text-emerald-500" : score >= 60 ? "text-yellow-500" : "text-red-500";
    const label = score >= 80 ? "Excellent" : score >= 60 ? "Good" : "Needs Work";
    return (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
            <div className={`text-4xl font-black ${color}`}>{score}</div>
            <div>
                <div className="text-sm font-semibold text-slate-700 dark:text-slate-200">SEO Score</div>
                <div className={`text-xs font-medium ${color}`}>{label}</div>
            </div>
            <TrendingUp className={`ml-auto h-8 w-8 ${color}`} />
        </div>
    );
}

// ─────────────────────────────────────────────────────────────────
// OutputSection Component
// ─────────────────────────────────────────────────────────────────
function OutputSection({ label, value, isCode = false, showCopy = true }) {
    const [open, setOpen] = useState(true);
    if (!value || (Array.isArray(value) && value.length === 0)) return null;

    const displayValue = Array.isArray(value)
        ? typeof value[0] === "object"
            ? null // handled separately
            : value.join(", ")
        : String(value);

    return (
        <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center justify-between w-full px-4 py-3 text-sm font-semibold text-slate-700 dark:text-slate-200 bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
                <span>{label}</span>
                <div className="flex items-center gap-2">
                    {showCopy && displayValue && <CopyButton text={displayValue} />}
                    {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </div>
            </button>
            {open && displayValue && (
                <div className={`px-4 py-3 text-sm text-slate-700 dark:text-slate-300 ${isCode ? "font-mono bg-slate-950 text-emerald-300" : "bg-white dark:bg-slate-950"}`}>
                    {displayValue}
                </div>
            )}
        </div>
    );
}

// ─────────────────────────────────────────────────────────────────
// ShopifyConnectModal Component
// ─────────────────────────────────────────────────────────────────
function ShopifyConnectModal({ isOpen, onClose, getToken }) {
    const [shopUrl, setShopUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [modalError, setModalError] = useState("");

    const handleConnect = async () => {
        if (!shopUrl.trim()) {
            setModalError("Please enter a valid Shopify store URL.");
            return;
        }

        setLoading(true);
        setModalError("");

        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/api/shopify/auth?shop=${encodeURIComponent(shopUrl)}`, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                throw new Error(data.detail || "Failed to initiate connection. Please check the URL.");
            }

            const data = await res.json();
            if (data.url) {
                window.location.href = data.url;
            } else {
                throw new Error("No redirect URL returned.");
            }
        } catch (err) {
            setModalError(err.message);
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-2xl border border-slate-200 dark:border-slate-800 relative"
            >
                <div className="text-center mb-6">
                    <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center mx-auto mb-3">
                        <ShoppingCart size={24} />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">Connect Shopify</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        Enter your Shopify store URL to connect your account.
                    </p>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                            Shopify Store URL
                        </label>
                        <input
                            type="text"
                            value={shopUrl}
                            onChange={(e) => setShopUrl(e.target.value)}
                            placeholder="e.g. my-store.myshopify.com"
                            className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                        />
                    </div>

                    {modalError && (
                        <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-700 dark:text-red-400">
                            <AlertCircle size={14} className="mt-0.5 shrink-0" />
                            {modalError}
                        </div>
                    )}

                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-semibold text-sm transition"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleConnect}
                            disabled={loading || !shopUrl.trim()}
                            className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-semibold text-sm transition flex items-center justify-center gap-2"
                        >
                            {loading ? "Connecting..." : "Connect Store"}
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
import ShopifyDashboard from "../components/shopify/ShopifyDashboard";

// ─────────────────────────────────────────────────────────────────
// Main Page wrapper
// ─────────────────────────────────────────────────────────────────
export default function EcommercePage() {
    const { user, getToken } = useAuth();
    const [connectedShop, setConnectedShop] = useState(null);
    const [checkingShop, setCheckingShop] = useState(true);

    const checkShopifyConnection = async () => {
        if (!user) {
            setCheckingShop(false);
            return;
        }
        
        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/api/shopify/status`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            
            if (res.ok) {
                const data = await res.json();
                if (data.connected && data.shop_domain) {
                    setConnectedShop(data.shop_domain);
                } else {
                    setConnectedShop(null);
                }
            }
        } catch (e) {
            console.error("Failed to check shopify status", e);
        } finally {
            setCheckingShop(false);
        }
    };

    useEffect(() => {
        checkShopifyConnection();
    }, [user]);

    if (checkingShop) {
        return <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center"><div className="animate-pulse bg-slate-200 dark:bg-slate-800 h-8 w-32 rounded"></div></div>;
    }

    if (connectedShop) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pt-20 pb-16 px-4">
                <div className="max-w-[1400px] mx-auto">
                    <ShopifyDashboard 
                        shopDomain={connectedShop} 
                        onDisconnect={() => setConnectedShop(null)} 
                    />
                </div>
            </div>
        );
    }
    
    return <EcommercePageFallback onConnected={() => checkShopifyConnection()} />;
}

// ─────────────────────────────────────────────────────────────────
// Original Generator Form (Fallback)
// ─────────────────────────────────────────────────────────────────
function EcommercePageFallback({ onConnected }) {
    const { user, getToken } = useAuth();

    // Form state
    const [contentType, setContentType] = useState("product_description");
    const [productName, setProductName] = useState("");
    const [productCategory, setProductCategory] = useState("");
    const [keyFeatures, setKeyFeatures] = useState("");
    const [painPoints, setPainPoints] = useState("");
    const [targetAudience, setTargetAudience] = useState("online shoppers");
    const [platform, setPlatform] = useState("shopify");
    const [tone, setTone] = useState("professional");
    
    const [showShopifyModal, setShowShopifyModal] = useState(false);

    // Result state
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const selectedType = CONTENT_TYPES.find((t) => t.id === contentType);

    const handleGenerate = async () => {
        if (!productName.trim()) {
            setError("Please enter a product or page name.");
            return;
        }
        if (!user) {
            setError("Please log in to generate content.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        const token = await getToken();
        if (!token) {
            setError("Session expired. Please log in again.");
            setLoading(false);
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/ecommerce/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    product_name: productName,
                    product_category: productCategory || "General",
                    key_features: keyFeatures,
                    pain_points: painPoints,
                    target_audience: targetAudience,
                    platform,
                    content_type: contentType,
                    tone,
                }),
            });

            if (res.status === 401) throw new Error("Authentication failed. Please log in again.");
            if (res.status === 402) throw new Error("Not enough credits. Please upgrade your plan.");
            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                throw new Error(data.detail || `Server error (${res.status})`);
            }

            const data = await res.json();
            setResult(data);
        } catch (err) {
            console.error("Ecommerce generate error:", err);
            setError(err.message || "Content generation failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Helmet>
                <title>Ecommerce SEO Content Generator | WriteSwift</title>
                <meta
                    name="description"
                    content="Generate SEO-optimized product descriptions, Amazon listings, blog posts, category pages, meta tags and FAQs for your ecommerce store instantly with AI."
                />
            </Helmet>

            <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pt-20 pb-16 px-4">
                <div className="max-w-6xl mx-auto space-y-10">

                    {/* ── Header ── */}
                    <motion.div
                        className="text-center"
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4 }}
                    >
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 text-xs font-semibold mb-4">
                            <Sparkles size={12} />
                            AI-Powered · SEO-Optimized · Ecommerce-Ready
                        </div>
                        <h1 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-slate-100 leading-tight">
                            Ecommerce Content Generator
                        </h1>
                        <p className="mt-3 text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                            Generate product descriptions, Amazon listings, blog posts, meta tags & FAQs
                            — all SEO-optimized and ready for your store.
                        </p>
                    </motion.div>

                    {/* ── Content Type Selector ── */}
                    <div>
                        <h2 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
                            Choose Content Type
                        </h2>
                        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                            {CONTENT_TYPES.map((type) => {
                                const Icon = type.icon;
                                const colors = COLOR_CLASSES[type.color];
                                const isActive = contentType === type.id;
                                return (
                                    <button
                                        key={type.id}
                                        onClick={() => setContentType(type.id)}
                                        className={`relative p-4 rounded-2xl border-2 text-left transition-all ${isActive
                                                ? `border-current ring-2 ${colors.ring} ${colors.bg}`
                                                : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700"
                                            }`}
                                    >
                                        <Icon className={`h-6 w-6 mb-2 ${isActive ? colors.icon : "text-slate-400"}`} />
                                        <div className={`text-xs font-semibold ${isActive ? "text-slate-900 dark:text-slate-100" : "text-slate-600 dark:text-slate-400"}`}>
                                            {type.label}
                                        </div>
                                        <div className={`mt-1 text-xs px-1.5 py-0.5 rounded-full inline-block ${colors.badge}`}>
                                            {type.cost} cr
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                        {selectedType && (
                            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                                {selectedType.desc}
                            </p>
                        )}
                    </div>

                    {/* ── Main Form + Results Grid ── */}
                    <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">

                        {/* Form */}
                        <div className="lg:col-span-2 space-y-5">
                            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-5 shadow-sm">
                                <h2 className="text-base font-bold text-slate-800 dark:text-slate-200">
                                    Product / Page Details
                                </h2>

                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Product / Page Name <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        id="ecommerce-product-name"
                                        type="text"
                                        value={productName}
                                        onChange={(e) => setProductName(e.target.value)}
                                        placeholder='e.g. "Wireless Noise Cancelling Headphones"'
                                        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Category
                                    </label>
                                    <input
                                        id="ecommerce-category"
                                        type="text"
                                        value={productCategory}
                                        onChange={(e) => setProductCategory(e.target.value)}
                                        placeholder='e.g. "Electronics", "Home & Garden"'
                                        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Key Features / Details
                                    </label>
                                    <textarea
                                        id="ecommerce-features"
                                        rows={3}
                                        value={keyFeatures}
                                        onChange={(e) => setKeyFeatures(e.target.value)}
                                        placeholder='e.g. "40hr battery, active noise cancelling, foldable, USB-C charging, built-in mic"'
                                        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition resize-none"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Customer Pain Points To Target
                                    </label>
                                    <textarea
                                        id="ecommerce-painpoints"
                                        rows={2}
                                        value={painPoints}
                                        onChange={(e) => setPainPoints(e.target.value)}
                                        placeholder='e.g. "Headphones are uncomfortable for long hours, battery dies quickly on flights"'
                                        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition resize-none"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Target Audience
                                    </label>
                                    <input
                                        id="ecommerce-audience"
                                        type="text"
                                        value={targetAudience}
                                        onChange={(e) => setTargetAudience(e.target.value)}
                                        placeholder='e.g. "Remote workers aged 25-45"'
                                        className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                                    />
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Platform
                                    </label>
                                    <div className="flex items-center gap-3">
                                        <select
                                            id="ecommerce-platform"
                                            value={platform}
                                            onChange={(e) => setPlatform(e.target.value)}
                                            className="flex-1 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                                        >
                                            {PLATFORMS.map((p) => (
                                                <option key={p.id} value={p.id}>{p.label}</option>
                                            ))}
                                        </select>
                                        {platform === "shopify" && user && (
                                            <button 
                                                onClick={() => setShowShopifyModal(true)}
                                                className="px-4 py-2 shrink-0 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-200 dark:hover:bg-emerald-800 rounded-lg text-sm font-semibold transition"
                                            >
                                                Connect Shopify
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide">
                                        Tone
                                    </label>
                                    <div className="flex flex-wrap gap-2">
                                        {TONES.map((t) => (
                                            <button
                                                key={t.id}
                                                onClick={() => setTone(t.id)}
                                                className={`px-3 py-1 rounded-full text-xs font-medium border transition ${tone === t.id
                                                        ? "bg-indigo-600 text-white border-indigo-600"
                                                        : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700 hover:border-indigo-400"
                                                    }`}
                                            >
                                                {t.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {error && (
                                    <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-700 dark:text-red-400">
                                        <AlertCircle size={14} className="mt-0.5 shrink-0" />
                                        {error}
                                    </div>
                                )}

                                <button
                                    id="ecommerce-generate-btn"
                                    onClick={handleGenerate}
                                    disabled={loading || !user}
                                    className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                                            </svg>
                                            Generating SEO Content...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles size={16} />
                                            Generate {selectedType?.label || "Content"} · {selectedType?.cost || 5} Credits
                                        </>
                                    )}
                                </button>

                                {!user && (
                                    <p className="text-xs text-center text-slate-500 dark:text-slate-400">
                                        <a href="/login" className="text-indigo-500 hover:underline">Log in</a> to start generating ecommerce content.
                                    </p>
                                )}
                            </div>

                            {/* Pro tips */}
                            <div className="bg-indigo-50 dark:bg-indigo-950/30 rounded-2xl border border-indigo-100 dark:border-indigo-900 p-4 space-y-2">
                                <div className="text-xs font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-wide">SEO Tips</div>
                                <ul className="space-y-1 text-xs text-indigo-700 dark:text-indigo-300">
                                    <li>✓ Include your main keyword in Key Features</li>
                                    <li>✓ Frame features as solutions via the <b>Customer Pain Points</b> field to skyrocket conversion</li>
                                    <li>✓ Be specific about your target audience</li>
                                    <li>✓ List exact product specs for better keyword targeting</li>
                                    <li>✓ Use "Persuasive" tone for Amazon listing conversions</li>
                                </ul>
                            </div>
                        </div>

                        {/* Results */}
                        <div className="lg:col-span-3">
                            <AnimatePresence mode="wait">
                                {!result && !loading && (
                                    <motion.div
                                        key="empty"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="flex flex-col items-center justify-center h-full min-h-[400px] rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-800 text-center p-8"
                                    >
                                        <div className="text-5xl mb-4">✍️</div>
                                        <p className="text-slate-500 dark:text-slate-400 font-medium">
                                            Fill in the details and click <strong>Generate</strong>
                                        </p>
                                        <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">
                                            Your SEO-optimized content will appear here
                                        </p>
                                    </motion.div>
                                )}

                                {loading && (
                                    <motion.div
                                        key="loading"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="flex flex-col items-center justify-center h-full min-h-[400px] rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900"
                                    >
                                        <svg className="animate-spin h-10 w-10 text-indigo-500 mb-4" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                                        </svg>
                                        <p className="text-slate-600 dark:text-slate-400 font-medium">Crafting your SEO content...</p>
                                        <p className="text-sm text-slate-400 dark:text-slate-500 mt-1">This usually takes 15-30 seconds</p>
                                    </motion.div>
                                )}

                                {result && !loading && (
                                    <motion.div
                                        key="result"
                                        initial={{ opacity: 0, y: 12 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.4 }}
                                        className="space-y-4"
                                    >
                                        {/* SEO Score */}
                                        <SeoScoreGauge score={result.seo_score || 0} />

                                        {/* Meta section */}
                                        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 space-y-3 shadow-sm">
                                            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
                                                <Tag size={14} /> SEO Meta Tags
                                            </h3>
                                            <OutputSection label="Meta Title" value={result.meta_title} />
                                            <OutputSection label="Meta Description" value={result.meta_description} />
                                            <OutputSection label="Focus Keyword" value={result.focus_keyword} />
                                            <OutputSection
                                                label="Secondary Keywords"
                                                value={result.secondary_keywords}
                                            />
                                            {result.og_title && <OutputSection label="Open Graph Title" value={result.og_title} />}
                                            {result.og_description && <OutputSection label="Open Graph Description" value={result.og_description} />}
                                            {result.twitter_title && <OutputSection label="Twitter Title" value={result.twitter_title} />}
                                            {result.twitter_description && <OutputSection label="Twitter Description" value={result.twitter_description} />}
                                        </div>

                                        {/* Main content */}
                                        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 space-y-3 shadow-sm">
                                            <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
                                                <FileText size={14} /> Content
                                            </h3>
                                            <OutputSection label="Page Title (H1)" value={result.title} />
                                            
                                            {/* A/B Test Hook Titles */}
                                            {result.ab_test_titles && result.ab_test_titles.length > 0 && (
                                                <div className="border border-indigo-200 dark:border-indigo-800 rounded-xl overflow-hidden shadow-sm">
                                                    <div className="flex items-center justify-between px-4 py-3 bg-indigo-50 dark:bg-indigo-900/40">
                                                        <span className="text-sm font-bold text-indigo-700 dark:text-indigo-300 flex items-center gap-2">
                                                            <Sparkles size={14} /> A/B Test Title Hooks
                                                        </span>
                                                        <CopyButton text={result.ab_test_titles.map((b, i) => `${i + 1}. ${b}`).join("\n")} />
                                                    </div>
                                                    <ul className="px-4 py-3 space-y-2 bg-white dark:bg-slate-950">
                                                        {result.ab_test_titles.map((title, i) => (
                                                            <li key={i} className="text-sm text-slate-700 dark:text-slate-300 flex gap-2">
                                                                <span className="text-indigo-500 font-bold shrink-0">{i + 1}.</span>
                                                                {title}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {/* Social Captions (Full Campaign Only) */}
                                            {result.social_captions && result.social_captions.length > 0 && (
                                                <div className="border border-sky-200 dark:border-sky-800 rounded-xl overflow-hidden shadow-sm">
                                                    <div className="flex items-center justify-between px-4 py-3 bg-sky-50 dark:bg-sky-900/40">
                                                        <span className="text-sm font-bold text-sky-700 dark:text-sky-300 flex items-center gap-2">
                                                            Brand Social Media Captions (Instagram/FB/X)
                                                        </span>
                                                        <CopyButton text={result.social_captions.join("\n\n---\n\n")} />
                                                    </div>
                                                    <ul className="px-4 py-3 space-y-4 bg-white dark:bg-slate-950">
                                                        {result.social_captions.map((caption, i) => (
                                                            <li key={i} className="text-sm text-slate-700 dark:text-slate-300 border-b border-slate-100 dark:border-slate-800 pb-3 last:border-0 last:pb-0">
                                                                {caption}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {/* Bullet points for marketplace listings */}
                                            {result.bullet_points && result.bullet_points.length > 0 && (
                                                <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
                                                    <div className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-slate-900">
                                                        <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Bullet Points</span>
                                                        <CopyButton text={result.bullet_points.map((b, i) => `• ${b}`).join("\n")} />
                                                    </div>
                                                    <ul className="px-4 py-3 space-y-2 bg-white dark:bg-slate-950">
                                                        {result.bullet_points.map((b, i) => (
                                                            <li key={i} className="text-sm text-slate-700 dark:text-slate-300 flex gap-2">
                                                                <span className="text-indigo-500 font-bold shrink-0">•</span>
                                                                {b}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            <OutputSection label="Body Copy" value={result.body} />
                                        </div>

                                        {/* FAQ */}
                                        {result.faq && result.faq.length > 0 && (
                                            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 space-y-3 shadow-sm">
                                                <h3 className="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
                                                    <HelpCircle size={14} /> FAQ (Schema-Ready)
                                                </h3>
                                                <div className="space-y-3">
                                                    {result.faq.map((item, i) => (
                                                        <div key={i} className="border border-slate-200 dark:border-slate-800 rounded-xl p-3">
                                                            <div className="flex items-start justify-between gap-2">
                                                                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                                                                    Q: {item.question}
                                                                </p>
                                                                <CopyButton text={`Q: ${item.question}\nA: ${item.answer}`} />
                                                            </div>
                                                            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                                                                A: {item.answer}
                                                            </p>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {/* Schema JSON-LD Section */}
                                        {result.schema_json_ld && (
                                            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-4 space-y-3 shadow-md mt-6">
                                                <div className="flex justify-between items-center mb-1">
                                                    <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                                                        <Code size={14} /> Raw Schema.org JSON-LD SEO Block
                                                    </h3>
                                                    <div className="text-xs px-2 py-0.5 rounded-full bg-emerald-900 text-emerald-300 font-mono">
                                                        {result.schema_type}
                                                    </div>
                                                </div>
                                                <p className="text-xs text-slate-400 mb-2">Paste this directly into the `&lt;head&gt;` of your Shopify template or standard webpage to enable instant SEO Rich Snippets in Google.</p>
                                                <div className="relative group">
                                                    <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <CopyButton text={result.schema_json_ld} />
                                                    </div>
                                                    <pre className="bg-black/50 p-4 rounded-xl text-xs font-mono text-emerald-300/90 overflow-x-auto whitespace-pre-wrap max-h-64 overflow-y-auto custom-scrollbar">
                                                        {result.schema_json_ld}
                                                    </pre>
                                                </div>
                                            </div>
                                        )}

                                        {/* Copy All Button */}
                                        <button
                                            onClick={() => {
                                                const all = [
                                                    result.title && `Title: ${result.title}`,
                                                    result.ab_test_titles?.length && `A/B Test Titles:\n${result.ab_test_titles.map(b => `• ${b}`).join("\n")}`,
                                                    result.meta_title && `Meta Title: ${result.meta_title}`,
                                                    result.meta_description && `Meta Description: ${result.meta_description}`,
                                                    result.focus_keyword && `Focus Keyword: ${result.focus_keyword}`,
                                                    result.secondary_keywords?.length && `Secondary Keywords: ${result.secondary_keywords.join(", ")}`,
                                                    result.bullet_points?.length && `\nBullet Points:\n${result.bullet_points.map(b => `• ${b}`).join("\n")}`,
                                                    result.body && `\nBody:\n${result.body}`,
                                                    result.social_captions?.length && `\nSocial Media Captions:\n${result.social_captions.join("\n\n")}`,
                                                    result.faq?.length && `\nFAQ:\n${result.faq.map(f => `Q: ${f.question}\nA: ${f.answer}`).join("\n\n")}`,
                                                    result.schema_json_ld && `\nSchema LD Block:\n${result.schema_json_ld}`
                                                ].filter(Boolean).join("\n");
                                                navigator.clipboard.writeText(all);
                                            }}
                                            className="w-full py-2.5 px-4 rounded-xl border border-slate-300 dark:border-slate-700 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center justify-center gap-2"
                                        >
                                            <Copy size={14} />
                                            Copy All Content
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                <ShopifyConnectModal 
                    key="shopify-modal"
                    isOpen={showShopifyModal} 
                    onClose={() => setShowShopifyModal(false)} 
                    getToken={getToken} 
                />
            </AnimatePresence>
        </>
    );
}
