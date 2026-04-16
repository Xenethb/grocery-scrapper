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

  // --- 1. Modern 2026 Autocomplete Logic ---
  useEffect(() => {
    const getSuggestions = async () => {
      if (addressInput.length < 3 || userCoords) {
        setSuggestions([]);
        return;
      }

      try {
        const { AutocompleteSuggestion, AutocompleteSessionToken } = 
          await (window as any).google.maps.importLibrary("places");

        const token = new AutocompleteSessionToken();
        const request = {
          input: addressInput,
          includedRegionCodes: ["lk"],
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

  // --- 2. Live Google Search Logic (Fixed Method Names) ---
  const calculateNearestStores = async (lat: number, lng: number) => {
    setIsLocating(true); // Start loading state
    try {
      const { Place } = await (window as any).google.maps.importLibrary("places");

      const findClosestGoogleStore = async (chainName: string): Promise<StoreLocation | null> => {
        const center = new (window as any).google.maps.LatLng(lat, lng);

        // searchByText is the correct 2026 method for brand-name searches
        const request = {
          textQuery: chainName,
          fields: ["displayName", "location", "formattedAddress"],
          locationBias: { center: center, radius: 2000 }, // Search within 2km bias
          maxResultCount: 1,
        };

        const { places } = await Place.searchByText(request);

        if (places && places.length > 0) {
          const store = places[0];
          const sLat = store.location.lat();
          const sLng = store.location.lng();
          
          return {
            logo: chainName[0].toUpperCase(),
            name: chainName,
            branch: store.displayName || chainName,
            address: store.formattedAddress || "Sri Lanka",
            distance: calculateDistance(lat, lng, sLat, sLng),
          };
        }
        return null;
      };

      // Query Google for all branches in parallel
      const [keells, glomark, cargills] = await Promise.all([
        findClosestGoogleStore("Keells Super"),
        findClosestGoogleStore("Glomark"),
        findClosestGoogleStore("Cargills Food City"),
      ]);

      setNearestBranches({
        keells: keells || { name: "Keells", branch: "Not Found", distance: 0, logo: "K", address: "" },
        glomark: glomark || { name: "Glomark", branch: "Not Found", distance: 0, logo: "G", address: "" },
        cargills: cargills || { name: "Cargills", branch: "Not Found", distance: 0, logo: "C", address: "" },
      });

    } catch (error) {
      console.error("Google API Search Error:", error);
    } finally {
      setIsLocating(false); // End loading state
    }
  };

  // --- 3. Handle Selection ---
  const handleSelect = async (suggestion: any) => {
    const placePrediction = suggestion.placePrediction;
    setAddressInput(placePrediction.text.text);
    setSuggestions([]);

    try {
      const { Place } = await (window as any).google.maps.importLibrary("places");
      const myPlace = new Place({ id: placePrediction.placeId });
      
      await myPlace.fetchFields({ fields: ["location", "displayName"] });

      const lat = myPlace.location.lat();
      const lng = myPlace.location.lng();

      setUserCoords({ lat, lng });
      setDisplayLocation(myPlace.displayName || placePrediction.text.text.split(',')[0]);
      
      // Immediately calculate the stores from the API
      await calculateNearestStores(lat, lng);
    } catch (error) {
      console.error("Place selection error:", error);
    }
  };

  // --- 4. Product Search Logic ---
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || !userCoords) return;
    
    setHasSearched(true);
    setIsLoading(true);
    setSelectedProduct(null); // Clear previous selection to avoid UI confusion

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
                  initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  className="absolute top-[110%] left-0 w-full bg-white border border-gray-200 rounded-xl shadow-2xl overflow-hidden z-[60]"
                >
                  {suggestions.map((s, i) => (
                    <li key={i} onClick={() => handleSelect(s)}
                      className="px-4 py-3 hover:bg-green-50 cursor-pointer flex items-start gap-3 border-b border-gray-50 last:border-none"
                    >
                      <Navigation className="w-4 h-4 text-gray-400 mt-1" />
                      <div className="text-[13px] text-gray-700 leading-tight">{s.placePrediction.text.text}</div>
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
              
              <div className="min-h-[400px]">
                {/* Fixed the detail showing logic here */}
                {selectedProduct && nearestBranches ? (
                  <PriceAnalysis
                    product={selectedProduct}
                    storeLocations={nearestBranches}
                    location={displayLocation}
                  />
                ) : (
                  <div className="h-full border-2 border-dashed border-gray-200 rounded-3xl flex flex-col items-center justify-center text-gray-400 p-12">
                    {isLocating ? (
                      <div className="flex flex-col items-center">
                        <Loader2 className="w-10 h-10 animate-spin mb-4 text-green-500" />
                        <p className="font-medium text-gray-600 text-center">Google is calculating exact distances...</p>
                      </div>
                    ) : (
                      <p className="text-center">Select a product to compare store prices</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}