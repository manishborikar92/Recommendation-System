// components/ProductGrid.jsx
import React from "react";

const ProductGrid = ({ products, onSelect, isLoggedIn }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <div
          key={product.product_id}
          onClick={() => isLoggedIn && onSelect(product)}
          className={`bg-white rounded-xl shadow-md overflow-hidden cursor-pointer transform transition-all ${
            isLoggedIn
              ? "hover:scale-105 hover:shadow-lg"
              : "opacity-75 cursor-not-allowed"
          }`}
        >
          <img
            src={product.img_link}
            alt={product.product_name}
            className="w-full h-48 object-contain bg-gray-100 p-1"
          />
          <div className="p-4">
            <h3 className="font-medium text-gray-900 truncate">
              {product.product_name}
            </h3>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-lg font-bold text-indigo-600">
                ${product.discounted_price}
              </span>
              <div className="flex items-center">
                <span className="text-yellow-500">★</span>
                <span className="ml-1 text-gray-600">
                  {product.rating} ({product.rating_count})
                </span>
              </div>
            </div>
            {product.discount_percentage > 0 && (
              <div className="mt-2 flex items-center">
                <span className="line-through text-gray-400 mr-2">
                  ${product.actual_price}
                </span>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                  {product.discount_percentage}% off
                </span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProductGrid;
