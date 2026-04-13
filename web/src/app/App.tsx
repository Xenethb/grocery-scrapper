import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { MapPin, Search, Loader2, Navigation, CheckCircle2 } from "lucide-react";
import { supabase } from "../lib/supabase"; 
import { Product, StoreLocation } from "../lib/types"; 
import { calculateDistance } from "../lib/distance";
import ProductList from "./components/ProductList";
import PriceAnalysis from "./components/PriceAnalysis";

export default function App() {
  // --- States ---
  const [addressInput, setAddressInput] = useState("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [displayLocation, setDisplayLocation] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [nearestBranches, setNearestBranches] = useState<any>(null);

  // --- 1. Modern 2026 Autocomplete Logic (Places API New) ---
  useEffect(() => {
    const getSuggestions = async () => {
      // Don't search if input is short or we already picked a location
      if (addressInput.length < 3 || userCoords) {
        setSuggestions([]);
        return;
      }

      try {
        // Import the NEW Places library (Google 2025+ Standard)
        const { AutocompleteSuggestion, AutocompleteSessionToken } = 
          await (window as any).google.maps.importLibrary("places");

        const token = new AutocompleteSessionToken();
        const request = {
          input: addressInput,
          includedRegionCodes: ["lk"], // Strict to Sri Lanka
          sessionToken: token,
        };

        const { suggestions } = await AutocompleteSuggestion.fetchAutocompleteSuggestions(request);
        setSuggestions(suggestions);
      } catch (err) {
        console.error("Autocomplete Error:", err);
      }
    };

    const delay = setTimeout(getSuggestions, 300);
    return () => clearTimeout(delay);
  }, [addressInput, userCoords]);

  // --- 2. Handle Selection and Distance Calculation ---
  const handleSelect = async (suggestion: any) => {
    setIsLocating(true);
    const placePrediction = suggestion.placePrediction;
    setAddressInput(placePrediction.text.text);
    setSuggestions([]);

    try {
      const { Place } = await (window as any).google.maps.importLibrary("places");
      const myPlace = new Place({ id: placePrediction.placeId });
      
      // Fetch precise Lat/Lng for 382 Hokandara etc.
      await myPlace.fetchFields({ fields: ["location", "displayName"] });

      const lat = myPlace.location.lat();
      const lng = myPlace.location.lng();

      setUserCoords({ lat, lng });
      setDisplayLocation(myPlace.displayName || placePrediction.text.text.split(',')[0]);
      
      await calculateNearestStores(lat, lng);
    } catch (error) {
      console.error("Place selection error:", error);
    } finally {
      setIsLocating(false);
    }
  };

  const calculateNearestStores = async (lat: number, lng: number) => {
    const { data: allStores } = await supabase.from('store_locations').select('*');
    if (allStores) {
      const findClosest = (chain: string): StoreLocation => {
        return allStores
          .filter(s => s.store_chain.toLowerCase() === chain.toLowerCase())
          .map(s => ({
            logo: chain[0].toUpperCase(),
            name: s.store_chain,
            branch: s.branch_name,
            address: s.address || "Sri Lanka",
            distance: calculateDistance(lat, lng, s.latitude, s.longitude)
          }))
          .sort((a, b) => a.distance - b.distance)[0];
      };

      setNearestBranches({
        keells: findClosest('Keells'),
        glomark: findClosest('Glomark'),
        cargills: findClosest('Cargills')
      });
    }
  };

  // --- 3. Product Search Logic ---
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || !userCoords) return;
    
    setHasSearched(true);
    setIsLoading(true);

    const { data } = await supabase
      .from('products')
      .select('*')
      .ilike('name', `%${searchQuery}%`)
      .limit(30);

    if (data) {
      const formatted: Product[] = data.map((p: any) => ({
        id: p.id,
        name: p.name,
        portion: "Unit", 
        image: "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400",
        prices: {
          keells: { price: p.keells_price || null, available: !!p.keells_price },
          glomark: { price: p.glomark_price || null, available: !!p.glomark_price },
          cargills: { price: p.cargills_price || null, available: !!p.cargills_price }
        }
      }));
      setProducts(formatted);
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#fafafa]">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-[1440px] mx-auto px-8 py-4 flex items-center justify-between">
          <div className="text-[28px] font-bold tracking-tight text-green-600">PriceFind</div>
          
          <div className="relative w-[500px]">
            <div className={`flex items-center gap-3 px-4 py-2 rounded-lg border transition-all ${userCoords ? 'border-green-500 bg-green-50/20' : 'border-gray-200 bg-gray-50'}`}>
              <MapPin className={`w-5 h-5 ${userCoords ? 'text-green-600' : 'text-gray-400'}`} />
              <div className="flex flex-col flex-1">
                <label className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Your Specific Address:</label>
                <input
                  type="text"
                  value={addressInput}
                  onChange={(e) => {
                    setAddressInput(e.target.value);
                    if (userCoords) setUserCoords(null);
                  }}
                  className="bg-transparent border-none outline-none text-[14px] p-0 text-gray-900 font-medium placeholder:text-gray-400"
                  placeholder="e.g. 382 Hokandara South..."
                />
              </div>
              {userCoords && <CheckCircle2 className="w-5 h-5 text-green-500" />}
            </div>

            <AnimatePresence>
              {suggestions.length > 0 && (
                <motion.ul 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="absolute top-[110%] left-0 w-full bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden z-[60]"
                >
                  {suggestions.map((s, i) => (
                    <li 
                      key={i}
                      onClick={() => handleSelect(s)}
                      className="px-4 py-3 hover:bg-green-50 cursor-pointer flex items-start gap-3 border-b border-gray-50 last:border-none"
                    >
                      <Navigation className="w-4 h-4 text-gray-400 mt-1" />
                      <div className="text-[13px] text-gray-700 leading-tight">
                        {s.placePrediction.text.text}
                      </div>
                    </li>
                  ))}
                </motion.ul>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      <div className="max-w-[1440px] mx-auto px-8 pt-24 pb-16">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-[48px] font-bold text-center mb-8 text-gray-900 tracking-tight leading-tight">
            {userCoords ? (
              <>Compare Grocery Prices in <br/><span className="text-green-600">{displayLocation}</span></>
            ) : (
              <>Find the Cheapest Groceries <br/> <span className="text-gray-300 text-[32px]">Select an address to begin</span></>
            )}
          </h1>

          <form onSubmit={handleSearch} className="max-w-[720px] mx-auto relative group">
            <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400 group-focus-within:text-green-600" />
            <input
              type="text"
              disabled={!userCoords}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={userCoords ? "What are you looking for?" : "Please select your address above first..."}
              className={`w-full pl-16 pr-16 py-5 text-[20px] border-2 rounded-2xl outline-none transition-all shadow-xl ${
                userCoords ? 'border-gray-200 focus:border-green-500 bg-white shadow-gray-100' : 'border-gray-100 bg-gray-50 cursor-not-allowed opacity-50'
              }`}
            />
            {isLoading && <Loader2 className="absolute right-6 top-1/2 -translate-y-1/2 animate-spin text-green-500" />}
          </form>
        </motion.div>
      </div>

      <AnimatePresence>
        {hasSearched && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-[1440px] mx-auto px-8 pb-16">
            <div className="grid grid-cols-[420px_1fr] gap-12">
              <ProductList
                products={products}
                selectedProduct={selectedProduct}
                onSelectProduct={setSelectedProduct}
                searchQuery={searchQuery}
              />
              
              {selectedProduct && nearestBranches ? (
                <PriceAnalysis
                  product={selectedProduct}
                  storeLocations={nearestBranches}
                  location={displayLocation}
                />
              ) : (
                <div className="h-[400px] border-2 border-dashed border-gray-200 rounded-3xl flex flex-col items-center justify-center text-gray-400">
                  {isLocating ? (
                    <div className="flex flex-col items-center">
                      <Loader2 className="w-10 h-10 animate-spin mb-4 text-green-500" />
                      <p className="font-medium text-gray-600">Google is calculating exact distances...</p>
                    </div>
                  ) : (
                    <p>Select a product to compare store prices</p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}