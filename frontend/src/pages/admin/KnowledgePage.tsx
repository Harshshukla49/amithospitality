import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Upload,
  FileText,
  Search,
  Filter,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Plus,
  Trash2,
  Eye,
  FileSpreadsheet,
  FileCode,
  ShieldCheck,
  ShieldAlert,
  Database,
  Layers,
  Sparkles,
  ToggleLeft,
  ToggleRight,
  HelpCircle,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { KnowledgeDocument, Environment } from '../../types';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import {
  fetchDocuments,
  fetchDocumentDetail,
  uploadDocument,
  createManualKnowledge,
  toggleDocumentStatus,
  reprocessDocument,
  deleteDocumentApi,
  searchKnowledge,
  fetchKnowledgeStats,
  BackendKnowledgeDoc,
  BackendKnowledgeDocDetail,
  BackendSearchHit,
  BackendKnowledgeStats,
} from '../../api/knowledge';

interface KnowledgePageProps {
  documents?: KnowledgeDocument[];
  onAddDocument?: (doc: KnowledgeDocument) => void;
  onDeleteDocument?: (id: number) => void;
}

export const KnowledgePage: React.FC<KnowledgePageProps> = () => {
  const { environment, isDemo, openSwitchModal } = useEnvironment();
  const [selectedEnvTab, setSelectedEnvTab] = useState<Environment>(environment);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedOutletId, setSelectedOutletId] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');

  // Live Backend State
  const [docs, setDocs] = useState<BackendKnowledgeDoc[]>([]);
  const [stats, setStats] = useState<BackendKnowledgeStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Modals
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isManualModalOpen, setIsManualModalOpen] = useState(false);
  const [inspectDoc, setInspectDoc] = useState<BackendKnowledgeDocDetail | null>(null);
  const [isInspectingLoading, setIsInspectingLoading] = useState(false);

  // Upload Form State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadCategory, setUploadCategory] = useState<'MENU' | 'POLICY' | 'TIMING' | 'EVENT' | 'GENERAL'>('POLICY');
  const [uploadOutletId, setUploadOutletId] = useState<number | ''>('');

  // Manual Creation State
  const [manualTitle, setManualTitle] = useState('');
  const [manualCategory, setManualCategory] = useState<'MENU' | 'POLICY' | 'TIMING' | 'EVENT' | 'GENERAL'>('POLICY');
  const [manualOutletId, setManualOutletId] = useState<number | ''>('');
  const [manualContent, setManualContent] = useState('');

  // Semantic Search Sandbox State
  const [isSandboxOpen, setIsSandboxOpen] = useState(false);
  const [sandboxQuery, setSandboxQuery] = useState('What are the rooftop dress code guidelines?');
  const [sandboxOutletId, setSandboxOutletId] = useState<string>('ALL');
  const [sandboxResults, setSandboxResults] = useState<BackendSearchHit[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Auto-dismiss notification
  useEffect(() => {
    if (actionMessage) {
      const timer = setTimeout(() => setActionMessage(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [actionMessage]);

  // Load documents and stats from backend
  const loadData = async () => {
    setIsLoading(true);
    try {
      const [fetchedDocs, fetchedStats] = await Promise.all([
        fetchDocuments({
          environment: selectedEnvTab,
          category: selectedCategory !== 'ALL' ? selectedCategory : undefined,
          outlet_id: selectedOutletId !== 'ALL' ? Number(selectedOutletId) : undefined,
          status: selectedStatus !== 'ALL' ? selectedStatus : undefined,
        }),
        fetchKnowledgeStats().catch(() => null),
      ]);
      setDocs(fetchedDocs);
      if (fetchedStats) setStats(fetchedStats);
    } catch (err: any) {
      console.warn('API error loading documents, falling back or empty state:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedEnvTab, selectedCategory, selectedOutletId, selectedStatus]);

  // Filter in memory for instantaneous search response
  const filteredDocs = docs.filter((doc) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return doc.title.toLowerCase().includes(q) || doc.file_name.toLowerCase().includes(q);
  });

  // Handle Real File Upload
  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('environment', selectedEnvTab);
      if (uploadOutletId !== '') {
        formData.append('outlet_id', String(uploadOutletId));
      }
      formData.append('category', uploadCategory);

      await uploadDocument(formData);
      setActionMessage({
        type: 'success',
        text: `Successfully uploaded, chunked, and vector-indexed '${uploadFile.name}' into ${selectedEnvTab} knowledge base.`,
      });
      setIsUploadModalOpen(false);
      setUploadFile(null);
      await loadData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Upload failed: ${err.message}` });
    } finally {
      setIsUploading(false);
    }
  };

  // Handle Manual Knowledge Submission
  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualTitle || !manualContent) return;

    try {
      await createManualKnowledge({
        title: manualTitle,
        content: manualContent,
        category: manualCategory,
        outlet_id: manualOutletId !== '' ? Number(manualOutletId) : undefined,
        environment: selectedEnvTab,
      });

      setActionMessage({
        type: 'success',
        text: `Indexed manual entry '${manualTitle}' into ${selectedEnvTab} knowledge base.`,
      });
      setIsManualModalOpen(false);
      setManualTitle('');
      setManualContent('');
      await loadData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Error adding entry: ${err.message}` });
    }
  };

  // Inspect Chunks
  const handleInspectDocument = async (docId: number) => {
    setIsInspectingLoading(true);
    try {
      const detail = await fetchDocumentDetail(docId);
      setInspectDoc(detail);
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Failed to inspect document: ${err.message}` });
    } finally {
      setIsInspectingLoading(false);
    }
  };

  // Toggle Active/Inactive
  const handleToggleStatus = async (doc: BackendKnowledgeDoc) => {
    try {
      const updated = await toggleDocumentStatus(doc.id, !doc.is_active);
      setActionMessage({
        type: 'success',
        text: `Document '${updated.title}' ${updated.is_active ? 'activated' : 'deactivated'}.`,
      });
      await loadData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Failed to toggle status: ${err.message}` });
    }
  };

  // Reprocess Document
  const handleReprocess = async (docId: number, title: string) => {
    try {
      await reprocessDocument(docId);
      setActionMessage({
        type: 'success',
        text: `Successfully reprocessed and re-indexed all vector chunks for '${title}'.`,
      });
      await loadData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Reprocess failed: ${err.message}` });
    }
  };

  // Delete Document
  const handleDelete = async (docId: number, title: string) => {
    if (!window.confirm(`Are you sure you want to permanently delete '${title}' and all its vector chunks?`)) {
      return;
    }
    try {
      await deleteDocumentApi(docId);
      setActionMessage({
        type: 'success',
        text: `Deleted '${title}' and associated vector embeddings.`,
      });
      await loadData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Delete failed: ${err.message}` });
    }
  };

  // Run Semantic Search Sandbox Query
  const handleRunSearch = async () => {
    if (!sandboxQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await searchKnowledge({
        q: sandboxQuery,
        environment: selectedEnvTab,
        outlet_id: sandboxOutletId !== 'ALL' ? Number(sandboxOutletId) : undefined,
        top_k: 5,
      });
      setSandboxResults(res.results);
    } catch (err: any) {
      setActionMessage({ type: 'error', text: `Semantic search failed: ${err.message}` });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {actionMessage && (
        <div
          className={`p-3.5 rounded-xl border flex items-center justify-between text-xs transition-all shadow-luxury ${
            actionMessage.type === 'success'
              ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-200'
              : 'bg-rose-950/80 border-rose-500/50 text-rose-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {actionMessage.type === 'success' ? (
              <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{actionMessage.text}</span>
          </div>
          <button onClick={() => setActionMessage(null)} className="text-slate-400 hover:text-white ml-3">
            ✕
          </button>
        </div>
      )}

      {/* Top Header & Environment Scope Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" />
              Dual-Environment Knowledge Base
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Knowledge Base & RAG Management
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Ingest and verify PDFs, menus, and policies. Strict isolation guarantees DEMO and REAL stores never mix or leak.
          </p>
        </div>

        {/* Environment Scope Switcher Tabs */}
        <div className="flex items-center p-1 rounded-xl bg-charcoal-900 border border-slate-700/80 self-start md:self-auto shadow-inner">
          <button
            onClick={() => setSelectedEnvTab('DEMO')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
              selectedEnvTab === 'DEMO'
                ? 'bg-amber-500/20 text-gold-300 border border-gold-400/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>DEMO KNOWLEDGE</span>
            {selectedEnvTab === 'DEMO' && environment === 'DEMO' && (
              <span className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-pulse" />
            )}
          </button>
          <button
            onClick={() => setSelectedEnvTab('REAL')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
              selectedEnvTab === 'REAL'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <span>REAL KNOWLEDGE</span>
            {selectedEnvTab === 'REAL' && environment === 'REAL' && (
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            )}
          </button>
        </div>
      </div>

      {/* Aggregate Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] uppercase tracking-wider font-medium">Active Store</span>
            <Database className="w-3.5 h-3.5 text-gold-400" />
          </div>
          <div className="text-lg font-serif font-bold text-white flex items-center gap-2">
            <span>{selectedEnvTab} REPOSITORY</span>
            <span
              className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                selectedEnvTab === 'DEMO'
                  ? 'bg-amber-500/20 text-gold-400 border border-amber-500/30'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}
            >
              {selectedEnvTab === environment ? 'LIVE IN AI' : 'STANDBY'}
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            {selectedEnvTab === 'DEMO' ? 'Fictional sample records' : 'Verified corporate assets'}
          </p>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] uppercase tracking-wider font-medium">Documents</span>
            <Layers className="w-3.5 h-3.5 text-slate-300" />
          </div>
          <div className="text-lg font-serif font-bold text-white">
            {stats ? (selectedEnvTab === 'DEMO' ? stats.demo_doc_count : stats.real_doc_count) : docs.length}{' '}
            <span className="text-xs font-sans text-slate-400 font-normal">indexed</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            {filteredDocs.filter((d) => d.is_active).length} currently active
          </p>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] uppercase tracking-wider font-medium">Vector Chunks</span>
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
          </div>
          <div className="text-lg font-serif font-bold text-gold-300">
            {stats
              ? selectedEnvTab === 'DEMO'
                ? stats.demo_chunk_count
                : stats.real_chunk_count
              : docs.reduce((acc, d) => acc + d.chunk_count, 0)}{' '}
            <span className="text-xs font-sans text-slate-400 font-normal">vectors</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Semantic 256-dim embeddings</p>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] uppercase tracking-wider font-medium">Verification</span>
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-lg font-serif font-bold text-white">
            {selectedEnvTab === 'REAL' ? (
              <span className="text-emerald-400">100% VERIFIED</span>
            ) : (
              <span className="text-amber-400 font-mono text-base">UNVERIFIED DEMO</span>
            )}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            {selectedEnvTab === 'REAL' ? 'Authorized corporate audit' : 'Presentation mockups'}
          </p>
        </div>
      </div>

      {/* Scope Advisory Banner */}
      <div
        className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs ${
          selectedEnvTab === 'DEMO'
            ? 'bg-amber-500/10 border-gold-400/30 text-gold-300'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
        }`}
      >
        <div className="flex items-center gap-2.5">
          {selectedEnvTab === 'DEMO' ? (
            <AlertTriangle className="w-5 h-5 text-gold-400 shrink-0" />
          ) : (
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          )}
          <div>
            <p className="font-semibold text-white">
              Viewing {selectedEnvTab} Knowledge Repository{' '}
              {environment !== selectedEnvTab && (
                <span className="text-[11px] font-mono text-slate-400">
                  (Note: Live AI Concierge is currently set to {environment} Mode)
                </span>
              )}
            </p>
            <p className="text-slate-300 text-[11px] mt-0.5">
              {selectedEnvTab === 'DEMO'
                ? 'All pricing, menus, timings, and policies here are fictional sample data for client presentation.'
                : 'Verified company knowledge. The AI only references these verified assets when REAL mode is active.'}
            </p>
          </div>
        </div>

        {environment !== selectedEnvTab && (
          <button
            onClick={() => openSwitchModal(selectedEnvTab)}
            className="px-3.5 py-1.5 rounded-lg bg-charcoal-900 border border-slate-700 hover:border-gold-400 text-xs text-white shrink-0 transition shadow-sm"
          >
            Switch System to {selectedEnvTab} Mode
          </button>
        )}
      </div>

      {/* Controls: Search, Filters, Upload, Add Manual, Sandbox Toggle */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="flex flex-1 flex-wrap items-center gap-2">
          {/* Search Bar */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search documents by title or file name..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
            />
          </div>

          {/* Outlet Filter */}
          <select
            value={selectedOutletId}
            onChange={(e) => setSelectedOutletId(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Outlets</option>
            {INITIAL_OUTLETS.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Categories</option>
            <option value="MENU">Menus & Pricing</option>
            <option value="TIMING">Timings & Locations</option>
            <option value="POLICY">Dress Code & Policies</option>
            <option value="EVENT">Events & Banquets</option>
            <option value="GENERAL">General FAQs</option>
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Status</option>
            <option value="ACTIVE">Active Only</option>
            <option value="INACTIVE">Inactive Only</option>
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => setIsSandboxOpen(!isSandboxOpen)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border text-xs font-semibold transition ${
              isSandboxOpen
                ? 'bg-gold-500/20 border-gold-400 text-gold-300'
                : 'bg-charcoal-900 border-slate-700 text-slate-300 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
            <span>Search Sandbox</span>
          </button>

          <button
            onClick={() => setIsManualModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 border border-slate-700 text-xs text-slate-200 transition"
          >
            <Plus className="w-3.5 h-3.5 text-gold-400" />
            <span>Manual Entry</span>
          </button>

          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* Semantic Search Sandbox Drawer / Accordion */}
      {isSandboxOpen && (
        <div className="p-5 rounded-2xl glass-panel-elevated border border-gold-400/40 space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-gold-400" />
              <h3 className="text-sm font-serif font-bold text-white tracking-wide">
                Interactive Semantic Retrieval Sandbox ({selectedEnvTab} Store)
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              Cosine Similarity + Lexical Token Overlap
            </span>
          </div>

          <p className="text-xs text-slate-300">
            Test vector retrieval in real-time. Verify that queries against <strong className="text-gold-400">{selectedEnvTab}</strong> only match documents from this active scope and never leak across stores.
          </p>

          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={sandboxQuery}
              onChange={(e) => setSandboxQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleRunSearch()}
              placeholder="Enter customer question or query (e.g. 'What is the dress code for Amber Terrace?')..."
              className="flex-1 px-3.5 py-2.5 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
            />
            <select
              value={sandboxOutletId}
              onChange={(e) => setSandboxOutletId(e.target.value)}
              className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
            >
              <option value="ALL">All Outlets</option>
              {INITIAL_OUTLETS.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleRunSearch}
              disabled={isSearching}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 shadow-gold-glow transition disabled:opacity-50 flex items-center justify-center gap-1.5 shrink-0"
            >
              {isSearching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              <span>Test Search</span>
            </button>
          </div>

          {/* Sandbox Results */}
          {sandboxResults.length > 0 && (
            <div className="space-y-2.5 pt-2">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                Top {sandboxResults.length} Vector Match(es) Found:
              </div>
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {sandboxResults.map((hit, idx) => (
                  <div
                    key={hit.chunk_id || idx}
                    className="p-3.5 rounded-xl bg-charcoal-900/90 border border-slate-700/80 text-xs space-y-1.5"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 text-[11px]">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{hit.document_title}</span>
                        <span className="px-1.5 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700 text-[10px] font-mono">
                          {hit.category}
                        </span>
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold ${
                            hit.environment === 'REAL'
                              ? 'bg-emerald-500/20 text-emerald-300'
                              : 'bg-amber-500/20 text-gold-300'
                          }`}
                        >
                          {hit.environment} STORE
                        </span>
                      </div>
                      <div className="flex items-center gap-3 font-mono text-slate-400 text-[10px]">
                        <span>Score: <strong className="text-gold-400">{(hit.score * 100).toFixed(1)}%</strong></span>
                        <span>Cosine: {(hit.cosine_similarity * 100).toFixed(1)}%</span>
                        <span>Lexical: {(hit.lexical_overlap * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    <p className="text-slate-300 text-xs leading-relaxed bg-charcoal-950/60 p-2.5 rounded-lg border border-slate-800 font-sans">
                      {hit.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Documents Table View */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden shadow-luxury">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Document Title</th>
                <th className="py-3 px-4">Outlet</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Chunks</th>
                <th className="py-3 px-4">Verification</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin text-gold-400 mx-auto mb-2" />
                    <span>Loading {selectedEnvTab} knowledge store...</span>
                  </td>
                </tr>
              ) : filteredDocs.length > 0 ? (
                filteredDocs.map((doc) => {
                  const outlet = INITIAL_OUTLETS.find((o) => o.id === doc.outlet_id);
                  return (
                    <tr
                      key={doc.id}
                      className={`hover:bg-charcoal-800/40 transition ${
                        !doc.is_active ? 'opacity-50 bg-charcoal-950/40' : ''
                      }`}
                    >
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="p-2 rounded-lg bg-charcoal-800 text-gold-400 border border-slate-700">
                            {doc.file_type === 'PDF' && <FileText className="w-4 h-4" />}
                            {doc.file_type === 'XLSX' && <FileSpreadsheet className="w-4 h-4" />}
                            {doc.file_type === 'DOCX' && <FileText className="w-4 h-4" />}
                            {doc.file_type === 'MANUAL' && <FileCode className="w-4 h-4" />}
                            {doc.file_type === 'CSV' && <FileSpreadsheet className="w-4 h-4" />}
                            {doc.file_type === 'TXT' && <FileText className="w-4 h-4" />}
                          </div>
                          <div>
                            <p className="font-semibold text-white">{doc.title}</p>
                            <p className="text-[11px] text-slate-500 font-mono">{doc.file_name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-medium text-slate-200">
                        {outlet ? outlet.name : 'Enterprise-wide'}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700 text-[10px] font-mono">
                          {doc.category}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                        {doc.file_type}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">
                        {doc.chunk_count} vectors
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                            doc.verification_status === 'VERIFIED'
                              ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                              : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          }`}
                        >
                          {doc.verification_status === 'VERIFIED' ? (
                            <CheckCircle className="w-3 h-3" />
                          ) : (
                            <AlertTriangle className="w-3 h-3" />
                          )}
                          <span>{doc.verification_status}</span>
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <button
                          onClick={() => handleToggleStatus(doc)}
                          className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white"
                          title={doc.is_active ? 'Click to deactivate' : 'Click to activate'}
                        >
                          {doc.is_active ? (
                            <>
                              <span className="w-2 h-2 rounded-full bg-emerald-400" />
                              <span className="text-emerald-400 font-medium">Active</span>
                            </>
                          ) : (
                            <>
                              <span className="w-2 h-2 rounded-full bg-slate-500" />
                              <span className="text-slate-500 font-medium">Inactive</span>
                            </>
                          )}
                        </button>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleInspectDocument(doc.id)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-gold-400 hover:bg-charcoal-800 transition"
                            title="Inspect Chunks"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleReprocess(doc.id, doc.title)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-gold-400 hover:bg-charcoal-800 transition"
                            title="Reprocess & Re-index Chunks"
                          >
                            <RefreshCw className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDelete(doc.id, doc.title)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-charcoal-800 transition"
                            title="Delete Permanently"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    <BookOpen className="w-10 h-10 text-slate-600 mx-auto mb-2 opacity-50" />
                    <p className="text-sm font-semibold text-slate-400">
                      No documents found in {selectedEnvTab} knowledge base.
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {selectedEnvTab === 'REAL'
                        ? 'Upload verified Amit Hospitality corporate documents to begin grounding in REAL mode.'
                        : 'Adjust filters or upload a sample document.'}
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Document Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/85 backdrop-blur-md">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">
                  Upload Corporate Document
                </h3>
                <p className="text-xs text-slate-400">
                  Target Environment: <strong className="text-gold-400">{selectedEnvTab} STORE</strong>
                </p>
              </div>
              <button onClick={() => setIsUploadModalOpen(false)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
              {/* File Dropzone */}
              <div>
                <label className="block text-slate-300 font-medium mb-1.5">Select Document File</label>
                <div className="border-2 border-dashed border-slate-700 hover:border-gold-400/60 rounded-xl p-5 text-center transition cursor-pointer bg-charcoal-900/60">
                  <input
                    type="file"
                    required
                    accept=".pdf,.docx,.xlsx,.csv,.txt"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="file-upload-input"
                  />
                  <label htmlFor="file-upload-input" className="cursor-pointer space-y-2 block">
                    <Upload className="w-8 h-8 text-gold-400 mx-auto" />
                    {uploadFile ? (
                      <div className="text-white font-semibold">
                        {uploadFile.name}{' '}
                        <span className="text-slate-400 font-mono text-[11px]">
                          ({(uploadFile.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                    ) : (
                      <>
                        <p className="font-semibold text-white">Click or drag file here to ingest</p>
                        <p className="text-[11px] text-slate-400 font-mono">
                          Supports PDF, DOCX, XLSX, CSV, and TXT
                        </p>
                      </>
                    )}
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Target Outlet</label>
                  <select
                    value={uploadOutletId}
                    onChange={(e) => setUploadOutletId(e.target.value === '' ? '' : Number(e.target.value))}
                    className="w-full px-2.5 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="">All Outlets / Corporate</option>
                    {INITIAL_OUTLETS.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Knowledge Category</label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value as any)}
                    className="w-full px-2.5 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="POLICY">Dress Code & Policies</option>
                    <option value="TIMING">Operating Timings</option>
                    <option value="MENU">Menus & Pricing</option>
                    <option value="EVENT">Events & Banquets</option>
                    <option value="GENERAL">General Guidelines</option>
                  </select>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-charcoal-900/80 border border-slate-800 text-[11px] text-slate-400">
                <span className="font-semibold text-slate-300">Processing pipeline:</span> Text extraction via PyMuPDF/python-docx/openpyxl → semantic chunking (450 words + 60 overlap) → vector embedding generation → indexed into {selectedEnvTab} store.
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsUploadModalOpen(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!uploadFile || isUploading}
                  className="px-5 py-2.5 font-bold rounded-lg bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 hover:brightness-110 shadow-gold-glow disabled:opacity-50 transition"
                >
                  {isUploading ? 'Processing & Indexing...' : 'Upload & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Knowledge Entry Modal */}
      {isManualModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/85 backdrop-blur-md">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">
                  Add Manual Knowledge Entry
                </h3>
                <p className="text-xs text-slate-400">
                  Target Store: <strong className="text-gold-400">{selectedEnvTab}</strong>
                </p>
              </div>
              <button onClick={() => setIsManualModalOpen(false)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <form onSubmit={handleManualSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Entry Title</label>
                <input
                  type="text"
                  required
                  value={manualTitle}
                  onChange={(e) => setManualTitle(e.target.value)}
                  placeholder="e.g. Amber Terrace Friday Live Jazz & Cover Charges"
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Outlet</label>
                  <select
                    value={manualOutletId}
                    onChange={(e) => setManualOutletId(e.target.value === '' ? '' : Number(e.target.value))}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="">All Outlets / Corporate</option>
                    {INITIAL_OUTLETS.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Category</label>
                  <select
                    value={manualCategory}
                    onChange={(e) => setManualCategory(e.target.value as any)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="POLICY">Policy & Dress Code</option>
                    <option value="TIMING">Operating Timings</option>
                    <option value="MENU">Menu & Wine Details</option>
                    <option value="EVENT">Event & Banquets</option>
                    <option value="GENERAL">General FAQs</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Knowledge Text Content
                </label>
                <textarea
                  rows={4}
                  required
                  value={manualContent}
                  onChange={(e) => setManualContent(e.target.value)}
                  placeholder="Provide precise policy wording, dates, prices, or details to ground the AI..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsManualModalOpen(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-bold rounded-lg bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 hover:brightness-110 shadow-gold-glow"
                >
                  Save & Index Chunks
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Real Document Chunks Inspector Preview Modal */}
      {inspectDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/85 backdrop-blur-md">
          <div className="relative w-full max-w-2xl p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">{inspectDoc.title}</h3>
                <p className="text-xs text-slate-400">
                  {inspectDoc.file_name} • {inspectDoc.chunks.length} indexed vector chunks • {inspectDoc.environment} Store
                </p>
              </div>
              <button onClick={() => setInspectDoc(null)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {inspectDoc.chunks.length > 0 ? (
                inspectDoc.chunks.map((chunk) => (
                  <div
                    key={chunk.id}
                    className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700/80 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-[11px] font-mono text-gold-400">
                      <span>Chunk #{chunk.chunk_index} [ID: {chunk.id}]</span>
                      <span className="text-slate-400">{chunk.is_active ? 'Active' : 'Inactive'}</span>
                    </div>
                    <p className="text-slate-200 leading-relaxed font-sans whitespace-pre-wrap bg-charcoal-950/50 p-2.5 rounded-lg border border-slate-800">
                      {chunk.content}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-400 text-center py-6">
                  No individual vector chunks stored for this document.
                </p>
              )}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setInspectDoc(null)}
                className="px-5 py-2 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-xs font-semibold text-white"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
