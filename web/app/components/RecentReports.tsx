'use client';

import { useEffect, useState } from 'react';

interface Report {
  id: number;
  doc_name: string;
  summary: string;
  overall_risk: number;
  ts: number;
}

export default function RecentReports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/reports?limit=5`);
      const data = await res.json();
      setReports(data.reports || []);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        <h3 className="text-xl font-bold mb-4 dark:text-white">Recent Reports</h3>
        <p className="text-gray-500 dark:text-gray-400">Loading...</p>
      </div>
    );
  }

  if (reports.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold mb-4 dark:text-white">Recent Reports</h3>
      <div className="space-y-3">
        {reports.map((report) => (
          <div
            key={report.id}
            className="p-4 border dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-semibold dark:text-white">{report.doc_name}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                  {report.summary}
                </p>
              </div>
              <div className="ml-4 text-right">
                <span className={`text-sm font-medium ${
                  report.overall_risk <= 0.4 ? 'text-green-600 dark:text-green-400' :
                  report.overall_risk <= 0.7 ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-red-600 dark:text-red-400'
                }`}>
                  {(report.overall_risk * 100).toFixed(1)}%
                </span>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  {new Date(report.ts).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
