import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://vvplwmwmrkqsodfwllrd.supabase.co';
const supabaseAnonKey = 'sb_publishable_7gbBM6fzNwpgvaYDDgUOyA_1HlFu5Y_';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
