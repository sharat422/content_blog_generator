// src/components/shopify/BulkQueue.jsx
import React, { useState } from "react";
import { ArrowLeft, Play, FastForward, Check, X, AlertCircle, Layers } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function BulkQueue({ items, shopDomain, onBack, onComplete }) {
    const { getToken } = useAuth();
    const [generating, setGenerating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [results, setResults] = useState({}); // { id: { title, desc, ... } }
    const [statuses, setStatuses] = useState({}); // { id: 'pending'|'approved'|'skipped' }
    const [publishing, setPublishing] = useState(false);
    const [error, setError] = useState("");

    const handleGenerateAll = async () => {
        setGenerating(true);
        setError("");
        
        try {
            const token = await getToken();
            
            // Sequential generation for simplicity in prototype, 
            // a true production app would queue these to a Celery worker via a single /bulk endpoint.
            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                
                try {
                    const res = await fetch(`${API_BASE}/api/ecommerce/generate`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
                        body: JSON.stringify({
                            product_name: item.title,
                            product_category: item.product_type,
                            key_features: item.tags,
                            platform: "shopify",
                            content_type: "product_description", 
                            tone: "professional",
                        }),
                    });

                    if (res.ok) {
                        const data = await res.json();
                        setResults(prev => ({
                            ...prev, 
                            [item.product_id]: data
                        }));
                    }
                } catch(e) {
                    console.error("Bulk generate item error", e);
                }
                
                setProgress(Math.round(((i + 1) / items.length) * 100));
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setGenerating(false);
        }
    };

    const handlePublishApproved = async () => {
        setPublishing(true);
        setError("");
        
        try {
             // In a real app we'd send the approved list to trigger_bulk_publish.
             // For this prototype, we simulate sending the batch.
             const approvedIds = Object.keys(statuses).filter(id => statuses[id] === 'approved');
             if (approvedIds.length === 0) throw new Error("No items approved for publishing.");

             console.log("Publishing approved items:", approvedIds);
             
             // Simulate network delay for the bulk job trigger
             await new Promise(resolve => setTimeout(resolve, 1500));
             
             onComplete();
             
        } catch (err) {
            setError(err.message);
            setPublishing(false);
        }
    };

    const setStatus = (id, status) => {
        setStatuses(prev => ({ ...prev, [id]: status }));
    };

    return (
        <div className="flex flex-col h-full absolute inset-0 bg-slate-50 dark:bg-slate-950">
             <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between z-10 sticky top-0">
                <div className="flex items-center gap-4">
                    <button onClick={onBack} disabled={generating || publishing} className="p-2 -ml-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition disabled:opacity-50">
                        <ArrowLeft size={20}/>
                    </button>
                    <div>
                        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                             <Layers size={18} className="text-indigo-500"/> Bulk Generation Queue
                        </h2>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{items.length} products selected</div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {Object.keys(results).length === 0 ? (
                        <button 
                            onClick={handleGenerateAll}
                            disabled={generating}
                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold shadow-sm transition flex items-center gap-2 disabled:opacity-50"
                        >
                            {generating ? <FastForward size={16} className="animate-pulse"/> : <Play size={16} className="fill-current"/>}
                            {generating ? `Generating... ${progress}%` : "Start Generation"}
                        </button>
                    ) : (
                        <button 
                            onClick={handlePublishApproved}
                            disabled={publishing || Object.values(statuses).filter(s => s === 'approved').length === 0}
                            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold shadow-sm transition flex items-center gap-2 disabled:opacity-50"
                        >
                            {publishing ? "Triggering Job..." : `Publish ${Object.values(statuses).filter(s => s === 'approved').length} Approved`}
                        </button>
                    )}
                </div>
            </div>

            {error && (
                <div className="m-4 p-3 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm font-medium rounded-xl flex items-center gap-2 border border-red-200 dark:border-red-800">
                    <AlertCircle size={16} /> {error}
                </div>
            )}

            <div className="flex-1 overflow-auto custom-scrollbar p-6 space-y-4">
                {items.map((item, i) => {
                    const result = results[item.product_id];
                    const status = statuses[item.product_id];
                    
                    return (
                        <div key={item.product_id} className={`bg-white dark:bg-slate-900 rounded-xl border p-4 shadow-sm transition ${
                            status === 'approved' ? 'border-emerald-500 ring-1 ring-emerald-500' : 
                            status === 'skipped' ? 'border-slate-200 dark:border-slate-800 opacity-50' : 
                            'border-slate-200 dark:border-slate-800'
                        }`}>
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-xs font-bold text-slate-400">#{i+1}</span>
                                        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">{item.title}</h3>
                                    </div>
                                    
                                    {result ? (
                                        <div className="mt-3 space-y-2">
                                            <div className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2 italic">"{result.body?.substring(0, 150)}..."</div>
                                            <div className="flex gap-2">
                                                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 font-mono">Title: {result.meta_title?.substring(0,20)}...</span>
                                                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 font-mono">Desc: {result.meta_description?.substring(0,20)}...</span>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="mt-3 text-xs text-slate-400 flex items-center gap-2 hidden group-hover:block">
                                            Waiting for generation...
                                        </div>
                                    )}
                                </div>
                                
                                {result && (
                                    <div className="flex flex-col gap-2 shrink-0">
                                        <button 
                                            onClick={() => setStatus(item.product_id, 'approved')}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition ${
                                                status === 'approved' 
                                                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400' 
                                                : 'bg-slate-50 border border-slate-200 text-slate-600 hover:border-emerald-500 hover:text-emerald-600 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'
                                            }`}
                                        >
                                            <Check size={14}/> Approve
                                        </button>
                                        <button 
                                            onClick={() => setStatus(item.product_id, 'skipped')}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition ${
                                                status === 'skipped' 
                                                ? 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-500' 
                                                : 'bg-slate-50 border border-slate-200 text-slate-600 hover:bg-slate-100 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'
                                            }`}
                                        >
                                            <X size={14}/> Skip
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
