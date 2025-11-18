/**
 * Configuration utilities for the Shrimp Vision application
 */

// Backend API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3100'

/**
 * Get the full URL for an image path
 * @param imagePath - The relative path to the image (e.g., "/static/uploads/filename.jpg")
 * @returns The full URL to the image
 */
export function getImageUrl(imagePath: string): string {
  // If the path already starts with http, return as is
  if (imagePath.startsWith('http')) {
    return imagePath
  }
  
  // In development/browser, use relative paths (proxied by Next.js)
  // This avoids CORS issues and uses the Next.js rewrite rules
  const useProxy = typeof window !== 'undefined'
  
  // If the path starts with /static, return as-is for proxy or with base URL for SSR
  if (imagePath.startsWith('/static')) {
    return useProxy ? imagePath : `${API_BASE_URL}${imagePath}`
  }
  
  // If it's a relative path, assume it's in the uploads directory
  if (imagePath.startsWith('/')) {
    const fullPath = `/static/uploads${imagePath}`
    return useProxy ? fullPath : `${API_BASE_URL}${fullPath}`
  }
  
  // If it's just a filename, prepend the uploads path
  const fullPath = `/static/uploads/${imagePath}`
  return useProxy ? fullPath : `${API_BASE_URL}${fullPath}`
}

/**
 * Get the API base URL
 * @returns The base URL for API calls
 */
export function getApiUrl(): string {
  return API_BASE_URL
}

/**
 * Get the full API endpoint URL
 * @param endpoint - The API endpoint path (e.g., "/api/upload/list")
 * @returns The full URL to the API endpoint
 */
export function getApiEndpoint(endpoint: string): string {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  
  // If it already includes the API prefix, use as is
  if (cleanEndpoint.startsWith('api/')) {
    return `${API_BASE_URL}/${cleanEndpoint}`
  }
  
  // Otherwise, add the API prefix
  return `${API_BASE_URL}/api/${cleanEndpoint}`
}
