import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { OutletsPage } from '../pages/admin/OutletsPage';
import { AuthProvider } from '../context/AuthContext';
import { EnvironmentProvider } from '../context/EnvironmentContext';
import * as outletsApi from '../api/outlets';

const mockOutlets = [
  {
    id: 1,
    name: 'Amber Terrace Rooftop',
    slug: 'amber-terrace',
    outletType: 'Rooftop Lounge',
    cuisineType: 'Pan-Asian & Cocktails',
    openingTime: '18:00',
    closingTime: '01:00',
    seatingCapacity: 80,
    description: 'Skyline lounge overlooking the sea',
    location: 'Level 12, Tower A',
    isPopular: true,
  },
  {
    id: 2,
    name: 'Saffron & Silk',
    slug: 'saffron-silk',
    outletType: 'Fine Dining',
    cuisineType: 'Awadhi & Royal Indian',
    openingTime: '12:30',
    closingTime: '23:30',
    seatingCapacity: 60,
    description: 'Opulent heritage dining',
    location: 'Ground Floor, Grand Atrium',
    isPopular: false,
  },
];

const mockMenuItems = [
  {
    id: 101,
    outletId: 1,
    environment: 'DEMO',
    name: 'Crispy Truffle Lotus Stem',
    description: 'Honey-chilli glaze with black truffle',
    price: 850,
    currency: 'INR',
    dietaryFlags: ['VEG'],
    isAvailable: true,
    isSignature: true,
    displayOrder: 1,
  },
];

vi.mock('../api/outlets', () => ({
  fetchOutletsApi: vi.fn(),
  fetchMenuItemsApi: vi.fn(),
  createMenuItemApi: vi.fn(),
  updateMenuItemApi: vi.fn(),
  deleteMenuItemApi: vi.fn(),
  updateOutletApi: vi.fn(),
}));

const renderComponent = () => {
  return render(
    <AuthProvider>
      <EnvironmentProvider>
        <OutletsPage />
      </EnvironmentProvider>
    </AuthProvider>
  );
};

describe('OutletsPage Live Database Integration & Management', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();

    vi.mocked(outletsApi.fetchOutletsApi).mockResolvedValue(mockOutlets as any);
    vi.mocked(outletsApi.fetchMenuItemsApi).mockResolvedValue(mockMenuItems as any);
    vi.mocked(outletsApi.updateMenuItemApi).mockResolvedValue({
      ...mockMenuItems[0],
      price: 950,
    } as any);
    vi.mocked(outletsApi.updateOutletApi).mockResolvedValue({
      ...mockOutlets[0],
      seatingCapacity: 100,
    } as any);
  });

  it('fetches and displays live outlets from backend database', async () => {
    renderComponent();

    // Verify loading skeleton resolves into live outlets
    await waitFor(() => {
      expect(screen.getByText('Amber Terrace Rooftop')).toBeInTheDocument();
      expect(screen.getByText('Saffron & Silk')).toBeInTheDocument();
    });

    expect(screen.getByText('Pan-Asian & Cocktails')).toBeInTheDocument();
    expect(screen.getByText('Awadhi & Royal Indian')).toBeInTheDocument();
  });

  it('fetches and displays menu items for selected outlet', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Crispy Truffle Lotus Stem')).toBeInTheDocument();
      expect(screen.getByText(/850/)).toBeInTheDocument();
    });
  });

  it('updates menu item price and persists through API', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Crispy Truffle Lotus Stem')).toBeInTheDocument();
    });

    // Find and click the edit menu item button
    const editButtons = screen.getAllByTitle('Edit price');
    expect(editButtons.length).toBeGreaterThan(0);
    fireEvent.click(editButtons[0]);

    // Modal should appear with edit price input
    await waitFor(() => {
      expect(screen.getByText('Update Dish Price')).toBeInTheDocument();
    });

    const priceInput = screen.getByDisplayValue('850');
    fireEvent.change(priceInput, { target: { value: '950' } });

    const saveButton = screen.getByRole('button', { name: /Save to Database/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(outletsApi.updateMenuItemApi).toHaveBeenCalledWith(101, expect.objectContaining({
        price: 950,
      }));
    });
  });

  it('allows manager/admin to configure operational rules and table capacity', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Edit Outlet Rules')).toBeInTheDocument();
    });

    const configButton = screen.getByText('Edit Outlet Rules');
    fireEvent.click(configButton);

    await waitFor(() => {
      expect(screen.getByText(/Configure Operational Rules/i)).toBeInTheDocument();
    });

    const capacityInput = screen.getByDisplayValue('80');
    fireEvent.change(capacityInput, { target: { value: '100' } });

    const saveRulesBtn = screen.getByRole('button', { name: /Save Operational Rules/i });
    fireEvent.click(saveRulesBtn);

    await waitFor(() => {
      expect(outletsApi.updateOutletApi).toHaveBeenCalledWith(1, expect.objectContaining({
        seating_capacity: 100,
      }));
    });
  });
});
