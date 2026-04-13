// web/src/app/components/ProductList.tsx
import { motion } from "motion/react";
import { Product } from "../../lib/types"; // Import from shared types

interface ProductListProps {
  products: Product[];
  selectedProduct: Product | null;
  onSelectProduct: (product: Product) => void;
  searchQuery: string;
}

export default function ProductList({
  products,
  selectedProduct,
  onSelectProduct,
  searchQuery
}: ProductListProps) {
  return (
    <div>
      <div className="mb-4 text-[14px] text-gray-600">
        {products.length} {products.length === 1 ? 'result' : 'results'} for "{searchQuery}"
      </div>

      <div className="space-y-3">
        {products.map((product, index) => (
          <motion.button
            key={product.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            onClick={() => onSelectProduct(product)}
            className={`w-full flex items-center gap-4 p-4 rounded-lg border-2 transition-all text-left ${
              selectedProduct?.id === product.id
                ? 'border-gray-900 bg-white shadow-md'
                : 'border-gray-200 bg-white hover:border-gray-400'
            }`}
          >
            <img
              src={product.image}
              alt={product.name}
              className="w-20 h-20 object-cover rounded-md flex-shrink-0"
            />

            <div className="flex-1 min-w-0">
              <div className="font-[500] text-[15px] text-gray-900 mb-1">
                {product.name}
              </div>
              <div className="text-[13px] text-gray-500">
                {product.portion}
              </div>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}