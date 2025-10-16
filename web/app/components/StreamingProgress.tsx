'use client';

interface StreamingProgressProps {
  stage: string;
  message: string;
}

export default function StreamingProgress({ stage, message }: StreamingProgressProps) {
  const stages = ['ingest', 'extract', 'analyze', 'done'];
  const currentIndex = stages.indexOf(stage);

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h3 className="text-lg font-semibold mb-4 dark:text-white">Analysis Progress</h3>
      
      <div className="space-y-4">
        {stages.slice(0, -1).map((s, idx) => {
          const isActive = idx === currentIndex;
          const isComplete = idx < currentIndex;
          
          return (
            <div key={s} className="flex items-center gap-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                  isComplete
                    ? 'bg-green-500 text-white'
                    : isActive
                    ? 'bg-blue-500 text-white animate-pulse'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-500'
                }`}
              >
                {isComplete ? '✓' : idx + 1}
              </div>
              <div className="flex-1">
                <p className={`font-medium ${isActive ? 'text-blue-600 dark:text-blue-400' : 'dark:text-gray-300'}`}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </p>
                {isActive && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
