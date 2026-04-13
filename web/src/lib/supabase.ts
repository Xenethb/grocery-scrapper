// web/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// If either of these is missing, the client won't work
if (!supabaseUrl || !supabaseKey) {
  console.error("Supabase environment variables are missing!")
}

export const supabase = createClient(supabaseUrl, supabaseKey)