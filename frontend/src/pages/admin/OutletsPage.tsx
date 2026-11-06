import React, { useState } from 'react';
import {
  UtensilsCrossed,
  Clock,
  MapPin,
  Users,
  Search,
  Plus,
  Edit2,
  CheckCircle,
  AlertTriangle,
  Sparkles,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { Outlet, MenuItem, DietaryFlag } from '../../types';
import { INITIAL_OUTLETS, DEMO_MENU_ITEMS } from '../../utils/mockData';

export const OutletsPage: React.FC = () => {
  const { environment, isDemo } = useEnvironment();
  const [outlets, setOutlets] = useState<Outlet[]>(INITIAL_OUTLETS);
  const [menuItems, setMenuItems] = useState<MenuItem[]>(DEMO_MENU_ITEMS);
  const [selectedOutletId, setSelectedOutletId] = useState<number>(INITIAL_OUTLETS[0].id);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // New item form
  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');
  const [newItemPrice, setNewItemPrice] = useState(750);
  const [newItemCat, setNewItemCat] = useState('Signature Dishes');
  const [newItemDiet, setNewItemDiet] = useState<DietaryFlag[]>(['VEG']);

  const activeOutlet = outlets.find((o) => o.id === selectedOutletId) || outlets[0];

  const filteredItems = menuItems.filter((item) => {
    const matchesOutlet = item.outletId === selectedOutletId;
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesOutlet && matchesSearch;
  });

  const handleUpdatePrice = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingItem) return;

    setMenuItems((prev) =>
      prev.map((i) => (i.id === editingItem.id ? { ...i, price: editingItem.price } : i))
    );
    setEditingItem(null);
  };

  const handleAddItem = (e: React.FormEvent) => {
    e.preventDefault();
    const created: MenuItem = {
      id: Date.now(),
      outletId: selectedOutletId,
      categoryId: 1,
      categoryName: newItemCat,
      name: newItemName,
      description: newItemDesc,
      price: newItemPrice,
      currency: 'INR',
      dietaryFlags: newItemDiet,
      isAvailable: true,
      isSignature: true,
      environment,
    };
    setMenuItems((prev) => [created, ...prev]);
    setIsAddModalOpen(false);
    setNewItemName('');
    setNewItemDesc('');
    setNewItemPrice(750);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Dining Portfolio
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Outlets & Culinary Menus
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Configure outlet details, operational hours, and menu pricing. Adjustments directly reflect in customer-facing concierge inquiries.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add Menu Item</span>
        </button>
      </div>

      {/* Outlet Selection Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {outlets.map((outlet) => {
          const isSelected = outlet.id === selectedOutletId;
          return (
            <div
              key={outlet.id}
              onClick={() => setSelectedOutletId(outlet.id)}
              className={`p-4 rounded-2xl cursor-pointer transition border relative ${
                isSelected
                  ? 'bg-charcoal-800/90 border-gold-400/80 shadow-gold-glow'
                  : 'glass-panel border-slate-800/80 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3
                    className={`font-serif font-bold text-base ${
                      isSelected ? 'text-gold-300' : 'text-white'
                    }`}
                  >
                    {outlet.name}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">{outlet.cuisineType}</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-charcoal-900 text-gold-400 border border-slate-700">
                  {outlet.seatingCapacity} seats
                </span>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-700/60 grid grid-cols-2 gap-2 text-[11px] text-slate-400">
                <div className="flex items-center gap-1.5 truncate">
                  <Clock className="w-3.5 h-3.5 text-gold-400 shrink-0" />
                  <span>{outlet.openingTime} - {outlet.closingTime}</span>
                </div>
                <div className="flex items-center gap-1.5 truncate">
                  <MapPin className="w-3.5 h-3.5 text-gold-400 shrink-0" />
                  <span className="truncate">{outlet.location.split(',')[0]}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Menu Catalog Section for Selected Outlet */}
      <div className="rounded-2xl glass-panel border border-slate-800 p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-serif font-bold text-white">
              Menu Catalog — {activeOutlet.name}
            </h3>
            <p className="text-xs text-slate-400">
              {filteredItems.length} dishes indexed in <strong className="text-gold-400">{environment}</strong> environment
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
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Dish Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Price (INR)</th>
                <th className="py-3 px-4">Dietary Attributes</th>
                <th className="py-3 px-4">Availability</th>
                <th className="py-3 px-4 text-right">Edit Price</th>
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
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => setEditingItem(item)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-gold-400 hover:bg-charcoal-800 transition"
                      title="Update item price"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Price Modal */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-md p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <h3 className="text-lg font-serif font-bold text-white">Update Item Price</h3>
            <p className="text-xs text-slate-400">
              Editing price for <strong className="text-gold-300">{editingItem.name}</strong>. The AI Concierge will immediately quote the updated price in subsequent inquiries.
            </p>

            <form onSubmit={handleUpdatePrice} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Price in INR (₹)
                </label>
                <input
                  type="number"
                  min={0}
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
                  onClick={() => setEditingItem(null)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-semibold rounded-lg bg-gold-500 text-obsidian-950 hover:bg-gold-400 shadow-gold-glow"
                >
                  Save & Invalidate Cache
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add New Item Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-md p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <h3 className="text-lg font-serif font-bold text-white">
              Add New Dish to {activeOutlet.name}
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
                <label className="block text-slate-300 font-medium mb-1">Description</label>
                <textarea
                  rows={2}
                  required
                  value={newItemDesc}
                  onChange={(e) => setNewItemDesc(e.target.value)}
                  placeholder="Culinary preparation, rare spices, cooking technique..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-semibold rounded-lg bg-gold-500 text-obsidian-950 hover:bg-gold-400 shadow-gold-glow"
                >
                  Create & Index
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
