// src/components/shopify/ProductBrowser.jsx
import React, { useState } from "react";
import { Search, Filter, Edit3, Image as ImageIcon, Zap, CheckCircle2, ChevronRight, AlertCircle } from "lucide-react";

export default function ProductBrowser({ products, loading, error, onEditProduct, onStartBulk }) {
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all"); // all, missing, draft, published
    const [selectedIds, setSelectedIds] = useState([]);

    // Filter Logic
    const filteredProducts = products.filter(p => {
        const matchesSearch = p.title.toLowerCase().includes(searchTerm.toLowerCase());
        
        // Mocking statuses for UI - eventually derived from DB/Shopify tags
        const status = p.internal_status || "missing"; 
        const matchesStatus = statusFilter === "all" || status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });

    const handleSelectAll = (e) => {
        if (e.target.checked) {
            setSelectedIds(filteredProducts.map(p => p.product_id));
        } else {
            setSelectedIds([]);
        }
    };

    const handleSelectRow = (id) => {
        setSelectedIds(prev => 
            prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
        );
    };

    // Render Status Badge
    const renderStatusBadge = (product) => {
        // Ideally mapped to true DB states
        const status = product.internal_status || "missing";
        
        if (status === "published") {
            return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400"><CheckCircle2 size={12}/> Published</span>;
        }
        if (status === "draft") {
            return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-400"><Edit3 size={12}/> Generated Draft</span>;
        }
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"><AlertCircle size={12}/> Needs Description</span>;
    };

    if (loading) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center min-h-[400px]">
                <svg className="animate-spin h-8 w-8 text-indigo-500 mb-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                <div className="text-slate-500 dark:text-slate-400 text-sm font-medium">Syncing catalog from Shopify...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center text-red-600 dark:text-red-400">
               <AlertCircle size={32} className="mb-2 opacity-50"/>
               <h3 className="font-bold">Error Loading Products</h3>
               <p className="text-sm opacity-80 mt-1">{error}</p>
            </div>
        );
    }

    if (!products.length) {
        return (
             <div className="flex-1 flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
                <div className="p-4 bg-slate-100 dark:bg-slate-800 rounded-full mb-4">
                    <Package size={32} className="text-slate-400 dark:text-slate-500"/>
                </div>
                <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">No products found</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-sm">We couldn't detect any products on your Shopify store. Please ensure you have products listed.</p>
             </div>
        );
    }

    return (
        <div className="flex flex-col h-full absolute inset-0">
            {/* Toolbar */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-900 sticky top-0 z-10">
                <div className="flex items-center gap-4 flex-1">
                    <div className="relative max-w-sm w-full">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input 
                            type="text" 
                            placeholder="Search products..." 
                            value={searchTerm}
                            onChange={e => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                        />
                    </div>
                    
                    <div className="flex items-center gap-2">
                        <Filter size={16} className="text-slate-400"/>
                        <select 
                            value={statusFilter}
                            onChange={e => setStatusFilter(e.target.value)}
                            className="bg-transparent border-none text-sm font-medium text-slate-700 dark:text-slate-300 focus:outline-none cursor-pointer"
                        >
                            <option value="all">All Products</option>
                            <option value="missing">Needs Description</option>
                            <option value="draft">Generated Drafts</option>
                            <option value="published">Published</option>
                        </select>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {selectedIds.length > 0 && (
                        <button 
                            onClick={() => onStartBulk(selectedIds)}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 shadow-sm transition"
                        >
                            <Zap size={14} className="fill-current"/> 
                            Generate Selected ({selectedIds.length})
                        </button>
                    )}
                </div>
            </div>

            {/* Table */}
            <div className="flex-1 overflow-auto custom-scrollbar">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
                        <tr>
                            <th className="p-4 w-12 text-center">
                                <input 
                                    type="checkbox" 
                                    checked={filteredProducts.length > 0 && selectedIds.length === filteredProducts.length}
                                    onChange={handleSelectAll}
                                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
                                />
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Product</th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                        {filteredProducts.map(product => (
                            <tr key={product.product_id} className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition group cursor-pointer bg-white dark:bg-transparent" onClick={() => handleSelectRow(product.product_id)}>
                                <td className="p-4 text-center" onClick={e => e.stopPropagation()}>
                                     <input 
                                        type="checkbox" 
                                        checked={selectedIds.includes(product.product_id)}
                                        onChange={() => handleSelectRow(product.product_id)}
                                        className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4 cursor-pointer"
                                    />
                                </td>
                                <td className="p-4 flex items-center gap-4">
                                    <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-center shrink-0 overflow-hidden">
                                        {product.image_url ? (
                                            <img src={product.image_url} alt={product.title} className="w-full h-full object-cover"/>
                                        ) : (
                                            <ImageIcon size={20} className="text-slate-400 opacity-50"/>
                                        )}
                                    </div>
                                    <div>
                                        <div className="font-bold text-slate-900 dark:text-slate-100 text-sm">{product.title}</div>
                                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{product.product_type || "Uncategorized"}</div>
                                    </div>
                                </td>
                                <td className="p-4">
                                    {renderStatusBadge(product)}
                                </td>
                                <td className="p-4 text-right">
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); onEditProduct(product); }}
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-lg text-xs font-bold text-slate-700 dark:text-slate-300 shadow-sm transition opacity-0 group-hover:opacity-100"
                                    >
                                        <Edit3 size={14} /> Open Editor <ChevronRight size={14}/>
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filteredProducts.length === 0 && (
                     <div className="p-8 text-center text-slate-500 dark:text-slate-400 text-sm">
                        No products match your filters.
                    </div>
                )}
            </div>
        </div>
    );
}
