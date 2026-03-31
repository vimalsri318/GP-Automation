'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Save, Plus, Trash2, RefreshCw, Layers } from 'lucide-react';

export default function CategoryMasterEditor() {
    const [mappings, setMappings] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState('');

    const fetchMappings = async () => {
        setLoading(true);
        try {
            const res = await axios.get('http://localhost:8000/api/categories/');
            if (res.data.success) {
                setMappings(res.data.mappings);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMappings();
    }, []);

    const handleAdd = () => {
        setMappings([...mappings, { type: '', category: '' }]);
    };

    const handleRemove = (index: number) => {
        setMappings(mappings.filter((_, i) => i !== index));
    };

    const handleChange = (index: number, field: string, value: string) => {
        const newMappings = [...mappings];
        newMappings[index][field] = value;
        setMappings(newMappings);
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage('');
        try {
            const res = await axios.post('http://localhost:8000/api/categories/', mappings);
            if (res.data.success) {
                setMessage('Mappings saved successfully to Master Excel.');
                setTimeout(() => setMessage(''), 3000);
            }
        } catch (e) {
            setMessage('Failed to save mappings.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-indigo-600 text-white rounded-lg shadow-sm">
                        <Layers size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-slate-900">Category Master Editor</h3>
                        <p className="text-xs text-slate-500">Manage CMIR to Category mappings directly in the Master Excel file.</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <button 
                        onClick={fetchMappings}
                        className="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                        title="Reload from Excel"
                    >
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                    </button>
                    <button 
                        onClick={handleSave}
                        disabled={saving || loading}
                        className="flex items-center space-x-2 px-4 py-2 bg-black text-white text-sm font-semibold rounded-lg hover:bg-neutral-800 disabled:opacity-50 transition-all shadow-sm"
                    >
                        {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                        <span>{saving ? 'Syncing...' : 'Save to Excel'}</span>
                    </button>
                </div>
            </div>

            <div className="p-0 max-h-[600px] overflow-y-auto custom-scrollbar">
                {loading ? (
                    <div className="flex flex-col items-center justify-center p-20 space-y-4">
                        <Loader2 className="animate-spin text-indigo-500" size={32} />
                        <p className="text-sm text-slate-500 font-medium tracking-tight">Syncing with Master Excel...</p>
                    </div>
                ) : (
                    <table className="w-full text-left border-collapse">
                        <thead className="sticky top-0 bg-white shadow-sm z-10">
                            <tr className="text-[10px] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100">
                                <th className="px-6 py-4">CMIR Type / Logic Reference</th>
                                <th className="px-6 py-4">Mapped Category</th>
                                <th className="px-6 py-4 w-16"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {mappings.map((m, idx) => (
                                <tr key={idx} className="group hover:bg-slate-50/50 transition-colors">
                                    <td className="px-6 py-3">
                                        <input 
                                            type="text" 
                                            value={m.type}
                                            onChange={(e) => handleChange(idx, 'type', e.target.value)}
                                            className="w-full bg-transparent border-none focus:ring-0 text-sm font-mono text-slate-700 placeholder:text-slate-300"
                                            placeholder="e.g. ZZ-SALARY"
                                        />
                                    </td>
                                    <td className="px-6 py-3">
                                        <input 
                                            type="text" 
                                            value={m.category}
                                            onChange={(e) => handleChange(idx, 'category', e.target.value)}
                                            className={`w-full bg-transparent border-none focus:ring-0 text-sm font-bold placeholder:text-slate-300 ${
                                                m.category === 'Salary' ? 'text-indigo-600' : 
                                                m.category === 'Reimbursement' ? 'text-violet-600' : 
                                                m.category === 'FNF' ? 'text-pink-600' : 
                                                'text-slate-800'
                                            }`}
                                            placeholder="e.g. Salary"
                                        />
                                    </td>
                                    <td className="px-6 py-3">
                                        <button 
                                            onClick={() => handleRemove(idx)}
                                            className="p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-md transition-all opacity-0 group-hover:opacity-100"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex justify-between items-center">
                <button 
                    onClick={handleAdd}
                    className="flex items-center space-x-2 px-3 py-1.5 text-indigo-600 hover:bg-indigo-50 border border-transparent hover:border-indigo-100 rounded-md text-xs font-bold transition-all"
                >
                    <Plus size={14} />
                    <span>Add New Mapping</span>
                </button>
                {message && (
                    <span className="text-xs font-bold text-emerald-600 flex items-center bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100 animate-in fade-in zoom-in duration-300">
                        <CheckCircle2 size={14} className="mr-1.5" />
                        {message}
                    </span>
                )}
                <div className="text-[10px] text-slate-400 font-medium">
                    Total: {mappings.length} Custom Mappings
                </div>
            </div>
        </div>
    );
}

function CheckCircle2({ size, className }: { size: number, className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
            <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/>
        </svg>
    )
}
