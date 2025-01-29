// components/ProductModal.jsx
const ProductModal = ({ product, recommendations, loading, onClose, onRecommendationClick }) => {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative bg-white rounded-xl mx-4 my-8 p-6 max-w-4xl lg:mx-auto">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
  
          <div className="grid md:grid-cols-2 gap-8">
            <img
              src={product.img_link}
              alt={product.product_name}
              className="w-full h-96 object-contain bg-gray-100 rounded-lg"
            />
            
            <div>
              <h2 className="text-2xl font-bold mb-4">{product.product_name}</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Price</h3>
                  <p className="text-3xl font-bold text-indigo-600">
                    ₹{product.discounted_price}
                    {product.discount_percentage > 0 && (
                      <span className="ml-2 text-lg text-green-600">
                        ({product.discount_percentage}% off)
                      </span>
                    )}
                  </p>
                  {product.actual_price > product.discounted_price && (
                    <p className="text-gray-400 line-through">
                      ₹{product.actual_price}
                    </p>
                  )}
                </div>
  
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Rating</h3>
                  <p className="text-lg">
                    ★ {product.rating} ({product.rating_count} reviews)
                  </p>
                </div>
  
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Description</h3>
                  <p className="text-gray-700 whitespace-pre-line">
                    {product.about_product}
                  </p>
                </div>
              </div>
            </div>
          </div>
  
          <div className="mt-8 pt-8 border-t border-gray-200">
            <h3 className="text-xl font-semibold mb-4">Recommended Products</h3>
            
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            ) : recommendations.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {recommendations.map((item) => (
                    <div
                        key={item.product_id}
                        onClick={() => onRecommendationClick(item)}
                        className={`bg-white rounded-xl shadow-md overflow-hidden cursor-pointer transform transition-all ₹{
                        isLoggedIn
                            ? "hover:scale-105 hover:shadow-lg"
                            : "opacity-75 cursor-not-allowed"
                        }`}
                    >

                        <img
                        src={item.img_link}
                        alt={item.product_name}
                        className="w-full h-48 object-contain bg-gray-100 p-4"
                        />
                        <div className="p-4">
                        <h3 className="font-medium text-gray-900 truncate">
                        {item.product_name}
                        </h3>
                        <div className="mt-2 flex items-center justify-between">
                            <span className="text-lg font-bold text-indigo-600">
                            ₹{item.discounted_price}
                            </span>
                            <div className="flex items-center">
                            <span className="text-yellow-500">★</span>
                            <span className="ml-1 text-gray-600">
                                {item.rating} ({item.rating_count})
                            </span>
                            </div>
                        </div>
                        {item.discount_percentage > 0 && (
                            <div className="mt-2 flex items-center">
                            <span className="line-through text-gray-400 mr-2">
                                ₹{item.actual_price}
                            </span>
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                                {item.discount_percentage}% off
                            </span>
                            </div>
                        )}
                        </div>
                    </div>
                    ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No recommendations available
              </p>
            )}
          </div>
        </div>
      </div>
    )
  }

  export default ProductModal;