'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  BarChart3, 
  Calculator, 
  Zap, 
  Database, 
  Activity,
  FileCheck2,
  FolderOpen
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'files' | 'validation'>('files');

  // System Files States
  const [systemFiles, setSystemFiles] = useState<any[]>([]);
  const [filesLoading, setFilesLoading] = useState(true);

  // Validation States
  const [validationLoading, setValidationLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validationError, setValidationError] = useState<string>('');
  
  const [steps, setSteps] = useState([
    { id: 'zrecon', name: 'Parsing Z-Recon Base File', status: 'idle', error: '' },
    { id: 'revenue', name: 'Parsing Revenue Dump', status: 'idle', error: '' },
    { id: 'cost', name: 'Parsing Cost Dump', status: 'idle', error: '' }
  ]);

  useEffect(() => {
    const fetchSystemFiles = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/step2/files');
        if (response.data && response.data.files) {
          setSystemFiles(response.data.files);
        }
      } catch (e) {
        console.error("Failed to load system files", e);
      } finally {
        setFilesLoading(false);
      }
    };
    fetchSystemFiles();
  }, []);

  const handleValidate = async () => {
    setValidationLoading(true);
    setValidationError('');
    setValidationResult(null);
    setSteps([
      { id: 'zrecon', name: 'Parsing Z-Recon Base File', status: 'idle', error: '' },
      { id: 'revenue', name: 'Parsing Revenue Dump', status: 'idle', error: '' },
      { id: 'cost', name: 'Parsing Cost Dump', status: 'idle', error: '' }
    ]);

    try {
      // Step 1: Z-Recon
      setSteps(s => s.map(st => st.id === 'zrecon' ? {...st, status: 'running'} : st));
      const zRes = await axios.get('http://localhost:8000/api/step2/validate/zrecon');
      if (!zRes.data.success) throw new Error(zRes.data.error || 'Z-Recon failure');
      setSteps(s => s.map(st => st.id === 'zrecon' ? {...st, status: 'done'} : st));

      // Step 2: Revenue
      setSteps(s => s.map(st => st.id === 'revenue' ? {...st, status: 'running'} : st));
      const rRes = await axios.get('http://localhost:8000/api/step2/validate/revenue');
      if (!rRes.data.success) throw new Error(rRes.data.error || 'Revenue Dump failure');
      setSteps(s => s.map(st => st.id === 'revenue' ? {...st, status: 'done'} : st));

      // Step 3: Cost
      setSteps(s => s.map(st => st.id === 'cost' ? {...st, status: 'running'} : st));
      const cRes = await axios.get('http://localhost:8000/api/step2/validate/cost');
      if (!cRes.data.success) throw new Error(cRes.data.error || 'Cost Dump failure');
      setSteps(s => s.map(st => st.id === 'cost' ? {...st, status: 'done'} : st));

      // Aggregate Results locally since the orchestrator successfully got all pieces
      const z_rev = zRes.data.data.revenue;
      const z_cost = zRes.data.data.cost;
      const r_sum = rRes.data.data.revenue_sum;
      const c_sum = cRes.data.data.cost_sum;
      
      const revVar = r_sum - z_rev;
      const costVar = c_sum - z_cost;

      setValidationResult({
        success: true,
        status: (Math.abs(revVar) < 100 && Math.abs(costVar) < 100) ? 'Match' : 'Mismatch',
        validation_details: {
            'Z Recon Total Revenue': z_rev,
            'Z Recon Total Cost': z_cost,
            'Revenue Dump Total': r_sum,
            'Cost Dump Total': c_sum
        },
        variances: {
           'Revenue Variance': revVar,
           'Cost Variance': costVar
        },
        pivot_data: {
           revenue_valid: rRes.data.data.pivots_consistent,
           revenue_count: rRes.data.data.pivot_count,
           cost_valid: cRes.data.data.pivots_consistent,
           cost_count: cRes.data.data.pivot_count
        }
      });

    } catch (err: any) {
      setSteps(s => s.map(st => st.status === 'running' ? {...st, status: 'error', error: err.message} : st));
      setValidationError(err.message || 'Validation engine failed unexpectedly.');
    } finally {
      setValidationLoading(false);
    }
  };

  const getFileIconColor = (type: string) => {
    if (type.includes("Z Recon")) return "text-emerald-500 bg-emerald-100";
    if (type.includes("Revenue")) return "text-indigo-500 bg-indigo-100";
    if (type.includes("Cost")) return "text-pink-500 bg-pink-100";
    return "text-slate-500 bg-slate-100";
  };

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900 font-sans">
      
      {/* LEFT SIDEBAR */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-2xl z-10 sticky top-0 h-screen">
        <div className="p-6 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center space-x-3 text-white">
            <div className="p-2 bg-indigo-500 rounded-lg">
              <Database size={24} className="text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">GP Auto POC</h1>
          </div>
          <p className="mt-2 text-xs text-slate-500 font-medium">Auto-Parsing Engine</p>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <button
            onClick={() => setActiveTab('files')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              activeTab === 'files' 
                ? 'bg-indigo-500/10 text-indigo-400 font-semibold border border-indigo-500/20' 
                : 'hover:bg-slate-800 hover:text-white border border-transparent'
            }`}
          >
            <FolderOpen size={20} />
            <span>System Files</span>
          </button>

          <button
            onClick={() => setActiveTab('validation')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              activeTab === 'validation' 
                ? 'bg-indigo-500/10 text-indigo-400 font-semibold border border-indigo-500/20' 
                : 'hover:bg-slate-800 hover:text-white border border-transparent'
            }`}
          >
            <Activity size={20} />
            <span>Workflow Checks</span>
          </button>
        </nav>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto relative bg-[conic-gradient(at_top_right,_var(--tw-gradient-stops))] from-slate-50 via-white to-slate-100">
        <div className="max-w-6xl mx-auto p-8 sm:p-12">

          {/* ========================================== */}
          {/* TAB: SYSTEM FILES (Replaces Upload) */}
          {/* ========================================== */}
          {activeTab === 'files' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="mb-8">
                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">Tracked System Files</h2>
                <p className="text-slate-500 mt-2 hover:text-slate-800 transition-colors">
                  Upload phase bypassed. Direct linking to <code className="bg-slate-200 px-1 rounded">/Input Files</code> directory to save processing time.
                </p>
              </div>

              {filesLoading ? (
                <div className="flex items-center justify-center p-20">
                  <Loader2 className="animate-spin text-indigo-500" size={40} />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {systemFiles.map((file, idx) => (
                    <div key={idx} className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6 hover:shadow-lg hover:border-indigo-200 transition-all duration-300 group">
                      <div className="flex items-start justify-between mb-4">
                        <div className={`p-3 rounded-xl ${getFileIconColor(file.type)} group-hover:scale-110 transition-transform`}>
                          <FileCheck2 size={24} />
                        </div>
                        <span className="flex items-center text-[10px] uppercase tracking-bolder font-bold text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-1 rounded-full">
                          <CheckCircle2 size={12} className="mr-1" /> Ready
                        </span>
                      </div>
                      <h3 className="font-bold text-slate-800 text-lg">{file.type}</h3>
                      <p className="text-sm text-slate-500 mt-1 truncate" title={file.name}>{file.name}</p>
                      
                      <div className="mt-6 pt-4 border-t border-slate-100 flex justify-between items-center text-sm font-medium">
                        <span className="text-slate-400">Disk Size</span>
                        <span className="text-slate-700 font-mono bg-slate-50 px-2 py-1 rounded-md border border-slate-100">{file.size_kb.toLocaleString()} KB</span>
                      </div>
                    </div>
                  ))}
                  
                  {systemFiles.length === 0 && (
                    <div className="col-span-3 text-center p-12 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200">
                      <AlertCircle className="mx-auto text-slate-400 mb-4" size={40} />
                      <h3 className="text-lg font-bold text-slate-700">No Files Found</h3>
                      <p className="text-slate-500 mt-1">Please ensure the files are placed in the `Input Files` root directory.</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}


          {/* ========================================== */}
          {/* TAB: VALIDATION WORKFLOW */}
          {/* ========================================== */}
          {activeTab === 'validation' && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
               <div className="mb-8">
                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">Workflow Validation</h2>
                <p className="text-slate-500 mt-2">Correlate and validate Z-Recon mathematical aggregates against Raw System Dumps programmatically using Pandas.</p>
              </div>

              <div className="bg-gradient-to-br from-indigo-950 to-slate-900 rounded-3xl p-8 sm:p-10 text-white shadow-2xl relative overflow-hidden ring-1 ring-indigo-500/20">
                <div className="absolute top-0 right-0 p-32 bg-indigo-500/10 rounded-full blur-3xl" />
                
                <div className="relative z-10">
                  <div className="flex items-center space-x-4 mb-6 text-indigo-300">
                    <div className="p-3 bg-indigo-500/20 rounded-xl">
                      <Calculator size={32} className="text-indigo-400" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">Reconciliation Core</h3>
                      <p className="text-sm text-slate-400 mt-1">Base vs Dump programmatic check.</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={handleValidate}
                    disabled={validationLoading}
                    className="flex items-center justify-center space-x-2 py-4 px-8 text-white text-base font-bold rounded-xl transition-all duration-300 shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] active:scale-[0.98] disabled:opacity-50 bg-indigo-600 hover:bg-indigo-500 w-full sm:w-auto"
                  >
                    {validationLoading ? (
                      <Loader2 size={20} className="animate-spin" />
                    ) : (
                      <Zap size={20} />
                    )}
                    <span>{validationLoading ? 'Executing Engine...' : 'Run Variance Validation'}</span>
                  </button>

                  {/* LIVE STEPS TRACKER */}
                  {(validationLoading || validationResult || validationError) && (
                    <div className="mt-8 space-y-3 bg-slate-900/80 p-6 rounded-2xl border border-slate-700/50">
                       <h4 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">Pipeline Execution Progress</h4>
                       {steps.map(step => (
                          <div key={step.id} className={`flex items-start space-x-4 p-3 rounded-lg border ${step.status === 'running' ? 'bg-indigo-500/10 border-indigo-500/30 shadow-[0_0_15px_rgba(79,70,229,0.15)]' : 'bg-transparent border-transparent'} transition-all`}>
                             <div className="shrink-0 mt-0.5">
                                {step.status === 'idle' && <div className="w-5 h-5 rounded-full border-2 border-slate-600" />}
                                {step.status === 'running' && <Loader2 size={20} className="text-indigo-400 animate-spin" />}
                                {step.status === 'done' && <CheckCircle2 size={20} className="text-emerald-400" />}
                                {step.status === 'error' && <AlertCircle size={20} className="text-red-400" />}
                             </div>
                             <div className="flex flex-col flex-1 pl-1">
                                <span className={`font-medium ${step.status === 'idle' ? 'text-slate-500' : 'text-slate-200'}`}>{step.name}</span>
                                {step.error && <span className="text-red-400 text-sm mt-1 bg-red-950/30 p-2 rounded border border-red-900/30">{step.error}</span>}
                             </div>
                          </div>
                       ))}
                    </div>
                  )}

                  {validationResult && validationResult.success && (
                    <div className="mt-10 space-y-6 animate-in fade-in duration-700">
                      <div className="flex items-center space-x-3 pb-4 border-b border-slate-700/50">
                        <BarChart3 size={24} className={validationResult.status === 'Match' ? 'text-emerald-400' : 'text-yellow-400'} />
                        <h4 className="text-xl font-bold">{validationResult.status === 'Match' ? 'Validation Passed successfully' : 'Variances Detected in Workflow'}</h4>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Revenue Block */}
                        <div className="bg-slate-800/80 border border-slate-700 rounded-2xl p-6 shadow-inner relative overflow-hidden group hover:border-indigo-500/50 transition-colors">
                          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition-all"></div>
                          <div className="flex justify-between items-start mb-4">
                            <h5 className="text-indigo-400 font-bold uppercase tracking-widest text-xs">Revenue Comparison</h5>
                            {validationResult.pivot_data?.revenue_valid ? (
                                <span className="flex items-center text-[10px] font-bold bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded border border-indigo-500/30">
                                   <CheckCircle2 size={12} className="mr-1" />
                                   {validationResult.pivot_data.revenue_count} Internal Pivots Matched
                                </span>
                            ) : (
                                <span className="flex items-center text-[10px] font-bold bg-red-500/20 text-red-300 px-2 py-1 rounded border border-red-500/30">
                                   <AlertCircle size={12} className="mr-1" />
                                   Pivots Mismatched
                                </span>
                            )}
                          </div>
                          <div className="space-y-4">
                            <div className="flex justify-between items-center border-b border-slate-700/50 pb-3">
                              <span className="text-slate-400 text-sm">Z-Recon Base File:</span>
                              <span className="font-mono text-lg">{validationResult.validation_details['Z Recon Total Revenue']?.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between items-center border-b border-slate-700/50 pb-3">
                              <span className="text-slate-400 text-sm">Revenue Dump:</span>
                              <span className="font-mono text-lg">{validationResult.validation_details['Revenue Dump Total']?.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between items-center pt-2">
                              <span className="text-white font-semibold text-sm">Calculated Variance:</span>
                              <span className={`font-mono text-xl font-bold px-3 py-1 rounded-lg ${Math.abs(validationResult.variances['Revenue Variance']) > 100 ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`}>
                                {validationResult.variances['Revenue Variance']?.toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Cost Block */}
                        <div className="bg-slate-800/80 border border-slate-700 rounded-2xl p-6 shadow-inner relative overflow-hidden group hover:border-pink-500/50 transition-colors">
                          <div className="absolute top-0 right-0 w-32 h-32 bg-pink-500/5 rounded-full blur-2xl group-hover:bg-pink-500/10 transition-all"></div>
                          <div className="flex justify-between items-start mb-4">
                            <h5 className="text-pink-400 font-bold uppercase tracking-widest text-xs">Cost Comparison</h5>
                            {validationResult.pivot_data?.cost_valid ? (
                                <span className="flex items-center text-[10px] font-bold bg-pink-500/20 text-pink-300 px-2 py-1 rounded border border-pink-500/30">
                                   <CheckCircle2 size={12} className="mr-1" />
                                   {validationResult.pivot_data.cost_count} Internal Pivots Matched
                                </span>
                            ) : (
                                <span className="flex items-center text-[10px] font-bold bg-red-500/20 text-red-300 px-2 py-1 rounded border border-red-500/30">
                                   <AlertCircle size={12} className="mr-1" />
                                   Pivots Mismatched
                                </span>
                            )}
                          </div>
                          <div className="space-y-4">
                            <div className="flex justify-between items-center border-b border-slate-700/50 pb-3">
                              <span className="text-slate-400 text-sm">Z-Recon Base File:</span>
                              <span className="font-mono text-lg">{validationResult.validation_details['Z Recon Total Cost']?.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between items-center border-b border-slate-700/50 pb-3">
                              <span className="text-slate-400 text-sm">Cost Dump:</span>
                              <span className="font-mono text-lg">{validationResult.validation_details['Cost Dump Total']?.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between items-center pt-2">
                              <span className="text-white font-semibold text-sm">Calculated Variance:</span>
                              <span className={`font-mono text-xl font-bold px-3 py-1 rounded-lg ${Math.abs(validationResult.variances['Cost Variance']) > 100 ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`}>
                                {validationResult.variances['Cost Variance']?.toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
