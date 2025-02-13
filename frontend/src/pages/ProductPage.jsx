// src/pages/ProductPage.jsx
import { useQuery } from "@tanstack/react-query";
import { useParams, useLocation } from "react-router-dom";
import { Loader2, Star } from "lucide-react";
import { Badge } from "../components/ui/badge";
import RecommendationSection from "../components/RecommendationSection";
import { logInteraction } from "../lib/interaction";

const ProductPage = () => {
  const { id } = useParams();
  const productId = id.toUpperCase();
  const { state } = useLocation();
  const cachedProduct = state?.product;
  const userId = localStorage.getItem('userId');

  const { data, isLoading, error } = useQuery({
    queryKey: [`product-${id}`],
    queryFn: async () => {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/recommendations/product/${productId}?response_limit=20`
      );
      if (!response.ok) throw new Error("Failed to fetch product");
      return response.json();
    },
    onSuccess: (data) => {
      logInteraction({
        user_id: userId,
        event_type: "product_click",
        product_id: productId,
      });
    },
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary/60" />
        <span className="text-gray-500 font-medium">Loading product details...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container py-8 text-center space-y-4">
        <div className="bg-destructive/10 p-4 rounded-full inline-block">
          <span className="text-2xl">⚠️</span>
        </div>
        <p className="text-destructive font-medium">Failed to load product details</p>
      </div>
    );
  }

  const product = cachedProduct || data?.similar.find(p => p.id.toUpperCase() === productId);

  if (!product) {
    return (
      <div className="container py-8 text-center space-y-4">
        <div className="bg-muted p-4 rounded-full inline-block">
          <span className="text-2xl">🔍</span>
        </div>
        <p className="text-gray-700 font-medium">Product not found</p>
      </div>
    );
  }

  return (
    <div className="container max-w-7xl mx-auto px-4 sm:px-6 pt-24 pb-12 space-y-16">
      <div className="grid md:grid-cols-2 gap-12 mb-20">
        {/* Product Image */}
        <div className="aspect-square rounded-xl overflow-hidden">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-contain transform transition-transform duration-300 hover:scale-105"
          />
        </div>

        {/* Product Details */}
        <div className="space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900">{product.name}</h1>
            <div className="inline-flex items-center px-4 py-2 bg-accent rounded-full">
              <span className="text-sm font-medium uppercase text-primary">
                {product.category}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center bg-background px-4 py-2 rounded-full shadow-sm">
              <Star className="h-6 w-6 fill-yellow-400 text-yellow-400" />
              <span className="ml-2 font-medium text-gray-900">{product.rating}</span>
            </div>
            <span className="text-gray-500">
              ({product.reviews.toLocaleString()} reviews)
            </span>
          </div>

          <div className="space-y-6">
            <div className="flex items-baseline gap-4">
              <span className="text-4xl font-bold text-gray-900">
                ${product.price.toLocaleString()}
              </span>
              {product.original_price > product.price && (
                <div className="flex items-center gap-3">
                  <span className="text-xl text-gray-500 line-through">
                    ${product.original_price.toLocaleString()}
                  </span>
                  <Badge variant="destructive" className="px-3 py-1 text-sm font-medium">
                    Save {Math.round(product.discount_ratio * 100)}%
                  </Badge>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Similar Products */}
      <RecommendationSection
        title="Similar Products"
        products={data?.similar.filter(p => p.id.toUpperCase() !== productId) || []}
        className="bg-gradient-to-r from-blue-50/50 to-background px-4 py-6 rounded-xl"
      />
    </div>
  );
};

export default ProductPage;