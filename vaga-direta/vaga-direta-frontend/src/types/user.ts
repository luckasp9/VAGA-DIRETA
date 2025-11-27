export type User = {
  id: number;
  fullName: string;
  email: string;
  course: string;
  semester: number;
  phone?: string;
  state?: string;
  isAdmin?: boolean;
};
