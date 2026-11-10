import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Filter,
  Star,
  Phone,
  Mail,
  UtensilsCrossed,
  Calendar,
  Clock,
  MessageSquare,
  FileText,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Edit2,
  Shield,
  Layers,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import {
  fetchGuestsApi,
  fetchGuestProfileApi,
  updateGuestProfileApi,
  fetchModificationRequestsApi,
  reviewModificationRequestApi,
  GuestProfileSummary,
  GuestProfileDetail,
  ModificationRequestItem,
} from '../../api/crm';
import { useAuth } from '../../context/AuthContext';
import { useEnvironment } from '../../context/EnvironmentContext';

export const GuestCrmPage: React.FC = () => {
  const { user } = useAuth();
  const { environment } = useEnvironment();

  const [guests, setGuests] = useState<GuestProfileSummary[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [outletIdFilter, setOutletIdFilter] = useState<number | undefined>(undefined);
  const [vipOnly, setVipOnly] = useState(false);
  const [dietaryFilter, setDietaryFilter] = useState<string>('ALL');

  // Selected Guest Modal / Drawer
  const [selectedGuestId, setSelectedGuestId] = useState<number | null>(null);
  const [guestDetail, setGuestDetail] = useState<GuestProfileDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'RESERVATIONS' | 'COMMUNICATIONS'>('OVERVIEW');

  // Edit Guest Preferences
  const [editDietary, setEditDietary] = useState('NONE');
  const [editAllergies, setEditAllergies] = useState('');
  const [editOccasions, setEditOccasions] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [editVip, setEditVip] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Staged Modification Requests
  const [modificationRequests, setModificationRequests] = useState<ModificationRequestItem[]>([]);

  const isStaff = user?.role === 'STAFF';
  const isManagerOrAdmin = ['SUPER_ADMIN', 'ADMIN', 'MANAGER'].includes(user?.role || '');

  const loadGuests = async () => {
    setLoading(true);
    try {
      const res = await fetchGuestsApi({
        environment,
        search: search.trim() || undefined,
        outlet_id: outletIdFilter,
        vip_only: vipOnly || undefined,
        dietary: dietaryFilter !== 'ALL' ? dietaryFilter : undefined,
      });
      setGuests(res.guests);
      setTotalCount(res.total);
    } catch (err) {
      console.warn('Error fetching CRM guests:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadModificationRequests = async () => {
    if (!isManagerOrAdmin) return;
    try {
      const requests = await fetchModificationRequestsApi('PENDING_APPROVAL');
      setModificationRequests(requests);
    } catch (err) {
      console.warn('Error fetching modification requests:', err);
    }
  };

  useEffect(() => {
    loadGuests();
    loadModificationRequests();
  }, [environment, search, outletIdFilter, vipOnly, dietaryFilter]);

  // Open Guest Detail
  const handleSelectGuest = async (id: number) => {
    setSelectedGuestId(id);
    setDetailLoading(true);
    setSaveMessage(null);
    try {
      const detail = await fetchGuestProfileApi(id);
      setGuestDetail(detail);
      setEditDietary(detail.dietary_preferences || 'NONE');
      setEditAllergies(detail.allergies || '');
      setEditOccasions(detail.special_occasions || '');
      setEditNotes(detail.staff_notes || '');
      setEditVip(detail.vip_status || false);
    } catch (err: any) {
      console.warn('Error loading guest details:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  // Save Preferences
  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGuestId) return;
    setSaveLoading(true);
    setSaveMessage(null);

    try {
      const updated = await updateGuestProfileApi(selectedGuestId, {
        dietary_preferences: editDietary,
        allergies: editAllergies,
        special_occasions: editOccasions,
        staff_notes: editNotes,
        vip_status: !isStaff ? editVip : undefined,
      });
      setGuestDetail(updated);
      setSaveMessage('Preferences updated successfully.');
      loadGuests();
      setTimeout(() => setSaveMessage(null), 2500);
    } catch (err: any) {
      setSaveMessage(err.message || 'Failed to update preferences.');
    } finally {
      setSaveLoading(false);
    }
  };

  // Review Modification
  const handleReviewMod = async (id: number, action: 'APPROVE' | 'REJECT') => {
    try {
      await reviewModificationRequestApi(id, action);
      loadModificationRequests();
      loadGuests();
    } catch (err: any) {
      alert(`Error reviewing modification: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-gold-400/10 border border-gold-400/20 text-gold-400 text-xs font-semibold mb-2">
            <Users className="w-3.5 h-3.5" /> Unified Guest CRM
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-white tracking-wide">
            Guest Relationship & Preferences Directory
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Centralized profile repository, dietary restrictions, visit history, and guest self-service requests.
          </p>
        </div>

        <button
          onClick={loadGuests}
          className="self-start sm:self-auto flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-charcoal-900 border border-slate-700 text-slate-300 hover:text-white transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-gold-400' : ''}`} />
          <span>Refresh Directory</span>
        </button>
      </div>

      {/* PENDING SELF-SERVICE MODIFICATION BANNER */}
      {isManagerOrAdmin && modificationRequests.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200">
          <div className="flex items-center justify-between gap-3 mb-3">
            <div className="flex items-center gap-2 text-sm font-bold text-amber-300">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              <span>Pending Guest Self-Service Modifications ({modificationRequests.length})</span>
            </div>
          </div>
          <div className="space-y-2">
            {modificationRequests.map((req) => (
              <div
                key={req.id}
                className="p-3 rounded-xl bg-charcoal-900/90 border border-slate-700/80 flex flex-wrap items-center justify-between gap-3 text-xs"
              >
                <div>
                  <span className="font-mono font-bold text-gold-300">{req.reference_id}</span>
                  <span className="text-slate-400 mx-2">•</span>
                  <span className="text-white">
                    Party size: {req.old_guest_count} → <strong>{req.new_guest_count} guests</strong>
                  </span>
                  <span className="text-slate-400 mx-2">•</span>
                  <span className="text-slate-300">
                    Date & Time: {req.new_date} at {req.new_time}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleReviewMod(req.id, 'APPROVE')}
                    className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition"
                  >
                    Approve Table
                  </button>
                  <button
                    onClick={() => handleReviewMod(req.id, 'REJECT')}
                    className="px-3 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold transition"
                  >
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FILTER & SEARCH BAR */}
      <div className="glass-panel border border-gold-400/20 rounded-2xl p-4 flex flex-wrap items-center gap-4">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <input
            type="text"
            placeholder="Search by guest name, phone, email, or UUID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-4 py-2 pl-10 text-xs text-white placeholder-slate-500 focus:border-gold-400 focus:outline-none"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
        </div>

        {/* Dietary Filter */}
        <select
          value={dietaryFilter}
          onChange={(e) => setDietaryFilter(e.target.value)}
          className="bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-300 focus:border-gold-400 focus:outline-none"
        >
          <option value="ALL">All Dietary Preferences</option>
          <option value="VEG">Vegetarian</option>
          <option value="NON_VEG">Non-Vegetarian</option>
          <option value="VEGAN">Vegan</option>
          <option value="JAIN">Jain</option>
          <option value="GLUTEN_FREE">Gluten-Free</option>
          <option value="HALAL">Halal</option>
        </select>

        {/* VIP Toggle */}
        <button
          onClick={() => setVipOnly(!vipOnly)}
          className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition ${
            vipOnly
              ? 'bg-gold-500/20 text-gold-300 border-gold-400/50'
              : 'bg-charcoal-900 text-slate-400 border-slate-700 hover:text-white'
          }`}
        >
          <Star className={`w-3.5 h-3.5 ${vipOnly ? 'fill-gold-400 text-gold-400' : ''}`} />
          <span>VIP Only</span>
        </button>

        {/* Total count badge */}
        <div className="text-xs text-slate-400 ml-auto">
          Total Guests: <strong className="text-gold-300 font-mono">{totalCount}</strong>
        </div>
      </div>

      {/* GUEST DIRECTORY TABLE */}
      <div className="glass-panel border border-gold-400/20 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-gold-400" />
            <span>Loading CRM Directory...</span>
          </div>
        ) : guests.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            No guest profiles found matching your search or filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-charcoal-900/80 text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-700/80 font-mono">
                <tr>
                  <th className="p-3.5 pl-4">Guest Profile</th>
                  <th className="p-3.5">Contact</th>
                  <th className="p-3.5">Preferred Venue</th>
                  <th className="p-3.5">Dietary & Preferences</th>
                  <th className="p-3.5 text-center">Visits</th>
                  <th className="p-3.5 text-right pr-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {guests.map((g) => (
                  <tr
                    key={g.id}
                    className="hover:bg-gold-500/5 transition cursor-pointer"
                    onClick={() => handleSelectGuest(g.id)}
                  >
                    <td className="p-3.5 pl-4">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{g.full_name}</span>
                        {g.vip_status && (
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-gold-400/20 text-gold-300 border border-gold-400/40">
                            <Star className="w-2.5 h-2.5 fill-gold-400" /> VIP
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">{g.guest_uuid}</span>
                    </td>

                    <td className="p-3.5">
                      <div className="flex items-center gap-1 text-slate-200">
                        <Phone className="w-3 h-3 text-slate-400" /> {g.phone}
                      </div>
                      {g.email && (
                        <div className="flex items-center gap-1 text-[11px] text-slate-400">
                          <Mail className="w-3 h-3 text-slate-400" /> {g.email}
                        </div>
                      )}
                    </td>

                    <td className="p-3.5">
                      <span className="text-slate-200">
                        {g.preferred_outlet_name || 'Multi-Outlet'}
                      </span>
                    </td>

                    <td className="p-3.5">
                      <div className="flex flex-wrap gap-1">
                        {g.dietary_preferences && g.dietary_preferences !== 'NONE' && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                            {g.dietary_preferences}
                          </span>
                        )}
                        {g.allergies && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-rose-500/15 text-rose-300 border border-rose-500/30">
                            Allergies: {g.allergies}
                          </span>
                        )}
                        {(!g.dietary_preferences || g.dietary_preferences === 'NONE') && !g.allergies && (
                          <span className="text-slate-400 text-[11px]">No restrictions</span>
                        )}
                      </div>
                    </td>

                    <td className="p-3.5 text-center font-mono font-bold text-gold-300">
                      {g.total_visits}
                    </td>

                    <td className="p-3.5 text-right pr-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectGuest(g.id);
                        }}
                        className="p-1.5 rounded-lg bg-charcoal-900 border border-slate-700 text-slate-300 hover:text-gold-300 transition"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* GUEST DETAIL MODAL / DRAWER */}
      {selectedGuestId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="glass-panel border border-gold-400/30 rounded-2xl p-6 sm:p-8 max-w-3xl w-full shadow-2xl relative max-h-[90vh] overflow-y-auto">
            {detailLoading || !guestDetail ? (
              <div className="p-12 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-gold-400" />
                <span>Loading Guest Portfolio...</span>
              </div>
            ) : (
              <div>
                {/* Header */}
                <div className="flex items-center justify-between pb-4 border-b border-slate-700">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-xl font-serif font-bold text-white">
                        {guestDetail.full_name}
                      </h2>
                      {guestDetail.vip_status && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-bold bg-gold-400/20 text-gold-300 border border-gold-400/40">
                          <Star className="w-3 h-3 fill-gold-400" /> VIP
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-slate-400 font-mono">
                      {guestDetail.guest_uuid} • Total Visits: {guestDetail.total_visits}
                    </span>
                  </div>

                  <button
                    onClick={() => setSelectedGuestId(null)}
                    className="p-2 rounded-xl bg-charcoal-900 border border-slate-700 text-slate-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>

                {/* Tabs */}
                <div className="flex items-center gap-3 pt-4 border-b border-slate-700 mb-6 text-xs">
                  <button
                    onClick={() => setActiveTab('OVERVIEW')}
                    className={`pb-2 font-semibold border-b-2 transition ${
                      activeTab === 'OVERVIEW'
                        ? 'border-gold-400 text-gold-300'
                        : 'border-transparent text-slate-400 hover:text-white'
                    }`}
                  >
                    Preferences & Notes
                  </button>
                  <button
                    onClick={() => setActiveTab('RESERVATIONS')}
                    className={`pb-2 font-semibold border-b-2 transition ${
                      activeTab === 'RESERVATIONS'
                        ? 'border-gold-400 text-gold-300'
                        : 'border-transparent text-slate-400 hover:text-white'
                    }`}
                  >
                    Dining History ({guestDetail.reservations.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('COMMUNICATIONS')}
                    className={`pb-2 font-semibold border-b-2 transition ${
                      activeTab === 'COMMUNICATIONS'
                        ? 'border-gold-400 text-gold-300'
                        : 'border-transparent text-slate-400 hover:text-white'
                    }`}
                  >
                    Notifications & Audits ({guestDetail.communication_logs.length})
                  </button>
                </div>

                {/* TAB 1: PREFERENCES & EDIT */}
                {activeTab === 'OVERVIEW' && (
                  <form onSubmit={handleSavePreferences} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">
                          Dietary Classification
                        </label>
                        <select
                          value={editDietary}
                          onChange={(e) => setEditDietary(e.target.value)}
                          className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                        >
                          <option value="NONE">No Restrictions</option>
                          <option value="VEG">Vegetarian</option>
                          <option value="NON_VEG">Non-Vegetarian</option>
                          <option value="VEGAN">Vegan</option>
                          <option value="JAIN">Jain</option>
                          <option value="GLUTEN_FREE">Gluten-Free</option>
                          <option value="HALAL">Halal</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-1">
                          Food Allergies & Health Notes
                        </label>
                        <input
                          type="text"
                          value={editAllergies}
                          onChange={(e) => setEditAllergies(e.target.value)}
                          placeholder="e.g. Peanuts, Shellfish, Lactose intolerance"
                          className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Special Occasions & Milestones
                      </label>
                      <input
                        type="text"
                        value={editOccasions}
                        onChange={(e) => setEditOccasions(e.target.value)}
                        placeholder="e.g. Wedding Anniversary: Oct 14, Birthday: Jan 5"
                        className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">
                        Internal Staff Notes & Table Preferences
                      </label>
                      <textarea
                        rows={3}
                        value={editNotes}
                        onChange={(e) => setEditNotes(e.target.value)}
                        placeholder="Private dining notes, preferred seating zone, beverage preferences..."
                        className="w-full bg-charcoal-900 border border-slate-700 rounded-xl p-3 text-xs text-white"
                      />
                    </div>

                    {!isStaff && (
                      <div className="flex items-center gap-2 pt-2">
                        <input
                          type="checkbox"
                          id="vip_checkbox"
                          checked={editVip}
                          onChange={(e) => setEditVip(e.target.checked)}
                          className="w-4 h-4 rounded text-gold-500 focus:ring-gold-400"
                        />
                        <label htmlFor="vip_checkbox" className="text-xs font-semibold text-gold-300">
                          Designate as VIP Guest (Elevated Hospitality Courtesy)
                        </label>
                      </div>
                    )}

                    {saveMessage && (
                      <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-xs text-emerald-300">
                        {saveMessage}
                      </div>
                    )}

                    <div className="pt-4 border-t border-slate-700 flex justify-end">
                      <button
                        type="submit"
                        disabled={saveLoading}
                        className="px-5 py-2.5 rounded-xl font-semibold bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 text-xs shadow-gold-glow disabled:opacity-50"
                      >
                        {saveLoading ? 'Saving...' : 'Save Preferences'}
                      </button>
                    </div>
                  </form>
                )}

                {/* TAB 2: RESERVATIONS */}
                {activeTab === 'RESERVATIONS' && (
                  <div className="space-y-3">
                    {guestDetail.reservations.length === 0 ? (
                      <p className="text-xs text-slate-400 text-center py-6">No reservations on file.</p>
                    ) : (
                      guestDetail.reservations.map((r) => (
                        <div
                          key={r.id}
                          className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700/80 flex items-center justify-between text-xs"
                        >
                          <div>
                            <span className="font-mono font-bold text-gold-300">{r.reference_id}</span>
                            <span className="text-slate-400 mx-2">•</span>
                            <span className="text-white font-semibold">{r.outlet_name}</span>
                            <p className="text-[11px] text-slate-400 mt-0.5">
                              {r.reservation_date} at {r.reservation_time} ({r.guest_count} covers)
                            </p>
                          </div>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300 border border-slate-700">
                            {r.status}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {/* TAB 3: COMMUNICATIONS */}
                {activeTab === 'COMMUNICATIONS' && (
                  <div className="space-y-3">
                    {guestDetail.communication_logs.length === 0 ? (
                      <p className="text-xs text-slate-400 text-center py-6">No communication logs recorded.</p>
                    ) : (
                      guestDetail.communication_logs.map((c) => (
                        <div
                          key={c.id}
                          className="p-3 rounded-xl bg-charcoal-900 border border-slate-700/80 flex items-center justify-between text-xs"
                        >
                          <div>
                            <span className="font-semibold text-slate-200">
                              {c.channel}: {c.event_type}
                            </span>
                            <p className="text-[11px] text-slate-400">
                              To: {c.recipient} • Ref: {c.reference_id || 'N/A'}
                            </p>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              c.status === 'SENT' || c.status === 'SIMULATED'
                                ? 'bg-emerald-500/20 text-emerald-300'
                                : 'bg-rose-500/20 text-rose-300'
                            }`}
                          >
                            {c.status}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
