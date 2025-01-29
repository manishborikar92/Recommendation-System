// Home.jsx
import { useState, useEffect } from 'react'
import axios from 'axios'
import ProductGrid from '../components/ProductGrid'
import ProductModal from '../components/ProductModal'

const Home = () => {//localStorage.setItem('userId', response.userId);
  const [userID, setuserID] = useState(localStorage.getItem('userId') || '')
  const [products, setProducts] = useState({})
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5001/trending')
        setProducts(response.data)
        console.log(response.data)
      } catch (error) {
        console.error('Error fetching products:', error)
      }
    }
    fetchProducts()
  }, [])

  const handleProductClick = async (product) => {
    if (!userID) return
    
    setSelectedProduct(product)
    setLoading(true)
    
    try {
      const response = await axios.post('http://127.0.0.1:5001/recommend', {
        userID,
        product_id: product.product_id
      })
      
      setRecommendations(response.data.recommended_products)
    } catch (error) {
      console.error('Recommendation error:', error)
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = (userID) => {
    localStorage.setItem('userID', userID)
    setuserID(userID)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Trending Products</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {Object.entries(products).map(([category, items]) => (
          <section key={category} className="mb-12">
            <h2 className="text-xl font-semibold mb-4 capitalize">{category}</h2>
            <ProductGrid 
              products={items} 
              onSelect={handleProductClick}
              isLoggedIn={!!userID}
            />
          </section>
        ))}
      </main>

      {selectedProduct && (
        <ProductModal
          product={selectedProduct}
          recommendations={recommendations}
          loading={loading}
          onClose={() => setSelectedProduct(null)}
          onRecommendationClick={handleProductClick}
        />
      )}
    </div>
  )
}

export default Home