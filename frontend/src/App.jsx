import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import { 
  uploadFile, 
  getProfile, 
  cleanDataset, 
  runValidation, 
  scanOutliers, 
  treatOutliers, 
  runPostStratification, 
  computeEstimation, 
  getInsights, 
  getAuditLogs, 
  generateReport 
} from './services/api';
import { 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Scale, 
  FileDown, 
  RefreshCw, 
  Upload, 
  Activity,
  Layers
} from 'lucide-react';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [activeDataset, setActiveDataset] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [estimationResult, setEstimationResult] = useState(null);
  
  // Pipeline State
  const [validationViolations, setValidationViolations] = useState([]);
  const [outlierResults, setOutlierResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const notify = (msg, type = 'info') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4500);
  };

  // Demo auto-loader
  const loadDemoDataset = async () => {
    setLoading(true);
    try {
      // Direct load synthetic profile
      const res = await getProfile(1);
      setActiveDataset({ id: res.dataset_id, filename: res.filename, status: res.status });
      setProfileData(res.profile);
      const ins = await getInsights(res.dataset_id);
      setInsightsData(ins.insights);
      const logs = await getAuditLogs(res.dataset_id);
      setAuditLogs(logs);
      notify('Demo Synthetic Household Survey loaded successfully!', 'success');
    } catch (err) {
      notify('Could not load demo dataset. Please upload the generated CSV from data/uploads.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadFile(file);
      setActiveDataset(data);
      setProfileData(data.summary_metrics);
      const ins = await getInsights(data.id);
      setInsightsData(ins.insights);
      const logs = await getAuditLogs(data.id);
      setAuditLogs(logs);
      notify(`Dataset '${file.name}' ingested and profiled!`, 'success');
      setCurrentTab('dashboard');
    } catch (err) {
      notify(err.response?.data?.detail || 'Failed to upload dataset.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRunCleaning = async () => {
    if (!activeDataset) return;
    setLoading(true);
    try {
      const ops = [
        { type: 'deduplicate', action: 'remove' },
        { type: 'impute', column: 'income', method: 'median' },
        { type: 'impute', column: 'education', method: 'mode' },
        { type: 'strip_whitespace' }
      ];
      const res = await cleanDataset(activeDataset.id, ops);
      notify(`Cleaning Complete! Quality Score raised to ${res.new_quality_score}/100`, 'success');
      // Refresh profile
      const prof = await getProfile(activeDataset.id);
      setProfileData(prof.profile);
      setActiveDataset(prev => ({ ...prev, status: 'CLEANED' }));
      const logs = await getAuditLogs(activeDataset.id);
      setAuditLogs(logs);
    } catch (err) {
      notify(err.response?.data?.detail || 'Cleaning execution failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRunValidation = async () => {
    if (!activeDataset) return;
    setLoading(true);
    try {
      const res = await runValidation(activeDataset.id);
      setValidationViolations(res.violations);
      notify(`Validation completed. Evaluated ${res.rules_evaluated} rules with ${res.total_violations} flags.`, 'info');
      const logs = await getAuditLogs(activeDataset.id);
      setAuditLogs(logs);
    } catch (err) {
      notify('Validation failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleScanOutliers = async () => {
    if (!activeDataset) return;
    setLoading(true);
    try {
      const res = await scanOutliers(activeDataset.id, 'iqr');
      setOutlierResults(res.anomalies);
      notify(`Identified ${res.total_anomalies} IQR numeric anomalies.`, 'info');
    } catch (err) {
      notify('Outlier scan failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyWeighting = async () => {
    if (!activeDataset) return;
    setLoading(true);
    try {
      const popDist = {
        "Maharashtra": 120000000,
        "Uttar Pradesh": 230000000,
        "Tamil Nadu": 75000000,
        "West Bengal": 99000000,
        "Gujarat": 70000000,
        "Karnataka": 68000000,
        "Bihar": 125000000
      };
      const res = await runPostStratification(activeDataset.id, 'state', popDist, 'survey_weight');
      notify(`Survey weights calibrated! Kish Eff Sample Size: ${res.diagnostics.effective_sample_size}`, 'success');
      setActiveDataset(prev => ({ ...prev, status: 'WEIGHTED' }));
      const logs = await getAuditLogs(activeDataset.id);
      setAuditLogs(logs);
    } catch (err) {
      notify('Weighting adjustment failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleComputeEstimation = async () => {
    if (!activeDataset) return;
    setLoading(true);
    try {
      const res = await computeEstimation(activeDataset.id, 'income', 'survey_weight', 0.95);
      setEstimationResult(res);
      notify(`Estimation completed for target variable 'income'.`, 'success');
      const logs = await getAuditLogs(activeDataset.id);
      setAuditLogs(logs);
    } catch (err) {
      notify(err.response?.data?.detail || 'Estimation computation failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async (type = 'PDF') => {
    if (!activeDataset) return;
    setLoading(true);
    try {
      const res = await generateReport(activeDataset.id, type, estimationResult);
      window.open(`http://127.0.0.1:8000${res.download_url}`, '_blank');
      notify(`Generated and downloaded ${type} report release!`, 'success');
      const logs = await getAuditLogs(activeDataset.id);
      setAuditLogs(logs);
    } catch (err) {
      notify('Report generation failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      <Navbar activeDataset={activeDataset} />

      {notification && (
        <div className={`fixed top-16 right-6 z-50 px-4 py-3 rounded-lg shadow-lg border text-sm font-medium transition-all ${
          notification.type === 'success' 
            ? 'bg-emerald-950/90 text-emerald-200 border-emerald-800' 
            : notification.type === 'error' 
            ? 'bg-rose-950/90 text-rose-200 border-rose-800' 
            : 'bg-sky-950/90 text-sky-200 border-sky-800'
        }`}>
          {notification.msg}
        </div>
      )}

      <div className="flex flex-1">
        <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

        <main className="flex-1 p-8 bg-slate-950 overflow-y-auto max-w-7xl">
          
          {/* TAB 1: OVERVIEW & PROFILE */}
          {currentTab === 'dashboard' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-slate-50">Survey Analytical Dashboard</h2>
                  <p className="text-slate-400 text-sm">Real-time data quality score & statistical distribution profiles</p>
                </div>
                {!activeDataset && (
                  <button 
                    onClick={loadDemoDataset}
                    className="bg-sky-600 hover:bg-sky-500 text-white font-medium px-4 py-2 rounded-lg text-sm flex items-center space-x-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Load Demo MoSPI Dataset</span>
                  </button>
                )}
              </div>

              {profileData ? (
                <>
                  {/* Top Quality Metric Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
                    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                      <div className="text-slate-400 text-xs font-semibold uppercase">Total Records</div>
                      <div className="text-3xl font-bold mt-2 text-sky-400">{profileData.total_rows.toLocaleString()}</div>
                      <div className="text-xs text-slate-400 mt-1">{profileData.total_columns} Attributes Detected</div>
                    </div>
                    
                    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                      <div className="text-slate-400 text-xs font-semibold uppercase">Data Quality Score</div>
                      <div className="text-3xl font-bold mt-2 text-emerald-400">{profileData.quality_score.overall_score}/100</div>
                      <div className="text-xs text-slate-400 mt-1">Application-defined Index</div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                      <div className="text-slate-400 text-xs font-semibold uppercase">Duplicate Records</div>
                      <div className="text-3xl font-bold mt-2 text-amber-400">{profileData.duplicate_rows}</div>
                      <div className="text-xs text-slate-400 mt-1">Deduplication suggested</div>
                    </div>

                    <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl">
                      <div className="text-slate-400 text-xs font-semibold uppercase">Memory Footprint</div>
                      <div className="text-3xl font-bold mt-2 text-purple-400">{(profileData.memory_usage_bytes / 1024).toFixed(1)} KB</div>
                      <div className="text-xs text-slate-400 mt-1">Optimized in-memory store</div>
                    </div>
                  </div>

                  {/* AI Executive Insights Card */}
                  {insightsData && (
                    <div className="bg-gradient-to-r from-sky-950/40 to-indigo-950/40 border border-sky-800/40 p-6 rounded-xl">
                      <div className="flex items-center space-x-2 text-sky-400 font-semibold mb-2">
                        <Sparkles className="w-5 h-5" />
                        <span>Automated AI Quality Assessment</span>
                      </div>
                      <p className="text-slate-200 text-sm leading-relaxed">{insightsData.executive_summary}</p>
                    </div>
                  )}

                  {/* Column Profile Table */}
                  <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                    <div className="p-4 border-b border-slate-800 font-semibold text-slate-200 text-sm">
                      Attribute Level Profiling & Missingness Diagnostics
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-slate-800/60 text-xs uppercase text-slate-400">
                          <tr>
                            <th className="p-3.5">Column</th>
                            <th className="p-3.5">Type</th>
                            <th className="p-3.5">Missingness</th>
                            <th className="p-3.5">Unique Values</th>
                            <th className="p-3.5">Mean / Distribution</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                          {Object.entries(profileData.columns).map(([colName, col]) => (
                            <tr key={colName} className="hover:bg-slate-800/30">
                              <td className="p-3.5 font-medium text-slate-100">{colName}</td>
                              <td className="p-3.5">
                                <span className={`text-[11px] px-2 py-0.5 rounded font-mono ${
                                  col.type === 'numeric' ? 'bg-sky-950 text-sky-300 border border-sky-800' : 'bg-slate-800 text-slate-300'
                                }`}>
                                  {col.type || col.dtype}
                                </span>
                              </td>
                              <td className="p-3.5">
                                <span className={col.missing_percentage > 0 ? 'text-amber-400 font-semibold' : 'text-slate-400'}>
                                  {col.missing_percentage}% ({col.missing_count})
                                </span>
                              </td>
                              <td className="p-3.5">{col.unique_count}</td>
                              <td className="p-3.5 text-xs text-slate-400">
                                {col.type === 'numeric' ? `Mean: ${col.mean} | Median: ${col.median}` : 'Categorical values'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-24 bg-slate-900/50 border border-dashed border-slate-800 rounded-xl">
                  <Layers className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400 font-medium">No active dataset selected.</p>
                  <p className="text-xs text-slate-400 mt-1">Upload a CSV or Click 'Load Demo MoSPI Dataset' to begin.</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: UPLOAD & INGEST */}
          {currentTab === 'upload' && (
            <div className="space-y-6 max-w-2xl mx-auto">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-slate-50">Data Ingestion Engine</h2>
                <p className="text-slate-400 text-sm mt-1">Upload raw survey files (.csv, .xlsx) for automatic schema mapping</p>
              </div>

              <div className="bg-slate-900 border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-2xl p-12 text-center transition-all cursor-pointer">
                <input 
                  type="file" 
                  accept=".csv,.xlsx,.xls" 
                  onChange={handleFileUpload} 
                  className="hidden" 
                  id="file-upload-input" 
                />
                <label htmlFor="file-upload-input" className="cursor-pointer flex flex-col items-center">
                  <div className="bg-sky-950 p-4 rounded-full text-sky-400 mb-4 border border-sky-800">
                    <Upload className="w-8 h-8" />
                  </div>
                  <span className="text-base font-semibold text-slate-100">Click to upload raw survey input</span>
                  <span className="text-xs text-slate-400 mt-2">Supports official MoSPI CSV and Excel survey formats</span>
                </label>
              </div>
            </div>
          )}

          {/* TAB 3: CLEAN & IMPUTE */}
          {currentTab === 'clean' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-50">Data Cleaning & Imputation</h2>
                <p className="text-slate-400 text-sm">Non-destructive batch imputation and deduplication engine</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
                <h3 className="text-base font-semibold text-slate-200">Recommended Cleaning Pipeline:</h3>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-400" />
                    <span>Deduplication: Remove fully duplicate records from dataset</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-400" />
                    <span>Impute <b>income</b> missingness using <b>Median Imputation</b></span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-400" />
                    <span>Impute <b>education</b> missingness using <b>Mode Imputation</b></span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-400" />
                    <span>Normalize text columns and strip leading/trailing whitespace</span>
                  </li>
                </ul>

                <button 
                  onClick={handleRunCleaning}
                  disabled={loading || !activeDataset}
                  className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium px-5 py-2.5 rounded-lg text-sm flex items-center space-x-2 mt-4"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Execute Approved Cleaning Operations</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 4: RULE VALIDATION */}
          {currentTab === 'validate' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-slate-50">Rule Validation & Consistency Checks</h2>
                  <p className="text-slate-400 text-sm">Evaluates survey bounds, skip patterns, and cross-attribute logic</p>
                </div>
                <button 
                  onClick={handleRunValidation}
                  disabled={loading || !activeDataset}
                  className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-medium px-4 py-2 rounded-lg text-sm flex items-center space-x-2"
                >
                  <Activity className="w-4 h-4" />
                  <span>Run MoSPI Rule Suite</span>
                </button>
              </div>

              {validationViolations.length > 0 ? (
                <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/60 text-xs uppercase text-slate-400">
                      <tr>
                        <th className="p-3.5">Rule Name</th>
                        <th className="p-3.5">Row Index</th>
                        <th className="p-3.5">Flagged Value</th>
                        <th className="p-3.5">Violation Detail</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {validationViolations.map((v, i) => (
                        <tr key={i} className="hover:bg-slate-800/30">
                          <td className="p-3.5 font-medium text-rose-400">{v.rule_name}</td>
                          <td className="p-3.5 font-mono text-xs text-slate-400">Row #{v.row_index}</td>
                          <td className="p-3.5 font-mono text-xs">{v.value}</td>
                          <td className="p-3.5 text-xs text-slate-300">{v.message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-400 text-sm">
                  Click 'Run MoSPI Rule Suite' to evaluate dataset consistency.
                </div>
              )}
            </div>
          )}

          {/* TAB 5: OUTLIERS */}
          {currentTab === 'outliers' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-slate-50">Outlier Detection (IQR / Z-Score)</h2>
                  <p className="text-slate-400 text-sm">Identifies statistical anomalies without destructive automated actions</p>
                </div>
                <button 
                  onClick={handleScanOutliers}
                  disabled={loading || !activeDataset}
                  className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-medium px-4 py-2 rounded-lg text-sm flex items-center space-x-2"
                >
                  <AlertCircle className="w-4 h-4" />
                  <span>Scan IQR Outliers</span>
                </button>
              </div>

              {outlierResults.length > 0 && (
                <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/60 text-xs uppercase text-slate-400">
                      <tr>
                        <th className="p-3.5">Row Index</th>
                        <th className="p-3.5">Column</th>
                        <th className="p-3.5">Detected Value</th>
                        <th className="p-3.5">Detection Method</th>
                        <th className="p-3.5">Recommendation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {outlierResults.map((o, i) => (
                        <tr key={i} className="hover:bg-slate-800/30">
                          <td className="p-3.5 font-mono text-xs text-slate-400">#{o.row_index}</td>
                          <td className="p-3.5 font-medium text-slate-200">{o.column}</td>
                          <td className="p-3.5 font-mono text-amber-400">{o.value?.toLocaleString()}</td>
                          <td className="p-3.5 text-xs">{o.method}</td>
                          <td className="p-3.5 text-xs text-sky-400">{o.recommended_action}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* TAB 6: WEIGHTING */}
          {currentTab === 'weighting' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-50">Survey Weight Calibration</h2>
                <p className="text-slate-400 text-sm">Post-stratification & Raking against external population totals</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
                <p className="text-sm text-slate-300">
                  Calibrate sampling weights across geographic strata (<b>state</b>) against target regional census distributions.
                </p>
                <button 
                  onClick={handleApplyWeighting}
                  disabled={loading || !activeDataset}
                  className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium px-5 py-2.5 rounded-lg text-sm flex items-center space-x-2"
                >
                  <Scale className="w-4 h-4" />
                  <span>Execute Post-Stratification Weighting</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 7: ESTIMATION */}
          {currentTab === 'estimation' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold text-slate-50">Statistical Estimation & Uncertainty</h2>
                  <p className="text-slate-400 text-sm">Weighted vs. Unweighted side-by-side estimates with Taylor Linearization MoE</p>
                </div>
                <button 
                  onClick={handleComputeEstimation}
                  disabled={loading || !activeDataset}
                  className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-medium px-4 py-2 rounded-lg text-sm flex items-center space-x-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Compute Income Estimates</span>
                </button>
              </div>

              {estimationResult && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Unweighted Card */}
                  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Unweighted Sample Estimate</div>
                    <div className="text-3xl font-bold mt-2 text-slate-100">
                      ₹{estimationResult.unweighted.point_estimate?.toLocaleString()}
                    </div>
                    <div className="mt-4 space-y-1.5 text-xs text-slate-400 border-t border-slate-800 pt-3">
                      <div>Std Error: <span className="text-slate-200">₹{estimationResult.unweighted.standard_error}</span></div>
                      <div>Margin of Error: <span className="text-slate-200">±₹{estimationResult.unweighted.margin_of_error}</span></div>
                      <div>95% CI: <span className="text-slate-200">[{estimationResult.unweighted.confidence_interval[0]}, {estimationResult.unweighted.confidence_interval[1]}]</span></div>
                    </div>
                  </div>

                  {/* Weighted Card */}
                  <div className="bg-gradient-to-br from-slate-900 to-sky-950/40 border border-sky-800/50 p-6 rounded-xl">
                    <div className="text-xs font-semibold text-sky-400 uppercase tracking-wide">Survey-Weighted Population Estimate</div>
                    <div className="text-3xl font-bold mt-2 text-sky-300">
                      ₹{estimationResult.weighted?.point_estimate?.toLocaleString()}
                    </div>
                    <div className="mt-4 space-y-1.5 text-xs text-slate-400 border-t border-sky-900/50 pt-3">
                      <div>Taylor Linearization Std Error: <span className="text-sky-200">₹{estimationResult.weighted?.standard_error}</span></div>
                      <div>Margin of Error: <span className="text-sky-200">±₹{estimationResult.weighted?.margin_of_error}</span></div>
                      <div>95% CI: <span className="text-sky-200">[{estimationResult.weighted?.confidence_interval[0]}, {estimationResult.weighted?.confidence_interval[1]}]</span></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 8: OFFICIAL REPORTS */}
          {currentTab === 'reports' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-50">Official Statistical Release Generator</h2>
                <p className="text-slate-400 text-sm">Download publication-ready PDF and HTML report releases</p>
              </div>

              <div className="flex space-x-4">
                <button 
                  onClick={() => handleDownloadReport('PDF')}
                  disabled={loading || !activeDataset}
                  className="bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white font-medium px-5 py-3 rounded-xl text-sm flex items-center space-x-2"
                >
                  <FileDown className="w-5 h-5" />
                  <span>Download Official PDF Release</span>
                </button>

                <button 
                  onClick={() => handleDownloadReport('HTML')}
                  disabled={loading || !activeDataset}
                  className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-medium px-5 py-3 rounded-xl text-sm flex items-center space-x-2"
                >
                  <FileDown className="w-5 h-5" />
                  <span>Download Interactive HTML Report</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB 9: AUDIT TRAIL */}
          {currentTab === 'audit' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-50">Reproducibility & Audit Trail</h2>
                <p className="text-slate-400 text-sm">Chronological record of every data manipulation and analytical operation</p>
              </div>

              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-800/60 text-xs uppercase text-slate-400">
                    <tr>
                      <th className="p-3.5">Timestamp (UTC)</th>
                      <th className="p-3.5">Module</th>
                      <th className="p-3.5">Action</th>
                      <th className="p-3.5">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-800/30">
                        <td className="p-3.5 font-mono text-xs text-slate-400">{log.timestamp.replace('T', ' ').substring(0, 19)}</td>
                        <td className="p-3.5 font-semibold text-sky-400 text-xs">{log.module}</td>
                        <td className="p-3.5 text-xs font-mono text-slate-200">{log.action}</td>
                        <td className="p-3.5 text-xs text-slate-300">{log.details}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}