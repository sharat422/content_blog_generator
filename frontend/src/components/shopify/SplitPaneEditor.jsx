// src/components/shopify/SplitPaneEditor.jsx
import React, { useState } from "react";
import { ArrowLeft, Send, Sparkles, AlertCircle, Maximize2, Tag as TagIcon, Layout } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function SplitPaneEditor({ product, shopDomain, onBack, onSaved }) {
    const { getToken } = useAuth();
    
    // Original Shopify Data
    const originalDesc = product.description || "No description currently exists.";
    const originalTags = product.tags || "None";
    
    // Generation State
    const [generating, setGenerating] = useState(false);
    const [publishLoading, setPublishLoading] = useState(false);
    const [error, setError] = useState("");
    
    // Editor State
    const [editorHtml, setEditorHtml] = useState(originalDesc);
    const [metaTitle, setMetaTitle] = useState(product.title);
    const [metaDesc, setMetaDesc] = useState("");

    const handleGenerate = async () => {
        setGenerating(true);
        setError("");
        
        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/api/ecommerce/generate`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    product_name: product.title,
                    product_category: product.product_type,
                    key_features: product.tags,
                    pain_points: "Address common objections for this category automatically.",
                    target_audience: "Online shoppers",
                    platform: "shopify",
                    content_type: "product_description", 
                    tone: "professional",
                }),
            });

            if (!res.ok) {
                const data = await res.json().catch(()=>({}));
                throw new Error(data.detail || "Generation failed");
            }

            const data = await res.json();
            
            // Format output as HTML for the rich text editor
            const formattedHtml = `
                <h2>${data.title || product.title}</h2>
                <p>${data.body}</p>
                ${data.bullet_points ? `<ul>${data.bullet_points.map(b => `<li>${b}</li>`).join('')}</ul>` : ""}
            `;
            
            setEditorHtml(formattedHtml);
            if(data.meta_title) setMetaTitle(data.meta_title);
            if(data.meta_description) setMetaDesc(data.meta_description);

        } catch (err) {
            setError(err.message);
        } finally {
            setGenerating(false);
        }
    };

    const handlePublish = async () => {
        setPublishLoading(true);
        setError("");
        
        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/api/shopify/publish-product`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    shop_domain: shopDomain,
                    product_id: product.product_id,
                    description_html: editorHtml,
                    meta_title: metaTitle,
                    meta_description: metaDesc
                }),
            });

            if (!res.ok) {
                const data = await res.json().catch(()=>({}));
                throw new Error(data.detail || "Failed to publish to Shopify");
            }
            
            // Update internal status conceptually
            onSaved();
            
        } catch (err) {
            setError(err.message);
            setPublishLoading(false); // only toggle if failed so we don't flash before unmount
        } 
    };

    return (
        <div className="flex flex-col h-full absolute inset-0 bg-slate-50 dark:bg-slate-950">
            {/* Topbar */}
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between z-10">
                <div className="flex items-center gap-4">
                    <button 
                        onClick={onBack}
                        className="p-2 -ml-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition"
                    >
                        <ArrowLeft size={20}/>
                    </button>
                    <div>
                        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 leading-tight">{product.title}</h2>
                        <div className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-0.5">{product.product_id?.replace('gid://shopify/Product/', '#')}</div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button 
                        onClick={handleGenerate}
                        disabled={generating}
                        className="px-4 py-2 border border-slate-200 dark:border-slate-700 hover:border-indigo-500 bg-white dark:bg-slate-800 rounded-lg text-sm font-bold shadow-sm transition flex items-center gap-2 group disabled:opacity-50"
                    >
                        {generating ? (
                           <svg className="animate-spin h-4 w-4 text-indigo-500" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                            </svg>
                        ) : (
                            <Sparkles size={16} className="text-indigo-500 group-hover:scale-110 transition-transform"/>
                        )}
                        {generating ? "Generating..." : "Generate AI Content"}
                    </button>

                    <button 
                        onClick={handlePublish}
                        disabled={publishLoading}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold shadow-sm transition flex items-center gap-2 disabled:opacity-50"
                    >
                        {publishLoading ? (
                             <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                            </svg>
                        ) : (
                            <Send size={14}/>
                        )}
                        Publish to Shopify
                    </button>
                </div>
            </div>

            {error && (
                <div className="m-4 p-3 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm font-medium rounded-xl flex items-center gap-2 border border-red-200 dark:border-red-800">
                    <AlertCircle size={16} /> {error}
                </div>
            )}

            {/* Split View */}
            <div className="flex-1 flex overflow-hidden">
                {/* LEFT PANE: Shopify Context */}
                <div className="w-1/3 border-r border-slate-200 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/30 p-6 overflow-y-auto custom-scrollbar flex flex-col gap-6">
                    <div>
                        <div className="flex justify-between items-center mb-3">
                            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 flex items-center gap-2"><Layout size={14}/> Original Context</h3>
                            <a href={`https://${shopDomain}/admin/products/${product.product_id?.split('/').pop()}`} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-indigo-500 transition">
                                <Maximize2 size={14}/>
                            </a>
                        </div>
                        
                        {product.image_url && (
                            <img src={product.image_url} alt="Product" className="w-full h-48 object-cover rounded-xl border border-slate-200 dark:border-slate-800 mb-4 shadow-sm" />
                        )}
                        
                        <div className="space-y-4">
                            <div>
                                <h4 className="text-xs font-semibold text-slate-500 mb-1">Tags</h4>
                                <div className="flex flex-wrap gap-1">
                                    {originalTags.split(',').map((t, i) => (
                                        <span key={i} className="inline-flex px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-xs font-medium text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                            <TagIcon size={10} className="mr-1 inline opacity-50"/>
                                            {t.trim() || 'none'}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            
                            <div>
                                <h4 className="text-xs font-semibold text-slate-500 mb-1">Price</h4>
                                <div className="text-sm font-medium text-slate-800 dark:text-slate-200">${product.price || '0.00'}</div>
                            </div>

                            <div>
                                <h4 className="text-xs font-semibold text-slate-500 mb-2">Original Description HTML</h4>
                                <div dangerouslySetInnerHTML={{ __html: originalDesc }} className="p-4 bg-slate-100 dark:bg-slate-800/50 rounded-xl text-sm prose prose-sm dark:prose-invert max-w-none opacity-70 border border-slate-200 dark:border-slate-700 custom-scrollbar max-h-96 overflow-y-auto" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* RIGHT PANE: Output Editor */}
                <div className="flex-1 bg-white dark:bg-slate-900 overflow-y-auto custom-scrollbar p-6">
                    <div className="max-w-3xl mx-auto space-y-6">
                        
                        {/* SEO Fields */}
                        <div className="grid grid-cols-2 gap-4">
                             <div>
                                <div className="flex justify-between items-center mb-1">
                                    <label className="text-xs font-bold text-slate-600 dark:text-slate-300">SEO Meta Title</label>
                                    <span className={`text-xs font-medium ${metaTitle.length > 60 ? 'text-red-500' : 'text-slate-400'}`}>
                                        {metaTitle.length}/60
                                    </span>
                                </div>
                                <input 
                                    type="text" 
                                    value={metaTitle}
                                    onChange={(e) => setMetaTitle(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-slate-900 transition font-medium"
                                />
                             </div>
                             <div>
                                <div className="flex justify-between items-center mb-1">
                                    <label className="text-xs font-bold text-slate-600 dark:text-slate-300">SEO Meta Description</label>
                                    <span className={`text-xs font-medium ${metaDesc.length > 160 ? 'text-red-500' : 'text-slate-400'}`}>
                                        {metaDesc.length}/160
                                    </span>
                                </div>
                                <textarea 
                                    rows={2}
                                    value={metaDesc}
                                    onChange={(e) => setMetaDesc(e.target.value)}
                                    className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-slate-900 transition leading-snug resize-none"
                                />
                             </div>
                        </div>

                        {/* Rich Text Area */}
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <label className="text-sm font-bold text-slate-800 dark:text-slate-200">Description HTML View</label>
                                <span className="text-xs px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-400 rounded font-medium">Synced to Shopify</span>
                            </div>
                            
                            <div className="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 transition shadow-sm">
                                {/* Basic Stub for toolbar */}
                                <div className="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-3 py-2 flex items-center gap-2">
                                   <div className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Editor Source</div>
                                </div>
                                <textarea 
                                    value={editorHtml}
                                    onChange={(e) => setEditorHtml(e.target.value)}
                                    className="w-full min-h-[400px] p-4 text-sm font-mono leading-relaxed bg-white dark:bg-slate-900 border-none focus:outline-none focus:ring-0 resize-y text-slate-700 dark:text-slate-300"
                                    placeholder="<p>Stunning AI description goes here...</p>"
                                />
                            </div>
                        </div>
                        
                    </div>
                </div>
            </div>
        </div>
    );
}
