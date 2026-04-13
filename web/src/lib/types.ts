// web/src/lib/types.ts
export interface Product {
  id: number;
  name: string;
  portion: string;
  image: string;
  prices: {
    keells: { price: number | null; available: boolean };
    glomark: { price: number | null; available: boolean };
    cargills: { price: number | null; available: boolean };
  };
}

export interface StoreLocation {
  logo: string;
  name: string;
  branch: string;
  address: string;
  distance: number;
}