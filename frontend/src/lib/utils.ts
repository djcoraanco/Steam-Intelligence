import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return "N/A";
  return new Intl.NumberFormat().format(num);
}

export function formatPrice(cents: number | null | undefined, currency: string = "USD"): string {
  if (cents === null || cents === undefined) return "N/A";
  if (cents === 0) return "Free";
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(cents / 100);
}
