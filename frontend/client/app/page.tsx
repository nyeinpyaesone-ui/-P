/**
 * ERP03 Client Portal - Next.js Entry Point
 * 
 * Main application component for the customer-facing portal.
 * Provides client access to orders, invoices, and account management.
 */
'use client';

import React from 'react';

export default function Home() {
  return (
    <main style={styles.main}>
      <div style={styles.container}>
        <header style={styles.header}>
          <h1 style={styles.title}>ERP03 Client Portal</h1>
          <p style={styles.subtitle}>Your Business Dashboard</p>
        </header>

        <div style={styles.hero}>
          <h2>Welcome to Your Business Hub</h2>
          <p>Manage your orders, track shipments, and access invoices all in one place.</p>
        </div>

        <div style={styles.grid}>
          <FeatureCard
            title="My Orders"
            description="View and track all your orders"
            icon="🛒"
            features={['Order History', 'Track Shipments', 'Reorder']}
          />
          <FeatureCard
            title="Invoices"
            description="Access your billing documents"
            icon="📄"
            features={['View Invoices', 'Download PDFs', 'Payment Status']}
          />
          <FeatureCard
            title="Products"
            description="Browse our product catalog"
            icon="🏪"
            features={['Product Catalog', 'Pricing', 'Availability']}
          />
          <FeatureCard
            title="Support"
            description="Get help when you need it"
            icon="💬"
            features={['Ticket System', 'Live Chat', 'FAQ']}
          />
          <FeatureCard
            title="Account"
            description="Manage your profile settings"
            icon="⚙️"
            features={['Profile', 'Addresses', 'Preferences']}
          />
          <FeatureCard
            title="Reports"
            description="Business analytics and insights"
            icon="📊"
            features=['Sales Reports', 'Usage Analytics', 'Exports']}
          />
        </div>

        <footer style={styles.footer}>
          <p>ERP03 v1.0.0 | Client Portal</p>
          <div style={styles.status}>
            <span style={styles.statusDot}>●</span>
            All Systems Online
          </div>
        </footer>
      </div>
    </main>
  );
}

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  features: string[];
}

function FeatureCard({ title, description, icon, features }: FeatureCardProps) {
  return (
    <div style={styles.card}>
      <div style={styles.cardIcon}>{icon}</div>
      <h3 style={styles.cardTitle}>{title}</h3>
      <p style={styles.cardDescription}>{description}</p>
      <ul style={styles.featureList}>
        {features.map((feature, index) => (
          <li key={index} style={styles.featureItem}>✓ {feature}</li>
        ))}
      </ul>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  main: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
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
    marginBottom: '40px',
  },
  title: {
    fontSize: '3rem',
    fontWeight: '700',
    marginBottom: '10px',
    background: 'linear-gradient(90deg, #ff6b6b, #feca57)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    fontSize: '1.2rem',
    color: '#a0a0a0',
  },
  hero: {
    textAlign: 'center',
    padding: '40px 20px',
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    marginBottom: '40px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '24px',
    marginBottom: '60px',
  },
  card: {
    background: 'rgba(255, 255, 255, 0.08)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderRadius: '16px',
    padding: '28px',
    transition: 'all 0.3s ease',
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
    fontSize: '0.95rem',
    color: '#b0b0b0',
    marginBottom: '16px',
    lineHeight: '1.5',
  },
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  featureItem: {
    fontSize: '0.85rem',
    color: '#00ff88',
    marginBottom: '6px',
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
