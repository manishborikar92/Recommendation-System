// src/components/RecommendationSection.jsx
import React from 'react';
import ProductCard from './ProductCard';
import PropTypes from 'prop-types';

const RecommendationSection = ({ title, products }) => {
  return (
    <section className="space-y-6 px-4 sm:px-6 lg:px-8">
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      {products.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          {products.map((product) => (
            <ProductCard key={`${product.id}_${Date.now()}`} product={product} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-muted rounded-xl">
          <p className="text-gray-500">No products available in this section</p>
        </div>
      )}
    </section>
  );
};

RecommendationSection.propTypes = {
  title: PropTypes.string.isRequired,
  products: PropTypes.arrayOf(PropTypes.object).isRequired
};

export default React.memo(RecommendationSection);