import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="container mx-auto px-6 py-16 text-center">
      <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4">
        Unlock Your Perfect Badminton Smash
      </h2>
      <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mb-8">
        Upload a video of your smash and get instant, AI-powered feedback. Our engine analyzes your form against professional data to provide actionable insights, injury risk assessment, and personalized drills.
      </p>
      <Link
        to="/analyze"
        className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-3 px-8 rounded-full text-lg transition-transform transform hover:scale-105"
      >
        Get Started
      </Link>
    </div>
  );
};

export default HomePage;