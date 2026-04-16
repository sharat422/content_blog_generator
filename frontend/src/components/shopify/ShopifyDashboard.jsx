// src/components/shopify/ShopifyDashboard.jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { Package, RefreshCw, Layers, CheckCircle, Clock } from "lucide-react";
import ProductBrowser from "./ProductBrowser";
import SplitPaneEditor from "./SplitPaneEditor";
import BulkQueue from "./BulkQueue";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function ShopifyDashboard({ shopDomain, onDisconnect }) {
    const { getToken } = useAuth();
    const [view, setView] = useState("browser"); // browser, editor, bulk
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [selectedForBulk, setSelectedForBulk] = useState([]);

    const fetchProducts = async () => {
        setLoading(true);
        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/api/shopify/products?shop=${shopDomain}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (!res.ok) throw new Error("Failed to fetch products");
            const data = await res.json();
            setProducts(data.products || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, [shopDomain]);

    // Handle single edit
    const handleEditProduct = (product) => {
        setSelectedProduct(product);
        setView("editor");
    };

    // Handle return to browser
    const handleBackToBrowser = (refresh = false) => {
        setView("browser");
        setSelectedProduct(null);
        if (refresh) fetchProducts();
    };

    // Handle Bulk Start
    const handleStartBulk = (selectedIds) => {
        const toGenerate = products.filter(p => selectedIds.includes(p.product_id));
        setSelectedForBulk(toGenerate);
        setView("bulk");
    };

    return (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden min-h-[600px] flex flex-col">
            {/* Header */}
            <div className="border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between bg-slate-50 dark:bg-slate-900/50">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400 rounded-lg">
                        <Package size={20} />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                            {shopDomain}
                            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 font-medium">Connected</span>
                        </h2>
                        <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                            <Layers size={12} /> {products.length} Products synced
                        </p>
                    </div>
                </div>
                
                <div className="flex items-center gap-3">
                    <button 
                        onClick={fetchProducts} 
                        disabled={loading}
                        className="p-2 text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 transition"
                        title="Force Sync"
                    >
                        <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
                    </button>
                    <button 
                        onClick={onDisconnect}
                        className="text-xs font-semibold text-red-600 dark:text-red-400 hover:underline"
                    >
                        Disconnect
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col relative bg-slate-50 dark:bg-slate-950">
                {view === "browser" && (
                    <ProductBrowser 
                        products={products} 
                        loading={loading} 
                        error={error}
                        onEditProduct={handleEditProduct}
                        onStartBulk={handleStartBulk}
                    />
                )}
                
                {view === "editor" && selectedProduct && (
                    <SplitPaneEditor 
                        product={selectedProduct} 
                        shopDomain={shopDomain}
                        onBack={() => handleBackToBrowser()}
                        onSaved={() => handleBackToBrowser(true)}
                    />
                )}
                
                {view === "bulk" && (
                    <BulkQueue 
                        items={selectedForBulk}
                        shopDomain={shopDomain}
                        onBack={() => { setView("browser"); setSelectedForBulk([]); }}
                        onComplete={() => handleBackToBrowser(true)}
                    />
                )}
            </div>
        </div>
    );
}
