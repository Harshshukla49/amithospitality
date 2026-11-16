import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MegaMenuOverlay } from '../components/common/MegaMenuOverlay';
import { AuthProvider } from '../context/AuthContext';
import { EnvironmentProvider } from '../context/EnvironmentContext';

describe('MegaMenuOverlay — Luxury Hospitality Mega Menu Component', () => {
  const onCloseMock = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderComponent = (isOpen = true, initialRoute = '/') => {
    return render(
      <AuthProvider>
        <EnvironmentProvider>
          <MemoryRouter initialEntries={[initialRoute]}>
            <MegaMenuOverlay isOpen={isOpen} onClose={onCloseMock} />
          </MemoryRouter>
        </EnvironmentProvider>
      </AuthProvider>
    );
  };

  it('does not render when isOpen is false', () => {
    renderComponent(false);
    expect(screen.queryByRole('dialog')).toBeNull();
  });

  it('renders dialog and brand header when isOpen is true', () => {
    renderComponent(true);

    const dialog = screen.getByRole('dialog', { name: /Amit Hospitality Luxury Navigation Menu/i });
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText('AMIT HOSPITALITY')).toBeInTheDocument();
    expect(screen.getByText(/LLP • ESTD 2018/i)).toBeInTheDocument();
  });

  it('renders all four authentic Amit Hospitality brand cards with photography', () => {
    renderComponent(true);

    // Verify all 4 brand names
    expect(screen.getByText('LORD OF THE DRINKS')).toBeInTheDocument();
    expect(screen.getByText('VENETO KITCHEN & BAR')).toBeInTheDocument();
    expect(screen.getByText('THE WAREHOUSE CAFE')).toBeInTheDocument();
    expect(screen.getByText('DELIITE')).toBeInTheDocument();

    // Verify brand images
    const images = screen.getAllByRole('img');
    const imageSrcs = images.map((img) => img.getAttribute('src'));
    expect(imageSrcs).toContain('/images/brands/lord-of-the-drinks.jpg');
    expect(imageSrcs).toContain('/images/brands/veneto.jpg');
    expect(imageSrcs).toContain('/images/brands/warehouse-cafe.jpg');
    expect(imageSrcs).toContain('/images/brands/deliite.jpg');
  });

  it('renders Group A (Explore) and Group B (Experience & Connect) navigation links', () => {
    renderComponent(true);

    // Group A
    expect(screen.getByRole('heading', { name: 'Explore' })).toBeInTheDocument();
    expect(screen.getByText('Know Us')).toBeInTheDocument();
    expect(screen.getByText('Digital Menus')).toBeInTheDocument();
    expect(screen.getByText('Gallery')).toBeInTheDocument();

    // Group B
    expect(screen.getByRole('heading', { name: /Experience & Connect/i })).toBeInTheDocument();
    expect(screen.getByText('Events')).toBeInTheDocument();
    expect(screen.getByText('Careers')).toBeInTheDocument();
    expect(screen.getByText('Enquiry')).toBeInTheDocument();
    expect(screen.getByText('Contact')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    renderComponent(true);

    const closeBtn = screen.getByRole('button', { name: /Close navigation menu/i });
    fireEvent.click(closeBtn);

    expect(onCloseMock).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape key is pressed', () => {
    renderComponent(true);

    fireEvent.keyDown(window, { key: 'Escape' });

    expect(onCloseMock).toHaveBeenCalledTimes(1);
  });

  it('renders quick action buttons for AI Concierge and My Booking', () => {
    renderComponent(true);

    expect(screen.getByRole('link', { name: /AI Concierge/i })).toHaveAttribute('href', '/concierge');
    expect(screen.getAllByRole('link', { name: /My Booking/i })[0]).toHaveAttribute('href', '/guest/reservations');
  });

  it('highlights the active navigation link correctly based on current route', () => {
    renderComponent(true, '/about');

    const knowUsLink = screen.getByText('Know Us').closest('a');
    expect(knowUsLink).toHaveClass('text-[#E2BE65]');
  });

  it('prevents background interaction by setting body overflow to hidden and restores on unmount', () => {
    const { unmount } = renderComponent(true);
    expect(document.body.style.overflow).toBe('hidden');

    unmount();
    expect(document.body.style.overflow).toBe('');
  });

  it('traps focus within the modal dialog on Tab and Shift+Tab', () => {
    renderComponent(true);

    const dialog = screen.getByRole('dialog');
    const focusableElements = dialog.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled])'
    );
    expect(focusableElements.length).toBeGreaterThan(2);

    const firstEl = focusableElements[0];
    const lastEl = focusableElements[focusableElements.length - 1];

    // Focus on last element and press Tab -> should wrap to first element
    lastEl.focus();
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: false });
    expect(document.activeElement).toBe(firstEl);

    // Focus on first element and press Shift+Tab -> should wrap to last element
    firstEl.focus();
    fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
    expect(document.activeElement).toBe(lastEl);
  });

  it('contains motion-reduce styles for users with reduced motion preferences', () => {
    renderComponent(true);
    const dialog = screen.getByRole('dialog');
    expect(dialog.className).toContain('motion-reduce:transition-none');
  });
});
