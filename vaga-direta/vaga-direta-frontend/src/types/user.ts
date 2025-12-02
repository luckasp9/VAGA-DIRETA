export type User = {
  id: number;
  fullName: string;
  email: string;
  course?: string | null;
  semester?: number | null;
  phone?: string | null;
  state?: string | null;
  userType?: string | null;
  isAdmin: boolean; 
};
