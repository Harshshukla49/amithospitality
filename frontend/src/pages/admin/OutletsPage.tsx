import React, { useState, useEffect } from 'react';
import {
  UtensilsCrossed,
  Clock,
  MapPin,
  Users,
  Search,
  Plus,
  Edit2,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Sparkles,
  RefreshCw,
  Sliders,
  X,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { useAuth } from '../../context/AuthContext';
import { Outlet, MenuItem, DietaryFlag } from '../../types';
import {
  fetchOutletsApi,
  fetchMenuItemsApi,
  createMenuItemApi,
  updateMenuItemApi,
  deleteMenuItemApi,
  updateOutletApi,
} from '../../api/outlets';

export const OutletsPage: React.FC = () => {
  const { environment, isDemo } = useEnvironment();
  const { user } = useAuth();

  const [outlets, setOutlets] = useState<Outlet[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [selectedOutletId, setSelectedOutletId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loadingOutlets, setLoadingOutlets] = useState(true);
  const [loadingMenu, setLoadingMenu] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Modals
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditOutletOpen, setIsEditOutletOpen] = useState(false);

  // New item form state
  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');
  const [newItemPrice, setNewItemPrice] = useState(750);
  const [newItemCat, setNewItemCat] = useState('Signature Specialties');
  const [newItemDiet, setNewItemDiet] = useState<DietaryFlag[]>(['VEG']);
  const [newItemSignature, setNewItemSignature] = useState(false);

  // Edit outlet form state
  const [outletHoursOpen, setOutletHoursOpen] = useState('');
  const [outletHoursClose, setOutletHoursClose] = useState('');
  const [outletDressCode, setOutletDressCode] = useState('');
  const [outletCapacity, setOutletCapacity] = useState(100);
  const [outletCuisine, setOutletCuisine] = useState('');

  // Check outlet permissions
  const isManager = user?.role === 'MANAGER';
  const managerOutletId = user?.outletId;

  // 1. Fetch Outlets on load
  const loadOutlets = async () => {
    try {
      setLoadingOutlets(true);
      setErrorMessage(null);
      const data = await fetchOutletsApi();
      setOutlets(data);
      if (data.length > 0) {
        if (isManager && managerOutletId) {
          const match = data.find((o) => o.id === managerOutletId);
          setSelectedOutletId(match ? match.id : data[0].id);
        } else {
          setSelectedOutletId(data[0].id);
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load restaurant outlets from backend.');
    } finally {
      setLoadingOutlets(false);
    }
  };

  useEffect(() => {
    loadOutlets();
  }, [user]);

  // 2. Fetch Menu Items whenever selected outlet or environment changes
  const loadMenu = async (outletId: number) => {
    try {
      setLoadingMenu(true);
      setErrorMessage(null);
      const items = await fetchMenuItemsApi({ outlet_id: outletId, environment });
      setMenuItems(items);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load menu items from backend.');
    } finally {
      setLoadingMenu(false);
    }
  };

  useEffect(() => {
    if (selectedOutletId) {
      loadMenu(selectedOutletId);
    }
  }, [selectedOutletId, environment]);

  const activeOutlet = outlets.find((o) => o.id === selectedOutletId) || outlets[0];

  useEffect(() => {
    if (activeOutlet) {
      setOutletHoursOpen(activeOutlet.openingTime || '17:30');
      setOutletHoursClose(activeOutlet.closingTime || '01:30');
      setOutletDressCode(activeOutlet.dressCode || 'Smart Casual');
      setOutletCapacity(activeOutlet.seatingCapacity || 100);
      setOutletCuisine(activeOutlet.cuisineType || '');
    }
  }, [activeOutlet]);

  const showToast = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(null), 3500);
  };

  const filteredItems = menuItems.filter((item) => {
    const matchesOutlet = item.outletId === selectedOutletId;
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesOutlet && matchesSearch;
  });

  const handleUpdatePrice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingItem) return;

    try {
      setActionLoading(true);
      setErrorMessage(null);
      const updated = await updateMenuItemApi(editingItem.id, {
        price: editingItem.price,
      });
      setMenuItems((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
      setEditingItem(null);
      showToast(`Updated price for "${updated.name}" to ₹${updated.price.toLocaleString('en-IN')}.`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to update menu item price.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOutletId) return;

    try {
      setActionLoading(true);
      setErrorMessage(null);
      const created = await createMenuItemApi({
        outlet_id: selectedOutletId,
        name: newItemName,
        description: newItemDesc,
        price: newItemPrice,
        dietary_flags: newItemDiet.join(','),
        environment,
        is_signature: newItemSignature,
      });
      setMenuItems((prev) => [created, ...prev]);
      setIsAddModalOpen(false);
      setNewItemName('');
      setNewItemDesc('');
      setNewItemPrice(750);
      setNewItemSignature(false);
      showToast(`Added "${created.name}" to ${activeOutlet?.name || 'outlet'} menu.`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create menu item on backend.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteItem = async (itemId: number, itemName: string) => {
    if (!window.confirm(`Are you sure you want to remove "${itemName}" from the active menu?`)) {
      return;
    }

    try {
      setActionLoading(true);
      setErrorMessage(null);
      await deleteMenuItemApi(itemId);
      setMenuItems((prev) => prev.filter((i) => i.id !== itemId));
      showToast(`Removed "${itemName}" from active menu.`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to delete menu item.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateOutlet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOutletId) return;

    try {
      setActionLoading(true);
      setErrorMessage(null);
      const updated = await updateOutletApi(selectedOutletId, {
        opening_time: outletHoursOpen,
        closing_time: outletHoursClose,
        dress_code: outletDressCode,
        seating_capacity: outletCapacity,
        cuisine_type: outletCuisine,
      });
      setOutlets((prev) => prev.map((o) => (o.id === updated.id ? updated : o)));
      setIsEditOutletOpen(false);
      showToast(`Operational details for ${updated.name} successfully updated.`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to update outlet settings.');
    } finally {
      setActionLoading(false);
    }
  };

  const canEditSelectedOutlet =
    user?.role === 'SUPER_ADMIN' ||
    user?.role === 'ADMIN' ||
    (user?.role === 'MANAGER' && user.outletId === selectedOutletId);

  return (
    <div className="space-y-6">
      {successMessage && (
        <div className="flex items-center gap-2 p-3.5 rounded-xl bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-xs animate-fade-in shadow-lg">
          <CheckCircle className="w-4 h-4 shrink-0 text-emerald-400" />
          <span>{successMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-rose-950/80 border border-rose-500/50 text-rose-300 text-xs animate-fade-in shadow-lg">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Dining Portfolio & Live Menus
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-charcoal-800 text-slate-300 border border-slate-700">
              Live PostgreSQL Connected
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Outlets & Culinary Menus
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Live database configuration. Menu prices, hours, and dishes directly drive the AI Concierge and customer reservation inquiries in real time.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          {canEditSelectedOutlet && activeOutlet && (
            <button
              onClick={() => setIsEditOutletOpen(true)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 text-slate-200 border border-slate-700 text-xs transition"
            >
              <Sliders className="w-3.5 h-3.5 text-gold-400" />
              <span>Edit Outlet Rules</span>
            </button>
          )}

          {canEditSelectedOutlet && (
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition"
            >
              <Plus className="w-4 h-4" />
              <span>Add Dish</span>
            </button>
          )}
        </div>
      </div>

      {/* Outlet Selection Cards */}
      {loadingOutlets ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-44 rounded-2xl bg-charcoal-900/60 animate-pulse border border-slate-800" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {outlets.map((outlet) => {
            const isSelected = outlet.id === selectedOutletId;
            const isAssigned = isManager && outlet.id === managerOutletId;
            return (
              <div
                key={outlet.id}
                onClick={() => setSelectedOutletId(outlet.id)}
                className={`rounded-2xl cursor-pointer transition border relative overflow-hidden flex flex-col ${
                  isSelected
                    ? 'bg-charcoal-800/95 border-gold-400 shadow-gold-glow'
                    : 'glass-panel border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="p-4 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <h3
                        className={`font-serif font-bold text-base ${
                          isSelected ? 'text-gold-300' : 'text-white'
                        }`}
                      >
                        {outlet.name}
                      </h3>
                      {isAssigned && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          Assigned
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{outlet.cuisineType}</p>
                    <p className="text-[11px] text-slate-500 mt-2 line-clamp-2">{outlet.description}</p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-700/60 grid grid-cols-2 gap-2 text-[11px] text-slate-400">
                    <div className="flex items-center gap-1.5 truncate">
                      <Clock className="w-3.5 h-3.5 text-gold-400 shrink-0" />
                      <span>{outlet.openingTime} - {outlet.closingTime}</span>
                    </div>
                    <div className="flex items-center gap-1.5 truncate">
                      <Users className="w-3.5 h-3.5 text-gold-400 shrink-0" />
                      <span>{outlet.seatingCapacity} Capacity</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Menu Catalog Section for Selected Outlet */}
      <div className="rounded-2xl glass-panel border border-slate-800 p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
              <span>Menu Catalog — {activeOutlet?.name || 'Selected Outlet'}</span>
              {loadingMenu && <RefreshCw className="w-4 h-4 text-gold-400 animate-spin" />}
            </h3>
            <p className="text-xs text-slate-400">
              {filteredItems.length} dishes indexed in <strong className="text-gold-400">{environment}</strong> mode (PostgreSQL storage)
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search dishes or ingredients..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
            />
          </div>
        </div>

        {/* Menu Items Table */}
        <div className="overflow-x-auto">
          {loadingMenu ? (
            <div className="p-8 text-center text-xs text-slate-400">
              <RefreshCw className="w-5 h-5 mx-auto text-gold-400 animate-spin mb-2" />
              <span>Fetching live culinary catalog from database...</span>
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="p-10 text-center glass-panel border border-dashed border-slate-800 rounded-xl space-y-2">
              <UtensilsCrossed className="w-8 h-8 mx-auto text-slate-600" />
              <p className="text-sm font-medium text-slate-300">No menu items found</p>
              <p className="text-xs text-slate-500">
                {searchQuery
                  ? `No dishes match "${searchQuery}"`
                  : `No menu items indexed for ${activeOutlet?.name} in ${environment} mode.`}
              </p>
            </div>
          ) : (
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Dish Name</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Price (INR)</th>
                  <th className="py-3 px-4">Dietary Attributes</th>
                  <th className="py-3 px-4">Status</th>
                  {canEditSelectedOutlet && <th className="py-3 px-4 text-right">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-charcoal-800/40 transition">
                    <td className="py-3.5 px-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white">{item.name}</span>
                          {item.isSignature && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold uppercase bg-gold-400/20 text-gold-300 border border-gold-400/30">
                              Signature
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{item.description}</p>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                      {item.categoryName}
                    </td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-gold-400 text-sm">
                      ₹{item.price.toLocaleString('en-IN')}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1">
                        {item.dietaryFlags.map((flag) => (
                          <span
                            key={flag}
                            className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-charcoal-800 text-slate-300 border border-slate-700"
                          >
                            {flag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1 text-emerald-400 text-[11px] font-medium">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Available</span>
                      </span>
                    </td>
                    {canEditSelectedOutlet && (
                      <td className="py-3.5 px-4 text-right space-x-1">
                        <button
                          onClick={() => setEditingItem(item)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-gold-400 hover:bg-charcoal-800 transition"
                          title="Edit price"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteItem(item.id, item.name)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-charcoal-800 transition"
                          title="Delete item"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Edit Price Modal */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-md p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <h3 className="text-lg font-serif font-bold text-white">Update Dish Price</h3>
            <p className="text-xs text-slate-400">
              Updating price for <strong className="text-gold-300">{editingItem.name}</strong>. Persisted directly in PostgreSQL; the AI Concierge will immediately quote this revised rate.
            </p>

            <form onSubmit={handleUpdatePrice} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Price in INR (₹)
                </label>
                <input
                  type="number"
                  min={0}
                  step={50}
                  required
                  value={editingItem.price}
                  onChange={(e) =>
                    setEditingItem({ ...editingItem, price: Number(e.target.value) })
                  }
                  className="w-full px-3 py-2 text-sm rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400 font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  disabled={actionLoading}
                  onClick={() => setEditingItem(null)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-5 py-2 font-semibold rounded-lg bg-gold-500 text-obsidian-950 hover:bg-gold-400 shadow-gold-glow disabled:opacity-50 flex items-center gap-1.5"
                >
                  {actionLoading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>Save to Database</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add New Item Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-md p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <h3 className="text-lg font-serif font-bold text-white">
              Add New Dish to {activeOutlet?.name}
            </h3>

            <form onSubmit={handleAddItem} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Dish Name</label>
                <input
                  type="text"
                  required
                  value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  placeholder="e.g. Saffron Infused Lobster Thermidor"
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Price (₹)</label>
                  <input
                    type="number"
                    required
                    min={0}
                    step={50}
                    value={newItemPrice}
                    onChange={(e) => setNewItemPrice(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Category</label>
                  <input
                    type="text"
                    value={newItemCat}
                    onChange={(e) => setNewItemCat(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Description & Ingredients</label>
                <textarea
                  rows={2}
                  required
                  value={newItemDesc}
                  onChange={(e) => setNewItemDesc(e.target.value)}
                  placeholder="Culinary preparation, rare spices, cooking technique..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                  <input
                    type="checkbox"
                    checked={newItemSignature}
                    onChange={(e) => setNewItemSignature(e.target.checked)}
                    className="rounded bg-charcoal-900 border-slate-700 text-gold-500 focus:ring-gold-400"
                  />
                  <span>Mark as Signature Dish</span>
                </label>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  disabled={actionLoading}
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-5 py-2 font-semibold rounded-lg bg-gold-500 text-obsidian-950 hover:bg-gold-400 shadow-gold-glow disabled:opacity-50 flex items-center gap-1.5"
                >
                  {actionLoading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>Persist to Database</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Outlet Operational Settings Modal */}
      {isEditOutletOpen && activeOutlet && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md animate-fade-in">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-gold-400" />
              <span>Configure Operational Rules — {activeOutlet.name}</span>
            </h3>
            <p className="text-xs text-slate-400">
              Modifies live seating threshold and operational schedule. Capacity directly enforces overbooking locks in REAL mode.
            </p>

            <form onSubmit={handleUpdateOutlet} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Opening Time</label>
                  <input
                    type="text"
                    required
                    value={outletHoursOpen}
                    onChange={(e) => setOutletHoursOpen(e.target.value)}
                    placeholder="17:30"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white font-mono focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Closing Time</label>
                  <input
                    type="text"
                    required
                    value={outletHoursClose}
                    onChange={(e) => setOutletHoursClose(e.target.value)}
                    placeholder="01:30"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white font-mono focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Seating Capacity Threshold</label>
                  <input
                    type="number"
                    min={10}
                    max={500}
                    required
                    value={outletCapacity}
                    onChange={(e) => setOutletCapacity(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white font-mono focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Dress Code Policy</label>
                  <input
                    type="text"
                    required
                    value={outletDressCode}
                    onChange={(e) => setOutletDressCode(e.target.value)}
                    placeholder="Elegant / Smart Casual"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Cuisine / Category</label>
                <input
                  type="text"
                  required
                  value={outletCuisine}
                  onChange={(e) => setOutletCuisine(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  disabled={actionLoading}
                  onClick={() => setIsEditOutletOpen(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-5 py-2 font-semibold rounded-lg bg-gold-500 text-obsidian-950 hover:bg-gold-400 shadow-gold-glow disabled:opacity-50 flex items-center gap-1.5"
                >
                  {actionLoading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>Save Operational Rules</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
