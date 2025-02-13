// src/pages/HomePage.jsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import RecommendationSection from '../components/RecommendationSection';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const userId = localStorage.getItem('userId');
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['home-recommendations'],
    queryFn: async () => {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/recommendations/home?user_id=${userId}`);
      if (!res.ok) throw new Error(`Failed to fetch recommendations: ${res.statusText}`);
      return res.json();
    },
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary/60" />
        <span className="text-lg font-medium text-gray-500 animate-pulse">
          Curating your recommendations...
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] space-y-4">
        <div className="bg-destructive/10 p-4 rounded-full">
          <span className="text-2xl">⚠️</span>
        </div>
        <p className="text-destructive font-medium">Failed to load recommendations</p>
        <p className="text-gray-500 text-sm">Please try refreshing the page</p>
      </div>
    );
  }

  return (
    <main className="container max-w-7xl mx-auto px-4 sm:px-6 pt-24 pb-12 space-y-16">
      {data?.personalized?.length > 0 && (
        <RecommendationSection
          title="Recommended for You"
          products={data.personalized}
          gradient="from-primary/10 to-background"
        />
      )}

      <RecommendationSection
        title="Trending Now"
        products={data?.trending || []}
        gradient="from-rose-100/50 to-background"
      />

      <RecommendationSection
        title="Best Value Deals"
        products={data?.best_value || []}
        gradient="from-emerald-100/50 to-background"
      />

      {Object.entries(data?.top_categories || {}).map(([category, products]) => (
        <RecommendationSection
          key={category}
          title={`Top in ${category}`}
          products={products}
          className="bg-gradient-to-r from-purple-100/30 to-background"
        />
      ))}

      <RecommendationSection
        title="Discover More"
        products={data?.diverse_picks || []}
        gradient="from-amber-100/50 to-background"
      />
    </main>
  );
};

export default HomePage;