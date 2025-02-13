// src/pages/SearchPage.jsx
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import ProductCard from "../components/ProductCard";
import { logInteraction } from "../lib/interaction";

const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const userId = localStorage.getItem('userId');

  const { data, isLoading, error } = useQuery({
    queryKey: [`search-${query}`],
    queryFn: async () => {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/recommendations/search?query=${encodeURIComponent(query)}&response_limit=2000`
      );
      if (!response.ok) throw new Error("Search failed");
      return response.json();
    },
    onSuccess: (data) => {
      logInteraction({
        user_id: userId,
        event_type: "search_query",
        query: query
      });
    },
    enabled: !!query.trim()
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary/60" />
        <span className="text-gray-500 font-medium">Searching for "{query}"...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-8 text-center space-y-4">
        <div className="bg-destructive/10 p-4 rounded-full inline-block">
          <span className="text-2xl">⚠️</span>
        </div>
        <p className="text-destructive font-medium">Failed to load search results</p>
      </div>
    );
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 sm:px-6 pt-24 pb-12 space-y-16">
      <div className="mb-12 space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">
          Search results for <span className="text-primary">"{query}"</span>
        </h1>
        {data?.fallback_reason && (
          <p className="text-gray-500 mt-2">
            Showing popular products instead
          </p>
        )}
      </div>

      {data?.results?.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6 sm:gap-8">
          {data.results.map((product) => (
            <ProductCard 
              key={product.id} 
              product={product} 
              className="hover:border-primary/20 transition-all"
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 space-y-4">
          <div className="bg-muted p-4 rounded-full inline-block">
            <span className="text-2xl">🔍</span>
          </div>
          <p className="text-xl font-medium text-gray-900">No products found</p>
          <p className="text-gray-500 mt-2">Try different search terms</p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;