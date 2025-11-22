import React from 'react';

/**
 * Dashboard page component
 * Main page for viewing groups, transactions, and financial stats
 */
export const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Total Groups</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Total Transactions</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">0</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-gray-500 text-sm font-medium">Balance</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">$0.00</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Transactions</h2>
          <p className="text-gray-500">No transactions yet. Create a group and start tracking!</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
