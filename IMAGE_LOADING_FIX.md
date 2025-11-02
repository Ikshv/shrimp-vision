# Image Loading Fix - Complete Solution

## Problem
Images were not loading in the annotation page and other pages of the application.

## Root Causes Identified

### 1. **Missing Next.js Proxy for Static Files**
- Next.js was only proxying `/api/*` requests to the backend
- Images served from `/static/*` were not being proxied
- This caused 404 errors or CORS issues

### 2. **Port Conflict**
- Frontend was trying to run on port 3000 (already in use)
- Needed to configure frontend to run on port 3099

### 3. **Incorrect Image URL Generation**
- `getImageUrl()` was always returning full URLs with `http://localhost:3100`
- Should use relative URLs in the browser to leverage Next.js proxy

## Solutions Applied

### 1. Updated Next.js Proxy Configuration
**File**: `frontend/next.config.js`

Added static file proxying:
```javascript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:3100/api/:path*',
    },
    {
      source: '/static/:path*',
      destination: 'http://localhost:3100/static/:path*',  // NEW
    },
  ]
}
```

### 2. Updated Image URL Generation
**File**: `frontend/lib/config.ts`

Modified `getImageUrl()` to use relative paths in the browser:
```typescript
export function getImageUrl(imagePath: string): string {
  // If the path already starts with http, return as is
  if (imagePath.startsWith('http')) {
    return imagePath
  }
  
  // In development/browser, use relative paths (proxied by Next.js)
  // This avoids CORS issues and uses the Next.js rewrite rules
  const useProxy = typeof window !== 'undefined'
  
  // If the path starts with /static, return as-is for proxy
  if (imagePath.startsWith('/static')) {
    return useProxy ? imagePath : `${API_BASE_URL}${imagePath}`
  }
  
  // Build full path with /static/uploads prefix
  const fullPath = imagePath.startsWith('/') 
    ? `/static/uploads${imagePath}` 
    : `/static/uploads/${imagePath}`
    
  return useProxy ? fullPath : `${API_BASE_URL}${fullPath}`
}
```

**Key Changes**:
- Detects if running in browser (`typeof window !== 'undefined'`)
- Returns relative paths `/static/...` in browser (proxied by Next.js)
- Returns full URLs `http://localhost:3100/static/...` during SSR

### 3. Fixed Port Configuration
**File**: `frontend/package.json`

Updated dev and start scripts:
```json
"scripts": {
  "dev": "next dev -p 3099",
  "start": "next start -p 3099"
}
```

### 4. Enhanced Image Rendering (from previous fix)
**Files**: All page components

- Fixed canvas sizing in annotation tool
- Added error handling for failed image loads
- Added window resize support
- Added proper onLoad callbacks

## How It Works Now

### Request Flow
1. **Frontend renders** → Image tag requests `/static/uploads/image.jpg`
2. **Next.js intercepts** → Rewrites to `http://localhost:3100/static/uploads/image.jpg`
3. **Backend serves** → FastAPI static files middleware returns the image
4. **Browser receives** → Image displays correctly, no CORS issues

### Benefits
✅ No CORS issues (same-origin requests)  
✅ Clean relative URLs in browser  
✅ SSR compatibility maintained  
✅ Development and production ready  
✅ Works with Next.js Image component  

## Testing Checklist

- [x] Backend running on port 3100
- [x] Frontend running on port 3099
- [x] Static file proxy configured
- [x] Image URL generation updated
- [x] Annotation page images load correctly
- [x] Gallery page images load correctly
- [x] Upload page thumbnails load correctly
- [x] Test page inference results load correctly

## URLs to Access

- **Frontend**: http://localhost:3099
- **Backend API**: http://localhost:3100
- **Backend Docs**: http://localhost:3100/docs
- **Static Images**: http://localhost:3099/static/uploads/ (proxied to backend)

## Troubleshooting

### If images still don't load:

1. **Check backend is running**:
   ```bash
   lsof -i:3100
   ```

2. **Check frontend is running**:
   ```bash
   lsof -i:3099
   ```

3. **Verify image path in response**:
   - Open browser DevTools → Network tab
   - Check the image request path
   - Should be `/static/uploads/...` not `http://localhost:3100/static/...`

4. **Check backend static directory**:
   ```bash
   ls -la backend/static/uploads/
   ```

5. **Test direct backend access**:
   ```bash
   curl http://localhost:3100/static/uploads/[filename]
   ```

6. **Test through Next.js proxy**:
   ```bash
   curl http://localhost:3099/static/uploads/[filename]
   ```

## Files Modified

### Configuration
- ✅ `frontend/next.config.js` - Added static file proxy
- ✅ `frontend/package.json` - Changed port to 3099
- ✅ `frontend/lib/config.ts` - Updated image URL generation

### Components (from previous rendering fix)
- ✅ `frontend/app/annotate/page.tsx`
- ✅ `frontend/app/gallery/page.tsx`
- ✅ `frontend/app/upload/page.tsx`
- ✅ `frontend/app/test/page.tsx`

## Next Steps

Images should now load correctly across all pages. If you encounter any issues:

1. Restart both backend and frontend servers
2. Clear browser cache
3. Check browser console for errors
4. Verify image files exist in `backend/static/uploads/`





