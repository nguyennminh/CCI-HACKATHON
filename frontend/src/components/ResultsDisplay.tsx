import React from 'react';

// --- TypeScript Interfaces for Type-Safety ---
interface CriticalIssue {
  body_part: string;
  problem: string;
  injury_risk: string;
  correction: string;
  drill: string;
}

interface FeedbackData {
  overall_score: number;
  injury_risk: 'LOW' | 'MODERATE' | 'HIGH';
  injury_risk_explanation: string;
  critical_issues: CriticalIssue[];
  positive_feedback: string;
  summary: string;
}

interface Props {
  feedback: FeedbackData;
  gifUrl: string;
}

const ResultsDisplay: React.FC<Props> = ({ feedback, gifUrl }) => {
  const scoreColor = feedback.overall_score > 70 ? 'text-green-400' : feedback.overall_score > 50 ? 'text-yellow-400' : 'text-red-400';
  const riskColor = feedback.injury_risk === 'HIGH' ? 'bg-red-500' : feedback.injury_risk === 'MODERATE' ? 'bg-yellow-500' : 'bg-green-500';

  return (
    <div className="w-full max-w-5xl mx-auto p-4 space-y-8">
      <h2 className="text-3xl font-bold text-center">Your Smash Analysis</h2>

      {/* --- Top Section: Score, GIF, and Summary --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        <div className="bg-gray-800 rounded-lg p-6 space-y-4">
          <div className="flex justify-between items-baseline">
            <h3 className="text-xl font-semibold text-cyan-400">Overall Score</h3>
            <p className={`text-5xl font-bold ${scoreColor}`}>{feedback.overall_score}<span className="text-3xl text-gray-400">/100</span></p>
          </div>
          <div className="flex justify-between items-baseline">
            <h3 className="text-xl font-semibold text-cyan-400">Injury Risk</h3>
            <span className={`px-4 py-1 rounded-full text-white font-semibold ${riskColor}`}>{feedback.injury_risk}</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-300 mb-1">Summary:</h4>
            <p className="text-gray-400">{feedback.summary}</p>
          </div>
           <div>
            <h4 className="font-semibold text-gray-300 mb-1">What You're Doing Well:</h4>
            <p className="text-gray-400">{feedback.positive_feedback}</p>
          </div>
        </div>
        <div className="flex justify-center">
            <img src={`http://127.0.0.1:8000${gifUrl}?t=${new Date().getTime()}`} alt="Smash Animation" className="rounded-lg border-2 border-gray-700 max-w-full h-auto" />
        </div>
      </div>

      {/* --- Areas for Improvement --- */}
      <div>
        <h3 className="text-2xl font-bold mb-4 text-center">⚠️ Areas for Improvement</h3>
        <div className="space-y-4">
          {feedback.critical_issues.map((issue, index) => (
            <div key={index} className="bg-gray-800 rounded-lg p-5">
              <h4 className="text-lg font-bold capitalize text-cyan-400 mb-2">{issue.body_part}</h4>
              <p><strong className="text-red-400">Problem:</strong> {issue.problem}</p>
              <p><strong className="text-yellow-400">Injury Risk:</strong> {issue.injury_risk}</p>
              <p><strong className="text-green-400">Correction:</strong> {issue.correction}</p>
              <p><strong className="text-blue-400">Drill:</strong> {issue.drill}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;