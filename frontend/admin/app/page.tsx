/**
 * ERP03 Admin Dashboard - Next.js Entry Point
 * 
 * Main application component for the admin dashboard.
 * Provides enterprise resource planning administration interface.
 */
'use client';

import React from 'react';

export default function Home() {
  return (
    <main style={styles.main}>
      <div style={styles.container}>
        <header style={styles.header}>
          <h1 style={styles.title}>ERP03 Admin Dashboard</h1>
          <p style={styles.subtitle}>Enterprise Resource Planning System</p>
        </header>

        <div style={styles.grid}>
          <ModuleCard
            title="Accounting"
            description="Financial management, general ledger, and reporting"
            icon="📊"
          />
          <ModuleCard
            title="Sales"
            description="Sales orders, invoices, and customer management"
            icon="💼"
          />
          <ModuleCard
            title="Inventory"
            description="Stock tracking and inventory management"
            icon="📦"
          />
          <ModuleCard
            title="HR"
            description="Human resources and employee management"
            icon="👥"
          />
          <ModuleCard
            title="CRM"
            description="Customer relationship management"
            icon="🤝"
          />
          <ModuleCard
            title="Warehouse"
            description="Warehouse operations and logistics"
            icon="🏭"
          />
          <ModuleCard
            title="Logistics"
            description="Supply chain and transportation management"
            icon="🚚"
          />
          <ModuleCard
            title="Reporting"
            description="Analytics and business intelligence"
            icon="📈"
          />
        </div>

        <footer style={styles.footer}>
          <p>ERP03 v1.0.0 | Admin Portal</p>
          <div style={styles.status}>
            <span style={styles.statusDot}>●</span>
            System Operational
          </div>
        </footer>
      </div>
    </main>
  );
}

interface ModuleCardProps {
  title: string;
  description: string;
  icon: string;
}

function ModuleCard({ title, description, icon }: ModuleCardProps) {
  return (
    <div style={styles.card}>
      <div style={styles.cardIcon}>{icon}</div>
      <h3 style={styles.cardTitle}>{title}</h3>
      <p style={styles.cardDescription}>{description}</p>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  main: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    color: '#ffffff',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '60px',
  },
  title: {
    fontSize: '3rem',
    fontWeight: '700',
    marginBottom: '10px',
    background: 'linear-gradient(90deg, #00d9ff, #00ff88)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    fontSize: '1.2rem',
    color: '#a0a0a0',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '24px',
    marginBottom: '60px',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '24px',
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  },
  cardIcon: {
    fontSize: '3rem',
    marginBottom: '16px',
  },
  cardTitle: {
    fontSize: '1.5rem',
    fontWeight: '600',
    marginBottom: '8px',
  },
  cardDescription: {
    fontSize: '0.9rem',
    color: '#a0a0a0',
    lineHeight: '1.5',
  },
  footer: {
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    paddingTop: '30px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '20px',
  },
  status: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '0.9rem',
    color: '#00ff88',
  },
  statusDot: {
    fontSize: '0.8rem',
  },
};
