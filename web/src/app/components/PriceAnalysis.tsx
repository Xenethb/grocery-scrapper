// web/src/app/components/PriceAnalysis.tsx
import { motion } from "motion/react";
import { Check, X, MapPin } from "lucide-react";
import { Product, StoreLocation } from "../../lib/types"; // Import both types

interface PriceAnalysisProps {
  product: Product;
  storeLocations: {
    keells: StoreLocation;
    glomark: StoreLocation;
    cargills: StoreLocation;
  };
  location: string;
}

export default function PriceAnalysis({ product, storeLocations, location }: PriceAnalysisProps) {
  const stores = [
    { key: 'keells', ...storeLocations.keells, ...product.prices.keells },
    { key: 'glomark', ...storeLocations.glomark, ...product.prices.glomark },
    { key: 'cargills', ...storeLocations.cargills, ...product.prices.cargills }
  ];

  // Filter out stores that are unavailable OR have a null price
  const availableStores = stores.filter(store => store.available && store.price !== null);
  
  // Use 'as number' to tell TypeScript we've already filtered out the nulls
  const lowestPrice = availableStores.length > 0
    ? Math.min(...availableStores.map(store => store.price as number))
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-[20px] font-[600] text-gray-900">Price Comparison</h2>
          <p className="text-[13px] text-gray-500 mt-1">{product.name}</p>
        </div>

        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-3 text-left text-[13px] font-[600] text-gray-700 uppercase">Store</th>
              <th className="px-6 py-3 text-left text-[13px] font-[600] text-gray-700 uppercase">Price</th>
              <th className="px-6 py-3 text-left text-[13px] font-[600] text-gray-700 uppercase">Stock</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {stores.map((store, index) => {
              const isLowest = store.available && store.price === lowestPrice && lowestPrice !== null;

              return (
                <tr key={store.key} className={isLowest ? 'bg-green-50' : 'bg-white'}>
                  <td className="px-6 py-4 font-[500]">{store.name}</td>
                  <td className="px-6 py-4">
                    {store.available && store.price ? `Rs. ${store.price}` : <span className="text-gray-400">—</span>}
                    {isLowest && <span className="ml-2 text-[10px] bg-green-200 text-green-800 px-2 py-0.5 rounded">BEST</span>}
                  </td>
                  <td className="px-6 py-4">
                    {store.available ? <Check className="text-green-600 w-5" /> : <X className="text-gray-300 w-5" />}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-[18px] font-[600] mb-4 text-gray-900">Closest to {location}</h2>
        <div className="grid grid-cols-3 gap-4">
          {stores.map((store) => (
            <div key={store.key} className="border rounded-lg p-3">
              <div className="text-[14px] font-bold">{store.name}</div>
              <div className="text-[12px] text-gray-500 mb-2">{store.branch}</div>
              <div className="text-[20px] font-bold text-gray-900">{store.distance} km</div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}