// components/ProductModal.jsx
import { useEffect } from 'react';

const ProductModal = ({ 
  product, 
  recommendations, 
  loading, 
  isLoggedIn,
  onClose, 
  onRecommendationClick 
}) => {
  // Prevent background scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => document.body.style.overflow = 'unset';
  }, []);

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative bg-white rounded-xl mx-4 my-8 p-6 max-w-4xl lg:mx-auto animate-fade-in-up">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors"
          aria-label="Close modal"
        >
          <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="relative aspect-square bg-gray-50 rounded-xl overflow-hidden">
            <img
              src={product.img_link}
              alt={product.product_name}
              className="w-full h-full object-contain p-8 hover:scale-105 transition-transform"
              loading="lazy"
            />
          </div>
          
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900">{product.product_name}</h2>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Price</p>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-indigo-600">
                    ₹{product.discounted_price}
                  </span>
                  {product.discount_percentage > 0 && (
                    <span className="text-sm font-medium text-green-600">
                      ({product.discount_percentage}% off)
                    </span>
                  )}
                </div>
                {product.actual_price > product.discounted_price && (
                  <p className="text-gray-400 line-through mt-1">
                    ₹{product.actual_price}
                  </p>
                )}
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500 mb-1">Rating</p>
                <div className="flex items-center gap-2">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <svg
                        key={i}
                        className={`w-5 h-5 ${i < Math.floor(product.rating) ? 'text-yellow-400' : 'text-gray-300'}`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <span className="text-gray-600">
                    {product.rating} ({product.rating_count.toLocaleString()} reviews)
                  </span>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-500 mb-2">Description</p>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {product.about_product}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <h3 className="text-xl font-semibold mb-6">Recommended Products</h3>
          
          {loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="animate-pulse bg-gray-100 rounded-xl p-4">
                  <div className="aspect-square bg-gray-200 rounded-lg mb-4" />
                  <div className="h-4 bg-gray-200 rounded mb-3 w-3/4" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : recommendations.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {recommendations.map((item) => (
                <div
                  key={item.product_id}
                  onClick={() => isLoggedIn && onRecommendationClick(item)}
                  className={`group relative bg-white rounded-xl shadow-sm hover:shadow-md transition-all ${
                    isLoggedIn 
                      ? 'cursor-pointer hover:-translate-y-1'
                      : 'cursor-not-allowed opacity-70'
                  }`}
                >
                  <div className="aspect-square bg-gray-50 rounded-t-xl overflow-hidden p-4">
                    <img
                      src={item.img_link}
                      alt={item.product_name}
                      className="w-full h-full object-contain transition-transform group-hover:scale-105"
                      loading="lazy"
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="font-medium text-gray-900 truncate mb-2">
                      {item.product_name}
                    </h3>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-indigo-600">
                        ₹{item.discounted_price}
                      </span>
                      <div className="flex items-center text-sm">
                        <span className="text-yellow-500">★</span>
                        <span className="ml-1 text-gray-600">
                          {item.rating} ({item.rating_count})
                        </span>
                      </div>
                    </div>
                    {item.discount_percentage > 0 && (
                      <div className="mt-2 flex items-center justify-between">
                        <span className="line-through text-gray-400 text-sm">
                          ₹{item.actual_price}
                        </span>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                          {item.discount_percentage}% off
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No recommendations available</p>
              {!isLoggedIn && (
                <p className="text-sm text-indigo-600">
                  Sign in to get personalized recommendations
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductModal;