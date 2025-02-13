// src/components/ProductCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Star } from 'lucide-react';
import { Badge } from './ui/badge';
import { logInteraction } from '../lib/interaction';
import PropTypes from 'prop-types';

const ProductCard = ({ product }) => {
  const userId = localStorage.getItem('userId');
  const handleInteraction = () => {
    logInteraction({
      user_id: userId, // Replace with actual user ID
      event_type: 'product_click',
      product_id: product.id
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <Link
      to={`/product/${product.id.toUpperCase()}`}
      state={{ product }}
      className="group block focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-xl"
      onClick={handleInteraction}
      aria-label={`View ${product.name} details`}
    >
      <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-lg transition-all duration-300 ease-in-out hover:-translate-y-1">
        <div className="aspect-square mb-4 rounded-lg overflow-hidden relative">
          <img
            src={product.image || '/placeholder-product.jpg'}
            alt={product.name}
            loading="lazy"
            className="w-full h-full object-contain transition-transform duration-300 group-hover:scale-105"
            onError={(e) => {
              e.target.src = '/placeholder-product.jpg';
            }}
          />
          {product.discount_ratio > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute top-2 right-2 text-xs px-2 py-1 shadow-sm"
            >
              {Math.round(product.discount_ratio * 100)}% OFF
            </Badge>
          )}
        </div>

        <h3 className="font-medium mb-1 truncate text-gray-900">
          {product.name}
        </h3>
        
        <div className="flex items-center gap-2 mb-2">
          <div className="flex items-center bg-muted px-2 py-1 rounded-md">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm ml-1 font-medium text-gray-700">
              {product.rating?.toFixed(1) || 'N/A'}
            </span>
          </div>
          <span className="text-sm text-gray-500">
            ({product.reviews?.toLocaleString() || 0} reviews)
          </span>
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-lg font-bold text-primary">
            {formatCurrency(product.price)}
          </span>
          {product.original_price > product.price && (
            <span className="text-sm text-gray-500 line-through">
              {formatCurrency(product.original_price)}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

ProductCard.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    image: PropTypes.string,
    rating: PropTypes.number,
    reviews: PropTypes.number,
    price: PropTypes.number.isRequired,
    original_price: PropTypes.number,
    discount_ratio: PropTypes.number
  }).isRequired
};

export default React.memo(ProductCard);