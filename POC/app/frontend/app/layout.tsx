import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Revenue Automation POC',
  description: 'Modular Workflow for Revenue Reconciliation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'system-ui, -apple-system, sans-serif', lineHeight: '1.6' }}>
        {children}
      </body>
    </html>
  );
}
