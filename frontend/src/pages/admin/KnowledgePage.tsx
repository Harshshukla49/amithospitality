import React, { useState } from 'react';
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
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { KnowledgeDocument, Environment } from '../../types';
import { INITIAL_OUTLETS } from '../../utils/mockData';

interface KnowledgePageProps {
  documents: KnowledgeDocument[];
  onAddDocument: (doc: KnowledgeDocument) => void;
  onDeleteDocument: (id: number) => void;
}

export const KnowledgePage: React.FC<KnowledgePageProps> = ({
  documents,
  onAddDocument,
  onDeleteDocument,
}) => {
  const { environment, isDemo, openSwitchModal } = useEnvironment();
  const [selectedEnvTab, setSelectedEnvTab] = useState<Environment>(environment);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedOutletId, setSelectedOutletId] = useState<string>('ALL');
  const [isUploading, setIsUploading] = useState(false);
  const [isManualModalOpen, setIsManualModalOpen] = useState(false);
  const [previewDoc, setPreviewDoc] = useState<KnowledgeDocument | null>(null);

  // Manual creation state
  const [manualTitle, setManualTitle] = useState('');
  const [manualCategory, setManualCategory] = useState<'MENU' | 'POLICY' | 'TIMING' | 'EVENT' | 'GENERAL'>('POLICY');
  const [manualOutletId, setManualOutletId] = useState<number>(INITIAL_OUTLETS[0].id);
  const [manualContent, setManualContent] = useState('');

  const filteredDocs = documents.filter((doc) => {
    const matchesEnv = doc.environment === selectedEnvTab;
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.fileName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'ALL' || doc.category === selectedCategory;
    const matchesOutlet =
      selectedOutletId === 'ALL' || (doc.outletId && doc.outletId === Number(selectedOutletId));
    return matchesEnv && matchesSearch && matchesCat && matchesOutlet;
  });

  const handleSimulateUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setTimeout(() => {
      const ext = file.name.split('.').pop()?.toUpperCase() as any;
      const newDoc: KnowledgeDocument = {
        id: Date.now(),
        environment: selectedEnvTab,
        outletId: INITIAL_OUTLETS[0].id,
        outletName: INITIAL_OUTLETS[0].name,
        title: file.name.replace(/\.[^/.]+$/, '').replace(/_/g, ' '),
        fileName: file.name,
        fileType: ['PDF', 'DOCX', 'XLSX', 'CSV', 'TXT'].includes(ext) ? ext : 'PDF',
        fileSizeBytes: file.size,
        category: 'POLICY',
        verificationStatus: selectedEnvTab === 'REAL' ? 'VERIFIED' : 'UNVERIFIED',
        verifiedBy: selectedEnvTab === 'REAL' ? 'Super Admin' : undefined,
        verifiedAt: selectedEnvTab === 'REAL' ? new Date().toISOString().substring(0, 10) : undefined,
        chunkCount: Math.floor(Math.random() * 12) + 4,
        isActive: true,
        createdAt: new Date().toISOString().substring(0, 10),
      };

      onAddDocument(newDoc);
      setIsUploading(false);
    }, 1000);
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualTitle || !manualContent) return;

    const outlet = INITIAL_OUTLETS.find((o) => o.id === manualOutletId);

    const newDoc: KnowledgeDocument = {
      id: Date.now(),
      environment: selectedEnvTab,
      outletId: manualOutletId,
      outletName: outlet?.name,
      title: manualTitle,
      fileName: `${manualTitle.toLowerCase().replace(/\s+/g, '_')}.txt`,
      fileType: 'MANUAL',
      fileSizeBytes: manualContent.length,
      category: manualCategory,
      verificationStatus: selectedEnvTab === 'REAL' ? 'VERIFIED' : 'UNVERIFIED',
      verifiedBy: selectedEnvTab === 'REAL' ? 'Super Admin' : undefined,
      verifiedAt: selectedEnvTab === 'REAL' ? new Date().toISOString().substring(0, 10) : undefined,
      chunkCount: Math.max(1, Math.ceil(manualContent.length / 500)),
      isActive: true,
      createdAt: new Date().toISOString().substring(0, 10),
    };

    onAddDocument(newDoc);
    setIsManualModalOpen(false);
    setManualTitle('');
    setManualContent('');
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Environment Scope Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              RAG & Document Intelligence
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Knowledge Base Management
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Upload and index verified PDFs, menus, and policies. Documents are strictly segregated between DEMO and REAL environments.
          </p>
        </div>

        {/* Environment Scope Switcher Tabs */}
        <div className="flex items-center p-1 rounded-xl bg-charcoal-900 border border-slate-700/80 self-start md:self-auto">
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
                ? 'Records here are fictional and used solely for presentation to Amit Hospitality stakeholders.'
                : 'Records here are verified company assets. The AI only references these when REAL mode is active.'}
            </p>
          </div>
        </div>

        {environment !== selectedEnvTab && (
          <button
            onClick={() => openSwitchModal(selectedEnvTab)}
            className="px-3 py-1.5 rounded-lg bg-charcoal-900 border border-slate-700 hover:border-gold-400 text-xs text-white shrink-0 transition"
          >
            Activate {selectedEnvTab} Mode
          </button>
        )}
      </div>

      {/* Controls: Search, Filters, Upload, Add Manual */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="flex flex-1 items-center gap-2">
          {/* Search Bar */}
          <div className="relative flex-1 max-w-md">
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
          </select>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsManualModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 border border-slate-700 text-xs text-slate-200 transition"
          >
            <Plus className="w-3.5 h-3.5 text-gold-400" />
            <span>Add Manual Entry</span>
          </button>

          <label className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow cursor-pointer transition">
            <Upload className="w-3.5 h-3.5" />
            <span>{isUploading ? 'Ingesting...' : 'Upload Document'}</span>
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.csv,.txt"
              onChange={handleSimulateUpload}
              disabled={isUploading}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Documents Table View */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
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
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredDocs.length > 0 ? (
                filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-charcoal-800/40 transition">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-lg bg-charcoal-800 text-gold-400 border border-slate-700">
                          {doc.fileType === 'PDF' && <FileText className="w-4 h-4" />}
                          {doc.fileType === 'XLSX' && <FileSpreadsheet className="w-4 h-4" />}
                          {doc.fileType === 'DOCX' && <FileText className="w-4 h-4" />}
                          {doc.fileType === 'MANUAL' && <FileCode className="w-4 h-4" />}
                          {doc.fileType === 'TXT' && <FileText className="w-4 h-4" />}
                        </div>
                        <div>
                          <p className="font-semibold text-white">{doc.title}</p>
                          <p className="text-[11px] text-slate-500 font-mono">{doc.fileName}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-200">
                      {doc.outletName || 'All Outlets'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700 text-[10px] font-mono">
                        {doc.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                      {doc.fileType}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">
                      {doc.chunkCount} vectors
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          doc.verificationStatus === 'VERIFIED'
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {doc.verificationStatus === 'VERIFIED' ? (
                          <CheckCircle className="w-3 h-3" />
                        ) : (
                          <AlertTriangle className="w-3 h-3" />
                        )}
                        <span>{doc.verificationStatus}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setPreviewDoc(doc)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-gold-400 hover:bg-charcoal-800 transition"
                          title="Inspect Chunks"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => onDeleteDocument(doc.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-charcoal-800 transition"
                          title="Delete from knowledge index"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500">
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

      {/* Manual Knowledge Entry Modal */}
      {isManualModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury">
            <h3 className="text-lg font-serif font-bold text-white mb-1">
              Add Manual Knowledge Entry
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Directly author a policy, timing update, or FAQ to be indexed into the{' '}
              <strong className="text-gold-400">{selectedEnvTab}</strong> vector store.
            </p>

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
                    onChange={(e) => setManualOutletId(Number(e.target.value))}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
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
                  className="px-5 py-2 font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 hover:brightness-110 shadow-gold-glow"
                >
                  Save & Index Chunks
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Chunks Inspector Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-2xl p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">{previewDoc.title}</h3>
                <p className="text-xs text-slate-400">
                  {previewDoc.fileName} • {previewDoc.chunkCount} indexed vector chunks • {previewDoc.environment}
                </p>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {[1, 2, 3].map((chunkIdx) => (
                <div
                  key={chunkIdx}
                  className="p-3 rounded-xl bg-charcoal-900 border border-slate-700/80 text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between text-[11px] font-mono text-gold-400">
                    <span>Chunk #{chunkIdx} [Tokens: 248]</span>
                    <span className="text-slate-400">Embedding: 768-dim</span>
                  </div>
                  <p className="text-slate-300">
                    {previewDoc.category === 'TIMING' &&
                      `Operating hours for ${previewDoc.outletName || 'Outlets'}: Monday through Sunday 17:30 to 01:30. Last food order accepted at 00:30. Complimentary valet parking is extended to all guests.`}
                    {previewDoc.category === 'MENU' &&
                      `Truffle Edamame & Wild Mushroom Dumplings priced at ₹695. Served with aged chili ponzu. Vegetarian and vegan friendly. Glazed Chilean Sea Bass Skewers priced at ₹1,250.`}
                    {previewDoc.category === 'POLICY' &&
                      `Dress code policy strictly observed: Smart casual attire. Tailored trousers, collared shirts, and evening dresses are welcomed. Flip-flops and athletic sleeveless jerseys are prohibited.`}
                  </p>
                </div>
              ))}
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setPreviewDoc(null)}
                className="px-5 py-2 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-xs font-semibold text-white"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
