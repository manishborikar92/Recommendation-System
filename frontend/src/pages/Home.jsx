// Home.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import ProductGrid from '../components/ProductGrid';
import ProductModal from '../components/ProductModal';

const Home = () => {
  const [userId, setuserId] = useState(localStorage.getItem('userId') || '');
  const [username, setusername] = useState(localStorage.getItem('username') || '');
  const [products, setProducts] = useState({});
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setError('');
        const response = await axios.get('http://127.0.0.1:5001/trending');
        setProducts(response.data);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('Failed to load products. Please try again later.');
      }
    };
    
    fetchProducts();
  }, []);

  const handleProductClick = async (product) => {
    if (!userId) {
      setError('Please sign in to view product details and recommendations');
      return;
    }

    setSelectedProduct(product);
    setLoading(true);
    
    try {
      const response = await axios.post('http://127.0.0.1:5001/recommend', {
        userId,
        product_id: product.product_id
      });
      
      setRecommendations(response.data.recommended_products || []);
      setError('');
    } catch (err) {
      console.error('Recommendation error:', err);
      setError('Failed to load recommendations. Please try again.');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Recommendation System</h1>
          <div className="flex items-center gap-4">
            {userId ? (
              <span className="text-gray-600">Welcome, {username}!</span>
            ) : (
              <button
                onClick={() => window.location.href = "/login"}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-8 p-4 bg-red-50 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {Object.keys(products).length === 0 && !error ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="animate-pulse bg-white rounded-xl p-4 shadow-sm">
                <div className="aspect-square bg-gray-200 rounded-lg mb-4" />
                <div className="h-4 bg-gray-200 rounded mb-3 w-3/4" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Overall Top Products */}
            {products.overall_top && products.overall_top.length > 0 && (
              <section key="overall_top" className="mb-12">
                <h2 className="text-xl font-semibold mb-6 capitalize text-gray-800">
                  Overall Top Products
                </h2>
                <ProductGrid 
                  products={products.overall_top} 
                  onSelect={handleProductClick}
                  isLoggedIn={!!userId}
                />
              </section>
            )}

            {/* Category Top Products */}
            {products.category_top && Object.entries(products.category_top).map(([category, items]) => (
              <section key={category} className="mb-12">
                <h2 className="text-xl font-semibold mb-6 capitalize text-gray-800">
                  {category.replace(/\|/g, ' > ').replace(/_/g, ' ').replace(/&/g, ' & ')}
                </h2>
                <ProductGrid 
                  products={items} 
                  onSelect={handleProductClick}
                  isLoggedIn={!!userId}
                />
              </section>
            ))}

            {/* Similar Products */}
            {products.similar_products && Object.entries(products.similar_products).map(([category, items]) => (
              <section key={category} className="mb-12">
                <h2 className="text-xl font-semibold mb-6 capitalize text-gray-800">
                  Similar Products in {category.replace(/\|/g, ' > ').replace(/_/g, ' ').replace(/&/g, ' & ')}
                </h2>
                <ProductGrid 
                  products={items} 
                  onSelect={handleProductClick}
                  isLoggedIn={!!userId}
                />
              </section>
            ))}
          </>
        )}
      </main>

      {selectedProduct && (
        <ProductModal
          product={selectedProduct}
          recommendations={recommendations}
          loading={loading}
          isLoggedIn={!!userId}
          onClose={() => setSelectedProduct(null)}
          onRecommendationClick={handleProductClick}
        />
      )}
    </div>
  );
};

export default Home;