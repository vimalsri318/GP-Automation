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
  FolderOpen,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'files' | 'validation'>('files');
  const [activeProcess, setActiveProcess] = useState<number | null>(1);
  const [expandedPivots, setExpandedPivots] = useState({ revenue: false, cost: false });

  // System Files States
  const [systemFiles, setSystemFiles] = useState<any[]>([]);
  const [filesLoading, setFilesLoading] = useState(true);

  // Validation States
  const [validationLoading, setValidationLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validationError, setValidationError] = useState<string>('');
  
  // Step 2 States (Cross-Invoice Integrity)
  const [loadingStep2, setLoadingStep2] = useState(false);
  const [step2Result, setStep2Result] = useState<any>(null);
  
  // Step 3 States (CMIR Type Resolution)
  const [loadingStep3, setLoadingStep3] = useState(false);
  const [step3Result, setStep3Result] = useState<any>(null);
  
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
           revenue_pivots: rRes.data.data.pivots || [],
           cost_valid: cRes.data.data.pivots_consistent,
           cost_count: cRes.data.data.pivot_count,
           cost_pivots: cRes.data.data.pivots || []
        }
      });

    } catch (err: any) {
      setSteps(s => s.map(st => st.status === 'running' ? {...st, status: 'error', error: err.message} : st));
      setValidationError(err.message || 'Validation engine failed unexpectedly.');
    } finally {
      setValidationLoading(false);
    }
  };

  const handleStep2 = async () => {
    setLoadingStep2(true);
    try {
      const response = await axios.get('http://localhost:8000/api/step2/validate/cross_invoice');
      if (response.data.success) {
        setStep2Result(response.data.data);
        setActiveProcess(2);
      } else {
        alert(response.data.error || "Failed Cross-Invoice Integrity check");
      }
    } catch (e) {
      console.error(e);
      alert("Error executing Step 2. Is the backend running?");
    } finally {
      setLoadingStep2(false);
    }
  };

  const handleStep3 = async () => {
    setLoadingStep3(true);
    try {
      const response = await axios.get('http://localhost:8000/api/step3/validate/cmir_resolution');
      if (response.data.success) {
        setStep3Result(response.data.data);
        setActiveProcess(3);
      } else {
        alert(response.data.error || "Failed CMIR Resolution");
      }
    } catch (e) {
      console.error(e);
      alert("Error executing Step 3. Is the backend running?");
    } finally {
      setLoadingStep3(false);
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
      <aside className="w-64 bg-black text-slate-300 flex flex-col shadow-xl z-10 sticky top-0 h-screen">
        <div className="p-6 border-b border-neutral-900">
          <div className="flex items-center space-x-3 text-white">
            <div className="p-2 bg-neutral-800 rounded-lg">
              <Database size={24} className="text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight">GP Auto POC</h1>
          </div>
          <p className="mt-2 text-xs text-neutral-500 font-medium">Auto-Parsing Engine</p>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto w-full">
          <button
            onClick={() => setActiveTab('files')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              activeTab === 'files' 
                ? 'bg-neutral-900 text-white font-semibold' 
                : 'hover:bg-neutral-900 hover:text-white border border-transparent'
            }`}
          >
            <FolderOpen size={20} />
            <span>System Files</span>
          </button>

          <button
            onClick={() => setActiveTab('validation')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              activeTab === 'validation' 
                ? 'bg-neutral-900 text-white font-semibold' 
                : 'hover:bg-neutral-900 hover:text-white border border-transparent'
            }`}
          >
            <Activity size={20} />
            <span>Workflow Checks</span>
          </button>
        </nav>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 overflow-y-auto relative bg-[#F9FAFB]">
        <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">

          {/* ========================================== */}
          {/* TAB: SYSTEM FILES */}
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
               <div className="mb-4">
                <h2 className="text-2xl font-extrabold tracking-tight text-slate-900">Workflow Validation</h2>
                <p className="text-sm text-slate-500 mt-1">Correlate and validate Z-Recon mathematical aggregates against Raw System Dumps programmatically using Pandas.</p>
              </div>

              <div className="space-y-4">
                 {/* PROCESS STEP 1 */}
                 <div className={`border rounded-2xl overflow-hidden transition-all duration-500 ease-in-out ${activeProcess === 1 ? 'border-indigo-600 shadow-md' : 'border-slate-200 shadow-sm hover:border-slate-300 bg-white'}`}>
                    
                    {/* Collapsible Header */}
                    <div 
                       onClick={() => setActiveProcess(activeProcess === 1 ? null : 1)}
                       className={`p-5 cursor-pointer flex items-center justify-between transition-colors duration-500 ease-in-out ${activeProcess === 1 ? 'bg-indigo-600 text-white' : 'bg-white text-slate-900'}`}
                    >
                       <div className="flex items-center space-x-4">
                          <div className={`flex items-center justify-center w-10 h-10 rounded-full font-bold font-mono text-lg shadow-sm transition-colors duration-500 ${activeProcess === 1 ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600 border border-slate-200'}`}>
                            1
                          </div>
                          <div>
                             <h3 className={`text-lg font-bold transition-colors duration-500 ${activeProcess === 1 ? 'text-white' : 'text-slate-900'}`}>Z-Recon vs SAP Data Dumps</h3>
                             <p className={`text-sm mt-0.5 transition-colors duration-500 ${activeProcess === 1 ? 'text-indigo-100' : 'text-slate-500'}`}>
                               Identify programmatic variances & audit internal pivot mappings.
                             </p>
                          </div>
                       </div>
                       <div>
                          <ChevronDown size={24} className={`transform transition-transform duration-500 ease-in-out ${activeProcess === 1 ? 'rotate-180 text-white' : 'text-slate-400'}`} />
                       </div>
                    </div>

                    {/* Step 1 Expanded Content Array */}
                    <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${activeProcess === 1 ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                        <div className="overflow-hidden">
                           <div className="bg-gradient-to-r from-slate-50 to-slate-100/50 p-5 sm:p-6 text-slate-900 relative border-t border-indigo-700">
                               <div className="absolute top-0 right-0 p-32 bg-indigo-500/5 rounded-full blur-3xl" />
                               
                               <div className="relative z-10">
                                 <div className="flex items-center justify-between mb-4 text-slate-800">
                                   <div className="flex items-center space-x-3">
                                     <div className="p-2 bg-indigo-600 text-white rounded-lg shadow-sm">
                                       <Calculator size={20} className="text-white" />
                                     </div>
                                     <div>
                                       <h3 className="text-base font-bold text-slate-900">Reconciliation Engine</h3>
                                     </div>
                                   </div>
                                   
                                   <button
                                     onClick={(e) => { e.stopPropagation(); handleValidate(); }}
                                     disabled={validationLoading}
                                     className="flex items-center justify-center space-x-2 py-2 px-5 text-white text-sm font-semibold rounded-lg transition-all duration-300 shadow-sm hover:shadow-md active:scale-[0.98] disabled:opacity-50 bg-black hover:bg-neutral-800 w-full sm:w-auto"
                                   >
                                     {validationLoading ? (
                                       <Loader2 size={18} className="animate-spin" />
                                     ) : (
                                       <Zap size={18} />
                                     )}
                                     <span>{validationLoading ? 'Executing Engine...' : 'Run Variance Validation'}</span>
                                   </button>
                                 </div>

                                 {/* LIVE STEPS TRACKER */}
                                 {(validationLoading || validationResult || validationError) && (
                                   <div className="mt-4 space-y-2 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                      <h4 className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-2">Pipeline Execution Progress</h4>
                                      {steps.map(step => (
                                         <div key={step.id} className={`flex items-start space-x-3 p-2 rounded-md border ${step.status === 'running' ? 'bg-slate-50 border-slate-200' : 'bg-transparent border-transparent'} transition-all`}>
                                            <div className="shrink-0 mt-0.5">
                                               {step.status === 'idle' && <div className="w-4 h-4 rounded-full border-2 border-slate-300" />}
                                               {step.status === 'running' && <Loader2 size={16} className="text-black animate-spin" />}
                                               {step.status === 'done' && <CheckCircle2 size={16} className="text-emerald-500" />}
                                               {step.status === 'error' && <AlertCircle size={16} className="text-red-500" />}
                                            </div>
                                            <div className="flex flex-col flex-1 pl-0.5">
                                               <span className={`text-sm font-medium ${step.status === 'idle' ? 'text-slate-400' : 'text-slate-800'}`}>{step.name}</span>
                                               {step.error && <span className="text-red-600 text-sm mt-1 bg-red-50 p-2 rounded border border-red-100">{step.error}</span>}
                                            </div>
                                         </div>
                                      ))}
                                   </div>
                                 )}

                                 {validationResult && validationResult.success && (
                                   <div className="mt-6 space-y-4 animate-in fade-in duration-700">
                                     <div className="flex items-center space-x-2 pb-2">
                                       <BarChart3 size={20} className={validationResult.status === 'Match' ? 'text-emerald-500' : 'text-yellow-500'} />
                                       <h4 className="text-lg font-bold text-slate-900">{validationResult.status === 'Match' ? 'Validation Passed successfully' : 'Variances Detected in Workflow'}</h4>
                                     </div>
                                     
                                     <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                                       {/* Revenue Block */}
                                       <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-sm relative overflow-hidden group hover:border-slate-300 transition-colors">
                                         <div className="absolute top-0 right-0 w-24 h-24 bg-slate-50 rounded-full blur-2xl group-hover:bg-slate-100 transition-all"></div>
                                         <div className="flex justify-between items-start mb-3">
                                           <h5 className="text-slate-700 font-bold uppercase tracking-widest text-[10px]">Revenue Comparison</h5>
                                           <button onClick={() => setExpandedPivots(p => ({...p, revenue: !p.revenue}))} className="flex items-center text-[10px] font-bold text-slate-500 hover:text-black transition-colors z-10 relative">
                                              Audit Breakdowns <ChevronDown size={14} className={`ml-1 transform transition-transform duration-300 ease-in-out ${expandedPivots.revenue ? 'rotate-180' : ''}`} />
                                           </button>
                                         </div>
                                         
                                         <div className="space-y-2 relative z-10">
                                           <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                                             <span className="text-slate-500 text-xs">Z-Recon Base File:</span>
                                             <span className="font-mono text-sm font-medium text-slate-900">{validationResult.validation_details['Z Recon Total Revenue']?.toLocaleString()}</span>
                                           </div>
                                           <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                                             <span className="text-slate-500 text-xs flex items-center">
                                                Revenue Dump:
                                                {validationResult.pivot_data?.revenue_valid ? (
                                                   <CheckCircle2 size={12} className="text-emerald-500 ml-2 mr-1" />
                                                ) : (
                                                   <AlertCircle size={12} className="text-red-500 ml-2 mr-1" />
                                                )}
                                             </span>
                                             <span className="font-mono text-sm font-medium text-slate-900">{validationResult.validation_details['Revenue Dump Total']?.toLocaleString()}</span>
                                           </div>
                                           <div className="flex justify-between items-center pt-1">
                                             <span className="text-slate-800 font-semibold text-xs">Calculated Variance:</span>
                                             <span className={`font-mono text-sm font-bold px-2 py-0.5 rounded-md ${Math.abs(validationResult.variances['Revenue Variance']) > 100 ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100'}`}>
                                               {validationResult.variances['Revenue Variance']?.toLocaleString()}
                                             </span>
                                           </div>
                                         </div>

                                         {/* Expandable Pivot Table */}
                                         <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${expandedPivots.revenue && validationResult.pivot_data?.revenue_pivots ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                                            <div className="overflow-hidden relative z-10">
                                               <div className="mt-5 border-t border-slate-100 pt-4">
                                                  <h6 className="text-[10px] font-bold text-slate-400 uppercase mb-3 tracking-widest">Internal Dump Groupings</h6>
                                                  <div className="space-y-4">
                                                     {validationResult.pivot_data.revenue_pivots.length > 0 ? validationResult.pivot_data.revenue_pivots.map((p: any, i: number) => (
                                                        <div key={i} className="rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                                                           <div className="flex justify-between items-center bg-slate-50 px-3 py-2 border-b border-slate-200">
                                                              <span className="text-[10px] font-bold text-slate-700 uppercase">{p.dimension}</span>
                                                              <span className="text-[10px] font-mono font-bold text-slate-600">Σ {p.total.toLocaleString()}</span>
                                                           </div>
                                                           <div className="max-h-56 overflow-y-auto bg-white custom-scrollbar">
                                                              <table className="w-full text-left text-xs">
                                                                 <tbody>
                                                                    {p.values.map((v: any, j: number) => (
                                                                       <tr key={j} className="border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors">
                                                                          <td className="py-2 px-3 text-slate-600 truncate max-w-[120px]" title={String(v.key)}>{v.key}</td>
                                                                          <td className="py-2 px-3 text-right font-mono text-slate-800">{v.amount.toLocaleString()}</td>
                                                                       </tr>
                                                                    ))}
                                                                 </tbody>
                                                              </table>
                                                           </div>
                                                        </div>
                                                     )) : (
                                                       <p className="text-xs text-slate-500 italic">No pivot data parsed.</p>
                                                     )}
                                                  </div>
                                               </div>
                                            </div>
                                         </div>
                                       </div>

                                       {/* Cost Block */}
                                       <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-sm relative overflow-hidden group hover:border-slate-300 transition-colors">
                                         <div className="absolute top-0 right-0 w-24 h-24 bg-slate-50 rounded-full blur-2xl group-hover:bg-slate-100 transition-all"></div>
                                         <div className="flex justify-between items-start mb-3">
                                           <h5 className="text-slate-700 font-bold uppercase tracking-widest text-[10px]">Cost Comparison</h5>
                                           <button onClick={() => setExpandedPivots(p => ({...p, cost: !p.cost}))} className="flex items-center text-[10px] font-bold text-slate-500 hover:text-black transition-colors z-10 relative">
                                              Audit Breakdowns <ChevronDown size={14} className={`ml-1 transform transition-transform duration-300 ease-in-out ${expandedPivots.cost ? 'rotate-180' : ''}`} />
                                           </button>
                                         </div>
                                         
                                         <div className="space-y-2 relative z-10">
                                           <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                                             <span className="text-slate-500 text-xs">Z-Recon Base File:</span>
                                             <span className="font-mono text-sm font-medium text-slate-900">{validationResult.validation_details['Z Recon Total Cost']?.toLocaleString()}</span>
                                           </div>
                                           <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                                             <span className="text-slate-500 text-xs flex items-center">
                                                Cost Dump:
                                                {validationResult.pivot_data?.cost_valid ? (
                                                   <CheckCircle2 size={12} className="text-emerald-500 ml-2 mr-1" />
                                                ) : (
                                                   <AlertCircle size={12} className="text-red-500 ml-2 mr-1" />
                                                )}
                                             </span>
                                             <span className="font-mono text-sm font-medium text-slate-900">{validationResult.validation_details['Cost Dump Total']?.toLocaleString()}</span>
                                           </div>
                                           <div className="flex justify-between items-center pt-1">
                                             <span className="text-slate-800 font-semibold text-xs">Calculated Variance:</span>
                                             <span className={`font-mono text-sm font-bold px-2 py-0.5 rounded-md ${Math.abs(validationResult.variances['Cost Variance']) > 100 ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100'}`}>
                                               {validationResult.variances['Cost Variance']?.toLocaleString()}
                                             </span>
                                           </div>
                                         </div>

                                         {/* Expandable Pivot Table */}
                                         <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${expandedPivots.cost && validationResult.pivot_data?.cost_pivots ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                                            <div className="overflow-hidden relative z-10">
                                               <div className="mt-5 border-t border-slate-100 pt-4">
                                                  <h6 className="text-[10px] font-bold text-slate-400 uppercase mb-3 tracking-widest">Internal Dump Groupings</h6>
                                                  <div className="space-y-4">
                                                     {validationResult.pivot_data.cost_pivots.length > 0 ? validationResult.pivot_data.cost_pivots.map((p: any, i: number) => (
                                                        <div key={i} className="rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                                                           <div className="flex justify-between items-center bg-slate-50 px-3 py-2 border-b border-slate-200">
                                                              <span className="text-[10px] font-bold text-slate-700 uppercase">{p.dimension}</span>
                                                              <span className="text-[10px] font-mono font-bold text-slate-600">Σ {p.total.toLocaleString()}</span>
                                                           </div>
                                                           <div className="max-h-56 overflow-y-auto bg-white custom-scrollbar">
                                                              <table className="w-full text-left text-xs">
                                                                 <tbody>
                                                                    {p.values.map((v: any, j: number) => (
                                                                       <tr key={j} className="border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors">
                                                                          <td className="py-2 px-3 text-slate-600 truncate max-w-[120px]" title={String(v.key)}>{v.key}</td>
                                                                          <td className="py-2 px-3 text-right font-mono text-slate-800">{v.amount.toLocaleString()}</td>
                                                                       </tr>
                                                                    ))}
                                                                 </tbody>
                                                              </table>
                                                           </div>
                                                        </div>
                                                     )) : (
                                                       <p className="text-xs text-slate-500 italic">No pivot data parsed.</p>
                                                     )}
                                                  </div>
                                               </div>
                                            </div>
                                         </div>
                                       </div>
                                     </div>
                                   </div>
                                 )}

                               </div>
                           </div>
                        </div>
                    </div>
                 </div>

                 {/* PROCESS STEP 2: Cross-Invoice Integrity */}
                 <div className="border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden flex flex-col transition-all">
                     <div 
                         onClick={() => setActiveProcess(activeProcess === 2 ? null : 2)}
                         className="p-5 flex flex-col sm:flex-row items-start sm:items-center cursor-pointer hover:bg-slate-50 transition-colors"
                     >
                         <div className={`flex shrink-0 items-center justify-center w-10 h-10 rounded-full font-bold font-mono text-lg ${activeProcess === 2 ? 'bg-black text-white' : 'bg-slate-100 text-slate-600'}`}>
                             2
                         </div>
                         <div className="flex-1 sm:px-4 mt-3 sm:mt-0">
                             <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                 Cross-Invoice Integrity Check
                                 {step2Result && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                             </h3>
                             <p className="text-sm text-slate-500 mt-0.5">Correlate underlying Z-Recon accounting documents with Revenue/Invoice physical files.</p>
                         </div>
                         <div className="shrink-0 mt-3 sm:mt-0 flex items-center gap-3">
                             <button 
                                 onClick={(e) => { e.stopPropagation(); handleStep2(); }}
                                 disabled={loadingStep2}
                                 className="px-5 py-2 bg-black text-white font-semibold text-sm rounded-lg shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-all flex items-center gap-2"
                             >
                                 {loadingStep2 ? <><Loader2 className="w-4 h-4 animate-spin"/> Executing...</> : <><Zap className="w-4 h-4"/> Run Integrity Check</>}
                             </button>
                             {activeProcess === 2 ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                         </div>
                     </div>

                     {/* Dropdown Audit Results */}
                     <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${activeProcess === 2 ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                         <div className="overflow-hidden">
                             {step2Result && (
                                 <div className="p-5 bg-slate-50 border-t border-slate-100">
                                     <h4 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                                         <Database className="w-5 h-5 text-blue-500" />
                                         Integrity Resolution Report
                                     </h4>
                                     <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                         <div className="bg-white p-4 border border-slate-200 rounded-xl shadow-sm">
                                             <p className="text-xs text-slate-500 font-semibold mb-1 uppercase">Total Baseline Scope</p>
                                             <p className="text-2xl font-bold font-mono text-slate-800">{step2Result.total_rows.toLocaleString()}</p>
                                             <p className="text-xs text-slate-400 mt-1">Z-Recon Rows Traversed</p>
                                         </div>
                                         <div className="bg-green-50 p-4 border border-green-200 rounded-xl shadow-sm">
                                             <p className="text-xs text-green-600 font-semibold mb-1 uppercase">SO Matches Resolved</p>
                                             <p className="text-2xl font-bold font-mono text-green-700">{step2Result.updates_applied.toLocaleString()}</p>
                                             <p className="text-xs text-green-600 mt-1 opacity-80">Populated via Cross-Link</p>
                                         </div>
                                         <div className="bg-amber-50 p-4 border border-amber-200 rounded-xl shadow-sm">
                                             <p className="text-xs text-amber-600 font-semibold mb-1 uppercase">Failed Mappings</p>
                                             <p className="text-2xl font-bold font-mono text-amber-700">{step2Result.unresolved_misses.toLocaleString()}</p>
                                             <p className="text-xs text-amber-600 mt-1 opacity-80">Reference Key / SO Missing</p>
                                         </div>
                                     </div>

                                     {/* PIPELINE BREAKDOWN UI - ENHANCED STEPPER */}
                                     {step2Result.process_steps && (
                                     <div className="mt-6 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                                         <h5 className="text-sm font-bold text-slate-800 mb-6 flex items-center gap-2">
                                             <Activity className="w-4 h-4 text-indigo-500" />
                                             Execution Timeline & Sub-Steps
                                         </h5>
                                         
                                         <div className="space-y-6">
                                             {step2Result.process_steps.map((step: any, idx: number) => (
                                                 <div key={idx} className="relative flex gap-4">
                                                     {/* Vertical Line Connector */}
                                                     {idx !== step2Result.process_steps.length - 1 && (
                                                         <div className="absolute left-[11px] top-6 w-[2px] h-full bg-slate-100" />
                                                     )}
                                                     
                                                     {/* Step Bubble */}
                                                     <div className={`z-10 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${idx === step2Result.process_steps.length - 1 ? 'bg-green-500 border-green-200 text-white' : 'bg-white border-slate-200 text-slate-400'}`}>
                                                         {idx + 1}
                                                     </div>
                                                     
                                                     {/* Step Content */}
                                                     <div className="flex-1 pb-2">
                                                         <p className="text-sm font-bold text-slate-700 leading-none">{step.label}</p>
                                                         <p className="text-xs text-slate-500 mt-1.5 bg-slate-50 inline-block px-2 py-0.5 rounded border border-slate-100 italic">
                                                             {step.detail}
                                                         </p>
                                                     </div>
                                                 </div>
                                             ))}
                                         </div>

                                         {/* Summary Warning if high misses */}
                                         {step2Result.unresolved_misses > 0 && (
                                             <div className="mt-6 p-3 bg-amber-50 border border-amber-100 rounded-lg flex items-start gap-3">
                                                 <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                                                 <p className="text-xs text-amber-700 leading-relaxed">
                                                     <span className="font-bold">Optimization Note:</span> {step2Result.unresolved_misses.toLocaleString()} records could not be resolved. This usually happens if the Accounting Document in Z-Recon doesn't have a matching Reference Key in the Revenue Dump, or the Invoice reference is missing from the Invoice Listing.
                                                 </p>
                                             </div>
                                         )}
                                     </div>
                                     )}
                                 </div>
                             )}
                             {!step2Result && !loadingStep2 && (
                                 <div className="p-8 text-center text-slate-400 text-sm">
                                     Execute the Integrity Check to view the mapping resolution results.
                                 </div>
                             )}
                         </div>
                     </div>
                 </div>

                 {/* PROCESS STEP 3: CMIR Type Resolution */}
                 <div className="border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden flex flex-col transition-all">
                     <div 
                         onClick={() => setActiveProcess(activeProcess === 3 ? null : 3)}
                         className="p-5 flex flex-col sm:flex-row items-start sm:items-center cursor-pointer hover:bg-slate-50 transition-colors"
                     >
                         <div className={`flex shrink-0 items-center justify-center w-10 h-10 rounded-full font-bold font-mono text-lg ${activeProcess === 3 ? 'bg-orange-600 text-white' : 'bg-slate-100 text-slate-600'}`}>
                             3
                         </div>
                         <div className="flex-1 sm:px-4 mt-3 sm:mt-0">
                             <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                 CMIR Type Alignment
                                 {step3Result && <CheckCircle2 className="w-5 h-5 text-orange-500" />}
                             </h3>
                             <p className="text-sm text-slate-500 mt-0.5">Resolve blank CMIR types (Column E) via SO Listing waterfall mapping.</p>
                         </div>
                         <div className="shrink-0 mt-3 sm:mt-0 flex items-center gap-3">
                             <button 
                                 onClick={(e) => { e.stopPropagation(); handleStep3(); }}
                                 disabled={loadingStep3}
                                 className="px-5 py-2 bg-black text-white font-semibold text-sm rounded-lg shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-all flex items-center gap-2"
                             >
                                 {loadingStep3 ? <><Loader2 className="w-4 h-4 animate-spin"/> Executing...</> : <><Zap className="w-4 h-4"/> Run CMIR Resolution</>}
                             </button>
                             {activeProcess === 3 ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                         </div>
                     </div>

                     {/* Dropdown Audit Results */}
                     <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${activeProcess === 3 ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}>
                         <div className="overflow-hidden">
                             {step3Result && (
                                 <div className="p-5 bg-orange-50/30 border-t border-slate-100">
                                     <h4 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                                         <Activity className="w-5 h-5 text-orange-500" />
                                         CMIR Resolution Report
                                     </h4>
                                     <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                         <div className="bg-white p-4 border border-slate-200 rounded-xl shadow-sm">
                                             <p className="text-xs text-slate-500 font-semibold mb-1 uppercase">Blanks Detected</p>
                                             <p className="text-2xl font-bold font-mono text-slate-800">{step3Result.total_rows_to_check.toLocaleString()}</p>
                                             <p className="text-xs text-slate-400 mt-1">Col E Rows Targeted</p>
                                         </div>
                                         <div className="bg-orange-500 p-4 border border-orange-600 rounded-xl shadow-md text-white">
                                             <p className="text-xs text-orange-100 font-semibold mb-1 uppercase">Matches Populated</p>
                                             <p className="text-2xl font-bold font-mono">{step3Result.updates_applied.toLocaleString()}</p>
                                             <p className="text-xs text-orange-100 mt-1 opacity-80">Bridged via SO Listing</p>
                                         </div>
                                         <div className="bg-white p-4 border border-slate-200 rounded-xl shadow-sm">
                                             <p className="text-xs text-slate-500 font-semibold mb-1 uppercase">Resolution Yield</p>
                                             <p className="text-2xl font-bold font-mono text-slate-800">
                                                 {step3Result.updates_applied.toLocaleString()} / {step3Result.total_rows_to_check.toLocaleString()}
                                             </p>
                                             <p className="text-xs text-slate-400 mt-1">Population Efficiency</p>
                                         </div>
                                     </div>

                                     {/* PIPELINE BREAKDOWN */}
                                     {step3Result.process_steps && (
                                     <div className="mt-6 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                                         <h5 className="text-sm font-bold text-slate-800 mb-6 flex items-center gap-2">
                                             <Database className="w-4 h-4 text-orange-500" />
                                             Execution Timeline & Sub-Steps
                                         </h5>
                                         
                                         <div className="space-y-6">
                                             {step3Result.process_steps.map((step: any, idx: number) => (
                                                 <div key={idx} className="relative flex gap-4">
                                                     {idx !== step3Result.process_steps.length - 1 && (
                                                         <div className="absolute left-[11px] top-6 w-[2px] h-full bg-slate-100" />
                                                     )}
                                                     <div className={`z-10 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 ${idx === step3Result.process_steps.length - 1 ? 'bg-orange-600 border-orange-200 text-white' : 'bg-white border-slate-200 text-slate-400'}`}>
                                                         {idx + 1}
                                                     </div>
                                                     <div className="flex-1 pb-2">
                                                         <p className="text-sm font-bold text-slate-700 leading-none">{step.label}</p>
                                                         <p className="text-xs text-slate-500 mt-1.5 bg-slate-50 inline-block px-2 py-0.5 rounded border border-slate-100 italic">
                                                             {step.detail}
                                                         </p>
                                                     </div>
                                                 </div>
                                             ))}
                                         </div>
                                     </div>
                                     )}
                                 </div>
                             )}
                             {!step3Result && !loadingStep3 && (
                                 <div className="p-8 text-center text-slate-400 text-sm">
                                     Execute the CMIR Resolution to view the waterfall mapping results.
                                 </div>
                             )}
                         </div>
                     </div>
                 </div>
              </div>
            </div>
          )}
        </div>
      </main>
      
      {/* ADD GLOBAL SCROLLBAR CSS */}
      <style dangerouslySetInnerHTML={{__html: `
         .custom-scrollbar::-webkit-scrollbar {
             width: 6px;
         }
         .custom-scrollbar::-webkit-scrollbar-track {
             background: #f8fafc; 
             border-radius: 4px;
         }
         .custom-scrollbar::-webkit-scrollbar-thumb {
             background: #cbd5e1; 
             border-radius: 4px;
         }
         .custom-scrollbar::-webkit-scrollbar-thumb:hover {
             background: #94a3b8; 
         }
      `}} />
    </div>
  );
}
